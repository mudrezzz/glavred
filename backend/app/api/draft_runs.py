from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.api.dependencies import create_draft_run_service
from backend.app.api.draft_generation_contracts import DraftGenerateRequest, to_draft_generation_request
from backend.app.application.draft_run_service import DraftRunService
from backend.app.domain.draft_run import DraftRun, DraftRunStep

router = APIRouter(prefix="/api/draft-runs")


class DraftRunCreateResponse(BaseModel):
    run_id: str = Field(serialization_alias="runId")
    status: str

    model_config = {"populate_by_name": True}


class DraftRunStepResponse(BaseModel):
    key: str
    status: str
    title: str
    artifact_payload: dict[str, Any] | None = Field(serialization_alias="artifactPayload")
    error: str | None
    started_at: str | None = Field(serialization_alias="startedAt")
    completed_at: str | None = Field(serialization_alias="completedAt")

    model_config = {"populate_by_name": True}


class DraftRunResponse(BaseModel):
    id: str
    status: str
    input_summary: dict[str, Any] = Field(serialization_alias="inputSummary")
    steps: list[DraftRunStepResponse]
    final_draft: dict[str, Any] | None = Field(serialization_alias="finalDraft")
    error: str | None
    ai_run_ids: list[str] = Field(serialization_alias="aiRunIds")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True}


@router.post("", response_model=DraftRunCreateResponse, response_model_by_alias=True)
def create_draft_run(
    request: DraftGenerateRequest,
    service: DraftRunService = Depends(create_draft_run_service),
) -> DraftRunCreateResponse:
    run = service.create_run(to_draft_generation_request(request))
    return DraftRunCreateResponse(run_id=run.id, status=run.status.value)


@router.get("/{run_id}", response_model=DraftRunResponse, response_model_by_alias=True)
def get_draft_run(
    run_id: str,
    service: DraftRunService = Depends(create_draft_run_service),
) -> DraftRunResponse:
    run = service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="DraftRun not found")
    return serialize_run(run)


@router.get("/{run_id}/events", response_model=DraftRunResponse, response_model_by_alias=True)
def get_draft_run_events(
    run_id: str,
    service: DraftRunService = Depends(create_draft_run_service),
) -> DraftRunResponse:
    return get_draft_run(run_id=run_id, service=service)


def serialize_run(run: DraftRun) -> DraftRunResponse:
    return DraftRunResponse(
        id=run.id,
        status=run.status.value,
        input_summary=run.input_summary,
        steps=[serialize_step(step) for step in run.steps],
        final_draft=run.final_draft,
        error=run.error,
        ai_run_ids=run.ai_run_ids,
        created_at=run.created_at.isoformat(),
        updated_at=run.updated_at.isoformat(),
    )


def serialize_step(step: DraftRunStep) -> DraftRunStepResponse:
    return DraftRunStepResponse(
        key=step.key.value,
        status=step.status.value,
        title=step.title,
        artifact_payload=step.artifact_payload,
        error=step.error,
        started_at=step.started_at.isoformat() if step.started_at else None,
        completed_at=step.completed_at.isoformat() if step.completed_at else None,
    )
