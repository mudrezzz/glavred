from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.app.api.ai_runs import AiRunResponse, serialize_run
from backend.app.api.dependencies import create_draft_generation_service
from backend.app.api.draft_generation_contracts import (
    DraftGenerateRequest,
    PostDraftResponse,
    serialize_draft,
    to_draft_generation_request,
)
from backend.app.application.draft_generation_service import DraftGenerationService

router = APIRouter(prefix="/api/drafts")


class DraftGenerateResponse(BaseModel):
    draft: PostDraftResponse
    ai_run: AiRunResponse = Field(serialization_alias="aiRun")

    model_config = {"populate_by_name": True}


@router.post("/generate", response_model=DraftGenerateResponse, response_model_by_alias=True)
def generate_draft(
    request: DraftGenerateRequest,
    service: DraftGenerationService = Depends(create_draft_generation_service),
) -> DraftGenerateResponse:
    draft, ai_run = service.generate(to_draft_generation_request(request))
    return DraftGenerateResponse(draft=serialize_draft(draft), ai_run=serialize_run(ai_run))
