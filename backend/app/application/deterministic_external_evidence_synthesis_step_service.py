from typing import Any

from backend.app.application.deterministic_external_evidence_synthesis import (
    DeterministicExternalEvidenceSynthesisService,
)
from backend.app.application.draft_planning_result import DraftPlanningStepResult


class DeterministicExternalEvidenceSynthesisStepService:
    def __init__(self, synthesis_service: DeterministicExternalEvidenceSynthesisService | None = None) -> None:
        self._synthesis_service = synthesis_service or DeterministicExternalEvidenceSynthesisService()

    def synthesize(self, *, context_artifact: dict[str, Any], public_evidence: dict[str, Any]) -> DraftPlanningStepResult:
        payload = self._synthesis_service.synthesize(public_evidence, context_artifact).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={"evidenceSynthesis": payload, "fallbackUsed": True},
            ai_run_id=None,
        )
