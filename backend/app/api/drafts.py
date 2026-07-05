from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.api.ai_runs import AiRunResponse, serialize_run
from backend.app.api.dependencies import create_draft_generation_service
from backend.app.api.draft_generation_contracts import (
    DraftGenerateRequest,
    PostDraftResponse,
    serialize_draft,
    to_draft_generation_request,
)
from backend.app.api.draft_revision_dependencies import create_draft_human_comment_revision_service
from backend.app.drafting.application.generation.draft_generation_service import DraftGenerationService
from backend.app.drafting.application.hitl.draft_human_comment_revision_service import DraftHumanCommentRevisionService, HumanCommentRevisionUnavailable

router = APIRouter(prefix="/api/drafts")


class DraftGenerateResponse(BaseModel):
    draft: PostDraftResponse
    ai_run: AiRunResponse = Field(serialization_alias="aiRun")

    model_config = {"populate_by_name": True}


class DraftCurrentVersionRequest(BaseModel):
    id: str
    version_number: int = Field(alias="versionNumber")
    title: str
    body: str


class DraftCommentRevisionRequest(BaseModel):
    draft_run_id: str | None = Field(default=None, alias="draftRunId")
    current_version: DraftCurrentVersionRequest = Field(alias="currentVersion")
    editor_comment: str = Field(alias="editorComment")


class DraftCommentRevisionResponse(BaseModel):
    title: str
    body: str
    revision_summary: str = Field(serialization_alias="revisionSummary")
    ai_run_id: str | None = Field(serialization_alias="aiRunId")
    selected_model: str | None = Field(serialization_alias="selectedModel")
    attempts: list[dict[str, Any]]
    quality_check: dict[str, Any] = Field(serialization_alias="qualityCheck")

    model_config = {"populate_by_name": True}


@router.post("/generate", response_model=DraftGenerateResponse, response_model_by_alias=True)
def generate_draft(
    request: DraftGenerateRequest,
    service: DraftGenerationService = Depends(create_draft_generation_service),
) -> DraftGenerateResponse:
    draft, ai_run = service.generate(to_draft_generation_request(request))
    return DraftGenerateResponse(draft=serialize_draft(draft), ai_run=serialize_run(ai_run))


@router.post("/revise-with-comment", response_model=DraftCommentRevisionResponse, response_model_by_alias=True)
def revise_with_comment(
    request: DraftCommentRevisionRequest,
    service: DraftHumanCommentRevisionService = Depends(create_draft_human_comment_revision_service),
) -> DraftCommentRevisionResponse:
    try:
        result = service.revise(
            draft_run_id=request.draft_run_id,
            current_version={
                "id": request.current_version.id,
                "versionNumber": request.current_version.version_number,
                "title": request.current_version.title,
                "body": request.current_version.body,
            },
            editor_comment=request.editor_comment,
        )
    except HumanCommentRevisionUnavailable as exc:
        raise HTTPException(status_code=503, detail={"message": str(exc), "attempts": exc.attempts}) from exc
    return DraftCommentRevisionResponse(
        title=result.title,
        body=result.body,
        revision_summary=result.revision_summary,
        ai_run_id=result.ai_run_id,
        selected_model=result.selected_model,
        attempts=result.attempts,
        quality_check=result.quality_check,
    )
