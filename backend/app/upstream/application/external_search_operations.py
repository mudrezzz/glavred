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
from backend.app.upstream.application.external_payloads import operation, raw_result, safe_error


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

    def search(self, *, run_id: str, query: dict[str, Any], started_at: str) -> dict[str, Any]:
        operation_id = f"{run_id}-search-{query['id']}"
        if not self._settings.openrouter_web_tools_enabled:
            return self._search_skip(operation_id, run_id, query, started_at, "openrouter-web-tools-disabled")
        if not self._openrouter_validator.evaluate(self._settings).configured:
            return self._search_skip(operation_id, run_id, query, started_at, "openrouter-not-configured")
        try:
            result = self._web_search_adapter.search(
                settings=self._settings,
                query=query["query"],
                messages=self._search_messages(query["query"]),
                max_results=int(self._settings.openrouter_web_search_max_results or 5),
            )
            payload = self._search_success(operation_id, run_id, query, started_at)
            payload["_rawResults"] = [raw_result(run_id, query, citation, index) for index, citation in enumerate(result.citations)]
            return payload
        except Exception as exc:
            return {**self._search_fail(operation_id, run_id, query, started_at, safe_error(exc)), "_rawResults": []}

    def _search_messages(self, query: str) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Use web search to find public source material. Return citations. Do not invent sources.",
            },
            {"role": "user", "content": query},
        ]

    def _search_success(self, operation_id: str, run_id: str, query: dict[str, Any], started_at: str) -> dict[str, Any]:
        return operation(
            operation_id=operation_id,
            run_id=run_id,
            source_handle_id=query["sourceHandleId"],
            kind="openWebQuery",
            label=query["label"],
            status="succeeded",
            started_at=started_at,
            target=query["query"],
        )

    def _search_skip(self, operation_id: str, run_id: str, query: dict[str, Any], started_at: str, reason: str) -> dict[str, Any]:
        return {
            **operation(
                operation_id=operation_id,
                run_id=run_id,
                source_handle_id=query["sourceHandleId"],
                kind="openWebQuery",
                label=query["label"],
                status="skipped",
                started_at=started_at,
                target=query["query"],
                skipped_reason=reason,
            ),
            "_rawResults": [],
        }

    def _search_fail(self, operation_id: str, run_id: str, query: dict[str, Any], started_at: str, error: str) -> dict[str, Any]:
        return operation(
            operation_id=operation_id,
            run_id=run_id,
            source_handle_id=query["sourceHandleId"],
            kind="openWebQuery",
            label=query["label"],
            status="failed",
            started_at=started_at,
            target=query["query"],
            error=error,
        )
