from fastapi import FastAPI

from backend.app.api.ai_runs import router as ai_runs_router
from backend.app.api.health import router as health_router
from backend.app.settings import BackendSettings, get_settings


def create_app(settings: BackendSettings | None = None) -> FastAPI:
    app = FastAPI(title="Glavred Backend", version="0.1.0")
    app.state.settings = settings or get_settings()
    app.include_router(health_router)
    app.include_router(ai_runs_router)
    return app
