from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_operation_progress_exposes_provider_runtime_fields(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)
    sink = DraftRunProgress(repository, run.id).operation_sink(DraftRunStepKey.MATERIAL_PLAN)

    sink.start_operation(
        "materialPlan",
        kind="materialPlan",
        label="Material plan",
        model_role="strategy",
        selected_model="z-ai/glm-5.2",
        prompt_char_estimate=346264,
        approx_token_estimate=86566,
        stale_after_seconds=900,
    )

    loaded = repository.get(run.id)
    step = next(item for item in loaded.steps if item.key == DraftRunStepKey.MATERIAL_PLAN)
    progress = step.artifact_payload["progress"]
    assert progress["currentOperationId"] == "materialPlan"
    assert progress["operationKind"] == "materialPlan"
    assert progress["selectedModel"] == "z-ai/glm-5.2"
    assert progress["promptCharEstimate"] == 346264
    assert progress["approxTokenEstimate"] == 86566
    assert progress["staleAfterSeconds"] == 900
    assert progress["slowButHealthy"] is True
