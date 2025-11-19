from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db_connection import get_db
from app.warehouse.client import get_warehouse_client
from app.warehouse.metadata import extract_table_metadata

router = APIRouter()


@router.get("/tables")
def list_tables(db: Session = Depends(get_db)):
    try:
        client = get_warehouse_client(db)
        return {"tables": client.list_tables()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables/{table}/columns")
def table_columns(table: str, db: Session = Depends(get_db)):
    try:
        client = get_warehouse_client(db)
        return {"columns": client.get_columns(table)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tables/{table}/metadata")
def table_metadata(table: str, db: Session = Depends(get_db)):
    try:
        return extract_table_metadata(db, table)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
