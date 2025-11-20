import os
import requests
from typing import Dict, Any, List, Tuple, Optional

BACKEND_URL = os.getenv("DRDB_BACKEND_URL", "http://localhost:8000")

def _url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# --- CONNECTION / CONFIG ENDPOINTS ---

def save_connection(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Uses new JSON endpoint: POST /config/save-json
    """
    try:
        resp = requests.post(_url("/config/save-json"), json=payload, timeout=10)
        data = resp.json()

        if data.get("ok"):
            return True, None

        return False, data.get("error", "Unknown error")
    except Exception as e:
        return False, str(e)


def test_connection() -> Tuple[bool, Optional[str]]:
    """
    Hit /dq/tables to verify DB engine exists and works.
    """
    try:
        resp = requests.get(_url("/dq/tables"), timeout=10)
        if resp.status_code == 200:
            return True, None
        return False, f"Status {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

# --- DATA + AGENT ENDPOINTS ---

def fetch_tables() -> Tuple[List[str], Optional[str]]:
    try:
        resp = requests.get(_url("/dq/tables"), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("tables", []), None
        return [], f"Status {resp.status_code}: {resp.text}"
    except Exception as e:
        return [], str(e)

def run_agents(question: str, tables: List[str], sql_text: Optional[str]):
    payload = {
        "question": question,
        "tables": tables,
        "sql_text": sql_text,
    }
    try:
        resp = requests.post(_url("/agents/run"), json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"Status {resp.status_code}: {resp.text}"
    except Exception as e:
        return None, str(e)
