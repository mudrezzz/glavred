from backend.app.application.deterministic_external_evidence_synthesis import (
    DeterministicExternalEvidenceSynthesisService,
)
from backend.app.application.source_ledger_external_evidence_merger import (
    SourceLedgerExternalEvidenceMerger,
)


def test_deterministic_synthesis_creates_claim_from_public_evidence_item() -> None:
    synthesis = DeterministicExternalEvidenceSynthesisService().synthesize(public_evidence()).to_payload()

    assert synthesis["externalClaims"][0]["publicEvidenceItemId"] == "public-evidence-1"
    assert synthesis["externalClaims"][0]["allowedUse"] == "needsQualification"
    assert synthesis["metadata"]["externalClaimCount"] == 1


def test_merger_adds_external_claims_and_warnings_to_source_ledger() -> None:
    synthesis = DeterministicExternalEvidenceSynthesisService().synthesize(public_evidence()).to_payload()

    merged = SourceLedgerExternalEvidenceMerger().merge(
        source_ledger={"claims": [{"id": "brief-thesis", "type": "briefIntent"}], "warnings": [], "metadata": {}},
        public_evidence=public_evidence(),
        evidence_synthesis=synthesis,
    )

    external_claim = next(claim for claim in merged["claims"] if claim["type"] == "externalEvidenceClaim")
    assert external_claim["id"] == "external-evidence-public-evidence-1"
    assert external_claim["provenance"]["sourceUrl"] == "https://example.com/report"
    assert merged["metadata"]["externalClaimCount"] == 1
    assert merged["metadata"]["internalClaimCount"] == 1
    assert any(warning["source"] == "publicEvidence" for warning in merged["warnings"])


def test_merger_records_no_external_claim_warning_when_no_items() -> None:
    synthesis = DeterministicExternalEvidenceSynthesisService().synthesize({"items": [], "attempts": []}).to_payload()

    merged = SourceLedgerExternalEvidenceMerger().merge(
        source_ledger={"claims": [], "warnings": [], "metadata": {}},
        public_evidence={"items": [], "attempts": []},
        evidence_synthesis=synthesis,
    )

    assert merged["claims"] == []
    assert merged["metadata"]["externalClaimCount"] == 0
    assert any(warning["id"] == "external-evidence-none-merged" for warning in merged["warnings"])


def public_evidence() -> dict:
    return {
        "items": [{
            "id": "public-evidence-1",
            "attemptId": "search-1",
            "sourceUrl": "https://example.com/report",
            "sourceTitle": "Independent report",
            "snippet": "AI demos often fail when workflow adoption is missing.",
            "textSummary": "AI demos often fail when workflow adoption and trust loops are missing.",
            "confidence": "medium",
            "allowedUse": "needsQualification",
        }],
        "attempts": [{
            "id": "search-1",
            "kind": "search",
            "status": "succeeded",
            "target": "workflow adoption",
        }, {
            "id": "search-2",
            "kind": "search",
            "status": "failed",
            "target": "evals",
        }],
        "warnings": [{"code": "openrouter-search-failed", "message": "one search failed"}],
    }
