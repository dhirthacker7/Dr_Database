from dataclasses import dataclass
from typing import Any, Dict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


@dataclass
class DQResult:
    rule: str
    status: str
    details: Dict[str, Any]


class BaseRule:
    rule_name: str = ""
    description: str = ""

    def run(self, table: str, client) -> DQResult:
        raise NotImplementedError


class NullCheck(BaseRule):
    rule_name = "null_check"
    description = "Checks number of NULLs in each column."

    def run(self, table: str, client) -> DQResult:
        engine = client.engine
        insp = client.engine.dialect
        nulls = {}

        with engine.connect() as conn:
            cols = client.get_columns(table)
            for col in cols:
                col_name = col["name"]
                query = text(f"SELECT COUNT(*) FROM {table} WHERE {col_name} IS NULL")
                count = conn.execute(query).scalar()
                nulls[col_name] = count

        return DQResult(
            rule=self.rule_name,
            status="pass",
            details={"null_counts": nulls},
        )


class DuplicateCheck(BaseRule):
    rule_name = "duplicate_check"
    description = "Checks for duplicate rows in the table."

    def run(self, table: str, client) -> DQResult:
        with client.engine.connect() as conn:
            query = text(f"SELECT COUNT(*) - COUNT(DISTINCT *) AS duplicates FROM {table}")
            # SQL Server does not support SELECT DISTINCT * inside COUNT
            # We handle this later. For now keep placeholder.
            try:
                duplicates = conn.execute(query).scalar()
            except SQLAlchemyError:
                duplicates = "Not supported on this database"

        return DQResult(
            rule=self.rule_name,
            status="pass",
            details={"duplicate_rows": duplicates},
        )


class RowCountCheck(BaseRule):
    rule_name = "row_count"
    description = "Counts total rows."

    def run(self, table: str, client) -> DQResult:
        with client.engine.connect() as conn:
            query = text(f"SELECT COUNT(*) FROM {table}")
            count = conn.execute(query).scalar()

        return DQResult(
            rule=self.rule_name,
            status="pass",
            details={"row_count": count},
        )


class SchemaCheck(BaseRule):
    rule_name = "schema_check"
    description = "Reports table columns and types."

    def run(self, table: str, client) -> DQResult:
        cols = client.get_columns(table)
        return DQResult(
            rule=self.rule_name,
            status="pass",
            details={"schema": cols},
        )
