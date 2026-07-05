"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.validation.draft_editorial_critique_prompts import EDITORIAL_CRITIQUE_TEMPERATURE
from backend.app.domain.ai_run import AiRunProvider


class EditorialCritiqueTraceBuilder:
    def request_trace(
        self,
        *,
        provider: AiRunProvider,
        model: str | None,
        messages: list[dict[str, str]],
        candidate_id: str,
        attempt: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        model_selection: dict[str, Any] | None = None,
        input_stats: dict[str, Any] | None = None,
        payload_stats: dict[str, Any] | None = None,
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
            "inputStats": input_stats or {},
            "payloadStats": payload_stats or {},
            "payloadBudget": (payload_stats or {}).get("payloadBudget"),
        }
        if context_pack is not None:
            payload["contextPack"] = context_pack
        if model_selection is not None:
            payload.update(model_selection)
        return payload

    def result_trace(
        self,
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
