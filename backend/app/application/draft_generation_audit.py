from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_generation import (
    DRAFT_RESPONSE_FORMAT,
    DRAFT_TEMPERATURE,
    DraftGenerationRequest,
    GeneratedDraft,
)


def build_draft_request_trace(
    request: DraftGenerationRequest,
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
) -> dict[str, object]:
    return {
        "requestSummary": {
            "briefId": request.brief.id,
            "title": request.brief.title,
            "rubric": request.brief.rubric,
            "audience": request.brief.audience,
            "thesis": request.brief.thesis,
            "modelAudience": request.editorial_model.audience,
        },
        "capabilityInput": {
            "brief": {
                "id": request.brief.id,
                "title": request.brief.title,
                "rubric": request.brief.rubric,
                "audience": request.brief.audience,
                "thesis": request.brief.thesis,
                "conflict": request.brief.conflict,
                "authorPosition": request.brief.author_position,
                "evidence": request.brief.evidence,
                "examples": request.brief.examples,
                "structure": request.brief.structure,
                "cta": request.brief.cta,
                "risks": request.brief.risks,
                "sources": request.brief.sources,
            },
            "editorialModel": {
                "audience": request.editorial_model.audience,
                "styleRules": request.editorial_model.style_rules,
                "forbiddenTopics": request.editorial_model.forbidden_topics,
                "goals": request.editorial_model.goals,
            },
        },
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": DRAFT_TEMPERATURE,
            "responseFormat": DRAFT_RESPONSE_FORMAT,
        },
    }


def build_draft_result_trace(
    draft: GeneratedDraft,
    *,
    provider_response: dict[str, object] | None,
    fallback: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "draft": {
            "draftId": draft.id,
            "briefId": draft.brief_id,
            "title": draft.title,
            "body": draft.body,
            "version": draft.version,
            "status": draft.status,
            "updatedAt": draft.updated_at,
        },
    }
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    if fallback is not None:
        payload["fallback"] = fallback
    return payload
