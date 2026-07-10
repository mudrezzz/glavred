"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.ai_run import AiRunProvider


class DraftRhetoricalPlanAuditComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
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
        context_pack: dict[str, Any] | None = None,
        attempt: dict[str, Any] | None = None,
        model_selection: dict[str, Any] | None = None,
        provider_dossier: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
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
        if context_pack is not None and provider_dossier is None:
            payload["contextPack"] = context_pack
        if provider_dossier is not None:
            payload["providerDossier"] = provider_dossier
        if model_selection is not None:
            payload.update(model_selection)
        return payload

    @staticmethod
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

    @staticmethod
    def _get(payload: dict[str, Any], *path: str) -> Any:
        current: Any = payload
        for key in path:
            current = current.get(key) if isinstance(current, dict) else None
        return current

build_rhetorical_plan_request_trace = DraftRhetoricalPlanAuditComponent.build_rhetorical_plan_request_trace
build_rhetorical_plan_result_trace = DraftRhetoricalPlanAuditComponent.build_rhetorical_plan_result_trace
_get = DraftRhetoricalPlanAuditComponent._get


__all__ = (
    'build_rhetorical_plan_request_trace',
    'build_rhetorical_plan_result_trace',
    'DraftRhetoricalPlanAuditComponent',
)
