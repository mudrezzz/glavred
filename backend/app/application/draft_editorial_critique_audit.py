from typing import Any

from backend.app.application.draft_editorial_critique_prompts import EDITORIAL_CRITIQUE_TEMPERATURE
from backend.app.domain.ai_run import AiRunProvider


def build_editorial_critique_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    candidate_id: str,
    attempt: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    model_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "draftRunStep": "editorialCritique",
        "candidateId": candidate_id,
        "requestSummary": "Report-only prosecutor/editor critique for one draft candidate.",
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": EDITORIAL_CRITIQUE_TEMPERATURE,
            "responseFormat": {"type": "json_object"},
        },
        "attempt": attempt,
    }
    if context_pack is not None:
        payload["contextPack"] = context_pack
    if model_selection is not None:
        payload.update(model_selection)
    return payload


def build_editorial_critique_result_trace(
    *,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    attempt: dict[str, Any],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "draftRunStep": "editorialCritique",
        "attempt": attempt,
        "critiqueResult": result_payload,
    }
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    return payload
