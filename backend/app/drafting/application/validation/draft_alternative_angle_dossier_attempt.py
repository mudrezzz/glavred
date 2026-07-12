"""Owner: drafting.application.validation

Used by: alternative-angle route provider attempts.
Does not own: dossier assembly, route parsing, provider transport, or tournament policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from backend.app.domain.ai_run import AiRunProvider
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.drafting.application.validation.draft_alternative_angle_audit import AlternativeAngleTraceBuilder
from backend.app.drafting.application.validation.draft_alternative_angle_prompts import AlternativeAnglePromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedAlternativeAngleAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]
    blocked_reason: str | None = None


class AlternativeAngleDossierAttemptBuilder:
    def __init__(self, budget_gate: ProviderInputBudgetGate | None = None) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._message_budget = ProviderMessageBudgetGuard()
        self._prompts = AlternativeAnglePromptBuilder()
        self._traces = AlternativeAngleTraceBuilder()

    def prepare(
        self,
        *,
        dossier: ProviderDossier,
        model: str,
        model_role: str,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        generation_params: dict[str, Any],
        execution_mode: str | None,
        repair_context: dict[str, Any] | None,
    ) -> PreparedAlternativeAngleAttempt:
        attempt_input = {**dossier.provider_input(), "repairContext": repair_context or {}}
        proof = self._budget_gate.evaluate(
            operation_id="alternativeAngleRoute",
            draft_run_step="alternativeAngleRoute",
            provider_input=attempt_input,
            execution_mode=execution_mode,
            model=model,
            model_role=model_role,
            generation_params=generation_params,
        )
        budgeted_input = dict(proof.budgeted_input.payload)
        budgeted_repair_context = budgeted_input.pop("repairContext", {})
        messages = self._prompts.build_from_provider_input(provider_input=budgeted_input, repair_context=budgeted_repair_context)
        request_payload = self._traces.request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=model,
            messages=messages,
            context_pack=None,
            attempt=attempt,
            model_selection=model_selection,
            generation_params=generation_params,
        )
        request_payload.pop("contextPack", None)
        request_fields = proof.request_payload_fields()
        request_fields["providerInput"] = budgeted_input
        message_budget = self._message_budget.evaluate(
            messages=messages,
            request_fields=request_fields,
            repair_context_char_count=(
                len(json.dumps(budgeted_repair_context, ensure_ascii=False, sort_keys=True))
                if budgeted_repair_context
                else 0
            ),
        )
        request_payload.update({**message_budget.request_fields, "providerDossier": dossier.to_payload()})
        return PreparedAlternativeAngleAttempt(messages, request_payload, message_budget.blocked_reason)


__all__ = ("AlternativeAngleDossierAttemptBuilder", "PreparedAlternativeAngleAttempt")
