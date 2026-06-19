from fastapi import Request

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_generation_service import DraftGenerationService
from backend.app.application.draft_run_service import DraftRunService
from backend.app.application.health_service import BackendHealthService
from backend.app.infrastructure.celery_draft_run_dispatcher import CeleryDraftRunDispatcher
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_draft_adapter import OpenRouterDraftAdapter
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import BackendSettings


def get_request_settings(request: Request) -> BackendSettings:
    return request.app.state.settings


def create_health_service(request: Request) -> BackendHealthService:
    return BackendHealthService(
        settings=get_request_settings(request),
        openrouter_validator=OpenRouterConfigValidator(),
    )


def create_ai_run_service(request: Request) -> AiRunService:
    settings = get_request_settings(request)
    return AiRunService(repository=SqliteAiRunRepository(settings.ai_run_audit_db_path))


def create_draft_generation_service(request: Request) -> DraftGenerationService:
    settings = get_request_settings(request)
    adapter = getattr(request.app.state, "openrouter_draft_adapter", None) or OpenRouterDraftAdapter()
    return DraftGenerationService(
        settings=settings,
        ai_run_service=create_ai_run_service(request),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_draft_service=DeterministicDraftService(),
    )


def create_draft_run_service(request: Request) -> DraftRunService:
    settings = get_request_settings(request)
    dispatcher = getattr(request.app.state, "draft_run_dispatcher", None) or CeleryDraftRunDispatcher()
    return DraftRunService(
        repository=SqliteDraftRunRepository(settings.draft_run_db_path),
        dispatcher=dispatcher,
    )
