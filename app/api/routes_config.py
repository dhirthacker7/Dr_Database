from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping_config():
    return {"message": "config OK"}
