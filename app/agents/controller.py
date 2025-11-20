from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.agents.metadata_agent import run_metadata_agent
from app.agents.dq_agent import run_dq_agent
from app.agents.sql_agent import run_sql_agent
from app.agents.rootcause_agent import run_rootcause_agent
from app.agents.base import get_llm


def classify_intent(user_query: str) -> str:
    """
    Very simple intent classifier using LLM.
    Returns one of: metadata, dq, sql, rootcause
    """
    llm = get_llm()
    prompt = f"""
You are an intent classifier for Dr. Database.

Decide which agent should handle the query.
Possible agents:
- metadata
- dq
- sql
- rootcause

User query:
{user_query}

Respond with ONLY one word from the list above.
"""
    resp = llm.invoke(prompt)
    text = (resp.content if hasattr(resp, "content") else str(resp)).strip().lower()
    if "dq" in text:
        return "dq"
    if "sql" in text:
        return "sql"
    if "root" in text:
        return "rootcause"
    # default
    return "metadata"


def run_controller(user_query: str, db: Session, table: list[str] | None = None, sql_text: Optional[str] = None):
    """
    Main entry point for the multi-agent system.
    """
    intent = classify_intent(user_query)

    if intent == "metadata":
        answer = run_metadata_agent(user_query, db, table)
    elif intent == "dq":
        answer = run_dq_agent(user_query, db, table)
    elif intent == "sql":
        answer = run_sql_agent(user_query, sql_text)
    elif intent == "rootcause":
        answer = run_rootcause_agent(user_query, db, table)
    else:
        answer = "Sorry, I could not classify your request."

    return {
        "intent": intent,
        "answer": answer,
    }
