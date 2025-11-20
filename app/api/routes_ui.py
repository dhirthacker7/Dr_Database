from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from app.core.db_connection import get_db
from app.db.models import DBConfig
from app.api.routes_config import set_connection, ConnectionParams
from app.dq.runner import run_dq_for_table, run_dq_for_all_tables
from app.agents.controller import run_controller
from app.graph.graph import run_langgraph_query

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/ui/connect")
def connect_page(request: Request, db: Session = Depends(get_db)):

    cfg = db.query(DBConfig).first()

    connection_ok = False
    db_name = None
    error_message = None

    # If config exists, test the connection
    if cfg:
        try:
            engine = create_engine(cfg.connection_string)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT DB_NAME()"))
                db_name = result.scalar()
            connection_ok = True
        except Exception as e:
            error_message = str(e)

    # Check for “saved” param
    saved = True if request.query_params.get("status") == "success" else False

    return templates.TemplateResponse(
        "connect_db.html",
        {
            "request": request,
            "saved": saved,
            "connection_ok": connection_ok,
            "db_name": db_name,
            "error": error_message,
        },
    )


@router.post("/ui/connect/save")
def connect_save(
    request: Request,
    db_type: str = Form("mssql"),
    host: str = Form(...),
    port: int = Form(1433),
    database: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):

    params = ConnectionParams(
        db_type=db_type,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
    )

    try:
        # this will run SELECT 1
        set_connection(params, db)
    except Exception as e:
        # ❗ Render the same form with a visible error message
        return templates.TemplateResponse(
            "connect_db.html",
            {
                "request": request,
                "connection_ok": False,
                "db_name": None,
                "error": str(e),
            },
            status_code=400,
        )

    # ✔ redirect only on success
    return RedirectResponse("/ui/connect?status=success", status_code=303)

@router.get("/ui/tables")
def ui_tables(request: Request, db: Session = Depends(get_db)):
    from app.warehouse.client import get_warehouse_client
    client = get_warehouse_client(db)
    tables = client.list_tables()
    return templates.TemplateResponse(
        "ui/tables.html",
        {"request": request, "tables": tables},
    )


@router.get("/ui/table/select")
def ui_select_table(request: Request, db: Session = Depends(get_db)):
    from app.warehouse.client import get_warehouse_client
    client = get_warehouse_client(db)
    tables = client.list_tables()
    return templates.TemplateResponse(
        "ui/table_select.html",
        {"request": request, "tables": tables},
    )


@router.get("/ui/table/view")
def ui_view_table(request: Request, table: str, db: Session = Depends(get_db)):
    from app.warehouse.client import get_warehouse_client
    from app.warehouse.metadata import extract_table_metadata

    client = get_warehouse_client(db)
    columns = client.get_columns(table)
    metadata = extract_table_metadata(db, table)

    return templates.TemplateResponse(
        "ui/table_detail.html",
        {
            "request": request,
            "table": table,
            "columns": columns,
            "metadata": metadata,
        },
    )


@router.get("/ui/dq")
def ui_dq(request: Request):
    return templates.TemplateResponse(
        "ui/dq_home.html", 
        {"request": request}
    )

@router.get("/ui/dq/select-table")
def dq_select(request: Request, db: Session = Depends(get_db)):
    from app.warehouse.client import get_warehouse_client

    client = get_warehouse_client(db)
    tables = client.list_tables()

    return templates.TemplateResponse(
        "ui/dq_select.html",
        {"request": request, "tables": tables},
    )


@router.get("/ui/dq/run")
def dq_run(request: Request, table: str, db: Session = Depends(get_db)):
    results = run_dq_for_table(db, table)

    return templates.TemplateResponse(
        "ui/dq_result.html",
        {
            "request": request,
            "table": table,
            "results": results["results"],
        },
    )

@router.get("/ui/report")
def ui_report(request: Request):
    return templates.TemplateResponse(
        "ui/report.html", 
        {"request": request}
    )


@router.get("/ui/agents")
def ui_agents(request: Request):
    return templates.TemplateResponse(
        "ui/agents.html", 
        {"request": request}
    )

@router.get("/ui/agents")
def ui_agents(request: Request, db: Session = Depends(get_db)):
    from app.warehouse.client import get_warehouse_client

    client = get_warehouse_client(db)
    tables = client.list_tables()

    return templates.TemplateResponse(
        "ui/agents.html",
        {
            "request": request,
            "result": None,
            "tables": tables,
        },
    )

@router.post("/ui/agents/query")
def ui_agents_query(
    request: Request,
    query: str = Form(...),
    table: list[str] | None = Form(None),
    sql_text: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Clean & normalize table list
    if table:
        table_list = [t.strip() for t in table if t and t.strip()]
        table_list = table_list if table_list else None
    else:
        table_list = None

    graph_result = run_langgraph_query(
        question=query,
        db=db,
        tables=table_list,
        sql_text=sql_text or None,
    )

    # Reload tables for dropdown
    from app.warehouse.client import get_warehouse_client
    client = get_warehouse_client(db)
    tables = client.list_tables()

    # Expose only what's needed to the template
    result = {
        "intent": graph_result.get("intent", "unknown"),
        "answer": graph_result.get("answer", ""),
        "debug": graph_result.get("debug", []),
    }

    return templates.TemplateResponse(
        "ui/agents.html",
        {
            "request": request,
            "result": result,
            "tables": tables,
        },
    )

