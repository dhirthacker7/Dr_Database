from typing import List, Dict
from app.dq.rules import (
    NullCheck,
    DuplicateCheck,
    RowCountCheck,
    SchemaCheck,
)
from app.warehouse.client import get_warehouse_client


ALL_RULES = [
    NullCheck(),
    DuplicateCheck(),
    RowCountCheck(),
    SchemaCheck(),
]


def run_dq_for_table(db, table: str):
    client = get_warehouse_client(db)
    results = []

    for rule in ALL_RULES:
        try:
            result = rule.run(table, client)
            results.append(result.__dict__)
        except Exception as e:
            results.append({
                "rule": rule.rule_name,
                "status": "error",
                "details": {"error": str(e)},
            })

    return {"table": table, "results": results}


def run_dq_for_all_tables(db):
    client = get_warehouse_client(db)
    tables = client.list_tables()
    output = {}

    for t in tables:
        output[t] = run_dq_for_table(db, t)

    return output
