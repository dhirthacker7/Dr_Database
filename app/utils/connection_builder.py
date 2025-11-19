from typing import Dict
import urllib.parse


def build_postgres_conn_string(params: Dict[str, str]) -> str:
    user = params["username"]
    pwd = params["password"]
    host = params.get("host", "localhost")
    port = params.get("port", 5432)
    db = params["database"]

    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


def build_mssql_conn_string(params: Dict[str, str]) -> str:
    """
    Build a SQL Server (MSSQL) connection string using pyodbc + ODBC Driver 18.

    Works with:
    - host like 'DHIR'
    - host like 'DHIR\\SQLEXPRESS' (named instance)
    """

    driver = "ODBC Driver 18 for SQL Server"
    server = params["host"]          # e.g. DHIR or DHIR\\SQLEXPRESS
    database = params["database"]
    uid = params["username"]
    pwd = params["password"]

    # Constructing raw ODBC string
    odbc_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "TrustServerCertificate=yes;"
        "Encrypt=no;"
    )

    # URL-encode for SQLAlchemy
    return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc_str)


def mask_connection_string(conn: str) -> str:
    """
    Mask password in connection string for safe display.

    Handles both:
    - postgresql+psycopg2://user:pass@host:port/db
    - mssql+pyodbc:///?odbc_connect=DRIVER=...;PWD=pass;...
    """
    # MSSQL odbc_connect case
    if "odbc_connect=" in conn and "PWD=" in conn:
        # crude but effective: hide PWD value between 'PWD=' and next ';'
        prefix, _, rest = conn.partition("odbc_connect=")
        decoded = urllib.parse.unquote_plus(rest)
        if "PWD=" in decoded:
            before_pwd, _, after_pwd = decoded.partition("PWD=")
            pwd_value, sep, tail = after_pwd.partition(";")
            masked_decoded = before_pwd + "PWD=***" + sep + tail
            return prefix + "odbc_connect=" + urllib.parse.quote_plus(masked_decoded)
        return conn

    # Generic URL case: driver://user:pass@host/...
    if "@" not in conn or "://" not in conn:
        return conn

    prefix, rest = conn.split("://", 1)
    creds, hostpart = rest.split("@", 1)

    if ":" in creds:
        user, _ = creds.split(":", 1)
        masked_creds = f"{user}:***"
    else:
        masked_creds = "***"

    return f"{prefix}://{masked_creds}@{hostpart}"
