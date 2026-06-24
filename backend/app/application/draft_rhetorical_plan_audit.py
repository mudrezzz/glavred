from typing import Any

from backend.app.domain.ai_run import AiRunProvider


def build_rhetorical_plan_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_summary: dict[str, Any],
    post_contract: dict[str, Any],
    rule_registry: dict[str, Any],
    material_plan: dict[str, Any],
    draft_strategy: dict[str, Any],
    attempt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "draftRunStep": "rhetoricalPlans",
        "provider": provider.value,
        "model": model,
        "providerRequest": {"messages": messages},
        "summary": {
            "topic": _get(context_summary, "topic", "title"),
            "fabula": _get(context_summary, "fabula", "title"),
            "contractStatus": post_contract.get("status"),
            "rules": len(rule_registry.get("rules") or []),
            "availableEvidence": len(material_plan.get("availableEvidence") or []),
            "strategyAngle": draft_strategy.get("thesisAngle"),
        },
        "attempt": attempt,
    }


def build_rhetorical_plan_result_trace(
    *,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    fallback: str | None = None,
    attempt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "draftRunStep": "rhetoricalPlans",
        "rhetoricalPlanSet": result_payload,
        "planCount": len(result_payload.get("plans") or []),
    }
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    if fallback:
        payload["fallback"] = fallback
    if attempt:
        payload["attempt"] = attempt
    return payload


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current
