from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from .schemas import AlertSchema, EventSchema, ModeRequest, StatusResponse
from ..simulation import SimulationManager

app = FastAPI(
    title="Passive Drone RF Observer",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATE_DIR = WEB_DIR / "templates"

manager = SimulationManager()


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "index.html")


@app.get("/static/{path:path}")
def static_file(path: str) -> FileResponse:
    file_path = STATIC_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Static file not found")
    return FileResponse(file_path)


@app.get("/api/status", response_model=StatusResponse)
def get_status() -> dict:
    return manager.get_status()


@app.get("/api/events", response_model=list[EventSchema])
def get_events() -> list[dict]:
    return manager.get_events()


@app.get("/api/alerts", response_model=list[AlertSchema])
def get_alerts() -> list[dict]:
    return manager.get_alerts()


@app.post("/api/simulation/start")
def start_simulation() -> dict:
    return manager.start()


@app.post("/api/simulation/stop")
def stop_simulation() -> dict:
    return manager.stop()


@app.post("/api/events/clear")
def clear_events() -> dict:
    return manager.clear_events()


@app.post("/api/simulation/mode")
def set_mode(data: ModeRequest) -> dict:
    return manager.set_mode(data.mode)
