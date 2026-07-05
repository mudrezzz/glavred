"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider


def build_llm_validation_request_trace(
    *,
    provider: AiRunProvider,
    model: str,
    messages: list[dict[str, str]],
    candidate_id: str,
    attempt: dict[str, Any],
    deterministic_report: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    model_selection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "draftRunStep": "llmValidation",
        "candidateId": candidate_id,
        "provider": provider.value,
        "model": model,
        "messages": messages,
        "attempt": attempt,
        "deterministicReport": deterministic_report,
        "requestSummary": "LLM-assisted report-only validation for one draft candidate.",
    }
    if context_pack is not None:
        payload["contextPack"] = context_pack
    if model_selection is not None:
        payload.update(model_selection)
    return payload


def build_llm_validation_result_trace(
    *,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    attempt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "draftRunStep": "llmValidation",
        "attempt": attempt,
        "validationResult": result_payload,
        "providerResponse": provider_response,
    }
