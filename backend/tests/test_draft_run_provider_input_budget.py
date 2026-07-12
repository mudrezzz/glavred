from datetime import UTC, datetime
from typing import Any

from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider, AiRunStatus
from backend.app.drafting.application.operations.provider_input_audit import ProviderInputAudit
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate


def test_provider_input_budget_gate_records_direct_current_call_proof() -> None:
    proof = ProviderInputBudgetGate().evaluate(
        operation_id="materialPlan",
        draft_run_step="materialPlan",
        provider_input={
            "context_artifact": {"contextSummary": {"brief": {"title": "Draft"}}},
            "rule_pack": {"ruleRegistrySnapshot": {"rules": [{"id": "source-required", "severity": "critical"}]}},
        },
        execution_mode="standard",
        model="openai/test",
        model_role="strategy",
    )

    payload = proof.request_payload_fields()

    assert payload["operationId"] == "materialPlan"
    assert payload["providerInput"]["rule_pack"]["ruleRegistrySnapshot"]["metadata"]["payloadBudgeted"] is True
    assert payload["payloadBudget"]["profileId"] == "materialPlan"
    assert payload["payloadBudget"]["executionMode"] == "standard"
    assert payload["payloadBudget"]["promptCharEstimate"] > 0
    assert payload["payloadBudget"]["approxTokenEstimate"] > 0
    assert payload["inputStats"]["modelRole"] == "strategy"
    assert payload["payloadStats"]["payloadBudget"]["profileId"] == "materialPlan"


def test_provider_input_budget_gate_supports_strategy_trace_alias() -> None:
    proof = ProviderInputBudgetGate().evaluate(
        operation_id="strategy",
        profile_operation_id="draftStrategy",
        draft_run_step="strategy",
        provider_input={
            "context_artifact": {"contextSummary": {"brief": {"title": "Draft"}}},
            "rule_pack": {"ruleRegistrySnapshot": {"rules": []}},
            "material_plan": {"availableEvidence": ["claim-1"]},
        },
        execution_mode="standard",
        model="openai/test",
        model_role="strategy",
    )

    payload = proof.request_payload_fields()

    assert payload["operationId"] == "strategy"
    assert payload["payloadBudget"]["profileId"] == "draftStrategy"
    assert payload["payloadBudget"]["operationAlias"] == "strategy"


def test_provider_input_audit_accepts_direct_budgeted_ai_run() -> None:
    report = ProviderInputAudit(target_operations=("materialPlan",)).audit_ai_runs(
        [
            ai_run(
                "ai-1",
                {
                    "draftRunStep": "materialPlan",
                    "operationId": "materialPlan",
                    "providerInput": {"rule_pack": {}},
                    "payloadBudget": {
                        "profileId": "materialPlan",
                        "promptCharEstimate": 1200,
                        "approxTokenEstimate": 300,
                        "limits": {"maxPromptChars": 18000},
                    },
                },
            )
        ]
    )

    payload = report.to_payload()
    assert payload["summary"]["clean"] is True
    assert payload["findings"][0]["status"] == "directlyBudgeted"


def test_provider_input_audit_rejects_nested_prior_budget_as_false_positive() -> None:
    report = ProviderInputAudit(target_operations=("materialPlan",)).audit_ai_runs(
        [
            ai_run(
                "ai-1",
                {
                    "draftRunStep": "materialPlan",
                    "operationId": "materialPlan",
                    "capabilityInput": {"priorArtifact": {"payloadBudget": {"profileId": "materialPlan"}}},
                },
            )
        ]
    )

    payload = report.to_payload()
    assert payload["summary"]["clean"] is False
    assert payload["findings"][0]["status"] == "nestedBudgetFalsePositive"


def test_provider_input_audit_reports_oversized_current_input() -> None:
    report = ProviderInputAudit(target_operations=("materialPlan",)).audit_ai_runs(
        [
            ai_run(
                "ai-1",
                {
                    "draftRunStep": "materialPlan",
                    "operationId": "materialPlan",
                    "providerInput": {},
                    "payloadBudget": {
                        "profileId": "materialPlan",
                        "promptCharEstimate": 25000,
                        "approxTokenEstimate": 6250,
                        "limits": {"maxPromptChars": 18000},
                    },
                },
            )
        ]
    )

    payload = report.to_payload()
    assert payload["summary"]["clean"] is False
    assert payload["findings"][0]["status"] == "overBudget"


def test_provider_input_audit_has_no_remaining_review_ranking_debt() -> None:
    report = ProviderInputAudit(target_operations=("pairwiseRanking", "directedRevision")).audit_ai_runs([])

    payload = report.to_payload()
    assert payload["summary"]["clean"] is True
    assert payload["findings"] == []


def ai_run(run_id: str, request_payload: dict[str, Any]) -> AiRun:
    now = datetime.now(UTC)
    return AiRun(
        id=run_id,
        capability=AiRunCapability.DRAFT_GENERATION,
        status=AiRunStatus.SUCCEEDED,
        provider=AiRunProvider.OPENROUTER,
        model="openai/test",
        request_payload=request_payload,
        result_payload={"ok": True},
        error=None,
        fallback_used=False,
        created_at=now,
        updated_at=now,
    )
