from typing import Any

from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.domain.draft_run import DraftRunStepStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_marks_long_steps_running_and_persists_child_ai_ids(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        material_plan_service=AssertingMaterialPlanService(repository, run.id),
        strategy_service=AssertingStrategyService(repository, run.id),
        rhetorical_plan_service=AssertingRhetoricalPlanService(repository, run.id),
        candidate_generation_service=AssertingDraftService(repository, run.id),
    ).execute(run.id)

    assert result.ai_run_ids == ["ai-material", "ai-strategy", "ai-plans", "ai-draft"]
    assert result.final_draft["body"] == "Generated body"


class AssertingMaterialPlanService:
    def __init__(self, repository: SqliteDraftRunRepository, run_id: str) -> None:
        self._repository = repository
        self._run_id = run_id

    def create(self, **_: Any) -> DraftPlanningStepResult:
        assert _step_status(self._repository, self._run_id, "materialPlan") == DraftRunStepStatus.RUNNING
        return DraftPlanningStepResult(
            artifact_payload={"source": "test", "aiRunId": "ai-material", "fallbackUsed": False, "materialPlan": {}},
            ai_run_id="ai-material",
        )


class AssertingStrategyService:
    def __init__(self, repository: SqliteDraftRunRepository, run_id: str) -> None:
        self._repository = repository
        self._run_id = run_id

    def create(self, **_: Any) -> DraftPlanningStepResult:
        run = self._repository.get(self._run_id)
        assert run and run.ai_run_ids == ["ai-material"]
        assert _step_status(self._repository, self._run_id, "strategy") == DraftRunStepStatus.RUNNING
        return DraftPlanningStepResult(
            artifact_payload={"source": "test", "aiRunId": "ai-strategy", "fallbackUsed": False, "draftStrategy": {}},
            ai_run_id="ai-strategy",
        )


class AssertingRhetoricalPlanService:
    def __init__(self, repository: SqliteDraftRunRepository, run_id: str) -> None:
        self._repository = repository
        self._run_id = run_id

    def create(self, **_: Any) -> DraftPlanningStepResult:
        run = self._repository.get(self._run_id)
        assert run and run.ai_run_ids == ["ai-material", "ai-strategy"]
        assert _step_status(self._repository, self._run_id, "rhetoricalPlans") == DraftRunStepStatus.RUNNING
        return DraftPlanningStepResult(
            artifact_payload={"source": "test", "aiRunId": "ai-plans", "fallbackUsed": False, "rhetoricalPlanSet": {"plans": []}},
            ai_run_id="ai-plans",
        )


class AssertingDraftService:
    def __init__(self, repository: SqliteDraftRunRepository, run_id: str) -> None:
        self._repository = repository
        self._run_id = run_id

    def create(self, *, request: DraftGenerationRequest, **_: Any) -> DraftCandidateGenerationResult:
        run = self._repository.get(self._run_id)
        assert run and run.ai_run_ids == ["ai-material", "ai-strategy", "ai-plans"]
        assert _step_status(self._repository, self._run_id, "draft") == DraftRunStepStatus.RUNNING
        return DraftCandidateGenerationResult(
            artifact_payload={"source": "test", "aiRunIds": ["ai-draft"], "candidates": []},
            final_draft=GeneratedDraft(
                id="draft-test",
                brief_id=request.brief.id,
                title="Generated title",
                body="Generated body",
                version=1,
                status="draft",
                updated_at="2026-06-23T00:00:00+00:00",
            ),
            ai_run_ids=["ai-draft"],
        )


def _step_status(repository: SqliteDraftRunRepository, run_id: str, key: str) -> DraftRunStepStatus | None:
    run = repository.get(run_id)
    step = next((item for item in run.steps if item.key.value == key), None) if run else None
    return step.status if step else None
