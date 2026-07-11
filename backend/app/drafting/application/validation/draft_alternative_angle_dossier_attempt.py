"""Owner: drafting.application.validation

Used by: alternative-angle route provider attempts.
Does not own: dossier assembly, route parsing, provider transport, or tournament policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.domain.ai_run import AiRunProvider
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.validation.draft_alternative_angle_audit import AlternativeAngleTraceBuilder
from backend.app.drafting.application.validation.draft_alternative_angle_prompts import AlternativeAnglePromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedAlternativeAngleAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class AlternativeAngleDossierAttemptBuilder:
    def __init__(self, budget_gate: ProviderInputBudgetGate | None = None) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
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
        proof = self._budget_gate.evaluate(
            operation_id="alternativeAngleRoute",
            draft_run_step="alternativeAngleRoute",
            provider_input=dossier.provider_input(),
            execution_mode=execution_mode,
            model=model,
            model_role=model_role,
            generation_params=generation_params,
        )
        messages = self._prompts.build_from_provider_input(
            provider_input=proof.budgeted_input.payload,
            repair_context=repair_context,
        )
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
        request_payload.update(
            {
                **proof.request_payload_fields(),
                "providerDossier": dossier.to_payload(),
            }
        )
        return PreparedAlternativeAngleAttempt(messages, request_payload)


__all__ = ("AlternativeAngleDossierAttemptBuilder", "PreparedAlternativeAngleAttempt")
