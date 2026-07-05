"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider

SOURCE_RESEARCH_TEMPERATURE = 0.15


class SourceResearchAuditComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_source_research_request_trace(
        *,
        provider: AiRunProvider,
        model: str | None,
        messages: list[dict[str, str]],
        context_artifact: dict[str, Any],
        source_intent: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "draftRunStep": "sourceIntentResearchPlan",
            "requestSummary": {
                "briefId": _get(context_artifact, "brief", "id"),
                "title": _get(context_artifact, "brief", "title"),
                "sourceIntentItems": len(source_intent.get("items", [])) if isinstance(source_intent.get("items"), list) else 0,
            },
            "capabilityInput": {
                "sourceIntent": source_intent,
                "contextSummary": {
                    "brief": context_artifact.get("brief"),
                    "candidate": context_artifact.get("candidate"),
                    "topic": context_artifact.get("topic"),
                    "fabula": context_artifact.get("fabula"),
                },
            },
            "providerRequest": {
                "provider": provider.value,
                "model": model,
                "messages": messages,
                "temperature": SOURCE_RESEARCH_TEMPERATURE,
                "responseFormat": {"type": "json_object"},
            },
        }

    @staticmethod
    def build_source_research_result_trace(
        *,
        result_payload: dict[str, Any],
        provider_response: dict[str, Any] | None,
        fallback: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "draftRunStep": "sourceIntentResearchPlan",
            "result": result_payload,
        }
        if provider_response is not None:
            payload["providerResponse"] = provider_response
        if fallback is not None:
            payload["fallback"] = fallback
        return payload

    @staticmethod
    def _get(payload: dict[str, Any], *path: str) -> Any:
        current: Any = payload
        for key in path:
            current = current.get(key) if isinstance(current, dict) else None
        return current

build_source_research_request_trace = SourceResearchAuditComponent.build_source_research_request_trace
build_source_research_result_trace = SourceResearchAuditComponent.build_source_research_result_trace
_get = SourceResearchAuditComponent._get


__all__ = (
    'SOURCE_RESEARCH_TEMPERATURE',
    'build_source_research_request_trace',
    'build_source_research_result_trace',
    'SourceResearchAuditComponent',
)
