from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import DBConfig


class WarehouseClient:
    """
    Unified interface for SQL Server and Postgres.
    Supports:
    - listing tables
    - listing columns
    - simple metadata extraction
    """

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def list_tables(self):
        insp = inspect(self.engine)
        return insp.get_table_names()

    def get_columns(self, table_name: str):
        insp = inspect(self.engine)
        cols = insp.get_columns(table_name)
        return [
            {
                "name": c["name"],
                "type": str(c["type"]),
                "nullable": c.get("nullable", True),
            }
            for c in cols
        ]


def get_warehouse_client(db: Session) -> WarehouseClient:
    cfg = db.query(DBConfig).first()

    if not cfg:
        raise Exception("No warehouse connection configured.")

    try:
        client = WarehouseClient(cfg.connection_string)
        return client
    except SQLAlchemyError as e:
        raise Exception(f"Failed to initialize WarehouseClient: {e}")
