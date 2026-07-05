from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.application.draft_validation_step_service import DraftValidationStepResult
from backend.app.domain.draft_generation import GeneratedDraft
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_allows_validation_to_rescue_blocked_initial_selection(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(request_payload=request_to_payload(request, draft_context), input_summary={"title": request.brief.title})
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        candidate_generation_service=BlockedCandidateGenerationService(),
        validation_step_service=RescuingValidationStepService(),
    ).execute(run.id)

    assert result.final_draft is not None
    assert result.final_draft["id"] == "rescued-draft"
    assert result.ai_run_ids == ["ai-candidate-1", "ai-alternative-1"]
    complete_step = next(step for step in result.steps if step.key == "complete")
    assert complete_step.artifact_payload["status"] == "succeeded"


class BlockedCandidateGenerationService:
    def create(self, **kwargs) -> DraftCandidateGenerationResult:
        return DraftCandidateGenerationResult(
            artifact_payload={"candidates": [{"id": "candidate-1", "title": "Fallback", "body": "Needs rewrite"}], "selection": {"selectedCandidateId": None}},
            final_draft=None,
            ai_run_ids=["ai-candidate-1"],
        )


class RescuingValidationStepService:
    def validate(self, **kwargs) -> DraftValidationStepResult:
        return DraftValidationStepResult({"status": "passed", "alternativeAngleTournament": {"status": "succeeded"}}, ["ai-alternative-1"], _draft())


def _draft() -> GeneratedDraft:
    return GeneratedDraft(
        id="rescued-draft",
        brief_id="brief-demo",
        title="Rescued",
        body="Alternative angle challenger body.",
        version=1,
        status="draft",
        updated_at="2026-06-26T00:00:00+00:00",
    )
