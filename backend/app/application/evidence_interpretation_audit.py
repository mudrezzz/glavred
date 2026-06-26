from typing import Any

from backend.app.application.evidence_interpretation_prompts import EVIDENCE_INTERPRETATION_TEMPERATURE
from backend.app.domain.ai_run import AiRunProvider


def build_evidence_interpretation_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_summary: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    context_pack: dict[str, Any] | None,
    attempt: dict[str, Any] | None = None,
    model_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "draftRunStep": "evidenceInterpretation",
        "requestSummary": {
            "briefId": _get(context_summary, "brief", "id"),
            "title": _get(context_summary, "brief", "title"),
            "topic": _get(context_summary, "topic", "title"),
            "fabula": _get(context_summary, "fabula", "title"),
            "externalClaimCount": _get(context_artifact, "sourceLedger", "metadata", "externalClaimCount"),
            "ruleCount": len(_get(rule_pack, "ruleRegistrySnapshot", "rules") or []),
        },
        "capabilityInput": {
            "postContract": context_artifact.get("postContract"),
            "sourceLedger": context_artifact.get("sourceLedger"),
            "publicEvidence": context_artifact.get("publicEvidence"),
            "evidenceSynthesis": context_artifact.get("evidenceSynthesis"),
            "ruleRegistrySnapshot": rule_pack.get("ruleRegistrySnapshot"),
            "contextPack": context_pack,
        },
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": EVIDENCE_INTERPRETATION_TEMPERATURE,
            "responseFormat": {"type": "json_object"},
        },
    }
    if attempt is not None:
        payload["attempt"] = attempt
    if model_selection is not None:
        payload.update(model_selection)
    return payload


def build_evidence_interpretation_result_trace(
    *,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    fallback: str | None = None,
    attempt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"draftRunStep": "evidenceInterpretation", "result": result_payload}
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    if fallback is not None:
        payload["fallback"] = fallback
    if attempt is not None:
        payload["attempt"] = attempt
    return payload


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current
