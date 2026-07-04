from backend.app.drafting.application.operations.payload_budget import DraftRunPayloadBudgetPolicy
from backend.app.shared.llm_operations.inventory import CURRENT_LLM_OPERATION_INVENTORY


def test_payload_budget_preserves_must_have_and_records_counts() -> None:
    policy = DraftRunPayloadBudgetPolicy()
    result = policy.compact(
        "directedRevision",
        {
            "candidate": {"id": "c1", "title": "Title", "body": "Body", "debug": "ignored"},
            "instruction": {"status": "created", "goals": ["sharpen stance"]},
            "context_artifact": _large_context(claim_count=40, evidence_count=40),
            "rule_pack": _large_rule_pack(rule_count=80),
            "material_plan": {"usableEvidence": [{"id": f"e{i}", "summary": "x"} for i in range(40)]},
            "fullRevisionTrace": {"raw": "diagnostic-only"},
        },
        execution_mode="smoke",
        model="model-a",
        model_role="writer",
    )

    assert result.compact_payload["candidate"]["id"] == "c1"
    assert result.compact_payload["instruction"]["status"] == "created"
    assert "fullRevisionTrace" not in result.compact_payload
    assert result.trimmed_counts["rules"] > 0
    assert result.trimmed_counts["claims"] > 0
    assert result.payload_budget["profileId"] == "directedRevision"
    assert result.payload_budget["approxTokenEstimate"] == (result.payload_budget["promptCharEstimate"] + 3) // 4
    assert result.input_stats["modelRole"] == "writer"


def test_payload_budget_never_sends_never_send_to_provider_fields() -> None:
    result = DraftRunPayloadBudgetPolicy().compact(
        "humanCommentRevision",
        {
            "current_version": {"id": "v1", "title": "T", "body": "B"},
            "editor_comment": "Make it clearer",
            "trace_context": {"draftRunId": "run-1", "revisionLoop": {"cycles": [{"id": "a"}, {"id": "b"}, {"id": "c"}]}},
            "rawDraftRun": {"full": "artifact"},
            "fullDraftRun": {"diagnostic": "artifact"},
        },
        execution_mode="smoke",
        model="model-a",
        model_role="writer",
    )

    assert "rawDraftRun" not in result.compact_payload
    assert "fullDraftRun" not in result.compact_payload
    assert "rawDraftRun" in result.payload_budget["suppressedFields"]
    assert "fullDraftRun" in result.payload_budget["suppressedFields"]
    assert result.payload_budget["trimmedCounts"]["priorDrafts"] == 2


def test_payload_budget_records_context_over_budget_incident() -> None:
    policy = DraftRunPayloadBudgetPolicy()
    result = policy.compact(
        "editorialCritique",
        {
            "candidate": {"id": "c1", "title": "T", "body": "x" * 20000},
            "context_artifact": _large_context(claim_count=2, evidence_count=2),
            "rule_pack": _large_rule_pack(rule_count=2),
            "material_plan": {"usableEvidence": []},
        },
        execution_mode="smoke",
        model="model-a",
        model_role="critic",
    )

    assert result.incident is not None
    assert result.incident.to_payload()["incidentType"] in {"contextOverBudget", "payloadTooLarge"}
    assert result.payload_budget["qualityRisk"] == "high"


def test_every_llm_operation_has_payload_budget_status_or_debt_allowlist() -> None:
    payloads = [entry.to_payload() for entry in CURRENT_LLM_OPERATION_INVENTORY]
    assert {entry["operationId"] for entry in payloads} >= {
        "evidenceInterpretation",
        "editorialCritique",
        "directedRevision",
        "humanCommentRevision",
        "humanCommentRevisionQualityCheck",
        "alternativeAngleRoute",
        "publicEvidenceSearch",
    }
    for entry in payloads:
        assert entry["payloadBudgetStatus"] in {"enforced", "debtAllowlisted"}
        assert entry["budgetPolicyId"]
        if entry["payloadBudgetStatus"] == "debtAllowlisted":
            assert entry["reasonNotBudgeted"]
            assert entry["payloadBudgetRemovalSlice"]


def _large_context(*, claim_count: int, evidence_count: int) -> dict:
    return {
        "postContract": {"thesis": "Thesis", "allowedClaimIds": ["claim-1"]},
        "sourceLedger": {
            "claims": [
                {
                    "id": f"claim-{index}",
                    "type": "externalEvidenceClaim",
                    "statement": "statement",
                    "provenance": {"sourceTitle": "Source", "sourceUrl": "https://example.com", "snippet": "snippet"},
                }
                for index in range(claim_count)
            ]
        },
        "publicEvidence": {
            "items": [
                {"id": f"evidence-{index}", "sourceTitle": "Source", "sourceUrl": "https://example.com", "snippet": "snippet"}
                for index in range(evidence_count)
            ]
        },
        "evidenceSynthesis": {"externalClaims": [{"id": f"synth-{index}", "statement": "statement"} for index in range(claim_count)]},
    }


def _large_rule_pack(*, rule_count: int) -> dict:
    return {
        "ruleRegistrySnapshot": {
            "rules": [
                {"id": f"rule-{index}", "title": "Evidence rule", "severity": "hard", "validatorType": "evidence"}
                for index in range(rule_count)
            ]
        }
    }
