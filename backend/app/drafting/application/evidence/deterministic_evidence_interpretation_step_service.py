"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.deterministic_evidence_interpretation import DeterministicEvidenceInterpretationService
from backend.app.drafting.application.evidence.evidence_interpretation_fidelity import EvidenceInterpretationFidelityPolicy
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.domain.draft_model_roles import DraftModelRole


class DeterministicEvidenceInterpretationStepService:
    def __init__(
        self,
        service: DeterministicEvidenceInterpretationService | None = None,
        fidelity_policy: EvidenceInterpretationFidelityPolicy | None = None,
    ) -> None:
        self._service = service or DeterministicEvidenceInterpretationService()
        self._fidelity_policy = fidelity_policy or EvidenceInterpretationFidelityPolicy()

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        progress: Any | None = None,
    ) -> DraftPlanningStepResult:
        if progress:
            progress.start_operation("evidence-interpretation-deterministic", kind="evidenceInterpretation", label="Evidence interpretation deterministic fallback")
        payload = self._service.interpret(context_artifact=context_artifact, rule_pack=rule_pack).to_payload()
        if progress:
            progress.complete_operation("evidence-interpretation-deterministic", notes=["Deterministic evidence interpretation completed."])
        fidelity = self._fidelity_policy.evaluate(
            context_artifact=context_artifact,
            evidence_interpretation=payload,
            attempts=[],
            fallback_used=True,
        ).to_payload()
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "deterministicFallback",
                "aiRunId": None,
                "fallbackUsed": True,
                "evidenceInterpretation": payload,
                "evidenceInterpretationFidelity": fidelity,
                "attempts": [],
                "modelRole": DraftModelRole.STRATEGY.value,
                "selectedModel": None,
                "modelSelectionSource": "unconfigured",
            },
            ai_run_id=None,
            ai_run_ids=[],
        )


DeterministicEvidenceInterpretationFallbackStepService = DeterministicEvidenceInterpretationStepService


__all__ = (
    'DeterministicEvidenceInterpretationStepService',
    'DeterministicEvidenceInterpretationFallbackStepService',
)
