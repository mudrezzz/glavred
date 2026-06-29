from fastapi import Request

from backend.app.api.dependencies import create_ai_run_service, get_request_settings
from backend.app.application.draft_human_comment_revision_service import DraftHumanCommentRevisionService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository


def create_draft_human_comment_revision_service(request: Request) -> DraftHumanCommentRevisionService:
    settings = get_request_settings(request)
    adapter = getattr(request.app.state, "openrouter_json_adapter", None) or OpenRouterJsonAdapter()
    return DraftHumanCommentRevisionService(
        settings=settings,
        ai_run_service=create_ai_run_service(request),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        draft_run_repository=SqliteDraftRunRepository(settings.draft_run_db_path),
    )
