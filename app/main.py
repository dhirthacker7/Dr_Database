from fastapi import FastAPI
from app.db.init_db import init_db

# Routers (will fill later)
from app.api import routes_config, routes_run, routes_reports, routes_ui

def create_app() -> FastAPI:
    app = FastAPI(title="Dr. Database", version="0.1.0")

    # Initialize internal DB (creates tables if not present)
    init_db()

    # Include routers
    app.include_router(routes_config.router, prefix="/config", tags=["config"])
    app.include_router(routes_run.router, prefix="/dq", tags=["dq"])
    app.include_router(routes_reports.router, prefix="/reports", tags=["reports"])
    app.include_router(routes_ui.router, tags=["ui"])

    return app


app = create_app()