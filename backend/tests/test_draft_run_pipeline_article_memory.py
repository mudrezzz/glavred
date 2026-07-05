from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_draft_run_pipeline_writes_article_dossier_and_context_packs(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)
    public_evidence = result.steps[2].artifact_payload
    rule_pack = result.steps[5].artifact_payload
    validation = result.steps[10].artifact_payload

    assert public_evidence["articleDossier"]["version"] == "article-dossier-v1"
    assert public_evidence["contextPacks"]["writer"]["version"] == "context-pack-v1"
    assert "evidenceInterpretation" in rule_pack
    assert rule_pack["contextPacks"]["strategy"]["metadata"]["itemCount"] >= 1
    assert any(card["source"] == "evidenceInterpretation" for card in rule_pack["articleDossier"]["cards"])
    assert validation["articleDossier"]["metadata"]["cardCount"] >= public_evidence["articleDossier"]["metadata"]["cardCount"]
