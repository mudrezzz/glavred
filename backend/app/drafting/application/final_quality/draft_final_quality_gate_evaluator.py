"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.final_quality.draft_final_quality_assessment import FinalQualityAssessmentPolicy
from backend.app.drafting.application.final_quality.draft_final_quality_gate_payloads import FinalQualityGatePayloadFactory
from backend.app.drafting.application.final_quality.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.drafting.application.validation.draft_validator_orchestrator import DraftValidatorOrchestrator


class FinalQualityGateEvaluator:
    def __init__(
        self,
        *,
        validator: DraftValidatorOrchestrator | None = None,
        review_service: DraftFinalQualityReviewService | None = None,
        assessment_policy: FinalQualityAssessmentPolicy | None = None,
        payloads: FinalQualityGatePayloadFactory | None = None,
    ) -> None:
        self._validator = validator or DraftValidatorOrchestrator()
        self._review = review_service
        self._assessment = assessment_policy or FinalQualityAssessmentPolicy()
        self._payloads = payloads or FinalQualityGatePayloadFactory()

    def validate_candidate(
        self,
        *,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> dict[str, Any]:
        artifact = {
            "candidates": [candidate],
            "selection": {
                "selectedCandidateId": candidate.get("id"),
                "scorecard": [{"candidateId": candidate.get("id"), "selectionStatus": "eligible", "publishable": True}],
            },
        }
        return self._validator.validate(
            draft_artifact=artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        ).to_payload()

    def evaluate(
        self,
        *,
        candidate: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        revision_loop_stop_reason: str,
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        deterministic = self._assessment.gate_payload(candidate, validation_report, context_artifact, revision_loop_stop_reason)
        independent = self._independent_review(candidate, contract, deterministic, validation_report)
        combined = dict(deterministic)
        combined["deterministicGate"] = deterministic
        combined["finalQualityContract"] = contract
        combined["independentReview"] = independent
        combined["modelIndependence"] = independent.get("modelIndependence", "unknown")
        combined["attributionReview"] = self._attribution_review(deterministic, independent)
        combined["status"] = self._payloads.worst_status(deterministic.get("status"), independent.get("status"))
        combined["publicProseStatus"] = self._payloads.worst_status(deterministic.get("publicProseStatus"), independent.get("publicProseStatus"))
        combined["sourceIntegrationStatus"] = self._payloads.worst_status(deterministic.get("sourceIntegrationStatus"), independent.get("sourceIntegrationStatus"))
        combined["authorVoiceStrength"] = self._payloads.worst_status(deterministic.get("authorVoiceStrength"), independent.get("authorVoiceStrength"))
        combined["readerValueClarity"] = self._payloads.worst_status(deterministic.get("readerValueClarity"), independent.get("readerValueClarity"))
        combined["finalRepairGoals"] = self._repair_goals(deterministic, independent)
        return combined

    def _independent_review(
        self,
        candidate: dict[str, Any],
        contract: dict[str, Any],
        deterministic: dict[str, Any],
        validation_report: dict[str, Any],
    ) -> dict[str, Any]:
        if not self._review:
            return {"status": "not-run", "reason": "independent-review-service-not-configured", "attempts": [], "aiRunIds": []}
        return self._review.review(
            candidate=candidate,
            contract=contract,
            deterministic_gate=deterministic,
            validation_report=validation_report,
        )

    def _repair_goals(self, deterministic: dict[str, Any], independent: dict[str, Any]) -> list[str]:
        goals = [*self._payloads.strings(deterministic.get("finalRepairGoals")), *self._payloads.strings(independent.get("repairGoals"))]
        for finding in self._payloads.list_value(independent.get("findings")):
            guidance = self._payloads.dict_value(finding).get("repairGuidance")
            if guidance:
                goals.append(str(guidance))
        return self._payloads.dedupe(goals)[:10]

    def _attribution_review(self, deterministic: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
        actionable = self._payloads.list_value(deterministic.get("actionableAttributionFindings"))
        diagnostic = self._payloads.list_value(deterministic.get("diagnosticAttributionNoise"))
        independent_source_status = str(independent.get("sourceIntegrationStatus") or independent.get("status") or "unknown")
        return {
            "actionableCount": len(actionable),
            "diagnosticCount": len(diagnostic),
            "independentSourceIntegrationStatus": independent_source_status,
            "independentClosedDiagnosticNoise": bool(diagnostic and not actionable and independent_source_status in {"passed", "clean"}),
        }
