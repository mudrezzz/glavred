from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_generation import GeneratedDraft
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_writes_draft_candidates_and_selected_final_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(request_payload=request_to_payload(request, draft_context), input_summary={"title": request.brief.title})
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        candidate_generation_service=StaticCandidateGenerationService(),
    ).execute(run.id)

    draft_step = result.steps[7].artifact_payload
    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.ai_run_ids == ["ai-candidate-1", "ai-candidate-2"]
    assert result.final_draft["title"] == "Selected title"
    assert draft_step["candidates"][0]["id"] == "candidate-1"
    assert draft_step["selection"]["selectedCandidateId"] == "candidate-2"


class StaticCandidateGenerationService:
    def create(self, **kwargs) -> DraftCandidateGenerationResult:
        assert kwargs["material_plan"] is not None
        assert kwargs["draft_strategy"] is not None
        assert kwargs["rhetorical_plans"]["plans"]
        return DraftCandidateGenerationResult(
            artifact_payload={
                "source": "mixed",
                "fallbackUsed": True,
                "aiRunIds": ["ai-candidate-1", "ai-candidate-2"],
                "directions": [{"id": "research"}, {"id": "polemic"}],
                "candidates": [
                    {"id": "candidate-1", "title": "First", "body": "First body"},
                    {"id": "candidate-2", "title": "Selected title", "body": "Selected body"},
                ],
                "selection": {"selectedCandidateId": "candidate-2", "scorecard": [], "unresolvedRisks": []},
            },
            final_draft=GeneratedDraft(
                id="draft-brief-demo",
                brief_id="brief-demo",
                title="Selected title",
                body="Selected body",
                version=1,
                status="draft",
                updated_at="2026-06-19T00:00:00+00:00",
            ),
            ai_run_ids=["ai-candidate-1", "ai-candidate-2"],
        )
