from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_final_quality_assessment import gate_payload, repair_instruction, repair_rejection_reasons
from backend.app.application.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator


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
    ) -> None:
        self._revision = revision_service
        self._validator = validator or DraftValidatorOrchestrator()
        self._regression = regression_guard or DraftRevisionRegressionGuard()

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
            return FinalQualityGateResult(_not_run("no-final-candidate"), None, [])
        if progress:
            progress.start_operation("final-quality-gate", kind="finalQualityGate", label="Check final public prose")
        current_report = self._validate(final_candidate, context_artifact, rule_pack, material_plan)
        initial = gate_payload(final_candidate, current_report, context_artifact, revision_loop_stop_reason)
        if progress:
            progress.complete_operation("final-quality-gate", notes=[f"status={initial['status']}"])
        if initial["status"] == "passed":
            initial["repair"] = {"status": "not-run", "reason": "final-quality-gate-passed"}
            initial["acceptedRepair"] = False
            initial["finalDecision"] = _decision(final_candidate, final_source, "final-quality-gate-passed")
            return FinalQualityGateResult(initial, final_candidate, [])
        instruction = repair_instruction(final_candidate, initial)
        if progress:
            progress.start_operation("final-quality-repair", kind="directedRevision", label="Repair final public prose")
        revision = self._revision.revise(
            candidate=final_candidate,
            instruction=instruction,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        repair = {"instruction": instruction, **revision}
        ai_run_ids = _strings(revision.get("aiRunIds"))
        if progress:
            if revision.get("status") == "succeeded":
                progress.complete_operation("final-quality-repair", ai_run_id=_last(ai_run_ids))
            else:
                progress.fail_operation("final-quality-repair", "final quality repair failed", ai_run_id=_last(ai_run_ids))
        revised = revision.get("revisedCandidate") if isinstance(revision.get("revisedCandidate"), dict) else None
        accepted, regression, repaired_gate, reasons = self._accept_repair(
            original=final_candidate,
            revised=revised,
            current_report=current_report,
            initial_gate=initial,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        repair.update({
            "accepted": accepted,
            "decisionStatus": "accepted" if accepted else "rejected" if revision.get("status") == "succeeded" else "failed",
            "rejectionReasons": [] if accepted else reasons,
        })
        initial.update({
            "repair": repair,
            "acceptedRepair": accepted,
            "repairGate": repaired_gate,
            "repairRegression": regression,
            "finalDecision": _decision(revised if accepted else final_candidate, "finalQualityRepair" if accepted else final_source, "final-quality-repair-accepted" if accepted else "; ".join(reasons)),
        })
        return FinalQualityGateResult(initial, revised if accepted else final_candidate, ai_run_ids)

    def _validate(self, candidate: dict[str, Any], context_artifact: dict[str, Any], rule_pack: dict[str, Any], material_plan: dict[str, Any]) -> dict[str, Any]:
        artifact = {"candidates": [candidate], "selection": {"selectedCandidateId": candidate.get("id"), "scorecard": [{"candidateId": candidate.get("id"), "selectionStatus": "eligible", "publishable": True}]}}
        return self._validator.validate(draft_artifact=artifact, context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan).to_payload()

    def _accept_repair(
        self,
        *,
        original: dict[str, Any],
        revised: dict[str, Any] | None,
        current_report: dict[str, Any],
        initial_gate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> tuple[bool, dict[str, Any] | None, dict[str, Any] | None, list[str]]:
        if progress:
            progress.start_operation("final-quality-regression", kind="regressionGuard", label="Check final repair regression")
        regression = self._regression.evaluate(original_candidate_id=str(original.get("id") or ""), revised_candidate=revised, validation_report=current_report, context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan).to_payload()
        repaired_gate = gate_payload(revised, regression.get("validationReport") or {}, context_artifact, "final-repair") if revised else None
        reasons = repair_rejection_reasons(initial_gate, repaired_gate, regression)
        if progress:
            progress.complete_operation("final-quality-regression", notes=["accepted" if not reasons else "rejected"])
        return not reasons, regression, repaired_gate, reasons

def _decision(candidate: dict[str, Any] | None, source: str, reason: str) -> dict[str, Any]:
    return {"finalCandidateId": (candidate or {}).get("id"), "source": source, "reason": reason}


def _not_run(reason: str) -> dict[str, Any]:
    return {"status": "not-run", "reason": reason, "acceptedRepair": False, "finalDecision": {"source": "none", "reason": reason}}


def _strings(value: Any) -> list[str]:
    return [str(item) for item in value if str(item).strip()] if isinstance(value, list) else []


def _last(values: list[str]) -> str | None:
    return values[-1] if values else None
