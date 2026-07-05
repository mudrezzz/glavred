from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_marks_candidate_selection_blocked_without_final_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(request_payload=request_to_payload(request, draft_context), input_summary={"title": request.brief.title})
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        candidate_generation_service=BlockedCandidateGenerationService(),
    ).execute(run.id)

    complete_step = next(step for step in result.steps if step.key == "complete")
    validation_step = next(step for step in result.steps if step.key == "validation")
    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft is None
    assert result.ai_run_ids == ["ai-candidate-1"]
    assert complete_step.artifact_payload["status"] == "blocked"
    assert complete_step.artifact_payload["blockedBy"] == "draftCandidateSelection"
    assert complete_step.artifact_payload["candidateIds"] == ["candidate-1"]
    assert validation_step.artifact_payload["status"] == "critical"
    assert validation_step.artifact_payload["candidateReports"][0]["candidateId"] == "candidate-1"


class BlockedCandidateGenerationService:
    def create(self, **kwargs) -> DraftCandidateGenerationResult:
        return DraftCandidateGenerationResult(
            artifact_payload={
                "source": "deterministicFallback",
                "fallbackUsed": True,
                "aiRunIds": ["ai-candidate-1"],
                "directions": [{"id": "research"}],
                "candidates": [{"id": "candidate-1", "title": "Fallback", "body": "Needs rewrite"}],
                "selection": {
                    "selectedCandidateId": None,
                    "reason": "No publishable draft candidate passed the selection guard.",
                    "scorecard": [
                        {
                            "candidateId": "candidate-1",
                            "selectionStatus": "excluded",
                            "selectionReasons": ["needs-provider-rewrite"],
                        }
                    ],
                    "unresolvedRisks": ["draft-candidate-selection-blocked"],
                },
            },
            final_draft=None,
            ai_run_ids=["ai-candidate-1"],
        )
