import os
from typing import Dict, Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

ENGINE: Optional[Engine] = None


# ---------------------------------------------------------
# Build SQLAlchemy URL from dict
# ---------------------------------------------------------
def _make_connection_url(details: Dict) -> str:
    db_type = details.get("db_type")

    if db_type == "mssql":
        host = details["host"]
        port = details.get("port", "1433")
        database = details["database"]
        username = details["username"]
        password = details["password"]
        driver = "ODBC Driver 18 for SQL Server"

        return (
            f"mssql+pyodbc://{username}:{password}@{host},{port}/{database}"
            f"?driver={driver.replace(' ', '+')}"
        )

    elif db_type == "postgres":
        host = details["host"]
        port = details.get("port", "5432")
        database = details["database"]
        username = details["username"]
        password = details["password"]

        return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

    else:
        raise ValueError("Unsupported db_type")


# ---------------------------------------------------------
# Save engine globally
# ---------------------------------------------------------
def create_engine_from_dict(details: Dict) -> Tuple[bool, Optional[str]]:
    global ENGINE
    try:
        url = _make_connection_url(details)
        ENGINE = create_engine(url)
        # Test connection
        with ENGINE.connect() as conn:
            conn.execute("SELECT 1")
        return True, None
    except Exception as e:
        ENGINE = None
        return False, str(e)


# ---------------------------------------------------------
# Test existing global engine
# ---------------------------------------------------------
def test_engine_connection() -> Tuple[bool, Optional[str]]:
    global ENGINE
    if ENGINE is None:
        return False, "No engine created."

    try:
        with ENGINE.connect() as conn:
            conn.execute("SELECT 1")
        return True, None
    except SQLAlchemyError as e:
        return False, str(e)


# ---------------------------------------------------------
# Retrieve global engine
# ---------------------------------------------------------
def get_engine() -> Optional[Engine]:
    return ENGINE
