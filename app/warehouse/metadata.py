from app.warehouse.client import WarehouseClient

def list_tables():
    client = WarehouseClient()
    return client.list_tables()

def extract_table_metadata(table_name):
    client = WarehouseClient()
    return client.get_columns(table_name)
