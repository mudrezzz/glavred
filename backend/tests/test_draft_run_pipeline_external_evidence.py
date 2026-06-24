from typing import Any

from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_public_evidence_step_service import PublicEvidenceStepService
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_public_evidence import (
    PublicEvidenceAllowedUse,
    PublicEvidenceAttempt,
    PublicEvidenceAttemptStatus,
    PublicEvidenceBatch,
    PublicEvidenceItem,
)
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


class FakePublicEvidenceService:
    def retrieve(self, *, source_intent_artifact: dict[str, Any], context_artifact: dict[str, Any] | None = None) -> PublicEvidenceBatch:
        return PublicEvidenceBatch(
            source="fake-public-evidence",
            attempts=[PublicEvidenceAttempt(
                id="search-1",
                task_id="task-1",
                source_intent_item_id="source-intent-1",
                kind="search",
                target="workflow adoption",
                status=PublicEvidenceAttemptStatus.SUCCEEDED,
            )],
            items=[PublicEvidenceItem(
                id="public-evidence-1",
                attempt_id="search-1",
                source_url="https://example.com/report",
                source_title="Independent report",
                snippet="AI demos fail without workflow adoption.",
                text_summary="AI demos fail without workflow adoption and trust loops.",
                provenance="openrouterWebSearch",
                confidence="medium",
                allowed_use=PublicEvidenceAllowedUse.NEEDS_QUALIFICATION,
            )],
        )


def test_pipeline_merges_public_evidence_before_feasibility_contract_and_rules(tmp_path) -> None:
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
        public_evidence_step_service=PublicEvidenceStepService(public_evidence_service=FakePublicEvidenceService()),
    ).execute(run.id)

    public_evidence_step = result.steps[2].artifact_payload
    enriched_ledger = public_evidence_step["enrichedSourceLedger"]
    claim_ids = {claim["id"] for claim in enriched_ledger["claims"]}
    contract_claim_ids = {claim["id"] for claim in result.steps[4].artifact_payload["claims"]}
    rule_registry = result.steps[5].artifact_payload["ruleRegistrySnapshot"]

    assert "external-evidence-public-evidence-1" in claim_ids
    assert "external-evidence-public-evidence-1" in contract_claim_ids
    assert public_evidence_step["evidenceSynthesis"]["metadata"]["externalClaimCount"] == 1
    assert rule_registry["metadata"]["sourceLedgerClaimCount"] == enriched_ledger["metadata"]["claimCount"]
    assert any(
        "external-evidence-public-evidence-1" in rule.get("claimIds", [])
        for rule in rule_registry["rules"]
    )
