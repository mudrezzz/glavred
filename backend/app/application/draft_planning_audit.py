from typing import Any

from backend.app.domain.ai_run import AiRunProvider

PLANNING_TEMPERATURE = 0.2
PLANNING_RESPONSE_FORMAT = {"type": "json_object"}


def build_planning_request_trace(
    *,
    step: str,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "draftRunStep": step,
        "requestSummary": {
            "briefId": _get(context_summary, "brief", "id"),
            "title": _get(context_summary, "brief", "title"),
            "topic": _get(context_summary, "topic", "title"),
            "fabula": _get(context_summary, "fabula", "title"),
            "rulePackVersion": _get(rule_pack, "metadata", "version"),
        },
        "capabilityInput": {"contextSummary": context_summary, "rulePack": rule_pack},
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": PLANNING_TEMPERATURE,
            "responseFormat": PLANNING_RESPONSE_FORMAT,
        },
    }
    if material_plan is not None:
        payload["capabilityInput"]["materialPlan"] = material_plan
    return payload


def build_planning_result_trace(
    *,
    step: str,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    fallback: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"draftRunStep": step, "result": result_payload}
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
