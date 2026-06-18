from fastapi import Request

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.health_service import BackendHealthService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
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
