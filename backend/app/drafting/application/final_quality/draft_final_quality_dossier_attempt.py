"""Owner: drafting.application.final_quality

Used by: independent final-quality provider review attempts.
Does not own: dossier assembly, gate decisions, provider transport, or repair acceptance.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.final_quality.draft_final_quality_review_prompts import FinalQualityReviewPromptBuilder
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedFinalQualityAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class FinalQualityDossierAttemptBuilder:
    def __init__(
        self,
        budget_gate: ProviderInputBudgetGate | None = None,
        prompt_builder: FinalQualityReviewPromptBuilder | None = None,
    ) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = prompt_builder or FinalQualityReviewPromptBuilder()

    def prepare(
        self,
        *,
        dossier: ProviderDossier,
        model: str,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        execution_mode: str | None,
        model_independence: str,
        repair_context: dict[str, Any] | None,
    ) -> PreparedFinalQualityAttempt:
        proof = self._budget_gate.evaluate(
            operation_id="finalQualityGateReview",
            profile_operation_id="finalQualityReviewRepair",
            draft_run_step="finalQualityGateReview",
            provider_input=dossier.provider_input(),
            execution_mode=execution_mode,
            model=model,
            model_role="finalGate",
        )
        messages = self._prompts.build_from_provider_input(
            provider_input=proof.budgeted_input.payload,
            repair_context=repair_context,
        )
        request_payload = {
            "draftRunStep": "finalQualityGateReview",
            "attempt": attempt,
            "messages": messages,
            "modelIndependence": model_independence,
            **model_selection,
            **proof.request_payload_fields(),
            "providerDossier": dossier.to_payload(),
        }
        return PreparedFinalQualityAttempt(messages, request_payload)


__all__ = ("FinalQualityDossierAttemptBuilder", "PreparedFinalQualityAttempt")
