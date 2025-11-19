from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app.core.db_connection import get_db
from app.db.models import DBConfig
from app.utils.connection_builder import (
    build_postgres_conn_string,
    build_mssql_conn_string,
    mask_connection_string,
)

router = APIRouter()


class ConnectionParams(BaseModel):
    db_type: str  # "postgres" or "mssql"
    host: str
    port: int | None = None  # optional; MSSQL can rely on instance name instead
    database: str
    username: str
    password: str


class RawConnection(BaseModel):
    db_type: str
    connection_string: str


def build_connection_string(params: ConnectionParams | RawConnection) -> tuple[str, str]:
    """
    Returns (db_type, connection_string)
    """
    if isinstance(params, RawConnection):
        return params.db_type, params.connection_string

    # Structured params
    if params.db_type == "postgres":
        return "postgres", build_postgres_conn_string(params.dict())

    if params.db_type in ("mssql", "sqlserver"):
        return "mssql", build_mssql_conn_string(params.dict())

    raise HTTPException(status_code=400, detail=f"Unsupported db_type: {params.db_type}")


def test_db_connection(conn_str: str):
    """Perform a simple SELECT 1 to validate the connection string."""
    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {e}")


@router.post("/connection")
def set_connection(
    params: ConnectionParams | RawConnection,
    db: Session = Depends(get_db),
):
    db_type, conn_str = build_connection_string(params)

    # Validate the connection
    test_db_connection(conn_str)

    # Upsert config
    existing = db.query(DBConfig).first()
    if existing:
        existing.db_type = db_type
        existing.connection_string = conn_str
    else:
        cfg = DBConfig(db_type=db_type, connection_string=conn_str)
        db.add(cfg)

    db.commit()

    return {
        "message": "Connection saved successfully.",
        "db_type": db_type,
        "connection_string_masked": mask_connection_string(conn_str),
    }


@router.get("/connection")
def get_connection(db: Session = Depends(get_db)):
    cfg = db.query(DBConfig).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="No connection configured")

    return {
        "db_type": cfg.db_type,
        "connection_string_masked": mask_connection_string(cfg.connection_string),
    }
