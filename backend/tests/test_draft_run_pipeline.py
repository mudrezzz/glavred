from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_generation import (
    DraftBriefContext,
    DraftEditorialModelContext,
    DraftGenerationRequest,
)
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context


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
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft["briefId"] == "brief-demo"
    assert result.final_draft["body"]
    assert [step.status.value for step in result.steps] == ["succeeded"] * 12
    assert result.steps[0].artifact_payload["brief"]["title"] == request.brief.title
    assert result.steps[0].artifact_payload["workItem"]["id"] == "work-item-1"
    assert result.steps[1].key.value == "sourceIntent"
    assert result.steps[1].artifact_payload["sourceIntent"]["items"][0]["instruction"] == "author note"
    assert result.steps[2].key.value == "publicEvidence"
    assert result.steps[2].artifact_payload["attempts"][0]["status"] == "notConfigured"
    assert result.steps[5].artifact_payload["metadata"]["version"] == "rule-pack-v1"
    assert result.steps[5].artifact_payload["draftIntent"]["title"] == request.brief.title

def test_draft_run_pipeline_writes_context_summary(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    context_step = result.steps[0].artifact_payload
    assert context_step["workItem"]["id"] == "work-item-1"
    assert context_step["planSlot"]["expectedEffect"] == "Clarify adoption gap"
    assert context_step["candidate"]["title"] == "AI-B2B demo"
    assert context_step["sourceSignal"]["rawNote"] == "Demo magic does not become workflow."
    assert context_step["topic"]["authorStance"] == "Workflow before model"
    assert context_step["fabula"]["dramaturgy"] == "Observation to principle"
    assert context_step["publisherRules"]["total"] == 1
    assert context_step["authorPositionEvidence"]["total"] == 1
    assert context_step["missingContext"][0]["entity"] == "topic"

    source_intent_step = result.steps[1].artifact_payload
    assert source_intent_step["researchPlan"]["verificationTasks"]

    public_evidence_step = result.steps[2].artifact_payload
    assert public_evidence_step["metadata"]["searchProvider"] == "notConfigured"

    rule_pack_step = result.steps[5].artifact_payload
    assert rule_pack_step["draftIntent"]["thesis"] == request.brief.thesis
    assert rule_pack_step["metadata"]["briefOnly"] is False
    assert rule_pack_step["topicFitRequirements"]
    assert rule_pack_step["dramaturgyRequirements"]
