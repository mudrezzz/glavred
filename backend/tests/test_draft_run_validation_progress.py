from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.application.operations.validation_runtime_budget import ValidationRuntimeBudgetPolicy, ValidationRuntimeGuard
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_validation_progress_persists_runtime_budget_snapshot(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)
    guard = ValidationRuntimeGuard(
        ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "standard"}})
    )
    sink = DraftRunProgress(repository, run.id).operation_sink(DraftRunStepKey.VALIDATION, runtime_guard=guard)

    sink.start_operation("pairwise-ranking", kind="pairwiseRanking", label="Rank draft candidates")

    step = next(item for item in repository.get(run.id).steps if item.key == DraftRunStepKey.VALIDATION)
    runtime_budget = step.artifact_payload["progress"]["runtimeBudget"]
    assert runtime_budget["profileId"] == "validationLoop:standard"
    assert runtime_budget["currentOperationId"] == "pairwise-ranking"
    assert runtime_budget["used"]["llmCalls"] == 1
    assert step.artifact_payload["progress"]["budget"]["staleAfterSeconds"] == 900
