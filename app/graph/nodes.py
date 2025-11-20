from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.agents.base import get_llm
from app.warehouse.client import get_warehouse_client
from app.dq.runner import run_dq_for_table


# ----------------------------------------------------------------------
# Helper: append debug
# ----------------------------------------------------------------------
def _append_debug(state: Dict[str, Any], msg: str) -> None:
    debug = state.get("debug") or []
    debug.append(msg)
    state["debug"] = debug


# ----------------------------------------------------------------------
# Node 1: Intent classifier
# ----------------------------------------------------------------------
def classify_intent_node(state, db: Session):
    """
    Decide which agent should handle the query:
    - metadata
    - dq
    - sql
    - rootcause
    """
    llm = get_llm()
    question = state.get("question", "")

    prompt = f"""
You are Dr. Database's intent classifier.

Classify the user request into exactly one of:
- metadata
- dq
- sql
- rootcause

User question:
{question}

Respond with ONLY one word: metadata, dq, sql, or rootcause.
"""

    resp = llm.invoke(prompt)
    intent = (getattr(resp, "content", str(resp)) or "").strip().lower()

    if intent not in ("metadata", "dq", "sql", "rootcause"):
        intent = "metadata"

    state["intent"] = intent
    _append_debug(state, f"classify_intent → {intent}")
    return state


# ----------------------------------------------------------------------
# Node 2: Metadata agent
# ----------------------------------------------------------------------
def metadata_node(state, db: Session):
    """
    Answer metadata questions about tables/columns using the connected warehouse.
    """
    llm = get_llm()
    client = get_warehouse_client(db)

    all_tables = client.list_tables()

    # user-selected tables from UI (multi-select)
    selected_tables: List[str] = state.get("tables") or []

    metadata_context = {}

    if selected_tables:
        for t in selected_tables:
            try:
                cols = client.get_columns(t)
                metadata_context[t] = cols
            except Exception as e:
                metadata_context[t] = {"error": str(e)}
    else:
        # no specific table selected → summarize all
        for t in all_tables:
            try:
                cols = client.get_columns(t)
                metadata_context[t] = cols
            except Exception as e:
                metadata_context[t] = {"error": str(e)}

    question = state.get("question", "")

    prompt = f"""
You are Dr. Database's Metadata Agent.

User question:
{question}

Available tables:
{all_tables}

Table metadata:
{metadata_context}

Explain the schema and answer the question using ONLY this information.
Keep it concise and practical.
"""

    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", str(resp))

    state["answer"] = answer
    _append_debug(state, "metadata_node")
    return state


# ----------------------------------------------------------------------
# Node 3: Data Quality agent
# ----------------------------------------------------------------------
def dq_node(state, db: Session):
    """
    Run data-quality checks for selected tables (or all tables if none selected),
    then interpret them with the LLM.
    """
    llm = get_llm()
    client = get_warehouse_client(db)

    all_tables = client.list_tables()
    selected_tables: List[str] = state.get("tables") or all_tables

    dq_results = {}

    for t in selected_tables:
        try:
            dq_results[t] = run_dq_for_table(db, t)
        except Exception as e:
            dq_results[t] = {"error": str(e)}

    question = state.get("question", "")

    prompt = f"""
You are Dr. Database's Data Quality Agent.

User question:
{question}

Data quality results (per table):
{dq_results}

Explain:
- Key issues by table
- How serious they are
- What should be done next
Use clear, structured bullet points.
"""

    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", str(resp))

    state["answer"] = answer
    _append_debug(state, "dq_node")
    return state


# ----------------------------------------------------------------------
# Node 4: SQL agent (schema-aware)
# ----------------------------------------------------------------------
def sql_node(state, db: Session):
    """
    Generate or explain SQL grounded in the actual warehouse schema.
    """
    llm = get_llm()
    client = get_warehouse_client(db)

    all_tables = client.list_tables()
    schema_map = {}

    for t in all_tables:
        try:
            cols = client.get_columns(t)
            schema_map[t] = [c.get("name") for c in cols]
        except Exception as e:
            schema_map[t] = [f"ERROR: {e}"]

    # Either explicit SQL snippet or user question
    sql_text = state.get("sql_text") or state.get("question", "")

    prompt = f"""
You are Dr. Database, an expert SQL assistant for SQL Server.

### DATABASE SCHEMA
{schema_map}

### RULES
- Use ONLY the tables and columns shown in the schema.
- If the user refers to non-existent tables/columns, point it out.
- Prefer readable SQL with CTEs when helpful.
- Target SQL Server dialect.

### USER REQUEST
{sql_text}

### OUTPUT
Return ONLY the final SQL (no commentary).
"""

    resp = llm.invoke(prompt)
    sql_answer = getattr(resp, "content", str(resp))

    state["answer"] = sql_answer
    state["sql"] = sql_answer  # optional convenience
    _append_debug(state, "sql_node")
    return state


# ----------------------------------------------------------------------
# Node 5: Root-cause agent
# ----------------------------------------------------------------------
def rootcause_node(state, db: Session):
    """
    Use metadata + DQ context to hypothesize root-cause of issues.
    """
    llm = get_llm()
    client = get_warehouse_client(db)

    all_tables = client.list_tables()
    selected_tables: List[str] = state.get("tables") or all_tables

    schema_map = {}
    for t in selected_tables:
        try:
            cols = client.get_columns(t)
            schema_map[t] = [c.get("name") for c in cols]
        except Exception as e:
            schema_map[t] = [f"ERROR: {e}"]

    dq_results = {}
    for t in selected_tables:
        try:
            dq_results[t] = run_dq_for_table(db, t)
        except Exception as e:
            dq_results[t] = {"error": str(e)}

    question = state.get("question", "")

    prompt = f"""
You are Dr. Database's Root-Cause Analysis Agent.

User question:
{question}

Relevant tables:
{selected_tables}

Schema:
{schema_map}

Data Quality results:
{dq_results}

Infer the MOST LIKELY root causes.
Explain your reasoning in 3–6 bullet points, and suggest concrete next steps.
"""

    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", str(resp))

    state["answer"] = answer
    _append_debug(state, "rootcause_node")
    return state


# ----------------------------------------------------------------------
# Node 6: Final node
# ----------------------------------------------------------------------
def final_node(state, db: Session):
    """
    No extra work – just mark that the final node was reached.
    """
    _append_debug(state, "final_node")
    return state
