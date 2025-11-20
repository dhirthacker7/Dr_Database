from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_config,
    routes_run,
    routes_reports,
    routes_ui,
    routes_agents,
)

from dotenv import load_dotenv
load_dotenv()


app = FastAPI(
    title="Dr Database",
    version="1.0",
    description="AI-driven data assistant with metadata, SQL, DQ, RCA agents."
)

# Optional: CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Root route → redirect to docs
# -----------------------------
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


# -----------------------------
# Routers
# -----------------------------
app.include_router(routes_config.router, prefix="/config", tags=["config"])
app.include_router(routes_run.router, prefix="/run", tags=["run"])
app.include_router(routes_reports.router, prefix="/reports", tags=["reports"])
app.include_router(routes_ui.router, prefix="/ui", tags=["ui"])
app.include_router(routes_agents.router, prefix="/agents", tags=["agents"])
