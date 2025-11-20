from typing import Optional, List
from sqlalchemy.orm import Session

from app.agents.base import get_llm
from app.warehouse.client import WarehouseClient
from app.dq.runner import run_dq_for_table


def run_rootcause_agent(user_query: str, db: Session, tables: List[str] | None = None) -> str:
    llm = get_llm()
    client = WarehouseClient(db)

    warehouse_tables = client.list_tables()
    metadata_context = {"warehouse_tables": warehouse_tables}

    dq_context = {}
    if tables:
        for t in tables:
            dq_context[t] = run_dq_for_table(db, t)

    prompt = f"""
You are Dr. Database's Root Cause Analysis Agent.

Metadata Context:
{metadata_context}

DQ Context:
{dq_context}

User Question:
{user_query}

Give the most likely root cause(s), explain your reasoning, and recommend next investigative actions.
"""

    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)
