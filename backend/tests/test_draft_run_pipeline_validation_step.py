from typing import Any

from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.generation.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.drafting.application.validation.draft_validation_step_service import DraftValidationStepResult
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_persists_validation_child_ai_run_ids(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        candidate_generation_service=OneDraftService(),
        validation_step_service=ValidationWithAiRuns(),
    ).execute(run.id)

    assert result.ai_run_ids == ["ai-validation-1", "ai-validation-2"]
    assert result.steps[-2].artifact_payload["llmValidationReport"]["status"] == "warning"


class OneDraftService:
    def create(self, *, request: DraftGenerationRequest, **_: Any) -> DraftCandidateGenerationResult:
        return DraftCandidateGenerationResult(
            artifact_payload={"source": "test", "aiRunIds": [], "candidates": [{"id": "candidate-1", "title": "Title", "body": "Body"}]},
            final_draft=GeneratedDraft(
                id="draft-test",
                brief_id=request.brief.id,
                title="Generated title",
                body="Generated body",
                version=1,
                status="draft",
                updated_at="2026-06-23T00:00:00+00:00",
            ),
            ai_run_ids=[],
        )


class ValidationWithAiRuns:
    def validate(self, **_: Any) -> DraftValidationStepResult:
        return DraftValidationStepResult(
            artifact_payload={"status": "warning", "llmValidationReport": {"status": "warning"}},
            ai_run_ids=["ai-validation-1", "ai-validation-2"],
        )

    def not_run(self, *, reason: str) -> DraftValidationStepResult:
        return DraftValidationStepResult({"status": "not-run", "reason": reason}, [])
