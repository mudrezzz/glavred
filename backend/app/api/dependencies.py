from fastapi import Request

from backend.app.application.health_service import BackendHealthService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


def get_request_settings(request: Request) -> BackendSettings:
    return request.app.state.settings


def create_health_service(request: Request) -> BackendHealthService:
    return BackendHealthService(
        settings=get_request_settings(request),
        openrouter_validator=OpenRouterConfigValidator(),
    )
