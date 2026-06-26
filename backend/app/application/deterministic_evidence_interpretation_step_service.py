from typing import Any

from backend.app.application.deterministic_evidence_interpretation import DeterministicEvidenceInterpretationService
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.domain.draft_model_roles import DraftModelRole


class DeterministicEvidenceInterpretationStepService:
    def __init__(self, service: DeterministicEvidenceInterpretationService | None = None) -> None:
        self._service = service or DeterministicEvidenceInterpretationService()

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
    ) -> DraftPlanningStepResult:
        payload = self._service.interpret(context_artifact=context_artifact, rule_pack=rule_pack).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "deterministicFallback",
                "aiRunId": None,
                "fallbackUsed": True,
                "evidenceInterpretation": payload,
                "attempts": [],
                "modelRole": DraftModelRole.STRATEGY.value,
                "selectedModel": None,
                "modelSelectionSource": "unconfigured",
            },
            ai_run_id=None,
            ai_run_ids=[],
        )
