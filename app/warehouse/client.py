# app/warehouse/client.py
from typing import List, Dict
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.connection import get_engine


class WarehouseClient:
    def __init__(self):
        self.engine = get_engine()

    # ----------------------------------------
    # List tables
    # ----------------------------------------
    def list_tables(self) -> List[str]:
        if not self.engine:
            return []
        insp = inspect(self.engine)
        return insp.get_table_names()

    # ----------------------------------------
    # Get columns for a specific table
    # ----------------------------------------
    def get_columns(self, table_name: str) -> List[Dict]:
        if not self.engine:
            return []
        insp = inspect(self.engine)
        return insp.get_columns(table_name)

    # ----------------------------------------
    # Run safe SQL (SELECT only)
    # ----------------------------------------
    def run_readonly_sql(self, sql: str):
        if not self.engine:
            raise ValueError("Engine not initialized.")

        sql = sql.strip().lower()
        if not sql.startswith("select"):
            raise ValueError("Read-only mode: Only SELECT statements allowed.")

        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            cols = result.keys()

        return {"columns": cols, "rows": rows}
