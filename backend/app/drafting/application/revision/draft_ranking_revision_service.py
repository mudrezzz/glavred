"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.drafting.application.revision.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.revision.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.drafting.application.final_quality.draft_final_quality_gate import DraftFinalQualityGateService
from backend.app.drafting.application.revision.draft_ranking_revision_mapping import RankingRevisionCandidateMapper
from backend.app.drafting.application.revision.draft_ranking_revision_result import DraftRankingRevisionResult
from backend.app.drafting.application.revision.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
from backend.app.drafting.application.revision.draft_revision_loop_service import DraftRevisionLoopService
from backend.app.drafting.application.revision.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.drafting.application.operations.validation_runtime_budget import STOP_BUDGET_EXHAUSTED, ValidationStopReasonPolicy


class DraftRankingRevisionService:
    def __init__(
        self,
        *,
        ranking_service: DraftPairwiseRankingService,
        revision_service: DraftDirectedRevisionService,
        instruction_builder: DraftRevisionInstructionBuilder | None = None,
        regression_guard: DraftRevisionRegressionGuard | None = None,
        final_quality_gate: DraftFinalQualityGateService | None = None,
        max_iterations: int = 3,
        candidate_mapper: RankingRevisionCandidateMapper | None = None,
    ) -> None:
        self._ranking = ranking_service
        self._candidates = candidate_mapper or RankingRevisionCandidateMapper()
        self._stop_reason_policy = ValidationStopReasonPolicy()
        guard = regression_guard or DraftRevisionRegressionGuard()
        self._loop = DraftRevisionLoopService(
            ranking_service=ranking_service,
            revision_service=revision_service,
            instruction_builder=instruction_builder or DraftRevisionInstructionBuilder(),
            regression_guard=guard,
            max_iterations=max_iterations,
        )
        self._final_gate = final_quality_gate or DraftFinalQualityGateService(revision_service=revision_service, regression_guard=guard)

    def run(
        self,
        *,
        request: DraftGenerationRequest,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftRankingRevisionResult:
        guard = progress.runtime_guard if progress else None
        initial_pairwise_denied = bool(guard and not guard.can_start_operation("pairwiseRanking", "pairwise-ranking"))
        if initial_pairwise_denied and guard:
            guard.record_stop(STOP_BUDGET_EXHAUSTED, detail="initial-pairwise-budget-denied")
        if progress:
            progress.start_operation("pairwise-ranking", kind="pairwiseRanking", label="Rank draft candidates")
        try:
            if initial_pairwise_denied:
                raise RuntimeError(STOP_BUDGET_EXHAUSTED)
            ranking = self._ranking.rank(
                draft_artifact=draft_artifact,
                validation_report=validation_report,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
            )
        except Exception as exc:
            if progress:
                if initial_pairwise_denied:
                    progress.complete_operation("pairwise-ranking", notes=[STOP_BUDGET_EXHAUSTED])
                else:
                    progress.fail_operation("pairwise-ranking", self._candidates.safe_error(exc))
            ranking = DeterministicPairwiseRanker().rank(draft_artifact=draft_artifact, validation_report=validation_report)
        if progress:
            progress.complete_operation("pairwise-ranking", ai_run_id=self._candidates.last(ranking.ai_run_ids))
        winner_id = ranking.decision.winner_candidate_id
        winner = self._candidates.candidate_by_id(draft_artifact, winner_id)
        loop = self._loop.run(
            winner=winner,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        final_candidate = loop.final_candidate
        final_source = loop.report.final_source
        final_gate = self._final_gate.run(
            final_candidate=final_candidate,
            final_source=final_source if final_candidate else "none",
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            revision_loop_stop_reason=loop.report.stop_reason,
            progress=progress,
        )
        final_candidate = final_gate.final_candidate
        final_decision = final_gate.artifact_payload.get("finalDecision", {})
        runtime_stop_reason = guard.stop_reason if guard and guard.stop_reason else None
        final_stop_reason = self._stop_reason_policy.final_validation_stop_reason(
            final_candidate=final_candidate,
            loop_stop_reason=loop.report.stop_reason,
            runtime_stop_reason=runtime_stop_reason,
            final_gate=final_gate.artifact_payload,
        )
        if guard:
            guard.record_stop(final_stop_reason, detail=loop.report.detail_stop_reason)
        artifact = {
            "status": "succeeded" if final_candidate else "blocked",
            "pairwiseRanking": ranking.to_payload(),
            "revisionInstruction": loop.first_instruction,
            "revisedCandidate": self._candidates.last_revised(loop.report.to_payload()),
            "revision": loop.last_revision,
            "revisionRegression": loop.last_regression,
            "revisionLoop": loop.report.to_payload(),
            "finalQualityGate": final_gate.artifact_payload,
            "runtimeBudget": guard.snapshot() if guard else {},
            "finalDecision": {
                "finalCandidateId": final_candidate.get("id") if final_candidate else None,
                "baseCandidateId": winner_id,
                "source": final_decision.get("source") or final_source if final_candidate else "none",
                "stopReason": final_stop_reason,
                "detailStopReason": loop.report.detail_stop_reason,
                "reason": final_decision.get("reason") or self._candidates.final_reason(final_source, ranking.decision.reason, loop.report.stop_reason),
            },
        }
        ai_run_ids = [*ranking.ai_run_ids, *loop.ai_run_ids, *final_gate.ai_run_ids]
        return DraftRankingRevisionResult(
            artifact_payload=artifact,
            final_draft=self._candidates.candidate_to_draft(request, final_candidate) if final_candidate else None,
            ai_run_ids=ai_run_ids,
        )
