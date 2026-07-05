from backend.app.drafting.application.validation.draft_attribution_requirements import normalize_attribution_requirements


def test_free_text_requirement_maps_to_external_claim_by_source_marker() -> None:
    result = normalize_attribution_requirements(
        ["95% of AI pilots fail - attribute to B2BNotes"],
        [
            {
                "id": "external-evidence-b2bnotes",
                "type": "externalEvidenceClaim",
                "source": "publicEvidence",
                "provenance": {"sourceTitle": "B2BNotes AI production gap", "sourceUrl": "https://b2bnotes.com/ai-production-gap"},
            }
        ],
    )

    assert result["resolvedClaimIds"] == ["external-evidence-b2bnotes"]
    assert result["unresolvedAttributionRequirements"] == []


def test_unresolved_free_text_requirement_stays_diagnostic() -> None:
    result = normalize_attribution_requirements(
        ["95% of AI pilots fail - attribute to Unknown Source"],
        [
            {
                "id": "external-evidence-b2bnotes",
                "type": "externalEvidenceClaim",
                "source": "publicEvidence",
                "provenance": {"sourceTitle": "B2BNotes AI production gap", "sourceUrl": "https://b2bnotes.com/ai-production-gap"},
            }
        ],
    )

    assert result["resolvedClaimIds"] == []
    assert result["unresolvedAttributionRequirements"][0]["reason"] == "unresolved-free-text-requirement"
