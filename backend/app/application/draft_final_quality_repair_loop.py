from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_final_quality_assessment import repair_instruction, repair_rejection_reasons
from backend.app.application.draft_final_quality_gate_evaluator import FinalQualityGateEvaluator
from backend.app.application.draft_final_quality_gate_payloads import final_decision, gate_improved, last, strings, unique
from backend.app.application.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink


@dataclass(frozen=True)
class FinalQualityRepairLoopResult:
    artifact_updates: dict[str, Any]
    final_candidate: dict[str, Any]
    ai_run_ids: list[str]


class FinalQualityRepairLoop:
    def __init__(
        self,
        *,
        revision_service: DraftDirectedRevisionService,
        evaluator: FinalQualityGateEvaluator,
        regression_guard: DraftRevisionRegressionGuard | None = None,
        max_iterations: int = 1,
    ) -> None:
        self._revision = revision_service
        self._evaluator = evaluator
        self._regression = regression_guard or DraftRevisionRegressionGuard()
        self._max_iterations = max(1, int(max_iterations or 1))

    def run(
        self,
        *,
        initial_gate: dict[str, Any],
        final_candidate: dict[str, Any],
        final_source: str,
        current_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        contract: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> FinalQualityRepairLoopResult:
        current_candidate = final_candidate
        current_gate = initial_gate
        cycles: list[dict[str, Any]] = []
        ai_run_ids: list[str] = strings(initial_gate.get("independentReview", {}).get("aiRunIds"))
        accepted_any = False
        last_repair: dict[str, Any] = {"status": "not-run", "reason": "no-final-repair-cycle"}
        repaired_gate: dict[str, Any] | None = None
        regression: dict[str, Any] | None = None
        reasons: list[str] = []
        for cycle in range(1, self._max_iterations + 1):
            if current_gate.get("status") == "passed":
                break
            repair, revised, cycle_ids = self._revise_cycle(
                cycle, current_candidate, current_gate, context_artifact, rule_pack, material_plan, progress
            )
            ai_run_ids.extend(cycle_ids)
            accepted, regression, repaired_gate, reasons = self._accept_repair(
                cycle=cycle,
                original=current_candidate,
                revised=revised,
                current_report=current_report,
                initial_gate=current_gate,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                contract=contract,
                progress=progress,
            )
            ai_run_ids.extend(strings((repaired_gate or {}).get("independentReview", {}).get("aiRunIds")))
            repair.update({
                "accepted": accepted,
                "decisionStatus": "accepted" if accepted else "rejected" if repair.get("status") == "succeeded" else "failed",
                "rejectionReasons": [] if accepted else reasons,
                "repairGate": repaired_gate,
                "repairRegression": regression,
            })
            cycles.append(repair)
            last_repair = repair
            if not accepted:
                break
            accepted_any = True
            current_candidate = revised or current_candidate
            current_gate = repaired_gate or current_gate
            current_report = regression.get("validationReport") if isinstance(regression, dict) else current_report
        updates = {
            "repair": last_repair,
            "repairCycles": cycles,
            "maxRepairIterations": self._max_iterations,
            "acceptedRepair": accepted_any,
            "repairGate": repaired_gate,
            "repairRegression": regression,
            "finalDecision": final_decision(
                current_candidate if accepted_any else final_candidate,
                "finalQualityRepair" if accepted_any else final_source,
                "final-quality-repair-accepted" if accepted_any else "; ".join(reasons),
            ),
        }
        return FinalQualityRepairLoopResult(updates, current_candidate if accepted_any else final_candidate, unique(ai_run_ids))

    def _revise_cycle(
        self,
        cycle: int,
        current_candidate: dict[str, Any],
        current_gate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> tuple[dict[str, Any], dict[str, Any] | None, list[str]]:
        operation_id = f"final-quality-repair-cycle-{cycle}"
        if progress:
            progress.start_operation(operation_id, kind="directedRevision", label=f"Repair final public prose cycle {cycle}")
        revision = self._revision.revise(candidate=current_candidate, instruction=repair_instruction(current_candidate, current_gate), context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan)
        ai_run_ids = strings(revision.get("aiRunIds"))
        if progress:
            if revision.get("status") == "succeeded":
                progress.complete_operation(operation_id, ai_run_id=last(ai_run_ids))
            else:
                progress.fail_operation(operation_id, "final quality repair failed", ai_run_id=last(ai_run_ids))
        revised = revision.get("revisedCandidate") if isinstance(revision.get("revisedCandidate"), dict) else None
        return {"cycleNumber": cycle, "instruction": repair_instruction(current_candidate, current_gate), **revision}, revised, ai_run_ids

    def _accept_repair(
        self,
        *,
        cycle: int,
        original: dict[str, Any],
        revised: dict[str, Any] | None,
        current_report: dict[str, Any],
        initial_gate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        contract: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> tuple[bool, dict[str, Any] | None, dict[str, Any] | None, list[str]]:
        operation_id = f"final-quality-regression-cycle-{cycle}"
        if progress:
            progress.start_operation(operation_id, kind="regressionGuard", label=f"Check final repair regression cycle {cycle}")
        regression = self._regression.evaluate(original_candidate_id=str(original.get("id") or ""), revised_candidate=revised, validation_report=current_report, context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan).to_payload()
        repaired_gate = self._evaluator.evaluate(candidate=revised, validation_report=regression.get("validationReport") or {}, context_artifact=context_artifact, revision_loop_stop_reason="final-repair", contract=contract) if revised else None
        reasons = repair_rejection_reasons(initial_gate, repaired_gate, regression)
        if repaired_gate and not gate_improved(initial_gate, repaired_gate):
            reasons.append("final-quality-contract-not-improved")
        if progress:
            progress.complete_operation(operation_id, notes=["accepted" if not reasons else "rejected"])
        return not reasons, regression, repaired_gate, reasons
