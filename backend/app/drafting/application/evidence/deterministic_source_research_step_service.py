"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.deterministic_source_research_plan_service import DeterministicSourceResearchPlanService
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.evidence.source_intent_normalizer import SourceIntentNormalizer
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
                "sourcesOrigin": _source_origin(context_artifact, request.brief.sources),
                "aiRunId": None,
                "fallbackUsed": True,
                "sourceIntent": source_intent.to_payload(),
                "researchPlan": research_plan.to_payload(),
                "warning": "OpenRouter research-plan service is not wired in this pipeline.",
            },
            ai_run_id=None,
        )


def _source_origin(context_artifact: dict[str, Any], sources: list[str]) -> str:
    defaults = context_artifact.get("sourceIntentDefaults")
    if isinstance(defaults, dict) and isinstance(defaults.get("sourcesOrigin"), str):
        return defaults["sourcesOrigin"]
    return "empty" if not sources else "userOverride"


DeterministicSourceResearchFallbackStepService = DeterministicSourceResearchStepService


__all__ = (
    'DeterministicSourceResearchStepService',
    'DeterministicSourceResearchFallbackStepService',
)
