"""Owner: drafting.application.revision

Used by: directed revision provider attempts.
Does not own: dossier assembly, revision acceptance, provider transport, or retry policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.revision.draft_directed_revision_prompts import DirectedRevisionPromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedRevisionAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class RevisionDossierAttemptBuilder:
    def __init__(
        self,
        budget_gate: ProviderInputBudgetGate | None = None,
        prompt_builder: DirectedRevisionPromptBuilder | None = None,
    ) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = prompt_builder or DirectedRevisionPromptBuilder()

    def prepare(
        self,
        *,
        dossier: ProviderDossier,
        model: str,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        generation_params: dict[str, Any],
        execution_mode: str | None,
        repair_context: dict[str, Any] | None,
    ) -> PreparedRevisionAttempt:
        proof = self._budget_gate.evaluate(
            operation_id="directedRevision",
            draft_run_step="directedRevision",
            provider_input=dossier.provider_input(),
            execution_mode=execution_mode,
            model=model,
            model_role="writer",
            generation_params=generation_params,
        )
        messages = self._prompts.build_from_provider_input(
            provider_input=proof.budgeted_input.payload,
            repair_context=repair_context,
        )
        request_payload = {
            "draftRunStep": "directedRevision",
            "attempt": attempt,
            "messages": messages,
            "generationParams": generation_params,
            **model_selection,
            **proof.request_payload_fields(),
            "providerDossier": dossier.to_payload(),
        }
        return PreparedRevisionAttempt(messages, request_payload)


__all__ = ("PreparedRevisionAttempt", "RevisionDossierAttemptBuilder")
