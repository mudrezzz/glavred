from typing import Any

from backend.app.application.draft_final_quality_assessment import gate_payload
from backend.app.application.draft_final_quality_gate_payloads import dedupe, dict_value, list_value, strings, worst_status
from backend.app.application.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator


class FinalQualityGateEvaluator:
    def __init__(
        self,
        *,
        validator: DraftValidatorOrchestrator | None = None,
        review_service: DraftFinalQualityReviewService | None = None,
    ) -> None:
        self._validator = validator or DraftValidatorOrchestrator()
        self._review = review_service

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
        deterministic = gate_payload(candidate, validation_report, context_artifact, revision_loop_stop_reason)
        independent = self._independent_review(candidate, contract, deterministic, validation_report)
        combined = dict(deterministic)
        combined["deterministicGate"] = deterministic
        combined["finalQualityContract"] = contract
        combined["independentReview"] = independent
        combined["modelIndependence"] = independent.get("modelIndependence", "unknown")
        combined["attributionReview"] = self._attribution_review(deterministic, independent)
        combined["status"] = worst_status(deterministic.get("status"), independent.get("status"))
        combined["publicProseStatus"] = worst_status(deterministic.get("publicProseStatus"), independent.get("publicProseStatus"))
        combined["sourceIntegrationStatus"] = worst_status(deterministic.get("sourceIntegrationStatus"), independent.get("sourceIntegrationStatus"))
        combined["authorVoiceStrength"] = worst_status(deterministic.get("authorVoiceStrength"), independent.get("authorVoiceStrength"))
        combined["readerValueClarity"] = worst_status(deterministic.get("readerValueClarity"), independent.get("readerValueClarity"))
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
        goals = [*strings(deterministic.get("finalRepairGoals")), *strings(independent.get("repairGoals"))]
        for finding in list_value(independent.get("findings")):
            guidance = dict_value(finding).get("repairGuidance")
            if guidance:
                goals.append(str(guidance))
        return dedupe(goals)[:10]

    def _attribution_review(self, deterministic: dict[str, Any], independent: dict[str, Any]) -> dict[str, Any]:
        actionable = list_value(deterministic.get("actionableAttributionFindings"))
        diagnostic = list_value(deterministic.get("diagnosticAttributionNoise"))
        independent_source_status = str(independent.get("sourceIntegrationStatus") or independent.get("status") or "unknown")
        return {
            "actionableCount": len(actionable),
            "diagnosticCount": len(diagnostic),
            "independentSourceIntegrationStatus": independent_source_status,
            "independentClosedDiagnosticNoise": bool(diagnostic and not actionable and independent_source_status in {"passed", "clean"}),
        }
