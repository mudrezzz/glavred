"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider


class AlternativeAngleTraceBuilder:
    def request_trace(
        self,
        *,
        provider: AiRunProvider,
        model: str | None,
        messages: list[dict[str, str]],
        context_pack: dict[str, Any] | None,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        generation_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        params = generation_params or {"temperature": 0.45}
        return {
            "draftRunStep": "alternativeAngleRoute",
            "attempt": attempt,
            "contextPack": context_pack,
            "providerRequest": {
                "provider": provider.value,
                "model": model,
                "messages": messages,
                "temperature": params.get("temperature"),
                "responseFormat": {"type": "json_object"},
            },
            "generationParams": generation_params,
            **model_selection,
        }

    def result_trace(
        self,
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
