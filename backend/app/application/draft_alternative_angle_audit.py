from typing import Any

from backend.app.application.draft_alternative_angle_prompts import ALTERNATIVE_ANGLE_TEMPERATURE
from backend.app.domain.ai_run import AiRunProvider


def build_alternative_angle_request_trace(
    *,
    provider: AiRunProvider,
    model: str | None,
    messages: list[dict[str, str]],
    context_pack: dict[str, Any] | None,
    attempt: dict[str, Any],
    model_selection: dict[str, Any],
) -> dict[str, Any]:
    return {
        "draftRunStep": "alternativeAngleRoute",
        "attempt": attempt,
        "contextPack": context_pack,
        "providerRequest": {
            "provider": provider.value,
            "model": model,
            "messages": messages,
            "temperature": ALTERNATIVE_ANGLE_TEMPERATURE,
            "responseFormat": {"type": "json_object"},
        },
        **model_selection,
    }


def build_alternative_angle_result_trace(
    *,
    result_payload: dict[str, Any],
    provider_response: dict[str, Any] | None,
    attempt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"draftRunStep": "alternativeAngleRoute", "result": result_payload}
    if attempt:
        payload["attempt"] = attempt
    if provider_response is not None:
        payload["providerResponse"] = provider_response
    return payload
