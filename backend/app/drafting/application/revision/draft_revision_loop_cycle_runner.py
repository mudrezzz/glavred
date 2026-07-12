"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.revision.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.drafting.application.revision.draft_revision_loop_policy import RevisionLoopPolicy
from backend.app.drafting.application.revision.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.drafting.application.validation.draft_validation_operation_safety import ValidationOperationFailureMapper
from backend.app.drafting.application.operations.validation_runtime_budget import STOP_BUDGET_EXHAUSTED, ValidationRuntimeBudgetIncidentFactory
from backend.app.drafting.application.context.review_context_checkpoint import ReviewContextCheckpointPublisher
from backend.app.drafting.application.dossiers.provider_dossier_factories import RankingDossierFactory, RevisionDossierFactory

class DraftRevisionLoopCycleRunner:
    def __init__(
        self,
        *,
        ranking_service: DraftPairwiseRankingService,
        revision_service: DraftDirectedRevisionService,
        regression_guard: DraftRevisionRegressionGuard,
        failure_mapper: ValidationOperationFailureMapper | None = None,
        loop_policy: RevisionLoopPolicy | None = None,
    ) -> None:
        self._ranking = ranking_service
        self._revision = revision_service
        self._regression = regression_guard
        self._failure_mapper = failure_mapper or ValidationOperationFailureMapper()
        self._policy = loop_policy or RevisionLoopPolicy()
        self._runtime_budget_incidents = ValidationRuntimeBudgetIncidentFactory()
        self._checkpoints = ReviewContextCheckpointPublisher()

    def revise(
        self,
        *,
        cycle_number: int,
        candidate: dict[str, Any] | None,
        instruction: dict[str, Any],
        current_validation: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        operation_id = f"directed-revision-cycle-{cycle_number}"
        if self._runtime_budget_incidents.operation_denied(progress, kind="directedRevision", operation_id=operation_id, detail="directed-revision-budget-denied"):
            guard = progress.runtime_guard if progress else None
            return self._failure_mapper.failed_revision_result(guard.stop_reason if guard and guard.stop_reason else STOP_BUDGET_EXHAUSTED)
        if progress:
            progress.start_operation(operation_id, kind="directedRevision", label=f"Revision cycle {cycle_number}", target=self._policy.candidate_id(candidate) or "none")
        self._checkpoints.publish(
            progress,
            stage=f"directed-revision-{cycle_number}",
            current_candidate=candidate,
            validation_report=current_validation,
            revision_instruction=instruction,
        )
        revision = self._failure_mapper.safe_call(
            progress=progress,
            operation_id=operation_id,
            fallback=self._failure_mapper.failed_revision_result,
            call=lambda: self._revision.revise(
                candidate=candidate,
                instruction=instruction,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                provider_dossier=RevisionDossierFactory(progress.context_access()).build(candidate_id=self._policy.candidate_id(candidate)) if progress else None,
            ),
        )
        if progress:
            if revision.get("status") != "succeeded":
                progress.fail_operation(operation_id, str(revision.get("error") or revision.get("reason") or "revision failed"), ai_run_id=self._policy.last_value(self._policy.string_list(revision.get("aiRunIds"))))
            else:
                progress.complete_operation(operation_id, ai_run_id=self._policy.last_value(self._policy.string_list(revision.get("aiRunIds"))), notes=[f"status={revision.get('status')}"])
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
        if self._runtime_budget_incidents.operation_denied(progress, kind="pairwiseRanking", operation_id=operation_id, detail="pairwise-ranking-budget-denied"):
            guard = progress.runtime_guard if progress else None
            return self._failure_mapper.failed_pairwise_result(guard.stop_reason if guard and guard.stop_reason else STOP_BUDGET_EXHAUSTED)
        if progress:
            progress.start_operation(operation_id, kind="pairwiseRanking", label=f"Compare revision cycle {cycle_number}")
        comparison_candidates = [item for item in [current, revised] if item]
        combined_validation = self._policy.combined_validation(current_validation, revised_validation)
        self._checkpoints.publish(
            progress,
            stage=f"revision-ranking-{cycle_number}",
            candidates=comparison_candidates,
            validation_report=combined_validation,
        )
        report = self._failure_mapper.safe_call(
            progress=progress,
            operation_id=operation_id,
            fallback=self._failure_mapper.failed_pairwise_result,
            call=lambda: self._ranking.rank(
                draft_artifact={"candidates": comparison_candidates, "selection": {"scorecard": []}},
                validation_report=combined_validation,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                provider_dossier=RankingDossierFactory(progress.context_access()).build() if progress else None,
            ).to_payload(),
        )
        if progress:
            if report.get("status") == "failed":
                progress.fail_operation(operation_id, str(report.get("error") or "pairwise failed"), ai_run_id=self._policy.last_value(self._policy.string_list(report.get("aiRunIds"))))
            else:
                progress.complete_operation(operation_id, ai_run_id=self._policy.last_value(self._policy.string_list(report.get("aiRunIds"))), notes=[f"winner={report.get('decision', {}).get('winnerCandidateId')}"])
        return report
