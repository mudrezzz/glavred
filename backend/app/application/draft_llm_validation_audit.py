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
) -> dict[str, Any]:
    return {
        "draftRunStep": "llmValidation",
        "candidateId": candidate_id,
        "provider": provider.value,
        "model": model,
        "messages": messages,
        "attempt": attempt,
        "deterministicReport": deterministic_report,
        "requestSummary": "LLM-assisted report-only validation for one draft candidate.",
    }


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
