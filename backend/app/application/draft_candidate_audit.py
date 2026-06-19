from typing import Any

from backend.app.application.draft_candidate_prompts import CANDIDATE_TEMPERATURE
from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_candidates import DraftCandidateDirection


def build_candidate_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_summary: dict[str, Any],
    direction: DraftCandidateDirection,
) -> dict[str, Any]:
    return {
        "draftRunStep": "draftCandidate",
        "direction": direction.to_payload(),
        "requestSummary": {
            "briefId": _get(context_summary, "brief", "id"),
            "title": _get(context_summary, "brief", "title"),
            "topic": _get(context_summary, "topic", "title"),
            "fabula": _get(context_summary, "fabula", "title"),
        },
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": CANDIDATE_TEMPERATURE,
            "responseFormat": {"type": "json_object"},
        },
    }


def build_candidate_result_trace(
    *,
    candidate_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    fallback: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"draftRunStep": "draftCandidate", "candidate": candidate_payload}
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    if fallback is not None:
        payload["fallback"] = fallback
    return payload


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current
