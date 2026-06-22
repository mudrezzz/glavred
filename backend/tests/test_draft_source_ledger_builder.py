from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_from_payload
from backend.app.application.draft_source_ledger_builder import SourceLedgerBuilder
from backend.tests.test_draft_run_context_builder import make_context, make_payload


def test_source_ledger_builds_claims_from_full_context() -> None:
    payload = make_payload()
    payload["draftContext"] = make_context()

    ledger = build_ledger_payload(payload)
    claim_ids = {claim["id"] for claim in ledger["claims"]}

    assert "brief-thesis" in claim_ids
    assert "candidate-evidence-summary" in claim_ids
    assert "signal-summary" in claim_ids
    assert "signal-author-correction" in claim_ids
    assert "fabula-proof-1" in claim_ids
    assert "assertion-1" in claim_ids
    assert ledger["metadata"]["version"] == "source-ledger-v1"
    assert ledger["metadata"]["briefOnly"] is False


def test_source_ledger_keeps_author_correction_as_framing() -> None:
    payload = make_payload()
    payload["draftContext"] = make_context()

    ledger = build_ledger_payload(payload)
    correction = find_by_id(ledger["claims"], "signal-author-correction")

    assert correction["allowedUse"] == "canUseAsFraming"
    assert correction["source"] == "sourceSignal.authorCorrection"
    assert "author-correction-not-external-proof" in correction["riskFlags"]


def test_source_ledger_records_candidate_risks_and_forbidden_inferences() -> None:
    payload = make_payload()
    payload["draftContext"] = make_context()

    ledger = build_ledger_payload(payload)

    assert find_by_id(ledger["risks"], "candidate-risk-1")["detail"] == "Do not sound anti-demo"
    assert find_by_id(ledger["forbiddenInferences"], "risks-are-not-facts")
    assert find_by_id(ledger["forbiddenInferences"], "position-is-not-market-fact")


def test_source_ledger_reports_missing_context_as_warnings() -> None:
    payload = make_payload()
    context = make_context()
    context.pop("sourceSignal")
    context.pop("candidate")
    context["authorPositionEvidence"] = []
    payload["draftContext"] = context

    ledger = build_ledger_payload(payload)
    warning_ids = {warning["id"] for warning in ledger["warnings"]}

    assert "missing-source-signal" in warning_ids
    assert "missing-candidate" in warning_ids
    assert "missing-author-position-evidence" in warning_ids
    assert "missing-context-1" in warning_ids


def test_source_ledger_keeps_brief_only_request_compatible() -> None:
    ledger = build_ledger_payload(make_payload())
    claim_ids = {claim["id"] for claim in ledger["claims"]}
    warning_ids = {warning["id"] for warning in ledger["warnings"]}

    assert "brief-thesis" in claim_ids
    assert "brief-evidence-1" in claim_ids
    assert "brief-source-1" in claim_ids
    assert ledger["metadata"]["briefOnly"] is True
    assert "missing-source-signal" in warning_ids
    assert "missing-candidate" in warning_ids


def test_source_ledger_warns_when_brief_thesis_has_no_evidence() -> None:
    payload = make_payload()
    payload["brief"]["evidence"] = []

    ledger = build_ledger_payload(payload)

    assert find_by_id(ledger["warnings"], "brief-thesis-no-evidence")


def build_ledger_payload(payload: dict) -> dict:
    request = request_from_payload(payload)
    summary = build_draft_run_context_summary(request=request, context=context_from_payload(payload))
    return SourceLedgerBuilder().build(summary, request).to_payload()


def find_by_id(items: list[dict], item_id: str) -> dict:
    return next(item for item in items if item["id"] == item_id)
