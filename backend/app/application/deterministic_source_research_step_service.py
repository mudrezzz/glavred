from typing import Any

from backend.app.application.deterministic_source_research_plan_service import DeterministicSourceResearchPlanService
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.source_intent_normalizer import SourceIntentNormalizer
from backend.app.domain.draft_generation import DraftGenerationRequest


class DeterministicSourceResearchStepService:
    def __init__(
        self,
        normalizer: SourceIntentNormalizer | None = None,
        plan_service: DeterministicSourceResearchPlanService | None = None,
    ) -> None:
        self._normalizer = normalizer or SourceIntentNormalizer()
        self._plan_service = plan_service or DeterministicSourceResearchPlanService()

    def create(self, *, request: DraftGenerationRequest, context_artifact: dict[str, Any]) -> DraftPlanningStepResult:
        source_intent = self._normalizer.normalize(request)
        research_plan = self._plan_service.create(source_intent)
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "deterministicFallback",
                "aiRunId": None,
                "fallbackUsed": True,
                "sourceIntent": source_intent.to_payload(),
                "researchPlan": research_plan.to_payload(),
                "warning": "OpenRouter research-plan service is not wired in this pipeline.",
            },
            ai_run_id=None,
        )
