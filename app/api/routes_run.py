from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db_connection import get_db
from app.warehouse.client import WarehouseClient
from app.warehouse.metadata import extract_table_metadata
from app.dq.runner import run_dq_for_table, run_dq_for_all_tables

router = APIRouter()

@router.get("/tables")
def list_tables(db: Session = Depends(get_db)):
    try:
        client = WarehouseClient(db)
        return {"tables": client.list_tables()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables/{table}/columns")
def table_columns(table: str, db: Session = Depends(get_db)):
    try:
        client = WarehouseClient(db)
        return {"columns": client.get_columns(table)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables/{table}/metadata")
def table_metadata(table: str, db: Session = Depends(get_db)):
    try:
        return extract_table_metadata(db, table)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dq/{table}")
def dq_table(table: str, db: Session = Depends(get_db)):
    return run_dq_for_table(db, table)

@router.get("/dq")
def dq_all(db: Session = Depends(get_db)):
    return run_dq_for_all_tables(db)
