from typing import Optional, List
from sqlalchemy.orm import Session

from app.agents.base import get_llm
from app.warehouse.client import WarehouseClient
from app.warehouse.metadata import extract_table_metadata


def run_metadata_agent(user_query: str, db: Session, tables: List[str] | None = None) -> str:
    client = WarehouseClient(db)
    llm = get_llm()

    all_tables = client.list_tables()
    context_parts = [f"Available tables: {all_tables}"]

    if tables:
        for t in tables:
            md = extract_table_metadata(db, t)
            context_parts.append(f"\nMetadata for table '{t}':\n{md}")

    context = "\n".join(context_parts)

    prompt = f"""
You are Dr. Database's Metadata Agent.

You have the following warehouse metadata context:
{context}

User question:
{user_query}

Answer using ONLY the metadata provided. Keep responses concise and useful.
"""

    resp = llm.invoke(prompt)
    return resp.content if hasattr(resp, "content") else str(resp)
