from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/")
def root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
