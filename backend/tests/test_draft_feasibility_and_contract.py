from backend.app.drafting.application.evidence.draft_feasibility_gate import FeasibilityGate
from backend.app.drafting.application.evidence.draft_post_contract_builder import PostContractBuilder
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_from_payload
from backend.app.drafting.application.artifacts.draft_source_ledger_builder import SourceLedgerBuilder
from backend.app.domain.draft_feasibility import FeasibilityStatus
from backend.tests.test_draft_run_context_builder import make_context, make_payload


def test_full_context_is_feasible_with_constraints_and_creates_contract() -> None:
    context_artifact = build_context_artifact(make_payload() | {"draftContext": make_context()})

    report = FeasibilityGate().evaluate(context_artifact)
    contract = PostContractBuilder().build(context_artifact, report).to_payload()

    assert report.status == FeasibilityStatus.FEASIBLE_WITH_CONSTRAINTS
    assert report.blocked is False
    assert "signal-summary" in report.allowed_claim_ids
    assert contract["status"] == "created"
    assert contract["title"] == "AI-B2B demo"
    assert contract["platform"] == "Telegram"
    assert contract["claims"]
    assert contract["forbiddenMoves"]


def test_missing_source_or_candidate_requires_human_decision() -> None:
    payload = make_payload()
    context = make_context()
    context.pop("sourceSignal")
    context.pop("candidate")
    payload["draftContext"] = context
    context_artifact = build_context_artifact(payload)

    report = FeasibilityGate().evaluate(context_artifact)
    contract = PostContractBuilder().not_created(report)

    assert report.status == FeasibilityStatus.NEEDS_HUMAN_DECISION
    assert report.blocked is True
    assert contract["status"] == "notCreated"
    assert contract["blockedBy"] == "feasibility"


def test_missing_candidate_can_proceed_when_source_and_brief_evidence_are_available() -> None:
    payload = make_payload()
    context = make_context()
    context.pop("candidate")
    payload["draftContext"] = context
    context_artifact = build_context_artifact(payload)

    report = FeasibilityGate().evaluate(context_artifact)
    contract = PostContractBuilder().build(context_artifact, report).to_payload()

    assert report.status == FeasibilityStatus.FEASIBLE_WITH_CONSTRAINTS
    assert report.blocked is False
    assert any(finding.id == "candidate-link-recovered-from-source" for finding in report.findings)
    assert contract["status"] == "created"


def test_missing_candidate_without_evidence_requires_human_decision() -> None:
    payload = make_payload()
    payload["brief"]["evidence"] = []
    context = make_context()
    context.pop("candidate")
    context["sourceSignal"]["evidence"] = []
    payload["draftContext"] = context
    context_artifact = build_context_artifact(payload)

    report = FeasibilityGate().evaluate(context_artifact)

    assert report.status == FeasibilityStatus.NEEDS_HUMAN_DECISION
    assert report.blocked is True


def test_missing_brief_intent_is_infeasible() -> None:
    payload = make_payload()
    payload["brief"]["title"] = ""
    payload["brief"]["thesis"] = ""
    context_artifact = build_context_artifact(payload)

    report = FeasibilityGate().evaluate(context_artifact)

    assert report.status == FeasibilityStatus.INFEASIBLE
    assert report.blocked is True


def build_context_artifact(payload: dict) -> dict:
    request = request_from_payload(payload)
    summary = build_draft_run_context_summary(request=request, context=context_from_payload(payload))
    return {**summary, "sourceLedger": SourceLedgerBuilder().build(summary, request).to_payload()}
