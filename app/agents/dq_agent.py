from typing import Optional, List
from sqlalchemy.orm import Session

from app.agents.base import get_llm
from app.dq.runner import run_dq_for_table


def run_dq_agent(user_query: str, db: Session, tables: List[str] | None = None) -> str:
    llm = get_llm()

    if tables:
        dq_results = {t: run_dq_for_table(db, t) for t in tables}
    else:
        dq_results = {"note": "No tables selected"}

    prompt = f"""
You are Dr. Database's Data Quality Insight Agent.

You are given the following DQ results:
{dq_results}

User question:
{user_query}

Interpret the results, identify issues, and recommend next steps.
"""

    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)
