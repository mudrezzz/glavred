from __future__ import annotations

import json
from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import (
    OpenRouterWebSearchCitation,
    OpenRouterWebSearchResult,
)
from backend.app.settings import BackendSettings
from backend.app.shared.llm_operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.upstream.application.external_payloads import budget_for_mode
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService
from backend.app.upstream.application.external_search_operations import OpenWebQueryOperationRunner
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.provider_input_budget_gate import UpstreamProviderInputBudgetGate


def test_upstream_direct_budget_proof_is_current_call_metadata() -> None:
    profile = UpstreamProviderBudgetProfileRegistry().resolve(
        operation_id="openWebQuery",
        execution_mode="standard",
        configured_max_results=12,
    )
    result = UpstreamProviderInputBudgetGate().evaluate(
        provider_input={"operationId": "openWebQuery", "queryId": "query-1", "query": "industrial AI"},
        query_text="industrial AI",
        profile=profile,
        run_budget=budget_for_mode("standard"),
    )

    assert result.blocked_reason is None
    assert result.request_fields["providerInput"]["queryId"] == "query-1"
    assert result.request_fields["payloadBudget"]["status"] == "directlyBudgeted"
    assert result.request_fields["payloadBudget"]["profileId"] == "upstream-open-web-query-v1-standard"
    assert profile.max_results_per_query == 5


def test_upstream_run_total_budget_blocks_before_provider_call() -> None:
    profile = UpstreamProviderBudgetProfileRegistry().resolve(
        operation_id="openWebQuery",
        execution_mode="smoke",
        configured_max_results=5,
    )
    result = UpstreamProviderInputBudgetGate().evaluate(
        provider_input={"operationId": "openWebQuery", "query": "industrial AI"},
        query_text="industrial AI",
        profile=profile,
        run_budget={"usedProviderInputChars": 3999, "usedProviderInputTokens": 999},
    )

    assert result.blocked_reason == "provider-input-over-budget"
    assert "radar-run-input-char-limit" in result.request_fields["payloadBudget"]["budgetIncidents"]
    assert result.request_fields["payloadBudget"]["incident"]["incidentType"] == "payloadTooLarge"


def test_serialized_message_guard_boundaries_3999_4000_4001() -> None:
    guard = ProviderMessageBudgetGuard()

    for target, blocked in ((3999, False), (4000, False), (4001, True)):
        messages = messages_with_serialized_size(target)
        result = guard.evaluate(
            messages=messages,
            request_fields={
                "payloadBudget": {
                    "providerInputCharEstimate": 100,
                    "limits": {"maxMessageChars": 4000},
                }
            },
        )
        assert result.request_fields["messageCharCount"] == target
        assert bool(result.blocked_reason) is blocked


def test_query_over_cap_skips_provider_with_structured_budget_incident() -> None:
    adapter = CapturingSearchAdapter(citation_count=1)
    runner = OpenWebQueryOperationRunner(
        settings=settings("smoke"),
        web_search_adapter=adapter,
        openrouter_validator=OpenRouterConfigValidator(),
    )
    oversized_query = query_payload("x" * 1001)

    operation = runner.search(
        run_id="radar-run-1",
        query=oversized_query,
        started_at="2026-07-13T00:00:00+00:00",
        run_budget=budget_for_mode("smoke"),
    )

    assert operation["status"] == "skipped"
    assert operation["skippedReason"] == "provider-input-over-budget"
    assert operation["payloadBudget"]["status"] == "blocked"
    assert operation["payloadBudget"]["incident"]["incidentType"] == "payloadTooLarge"
    assert adapter.calls == []


def test_open_web_query_trace_has_direct_and_final_message_budget_proof() -> None:
    adapter = CapturingSearchAdapter(citation_count=2)
    runner = OpenWebQueryOperationRunner(
        settings=settings("standard"),
        web_search_adapter=adapter,
        openrouter_validator=OpenRouterConfigValidator(),
    )
    run_budget = budget_for_mode("standard")

    operation = runner.search(
        run_id="radar-run-1",
        query=query_payload("industrial AI maintenance case"),
        started_at="2026-07-13T00:00:00+00:00",
        run_budget=run_budget,
    )

    assert operation["status"] == "succeeded"
    assert operation["providerInput"]["operationId"] == "openWebQuery"
    assert operation["payloadBudget"]["status"] == "directlyBudgeted"
    assert operation["messageCharCount"] <= 4000
    assert operation["providerUsage"] == {"prompt_tokens": 111, "completion_tokens": 22}
    assert operation["selectedModel"] == "test-model"
    assert run_budget["usedProviderInputChars"] > 0
    assert run_budget["usedProviderInputTokens"] > 0
    assert adapter.calls[0]["max_results"] == 5


def test_provider_returning_more_citations_keeps_complete_bounded_triage_trace() -> None:
    adapter = CapturingSearchAdapter(citation_count=10)
    service = UpstreamRadarExternalRunService(
        settings=settings("smoke"),
        web_search_adapter=adapter,
        url_reader=Reader(),
        openrouter_validator=OpenRouterConfigValidator(),
    )

    result = service.run(workspace=workspace(), radar_id="radar-1")
    run = result["run"]

    assert adapter.calls[0]["max_results"] == 3
    assert len(run["rawResults"]) == 10
    assert run["searchTriage"]["decisionCounts"]["total"] == 10
    assert run["searchTriage"]["decisionCounts"]["selected"] == 1
    assert len(run["selectedForRead"]) == 1


def messages_with_serialized_size(target: int) -> list[dict[str, str]]:
    empty = [{"role": "user", "content": ""}]
    overhead = len(json.dumps(empty, ensure_ascii=False, sort_keys=True))
    assert target >= overhead
    messages = [{"role": "user", "content": "x" * (target - overhead)}]
    assert len(json.dumps(messages, ensure_ascii=False, sort_keys=True)) == target
    return messages


def settings(mode: str) -> BackendSettings:
    return BackendSettings(
        OPENROUTER_API_KEY="test-token",
        OPENROUTER_DEFAULT_MODEL="test-model",
        OPENROUTER_WEB_TOOLS_ENABLED=True,
        OPENROUTER_WEB_SEARCH_MODEL="test-model",
        OPENROUTER_WEB_SEARCH_MAX_RESULTS=12,
        DRAFT_RUN_EXECUTION_MODE=mode,
    )


def query_payload(text: str) -> dict[str, Any]:
    return {
        "id": "query-1",
        "intentId": "intent-case",
        "sourceHandleId": "source-open-web",
        "family": "caseExample",
        "evidenceType": "caseExample",
        "priority": 1,
        "query": text,
        "label": "case search",
    }


class CapturingSearchAdapter:
    def __init__(self, *, citation_count: int) -> None:
        self._citation_count = citation_count
        self.calls: list[dict[str, Any]] = []

    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        self.calls.append(kwargs)
        return OpenRouterWebSearchResult(
            content="search",
            citations=[
                OpenRouterWebSearchCitation(
                    title=f"Industrial maintenance case {index}",
                    url=f"https://source-{index}.example/case",
                    snippet="Implementation data metrics constraints and reliability results.",
                )
                for index in range(self._citation_count)
            ],
            raw_response={
                "id": "search-1",
                "model": "test-model",
                "usage": {"prompt_tokens": 111, "completion_tokens": 22},
            },
        )


class Reader:
    def read(self, url: str) -> PublicUrlReadResult:
        return PublicUrlReadResult(url=url, final_url=url, title="Read", text="Detailed implementation evidence.")


def workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en", "name": "Industrial AI"},
        "sourceRegistry": {
            "handles": [
                {
                    "id": "source-open-web",
                    "type": "openWebQuery",
                    "title": "Industrial AI web",
                    "locator": "industrial AI maintenance",
                    "status": "active",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                }
            ]
        },
        "radars": [
            {
                "id": "radar-1",
                "title": "Industrial AI radar",
                "scope": "Find industrial AI implementation patterns",
                "sourceHandleIds": ["source-open-web"],
                "rules": [{"statement": "Operational proof"}],
            }
        ],
        "radarRuns": [],
    }
