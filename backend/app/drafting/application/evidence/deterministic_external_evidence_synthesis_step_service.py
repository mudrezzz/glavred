"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.deterministic_external_evidence_synthesis import (
    DeterministicExternalEvidenceSynthesisService,
)
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult


class DeterministicExternalEvidenceSynthesisStepService:
    def __init__(self, synthesis_service: DeterministicExternalEvidenceSynthesisService | None = None) -> None:
        self._synthesis_service = synthesis_service or DeterministicExternalEvidenceSynthesisService()

    def synthesize(self, *, context_artifact: dict[str, Any], public_evidence: dict[str, Any]) -> DraftPlanningStepResult:
        payload = self._synthesis_service.synthesize(public_evidence, context_artifact).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={"evidenceSynthesis": payload, "fallbackUsed": True},
            ai_run_id=None,
        )


DeterministicExternalEvidenceSynthesisFallbackStepService = DeterministicExternalEvidenceSynthesisStepService


__all__ = (
    'DeterministicExternalEvidenceSynthesisStepService',
    'DeterministicExternalEvidenceSynthesisFallbackStepService',
)
