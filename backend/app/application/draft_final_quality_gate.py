from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_final_quality_contract import build_final_quality_contract
from backend.app.application.draft_final_quality_gate_evaluator import FinalQualityGateEvaluator
from backend.app.application.draft_final_quality_gate_payloads import final_decision, not_run_payload, strings
from backend.app.application.draft_final_quality_repair_loop import FinalQualityRepairLoop
from backend.app.application.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.application.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator
from backend.app.drafting.application.operations.validation_runtime_budget import STOP_BUDGET_EXHAUSTED


@dataclass(frozen=True)
class FinalQualityGateResult:
    artifact_payload: dict[str, Any]
    final_candidate: dict[str, Any] | None
    ai_run_ids: list[str]


class DraftFinalQualityGateService:
    def __init__(
        self,
        *,
        revision_service: DraftDirectedRevisionService,
        validator: DraftValidatorOrchestrator | None = None,
        regression_guard: DraftRevisionRegressionGuard | None = None,
        review_service: DraftFinalQualityReviewService | None = None,
        max_repair_iterations: int = 1,
    ) -> None:
        self._evaluator = FinalQualityGateEvaluator(validator=validator, review_service=review_service)
        self._repair_loop = FinalQualityRepairLoop(
            revision_service=revision_service,
            evaluator=self._evaluator,
            regression_guard=regression_guard,
            max_iterations=max_repair_iterations,
        )

    def run(
        self,
        *,
        final_candidate: dict[str, Any] | None,
        final_source: str,
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        revision_loop_stop_reason: str,
        progress: DraftRunStepOperationSink | None = None,
    ) -> FinalQualityGateResult:
        if not final_candidate:
            return FinalQualityGateResult(not_run_payload("no-final-candidate"), None, [])
        guard = progress.runtime_guard if progress else None
        if guard and not guard.can_start_operation("finalQualityGate", "final-quality-gate"):
            guard.record_stop(STOP_BUDGET_EXHAUSTED, detail="final-quality-gate-budget-denied")
            payload = not_run_payload(STOP_BUDGET_EXHAUSTED)
            payload["runtimeBudget"] = guard.snapshot()
            return FinalQualityGateResult(payload, final_candidate, [])
        if progress:
            progress.start_operation("final-quality-gate", kind="finalQualityGate", label="Check final public prose")
        current_report = self._evaluator.validate_candidate(
            candidate=final_candidate,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        contract = build_final_quality_contract(context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan)
        initial = self._evaluator.evaluate(
            candidate=final_candidate,
            validation_report=current_report,
            context_artifact=context_artifact,
            revision_loop_stop_reason=revision_loop_stop_reason,
            contract=contract,
        )
        if progress:
            progress.complete_operation("final-quality-gate", notes=[f"status={initial['status']}"])
        if initial["status"] == "passed":
            initial["repair"] = {"status": "not-run", "reason": "final-quality-gate-passed"}
            initial["acceptedRepair"] = False
            initial["finalDecision"] = final_decision(final_candidate, final_source, "final-quality-gate-passed")
            return FinalQualityGateResult(initial, final_candidate, strings(initial.get("independentReview", {}).get("aiRunIds")))
        repair = self._repair_loop.run(
            initial_gate=initial,
            final_candidate=final_candidate,
            final_source=final_source,
            current_report=current_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            contract=contract,
            progress=progress,
        )
        initial.update(repair.artifact_updates)
        return FinalQualityGateResult(initial, repair.final_candidate, repair.ai_run_ids)
