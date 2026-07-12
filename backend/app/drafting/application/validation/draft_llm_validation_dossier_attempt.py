"""Owner: drafting.application.validation

Used by: LLM validation provider attempts.
Does not own: dossier assembly, provider transport, result parsing, or retry policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.domain.ai_run import AiRunProvider
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.validation.draft_llm_validation_audit import LlmValidationTraceBuilder
from backend.app.drafting.application.validation.draft_llm_validation_prompts import LlmValidationPromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedLlmValidationAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class LlmValidationDossierAttemptBuilder:
    def __init__(self, budget_gate: ProviderInputBudgetGate | None = None) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = LlmValidationPromptBuilder()
        self._traces = LlmValidationTraceBuilder()

    def prepare(
        self,
        *,
        dossier: ProviderDossier,
        candidate_id: str,
        model: str,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        execution_mode: str | None,
        repair_context: dict[str, Any] | None,
    ) -> PreparedLlmValidationAttempt:
        proof = self._budget_gate.evaluate(
            operation_id="llmValidation",
            draft_run_step="llmValidation",
            provider_input=dossier.provider_input(),
            execution_mode=execution_mode,
            model=model,
            model_role="review",
        )
        messages = self._prompts.build_from_provider_input(
            provider_input=proof.budgeted_input.payload,
            repair_context=repair_context,
        )
        request_payload = self._traces.request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=model,
            messages=messages,
            candidate_id=candidate_id,
            attempt=attempt,
            deterministic_report={"issues": proof.budgeted_input.payload.get("validationIssues", [])},
            model_selection=model_selection,
        )
        request_payload.update({**proof.request_payload_fields(), "providerDossier": dossier.to_payload()})
        return PreparedLlmValidationAttempt(messages, request_payload)


__all__ = ("LlmValidationDossierAttemptBuilder", "PreparedLlmValidationAttempt")
