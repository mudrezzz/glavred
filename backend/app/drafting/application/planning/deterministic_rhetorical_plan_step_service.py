"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.planning.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.domain.provider_dossier import ProviderDossier


class DeterministicRhetoricalPlanStepService:
    def __init__(self, plan_service: DeterministicRhetoricalPlanService | None = None) -> None:
        self._plan_service = plan_service or DeterministicRhetoricalPlanService()

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        provider_dossier: ProviderDossier | None = None,
    ) -> DraftPlanningStepResult:
        payload = self._plan_service.create_plans(
            context_summary=context_summary,
            rule_registry=_record(rule_pack.get("ruleRegistrySnapshot")),
            post_contract=_record(context_artifact.get("postContract")),
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        ).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "deterministicFallback",
                "fallbackUsed": True,
                "aiRunId": None,
                "rhetoricalPlanSet": payload,
            },
            ai_run_id=None,
        )


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


DeterministicRhetoricalPlanFallbackStepService = DeterministicRhetoricalPlanStepService


__all__ = (
    'DeterministicRhetoricalPlanStepService',
    'DeterministicRhetoricalPlanFallbackStepService',
)
