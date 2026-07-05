"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_candidates import DraftCandidateDirection


def build_candidate_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_summary: dict[str, Any],
    direction: DraftCandidateDirection,
    context_pack: dict[str, Any] | None = None,
    model_selection: dict[str, Any] | None = None,
    attempt: dict[str, Any] | None = None,
    generation_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params = generation_params or {"temperature": 0.55}
    payload = {
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
            "temperature": params.get("temperature"),
            "responseFormat": {"type": "json_object"},
        },
    }
    if params.get("topP") is not None:
        payload["providerRequest"]["topP"] = params.get("topP")
    if generation_params is not None:
        payload["generationParams"] = generation_params
    if context_pack is not None:
        payload["contextPack"] = context_pack
    if model_selection is not None:
        payload.update(model_selection)
    if attempt is not None:
        payload["attempt"] = attempt
    return payload


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
