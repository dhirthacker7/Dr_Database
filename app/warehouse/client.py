from sqlalchemy import inspect, text
from app.state import get_engine


class WarehouseClient:
    def __init__(self):
        self.engine = get_engine()
        if not self.engine:
            raise ValueError("No active database engine. Connect first.")

        self.insp = inspect(self.engine)

    def list_tables(self):
        return self.insp.get_table_names()

    def get_columns(self, table_name):
        return self.insp.get_columns(table_name)

    def preview(self, table_name, limit=50):
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT TOP {limit} * FROM {table_name}"))
            rows = result.fetchall()
        return rows

    def run_sql(self, sql):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            try:
                rows = result.fetchall()
                return rows
            except:
                return None
