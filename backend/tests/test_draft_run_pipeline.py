from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_generation import (
    DraftBriefContext,
    DraftEditorialModelContext,
    DraftGenerationRequest,
)
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository


def make_request() -> DraftGenerationRequest:
    return DraftGenerationRequest(
        brief=DraftBriefContext(
            id="brief-demo",
            title="AI-B2B demo еще не продукт",
            rubric="AI product discovery",
            audience="AI PM",
            thesis="Demo magic не равно adoption.",
            conflict="Demo красиво, rollout слабый.",
            author_position="Сначала workflow, потом модель.",
            evidence=["usage после пилота не растет"],
            examples=["нет evals"],
            structure=["конфликт", "позиция"],
            cta="Проверьте продуктовую петлю.",
            risks=["не звучать против прототипов"],
            sources=["author note"],
        ),
        editorial_model=DraftEditorialModelContext(
            audience="AI Product Manager",
            style_rules=["исследовательский тон"],
            forbidden_topics=["generic AI hype"],
            goals=["объяснить adoption gap"],
        ),
    )


def test_draft_run_pipeline_executes_all_steps_and_writes_final_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft["briefId"] == "brief-demo"
    assert result.final_draft["body"]
    assert [step.status.value for step in result.steps] == ["succeeded"] * 7
    assert result.steps[0].artifact_payload["briefTitle"] == request.brief.title
