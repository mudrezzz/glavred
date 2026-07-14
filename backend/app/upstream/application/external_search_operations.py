"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService.
Does not own: API routing, SQLite persistence, signal scoring, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.settings import BackendSettings
from backend.app.shared.llm_operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.upstream.application.external_run_payloads import UpstreamRadarPayloadFactory
from backend.app.upstream.application.open_web_query_input import OpenWebQueryInputBuilder
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.provider_input_budget_gate import UpstreamProviderInputBudgetGate


class OpenWebQueryOperationRunner:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        web_search_adapter: OpenRouterWebSearchAdapter,
        openrouter_validator: OpenRouterConfigValidator,
    ) -> None:
        self._settings = settings
        self._web_search_adapter = web_search_adapter
        self._openrouter_validator = openrouter_validator
        self._profile_registry = UpstreamProviderBudgetProfileRegistry()
        self._input_budget_gate = UpstreamProviderInputBudgetGate()
        self._message_budget_guard = ProviderMessageBudgetGuard()
        self._payloads = UpstreamRadarPayloadFactory()
        self._input_builder = OpenWebQueryInputBuilder()

    def search(
        self,
        *,
        run_id: str,
        query: dict[str, Any],
        started_at: str,
        run_budget: dict[str, Any],
    ) -> dict[str, Any]:
        operation_id = f"{run_id}-search-{query['id']}"
        profile = self._profile_registry.resolve(
            operation_id="openWebQuery",
            execution_mode=self._settings.draft_run_execution_mode,
            configured_max_results=int(self._settings.openrouter_web_search_max_results or 5),
        )
        provider_input = self._input_builder.provider_input(run_id=run_id, query=query)
        input_budget = self._input_budget_gate.evaluate(
            provider_input=provider_input,
            query_text=provider_input["query"],
            profile=profile,
            run_budget=run_budget,
        )
        messages = self._input_builder.messages(provider_input)
        message_budget = self._message_budget_guard.evaluate(
            messages=messages,
            request_fields=input_budget.request_fields,
        )
        trace = {
            **message_budget.request_fields,
            "messageCharCount": message_budget.request_fields.get("messageCharCount"),
            "selectedModel": self._settings.openrouter_web_search_model,
            "maxResults": profile.max_results_per_query,
        }
        if not self._settings.openrouter_web_tools_enabled:
            return self._search_skip(
                operation_id,
                run_id,
                query,
                started_at,
                "openrouter-web-tools-disabled",
                trace=trace,
            )
        if not self._openrouter_validator.evaluate(self._settings).configured:
            return self._search_skip(
                operation_id,
                run_id,
                query,
                started_at,
                "openrouter-not-configured",
                trace=trace,
            )
        if input_budget.blocked_reason or message_budget.blocked_reason:
            return self._search_skip(
                operation_id,
                run_id,
                query,
                started_at,
                "provider-input-over-budget",
                trace=trace,
            )
        run_budget["usedProviderInputChars"] = int(run_budget.get("usedProviderInputChars") or 0) + input_budget.provider_input_chars
        run_budget["usedProviderInputTokens"] = int(run_budget.get("usedProviderInputTokens") or 0) + input_budget.approx_tokens
        try:
            result = self._web_search_adapter.search(
                settings=self._settings,
                query=provider_input["query"],
                messages=messages,
                max_results=profile.max_results_per_query,
            )
            raw_response = result.raw_response if isinstance(result.raw_response, dict) else {}
            trace.update(
                {
                    "providerUsage": raw_response.get("usage"),
                    "providerRequestId": raw_response.get("id"),
                    "selectedModel": raw_response.get("model") or trace["selectedModel"],
                    "payloadStats": {
                        **dict(trace.get("payloadStats") or {}),
                        "returnedCitationCount": len(result.citations),
                        "requestedMaxResults": profile.max_results_per_query,
                    },
                }
            )
            payload = self._search_success(operation_id, run_id, query, started_at, trace=trace)
            payload["_rawResults"] = [
                self._payloads.raw_result(run_id, query, citation, index)
                for index, citation in enumerate(result.citations)
            ]
            return payload
        except Exception as exc:
            return {
                **self._search_fail(
                    operation_id,
                    run_id,
                    query,
                    started_at,
                    self._payloads.safe_error(exc),
                    trace=trace,
                ),
                "_rawResults": [],
            }

    def _search_success(
        self,
        operation_id: str,
        run_id: str,
        query: dict[str, Any],
        started_at: str,
        *,
        trace: dict[str, Any],
    ) -> dict[str, Any]:
        return self._payloads.operation(
            operation_id=operation_id,
            run_id=run_id,
            source_handle_id=query["sourceHandleId"],
            kind="openWebQuery",
            label=query["label"],
            status="succeeded",
            started_at=started_at,
            target=query["query"],
            trace=trace,
        )

    def _search_skip(
        self,
        operation_id: str,
        run_id: str,
        query: dict[str, Any],
        started_at: str,
        reason: str,
        *,
        trace: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            **self._payloads.operation(
                operation_id=operation_id,
                run_id=run_id,
                source_handle_id=query["sourceHandleId"],
                kind="openWebQuery",
                label=query["label"],
                status="skipped",
                started_at=started_at,
                target=query["query"],
                skipped_reason=reason,
                trace=trace,
            ),
            "_rawResults": [],
        }

    def _search_fail(
        self,
        operation_id: str,
        run_id: str,
        query: dict[str, Any],
        started_at: str,
        error: str,
        *,
        trace: dict[str, Any],
    ) -> dict[str, Any]:
        return self._payloads.operation(
            operation_id=operation_id,
            run_id=run_id,
            source_handle_id=query["sourceHandleId"],
            kind="openWebQuery",
            label=query["label"],
            status="failed",
            started_at=started_at,
            target=query["query"],
            error=error,
            trace=trace,
        )
