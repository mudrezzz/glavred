"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.revision.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.drafting.application.revision.draft_revision_loop_policy import candidate_id, combined_validation, last_value, string_list
from backend.app.drafting.application.revision.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.drafting.application.validation.draft_validation_operation_safety import failed_pairwise_result, failed_revision_result, safe_call
from backend.app.drafting.application.operations.validation_runtime_budget import STOP_BUDGET_EXHAUSTED, operation_denied_by_runtime_budget

class DraftRevisionLoopCycleRunner:
    def __init__(self, *, ranking_service: DraftPairwiseRankingService, revision_service: DraftDirectedRevisionService, regression_guard: DraftRevisionRegressionGuard) -> None:
        self._ranking = ranking_service
        self._revision = revision_service
        self._regression = regression_guard

    def revise(
        self,
        *,
        cycle_number: int,
        candidate: dict[str, Any] | None,
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        operation_id = f"directed-revision-cycle-{cycle_number}"
        if operation_denied_by_runtime_budget(progress, kind="directedRevision", operation_id=operation_id, detail="directed-revision-budget-denied"):
            return failed_revision_result(STOP_BUDGET_EXHAUSTED)
        if progress:
            progress.start_operation(operation_id, kind="directedRevision", label=f"Revision cycle {cycle_number}", target=candidate_id(candidate) or "none")
        revision = safe_call(
            progress=progress,
            operation_id=operation_id,
            fallback=failed_revision_result,
            call=lambda: self._revision.revise(candidate=candidate, instruction=instruction, context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan),
        )
        if progress:
            if revision.get("status") != "succeeded":
                progress.fail_operation(operation_id, str(revision.get("error") or revision.get("reason") or "revision failed"), ai_run_id=last_value(string_list(revision.get("aiRunIds"))))
            else:
                progress.complete_operation(operation_id, ai_run_id=last_value(string_list(revision.get("aiRunIds"))), notes=[f"status={revision.get('status')}"])
        return revision
    def regress(
        self,
        *,
        cycle_number: int,
        current_id: str | None,
        revised: dict[str, Any],
        current_validation: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ):
        operation_id = f"revision-regression-cycle-{cycle_number}"
        if progress:
            progress.start_operation(operation_id, kind="revisionRegression", label=f"Regression guard cycle {cycle_number}")
        regression = self._regression.evaluate(
            original_candidate_id=str(current_id or ""),
            revised_candidate=revised,
            validation_report=current_validation,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        if progress:
            progress.complete_operation(operation_id, notes=[f"accepted={regression.accepted}"])
        return regression
    def compare(
        self,
        *,
        cycle_number: int,
        current: dict[str, Any] | None,
        revised: dict[str, Any],
        current_validation: dict[str, Any],
        revised_validation: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        operation_id = f"revision-pairwise-cycle-{cycle_number}"
        if operation_denied_by_runtime_budget(progress, kind="pairwiseRanking", operation_id=operation_id, detail="pairwise-ranking-budget-denied"):
            return failed_pairwise_result(STOP_BUDGET_EXHAUSTED)
        if progress:
            progress.start_operation(operation_id, kind="pairwiseRanking", label=f"Compare revision cycle {cycle_number}")
        report = safe_call(
            progress=progress,
            operation_id=operation_id,
            fallback=failed_pairwise_result,
            call=lambda: self._ranking.rank(
                draft_artifact={"candidates": [item for item in [current, revised] if item], "selection": {"scorecard": []}},
                validation_report=combined_validation(current_validation, revised_validation),
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
            ).to_payload(),
        )
        if progress:
            if report.get("status") == "failed":
                progress.fail_operation(operation_id, str(report.get("error") or "pairwise failed"), ai_run_id=last_value(string_list(report.get("aiRunIds"))))
            else:
                progress.complete_operation(operation_id, ai_run_id=last_value(string_list(report.get("aiRunIds"))), notes=[f"winner={report.get('decision', {}).get('winnerCandidateId')}"])
        return report
