from sqlalchemy.orm import Session
from app.warehouse.client import get_warehouse_client


def extract_table_metadata(db: Session, table_name: str):
    client = get_warehouse_client(db)

    cols = client.get_columns(table_name)
    metadata = {
        "table": table_name,
        "columns": cols,
        "column_count": len(cols),
    }

    return metadata
