# app/api/routes_config.py
from fastapi import APIRouter
from pydantic import BaseModel

from app.db.connection import (
    create_engine_from_dict,
    test_engine_connection
)

router = APIRouter(prefix="/config")


# -----------------------------
# Request Model
# -----------------------------
class ConnectionPayload(BaseModel):
    db_type: str
    host: str
    port: str | int
    database: str
    username: str
    password: str


# -----------------------------
# Save + connect
# -----------------------------
@router.post("/save")
def save_connection(payload: ConnectionPayload):
    ok, err = create_engine_from_dict(payload.dict())
    return {"success": ok, "error": err}


# -----------------------------
# Test existing connection
# -----------------------------
@router.get("/test")
def test_connection():
    ok, err = test_engine_connection()
    return {"success": ok, "error": err}
