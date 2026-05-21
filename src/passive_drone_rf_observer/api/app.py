from __future__ import annotations
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from ..config import Config, load_config
from .schemas import (
    AlertSchema,
    EventSchema,
    ModeRequest,
    StatusResponse,
    WifiEnvironmentEventSchema,
    WifiObservationSchema,
)
from ..simulation import SimulationManager


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATE_DIR = WEB_DIR / "templates"


def create_app(config: Optional[Config] = None) -> FastAPI:
    app = FastAPI(
        title="Passive Drone RF Observer",
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    runtime = SimulationManager(config or load_config())
    app.state.runtime = runtime

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
        return app.state.runtime.get_status()

    @app.get("/api/events", response_model=list[EventSchema])
    def get_events() -> list[dict]:
        return app.state.runtime.get_events()

    @app.get("/api/alerts", response_model=list[AlertSchema])
    def get_alerts() -> list[dict]:
        return app.state.runtime.get_alerts()

    @app.get("/api/wifi/observations", response_model=list[WifiObservationSchema])
    def get_wifi_observations() -> list[dict]:
        return app.state.runtime.get_wifi_observations()

    @app.get("/api/wifi/environment-events", response_model=list[WifiEnvironmentEventSchema])
    def get_wifi_environment_events() -> list[dict]:
        return app.state.runtime.get_wifi_environment_events()

    @app.post("/api/wifi/scan", response_model=list[WifiObservationSchema])
    def scan_wifi() -> list[dict]:
        return app.state.runtime.scan_wifi()

    @app.post("/api/wifi/clear")
    def clear_wifi_observations() -> dict:
        return app.state.runtime.clear_wifi_observations()

    @app.post("/api/simulation/start")
    def start_simulation() -> dict:
        return app.state.runtime.start()

    @app.post("/api/simulation/stop")
    def stop_simulation() -> dict:
        return app.state.runtime.stop()

    @app.post("/api/events/clear")
    def clear_events() -> dict:
        return app.state.runtime.clear_events()

    @app.post("/api/simulation/mode")
    def set_mode(data: ModeRequest) -> dict:
        return app.state.runtime.set_mode(data.mode)

    return app


app = create_app()
