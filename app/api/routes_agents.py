from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db_connection import get_db
from app.agents.controller import run_controller

router = APIRouter()


class AgentQuery(BaseModel):
    query: str
    table: str | None = None
    sql_text: str | None = None


@router.post("/query")
def agent_query(payload: AgentQuery, db: Session = Depends(get_db)):
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query text is required")

    result = run_controller(
        user_query=payload.query,
        db=db,
        table=payload.table,
        sql_text=payload.sql_text,
    )
    return result
