"""Owner: drafting.application.generation

Used by: draft candidate and alternative-angle candidate provider attempts.
Does not own: dossier assembly, provider transport, result parsing, or fallback policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.domain.ai_run import AiRunProvider
from backend.app.domain.draft_candidates import DraftCandidateDirection
from backend.app.drafting.application.generation.draft_candidate_audit import build_candidate_request_trace
from backend.app.drafting.application.generation.draft_candidate_prompts import DraftCandidatePromptBuilder
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedWriterDossierAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class WriterDossierAttemptBuilder:
    def __init__(self, budget_gate: ProviderInputBudgetGate | None = None) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = DraftCandidatePromptBuilder()

    def prepare(
        self,
        *,
        operation_id: str,
        draft_run_step: str,
        dossier: ProviderDossier,
        context_summary: dict[str, Any],
        direction: DraftCandidateDirection,
        provider: AiRunProvider,
        model: str | None,
        model_role: str,
        model_selection: dict[str, Any],
        attempt: dict[str, Any] | None,
        generation_params: dict[str, Any],
        execution_mode: str | None,
        repair_context: dict[str, Any] | None,
        route: dict[str, Any] | None = None,
    ) -> PreparedWriterDossierAttempt:
        proof = self._budget_gate.evaluate(
            operation_id=operation_id,
            draft_run_step=draft_run_step,
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
        request_payload = build_candidate_request_trace(
            provider=provider,
            model=model,
            messages=messages,
            context_summary=context_summary,
            direction=direction,
            model_selection=model_selection,
            attempt=attempt,
            generation_params=generation_params,
        )
        request_payload.update(
            {
                "draftRunStep": draft_run_step,
                **proof.request_payload_fields(),
                "providerDossier": dossier.to_payload(),
            }
        )
        if route is not None:
            request_payload["route"] = route
        return PreparedWriterDossierAttempt(messages, request_payload)


__all__ = ("PreparedWriterDossierAttempt", "WriterDossierAttemptBuilder")
