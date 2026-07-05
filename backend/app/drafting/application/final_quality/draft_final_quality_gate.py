"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.final_quality.draft_final_quality_contract import FinalQualityContractBuilder
from backend.app.drafting.application.final_quality.draft_final_quality_gate_evaluator import FinalQualityGateEvaluator
from backend.app.drafting.application.final_quality.draft_final_quality_gate_payloads import FinalQualityGatePayloadFactory
from backend.app.drafting.application.final_quality.draft_final_quality_repair_loop import FinalQualityRepairLoop
from backend.app.drafting.application.final_quality.draft_final_quality_review_service import DraftFinalQualityReviewService
from backend.app.drafting.application.revision.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.drafting.application.validation.draft_validator_orchestrator import DraftValidatorOrchestrator
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
        contract_builder: FinalQualityContractBuilder | None = None,
        payloads: FinalQualityGatePayloadFactory | None = None,
    ) -> None:
        self._contract_builder = contract_builder or FinalQualityContractBuilder()
        self._payloads = payloads or FinalQualityGatePayloadFactory()
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
            return FinalQualityGateResult(self._payloads.not_run_payload("no-final-candidate"), None, [])
        guard = progress.runtime_guard if progress else None
        if guard and not guard.can_start_operation("finalQualityGate", "final-quality-gate"):
            guard.record_stop(STOP_BUDGET_EXHAUSTED, detail="final-quality-gate-budget-denied")
            payload = self._payloads.not_run_payload(STOP_BUDGET_EXHAUSTED)
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
        contract = self._contract_builder.build(context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan)
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
            initial["finalDecision"] = self._payloads.final_decision(final_candidate, final_source, "final-quality-gate-passed")
            return FinalQualityGateResult(initial, final_candidate, self._payloads.strings(initial.get("independentReview", {}).get("aiRunIds")))
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
