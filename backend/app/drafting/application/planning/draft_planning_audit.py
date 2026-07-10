"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider

PLANNING_TEMPERATURE = 0.2
PLANNING_RESPONSE_FORMAT = {"type": "json_object"}


class DraftPlanningAuditComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_planning_request_trace(
        *,
        step: str,
        provider: AiRunProvider,
        model: str | None,
        messages: list[dict[str, str]],
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any] | None = None,
        usable_evidence_candidates: list[dict[str, Any]] | None = None,
        context_pack: dict[str, Any] | None = None,
        attempt: dict[str, Any] | None = None,
        model_selection: dict[str, Any] | None = None,
        provider_dossier: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        capability_input = (
            {
                "dossierProfileId": provider_dossier.get("profileId"),
                "runtimeMigrated": provider_dossier.get("runtimeMigrated"),
            }
            if provider_dossier is not None
            else {"contextSummary": context_summary, "rulePack": rule_pack}
        )
        payload: dict[str, Any] = {
            "draftRunStep": step,
            "requestSummary": {
                "briefId": _get(context_summary, "brief", "id"),
                "title": _get(context_summary, "brief", "title"),
                "topic": _get(context_summary, "topic", "title"),
                "fabula": _get(context_summary, "fabula", "title"),
                "rulePackVersion": _get(rule_pack, "metadata", "version"),
            },
            "capabilityInput": capability_input,
            "providerRequest": {
                "provider": provider.value,
                "model": model,
                "messages": messages,
                "temperature": PLANNING_TEMPERATURE,
                "responseFormat": PLANNING_RESPONSE_FORMAT,
            },
        }
        if material_plan is not None and provider_dossier is None:
            payload["capabilityInput"]["materialPlan"] = material_plan
        if usable_evidence_candidates is not None and provider_dossier is None:
            payload["capabilityInput"]["usableEvidenceCandidates"] = usable_evidence_candidates
        if context_pack is not None and provider_dossier is None:
            payload["capabilityInput"]["contextPack"] = context_pack
        if provider_dossier is not None:
            payload["providerDossier"] = provider_dossier
        if attempt is not None:
            payload["attempt"] = attempt
        if model_selection is not None:
            payload.update(model_selection)
        return payload

    @staticmethod
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

    @staticmethod
    def _get(payload: dict[str, Any], *path: str) -> Any:
        current: Any = payload
        for key in path:
            current = current.get(key) if isinstance(current, dict) else None
        return current

build_planning_request_trace = DraftPlanningAuditComponent.build_planning_request_trace
build_planning_result_trace = DraftPlanningAuditComponent.build_planning_result_trace
_get = DraftPlanningAuditComponent._get


__all__ = (
    'PLANNING_TEMPERATURE',
    'PLANNING_RESPONSE_FORMAT',
    'build_planning_request_trace',
    'build_planning_result_trace',
    'DraftPlanningAuditComponent',
)
