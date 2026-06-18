from fastapi import APIRouter, Depends

from backend.app.api.dependencies import create_health_service
from backend.app.application.health_service import BackendHealthService

router = APIRouter()


@router.get("/health")
def health(service: BackendHealthService = Depends(create_health_service)) -> dict[str, str]:
    return service.liveness()


@router.get("/api/health")
def api_health(service: BackendHealthService = Depends(create_health_service)) -> dict[str, object]:
    return service.readiness()
