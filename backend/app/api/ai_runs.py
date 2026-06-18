from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.api.dependencies import create_ai_run_service
from backend.app.application.ai_run_service import AiRunService
from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider

router = APIRouter(prefix="/api/ai-runs")


class AiRunCreateRequest(BaseModel):
    capability: AiRunCapability
    provider: AiRunProvider
    model: str | None = None
    request_payload: dict[str, Any] = Field(default_factory=dict, alias="requestPayload")


class AiRunResponse(BaseModel):
    id: str
    capability: AiRunCapability
    status: str
    provider: AiRunProvider
    model: str | None
    request_payload: dict[str, Any] = Field(serialization_alias="requestPayload")
    result_payload: dict[str, Any] | None = Field(serialization_alias="resultPayload")
    error: str | None
    fallback_used: bool = Field(serialization_alias="fallbackUsed")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True}


def serialize_run(run: AiRun) -> AiRunResponse:
    return AiRunResponse(
        id=run.id,
        capability=run.capability,
        status=run.status.value,
        provider=run.provider,
        model=run.model,
        request_payload=run.request_payload,
        result_payload=run.result_payload,
        error=run.error,
        fallback_used=run.fallback_used,
        created_at=run.created_at.isoformat(),
        updated_at=run.updated_at.isoformat(),
    )


@router.post("", response_model=AiRunResponse, response_model_by_alias=True)
def create_ai_run(
    request: AiRunCreateRequest,
    service: AiRunService = Depends(create_ai_run_service),
) -> AiRunResponse:
    run = service.create_recorded_run(
        capability=request.capability,
        provider=request.provider,
        model=request.model,
        request_payload=request.request_payload,
    )
    return serialize_run(run)


@router.get("/{run_id}", response_model=AiRunResponse, response_model_by_alias=True)
def get_ai_run(
    run_id: str,
    service: AiRunService = Depends(create_ai_run_service),
) -> AiRunResponse:
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="AI run not found")
    return serialize_run(run)


@router.get("", response_model=list[AiRunResponse], response_model_by_alias=True)
def list_ai_runs(
    limit: int = Query(default=20, ge=1, le=100),
    capability: AiRunCapability | None = None,
    service: AiRunService = Depends(create_ai_run_service),
) -> list[AiRunResponse]:
    return [
        serialize_run(run)
        for run in service.list_runs(limit=limit, capability=capability)
    ]
