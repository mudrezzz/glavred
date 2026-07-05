from fastapi import Request

from backend.app.api.dependencies import create_ai_run_service, get_request_settings
from backend.app.drafting.application.hitl.draft_human_comment_quality_service import DraftHumanCommentQualityService
from backend.app.drafting.application.hitl.draft_human_comment_revision_service import DraftHumanCommentRevisionService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository


def create_draft_human_comment_revision_service(request: Request) -> DraftHumanCommentRevisionService:
    settings = get_request_settings(request)
    adapter = getattr(request.app.state, "openrouter_json_adapter", None) or OpenRouterJsonAdapter()
    validator = OpenRouterConfigValidator()
    ai_run_service = create_ai_run_service(request)
    quality_service = DraftHumanCommentQualityService(
        settings=settings,
        ai_run_service=ai_run_service,
        openrouter_validator=validator,
        openrouter_adapter=adapter,
    )
    return DraftHumanCommentRevisionService(
        settings=settings,
        ai_run_service=ai_run_service,
        openrouter_validator=validator,
        openrouter_adapter=adapter,
        draft_run_repository=SqliteDraftRunRepository(settings.draft_run_db_path),
        quality_service=quality_service,
    )
