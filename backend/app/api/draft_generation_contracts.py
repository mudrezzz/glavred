from pydantic import BaseModel, Field

from backend.app.domain.draft_generation import (
    DraftBriefContext,
    DraftEditorialModelContext,
    DraftGenerationRequest,
    GeneratedDraft,
)


class DraftBriefRequest(BaseModel):
    id: str
    title: str
    rubric: str = ""
    audience: str = ""
    thesis: str
    conflict: str
    author_position: str = Field(alias="authorPosition")
    evidence: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    structure: list[str] = Field(default_factory=list)
    cta: str = ""
    risks: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class DraftEditorialModelRequest(BaseModel):
    audience: str = ""
    style_rules: list[str] = Field(default_factory=list, alias="styleRules")
    forbidden_topics: list[str] = Field(default_factory=list, alias="forbiddenTopics")
    goals: list[str] = Field(default_factory=list)


class DraftGenerateRequest(BaseModel):
    brief: DraftBriefRequest
    editorial_model: DraftEditorialModelRequest = Field(alias="editorialModel")


class PostDraftResponse(BaseModel):
    id: str
    brief_id: str = Field(serialization_alias="briefId")
    title: str
    body: str
    version: int
    status: str
    updated_at: str = Field(serialization_alias="updatedAt")

    model_config = {"populate_by_name": True}


def to_draft_generation_request(request: DraftGenerateRequest) -> DraftGenerationRequest:
    return DraftGenerationRequest(
        brief=DraftBriefContext(
            id=request.brief.id,
            title=request.brief.title,
            rubric=request.brief.rubric,
            audience=request.brief.audience,
            thesis=request.brief.thesis,
            conflict=request.brief.conflict,
            author_position=request.brief.author_position,
            evidence=request.brief.evidence,
            examples=request.brief.examples,
            structure=request.brief.structure,
            cta=request.brief.cta,
            risks=request.brief.risks,
            sources=request.brief.sources,
        ),
        editorial_model=DraftEditorialModelContext(
            audience=request.editorial_model.audience,
            style_rules=request.editorial_model.style_rules,
            forbidden_topics=request.editorial_model.forbidden_topics,
            goals=request.editorial_model.goals,
        ),
    )


def serialize_draft(draft: GeneratedDraft) -> PostDraftResponse:
    return PostDraftResponse(
        id=draft.id,
        brief_id=draft.brief_id,
        title=draft.title,
        body=draft.body,
        version=draft.version,
        status=draft.status,
        updated_at=draft.updated_at,
    )
