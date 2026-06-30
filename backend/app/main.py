from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.ai_runs import router as ai_runs_router
from backend.app.api.draft_runs import router as draft_runs_router
from backend.app.api.drafts import router as drafts_router
from backend.app.api.health import router as health_router
from backend.app.api.portfolio import router as portfolio_router
from backend.app.settings import BackendSettings, get_settings


def create_app(
    settings: BackendSettings | None = None,
    openrouter_draft_adapter: object | None = None,
    openrouter_json_adapter: object | None = None,
    draft_run_dispatcher: object | None = None,
) -> FastAPI:
    app = FastAPI(title="Glavred Backend", version="0.1.0")
    app.state.settings = settings or get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.state.settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if openrouter_draft_adapter is not None:
        app.state.openrouter_draft_adapter = openrouter_draft_adapter
    if openrouter_json_adapter is not None:
        app.state.openrouter_json_adapter = openrouter_json_adapter
    if draft_run_dispatcher is not None:
        app.state.draft_run_dispatcher = draft_run_dispatcher
    app.include_router(health_router)
    app.include_router(ai_runs_router)
    app.include_router(drafts_router)
    app.include_router(draft_runs_router)
    app.include_router(portfolio_router)
    return app
