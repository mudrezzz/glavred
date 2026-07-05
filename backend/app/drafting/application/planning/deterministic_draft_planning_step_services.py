"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult


class DeterministicMaterialPlanStepService:
    def __init__(self, planning_service: DeterministicDraftPlanningService) -> None:
        self._planning_service = planning_service

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        context_artifact: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        payload = self._planning_service.create_material_plan(
            context_summary=context_summary,
            rule_pack=rule_pack,
        ).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={"source": "deterministicFallback", "fallbackUsed": True, "materialPlan": payload},
            ai_run_id=None,
        )


class DeterministicStrategyStepService:
    def __init__(self, planning_service: DeterministicDraftPlanningService) -> None:
        self._planning_service = planning_service

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        payload = self._planning_service.create_strategy(
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
        ).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={"source": "deterministicFallback", "fallbackUsed": True, "draftStrategy": payload},
            ai_run_id=None,
        )


class DeterministicDraftPlanningFallbackStepServices:
    material_plan_service = DeterministicMaterialPlanStepService
    strategy_service = DeterministicStrategyStepService


__all__ = (
    'DeterministicMaterialPlanStepService',
    'DeterministicStrategyStepService',
    'DeterministicDraftPlanningStepServices',
    'DeterministicDraftPlanningFallbackStepServices',
)
