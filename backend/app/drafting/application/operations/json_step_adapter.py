"""Owner: drafting.application.operations

Used by: migrated DraftRun provider-heavy services that need JSON completion.
Does not own: provider transport, prompt text, AI run persistence, or operation-specific fallback policy.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any, Protocol

from backend.app.settings import BackendSettings


class OpenRouterJsonStepAdapter(Protocol):
    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any: ...


class DraftingJsonOperationClient:
    def __init__(self, adapter: Any) -> None:
        self._adapter = adapter

    def complete(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any:
        complete_operation = getattr(self._adapter, "complete_operation_json", None)
        if callable(complete_operation):
            return complete_operation(
                settings=settings,
                messages=messages,
                expected_keys=expected_keys,
                temperature=temperature,
                top_p=top_p,
                model=model,
            )
        complete_legacy = getattr(self._adapter, "complete_json")
        return complete_legacy(
            settings=settings,
            messages=messages,
            expected_keys=expected_keys,
            temperature=temperature,
            top_p=top_p,
            model=model,
        )


class DraftingJsonStepAdapter:
    def __init__(self, provider_adapter: OpenRouterJsonStepAdapter) -> None:
        self._provider_adapter = provider_adapter

    def complete_operation_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any:
        return DraftingJsonOperationClient(self._provider_adapter).complete(
            settings=settings,
            messages=messages,
            expected_keys=expected_keys,
            temperature=temperature,
            top_p=top_p,
            model=model,
        )

    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any:
        return self.complete_operation_json(
            settings=settings,
            messages=messages,
            expected_keys=expected_keys,
            temperature=temperature,
            top_p=top_p,
            model=model,
        )


__all__ = ("DraftingJsonOperationClient", "DraftingJsonStepAdapter", "OpenRouterJsonStepAdapter")
