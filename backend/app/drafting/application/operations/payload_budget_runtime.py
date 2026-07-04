"""Owner: drafting.application.operations

Used by: legacy DraftRun provider-heavy services while payload budgeting migrates inward.
Does not own: prompt wording, provider calls, model selection, persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.drafting.application.operations.payload_budget import DraftRunPayloadBudgetPolicy


@dataclass(frozen=True)
class BudgetedProviderInput:
    payload: dict[str, Any]
    input_stats: dict[str, Any]
    payload_stats: dict[str, Any]

    @property
    def payload_budget(self) -> dict[str, Any]:
        return dict(self.payload_stats.get("payloadBudget") or {})


class DraftRunPayloadBudgetRuntime:
    def __init__(self, policy: DraftRunPayloadBudgetPolicy | None = None) -> None:
        self._policy = policy or DraftRunPayloadBudgetPolicy()

    def compact(
        self,
        operation_id: str,
        payload: Mapping[str, Any],
        *,
        execution_mode: str | None,
        model: str | None,
        model_role: str,
        generation_params: Mapping[str, Any] | None = None,
    ) -> BudgetedProviderInput:
        result = self._policy.compact(
            operation_id,
            payload,
            execution_mode=execution_mode,
            model=model,
            model_role=model_role,
            generation_params=generation_params,
        )
        return BudgetedProviderInput(
            payload=result.compact_payload,
            input_stats=result.input_stats,
            payload_stats=result.payload_stats,
        )


def last_input_stats(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return next((dict(item.get("inputStats")) for item in reversed(attempts) if isinstance(item.get("inputStats"), dict)), {})


def last_payload_stats(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return next((dict(item.get("payloadStats")) for item in reversed(attempts) if isinstance(item.get("payloadStats"), dict)), {})
