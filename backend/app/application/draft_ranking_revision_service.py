from datetime import UTC, datetime
from typing import Any

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_ranking_revision_result import DraftRankingRevisionResult
from backend.app.application.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
from backend.app.application.draft_revision_loop_service import DraftRevisionLoopService
from backend.app.application.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


class DraftRankingRevisionService:
    def __init__(
        self,
        *,
        ranking_service: DraftPairwiseRankingService,
        revision_service: DraftDirectedRevisionService,
        instruction_builder: DraftRevisionInstructionBuilder | None = None,
        regression_guard: DraftRevisionRegressionGuard | None = None,
        max_iterations: int = 3,
    ) -> None:
        self._ranking = ranking_service
        self._loop = DraftRevisionLoopService(
            ranking_service=ranking_service,
            revision_service=revision_service,
            instruction_builder=instruction_builder or DraftRevisionInstructionBuilder(),
            regression_guard=regression_guard or DraftRevisionRegressionGuard(),
            max_iterations=max_iterations,
        )

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
        if progress:
            progress.start_operation("pairwise-ranking", kind="pairwiseRanking", label="Rank draft candidates")
        try:
            ranking = self._ranking.rank(
                draft_artifact=draft_artifact,
                validation_report=validation_report,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
            )
        except Exception as exc:
            if progress:
                progress.fail_operation("pairwise-ranking", _safe_error(exc))
            ranking = DeterministicPairwiseRanker().rank(draft_artifact=draft_artifact, validation_report=validation_report)
        if progress:
            progress.complete_operation("pairwise-ranking", ai_run_id=_last(ranking.ai_run_ids))
        winner_id = ranking.decision.winner_candidate_id
        winner = _candidate_by_id(draft_artifact, winner_id)
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
        artifact = {
            "status": "succeeded" if final_candidate else "blocked",
            "pairwiseRanking": ranking.to_payload(),
            "revisionInstruction": loop.first_instruction,
            "revisedCandidate": _last_revised(loop.report.to_payload()),
            "revision": loop.last_revision,
            "revisionRegression": loop.last_regression,
            "revisionLoop": loop.report.to_payload(),
            "finalDecision": {
                "finalCandidateId": final_candidate.get("id") if final_candidate else None,
                "baseCandidateId": winner_id,
                "source": final_source if final_candidate else "none",
                "stopReason": loop.report.stop_reason,
                "reason": _final_reason(final_source, ranking.decision.reason, loop.report.stop_reason),
            },
        }
        ai_run_ids = [*ranking.ai_run_ids, *loop.ai_run_ids]
        return DraftRankingRevisionResult(
            artifact_payload=artifact,
            final_draft=_candidate_to_draft(request, final_candidate) if final_candidate else None,
            ai_run_ids=ai_run_ids,
        )


def _candidate_by_id(draft_artifact: dict[str, Any], candidate_id: str | None) -> dict[str, Any] | None:
    for candidate in draft_artifact.get("candidates", []):
        if isinstance(candidate, dict) and candidate.get("id") == candidate_id:
            return candidate
    return None


def _candidate_to_draft(request: DraftGenerationRequest, candidate: dict[str, Any]) -> GeneratedDraft:
    return GeneratedDraft(
        id=f"draft-{request.brief.id}",
        brief_id=request.brief.id,
        title=str(candidate.get("title") or request.brief.title),
        body=str(candidate.get("body") or ""),
        version=1,
        status="draft",
        updated_at=datetime.now(UTC).isoformat(),
    )


def _last_revised(loop_payload: dict[str, Any]) -> dict[str, Any] | None:
    for cycle in reversed(loop_payload.get("cycles", [])):
        if isinstance(cycle, dict) and isinstance(cycle.get("revisedCandidate"), dict):
            return cycle["revisedCandidate"]
    return None


def _final_reason(source: str, ranking_reason: str, stop_reason: str) -> str:
    if source == "revisionLoop":
        return f"Accepted best candidate from revision loop. Stop reason: {stop_reason}."
    return f"Kept original ranked candidate. Ranking: {ranking_reason}. Stop reason: {stop_reason}."


def _last(values: list[str]) -> str | None:
    return values[-1] if values else None


def _safe_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {' '.join(str(error).split())[:240]}"
