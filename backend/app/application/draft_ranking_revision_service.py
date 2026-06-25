from datetime import UTC, datetime
from typing import Any

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_ranking_revision_result import DraftRankingRevisionResult
from backend.app.application.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
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
    ) -> None:
        self._ranking = ranking_service
        self._revision = revision_service
        self._instruction_builder = instruction_builder or DraftRevisionInstructionBuilder()
        self._regression = regression_guard or DraftRevisionRegressionGuard()

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
        ranking = self._ranking.rank(
            draft_artifact=draft_artifact,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        if progress:
            progress.complete_operation("pairwise-ranking", ai_run_id=_last(ranking.ai_run_ids))
        winner_id = ranking.decision.winner_candidate_id
        winner = _candidate_by_id(draft_artifact, winner_id)
        instruction = self._instruction_builder.build(candidate_id=winner_id, validation_report=validation_report)
        if progress:
            progress.start_operation("directed-revision", kind="directedRevision", label="Revise ranked winner", target=str(winner_id or "none"))
        revision = self._revision.revise(
            candidate=winner,
            instruction=instruction.to_payload(),
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        revision_ai_ids = [str(item) for item in revision.get("aiRunIds", [])]
        if progress:
            progress.complete_operation("directed-revision", ai_run_id=_last(revision_ai_ids), notes=[f"status={revision.get('status')}"])
        revised_candidate = revision.get("revisedCandidate") if isinstance(revision.get("revisedCandidate"), dict) else None
        if progress:
            progress.start_operation("revision-regression", kind="revisionRegression", label="Check revised candidate regression")
        regression = self._regression.evaluate(
            original_candidate_id=str(winner_id or ""),
            revised_candidate=revised_candidate,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        if progress:
            progress.complete_operation("revision-regression", notes=[f"accepted={regression.accepted}"])
        revision_accepted = regression.accepted and revised_candidate is not None
        final_candidate = revised_candidate if revision_accepted else winner
        final_source = "revisedCandidate" if revision_accepted else "originalCandidate"
        artifact = {
            "status": "succeeded" if final_candidate else "blocked",
            "pairwiseRanking": ranking.to_payload(),
            "revisionInstruction": instruction.to_payload(),
            "revisedCandidate": revision.get("revisedCandidate"),
            "revision": revision,
            "revisionRegression": regression.to_payload(),
            "finalDecision": {
                "finalCandidateId": final_candidate.get("id") if final_candidate else None,
                "baseCandidateId": winner_id,
                "source": final_source if final_candidate else "none",
                "reason": _final_reason(final_source, ranking.decision.reason, regression.reasons),
            },
        }
        ai_run_ids = [*ranking.ai_run_ids, *revision_ai_ids]
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


def _final_reason(source: str, ranking_reason: str, regression_reasons: list[str]) -> str:
    if source == "revisedCandidate":
        return "Accepted directed revision after regression guard."
    return f"Kept original ranked candidate. Ranking: {ranking_reason}. Revision/regression: {'; '.join(regression_reasons)}"


def _last(values: list[str]) -> str | None:
    return values[-1] if values else None
