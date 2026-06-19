from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_pipeline import make_request


def test_draft_run_pipeline_writes_planning_steps_and_ai_run_ids(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(request_payload=request_to_payload(request), input_summary={"title": request.brief.title})
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        material_plan_service=StaticMaterialPlanService(),
        strategy_service=StaticStrategyService(),
    ).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.ai_run_ids == ["ai-material", "ai-strategy"]
    assert result.steps[2].artifact_payload["materialPlan"]["availableEvidence"] == ["evidence"]
    assert result.steps[3].artifact_payload["draftStrategy"]["thesisAngle"] == "angle"


class StaticMaterialPlanService:
    def create(self, **kwargs) -> DraftPlanningStepResult:
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "openrouter",
                "aiRunId": "ai-material",
                "fallbackUsed": False,
                "materialPlan": {"availableEvidence": ["evidence"]},
            },
            ai_run_id="ai-material",
        )


class StaticStrategyService:
    def create(self, **kwargs) -> DraftPlanningStepResult:
        assert kwargs["material_plan"]["availableEvidence"] == ["evidence"]
        return DraftPlanningStepResult(
            artifact_payload={
                "source": "openrouter",
                "aiRunId": "ai-strategy",
                "fallbackUsed": False,
                "draftStrategy": {"thesisAngle": "angle"},
            },
            ai_run_id="ai-strategy",
        )
