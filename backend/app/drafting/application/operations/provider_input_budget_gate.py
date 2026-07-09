"""Owner: drafting.application.operations

Used by: DraftRun provider-heavy services before constructing provider messages.
Does not own: prompt wording, provider transport, model selection, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.drafting.application.operations.payload_budget_runtime import (
    BudgetedProviderInput,
    DraftRunPayloadBudgetRuntime,
)


@dataclass(frozen=True)
class ProviderInputBudgetProof:
    operation_id: str
    draft_run_step: str
    provider_input: dict[str, Any]
    budgeted_input: BudgetedProviderInput
    profile_operation_id: str

    @property
    def payload_budget(self) -> dict[str, Any]:
        return self.budgeted_input.payload_budget

    @property
    def prompt_char_estimate(self) -> int:
        return int(self.payload_budget.get("promptCharEstimate") or 0)

    @property
    def approx_token_estimate(self) -> int:
        return int(self.payload_budget.get("approxTokenEstimate") or 0)

    def request_payload_fields(self) -> dict[str, Any]:
        payload_budget = dict(self.payload_budget)
        return {
            "operationId": self.operation_id,
            "providerInput": self.budgeted_input.payload,
            "payloadBudget": payload_budget,
            "inputStats": self.budgeted_input.input_stats,
            "payloadStats": self.budgeted_input.payload_stats,
        }


class ProviderInputBudgetGate:
    """Applies direct current-call budget proof before provider prompt construction."""

    def __init__(self, runtime: DraftRunPayloadBudgetRuntime | None = None) -> None:
        self._runtime = runtime or DraftRunPayloadBudgetRuntime()

    def evaluate(
        self,
        *,
        operation_id: str,
        draft_run_step: str,
        provider_input: Mapping[str, Any],
        execution_mode: str | None,
        model: str | None,
        model_role: str,
        generation_params: Mapping[str, Any] | None = None,
        profile_operation_id: str | None = None,
    ) -> ProviderInputBudgetProof:
        budget_operation_id = profile_operation_id or operation_id
        budgeted = self._runtime.compact(
            budget_operation_id,
            provider_input,
            execution_mode=execution_mode,
            model=model,
            model_role=model_role,
            generation_params=generation_params,
        )
        payload_budget = dict(budgeted.payload_budget)
        if budget_operation_id != operation_id:
            payload_budget["operationAlias"] = operation_id
            budgeted = BudgetedProviderInput(
                payload=budgeted.payload,
                input_stats=budgeted.input_stats,
                payload_stats={**budgeted.payload_stats, "payloadBudget": payload_budget},
                incident=budgeted.incident,
            )
        return ProviderInputBudgetProof(
            operation_id=operation_id,
            draft_run_step=draft_run_step,
            provider_input=dict(provider_input),
            budgeted_input=budgeted,
            profile_operation_id=budget_operation_id,
        )


__all__ = ("ProviderInputBudgetGate", "ProviderInputBudgetProof")
