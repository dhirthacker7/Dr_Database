from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping_reports():
    return {"message": "reports OK"}
