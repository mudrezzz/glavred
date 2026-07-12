"""Owner: drafting.application.revision

Used by: pairwise ranking provider attempts.
Does not own: dossier assembly, ranking decisions, provider transport, or fallback policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.revision.draft_pairwise_ranking_prompts import PairwiseRankingPromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedPairwiseRankingAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]


class PairwiseRankingDossierAttemptBuilder:
    def __init__(
        self,
        budget_gate: ProviderInputBudgetGate | None = None,
        prompt_builder: PairwiseRankingPromptBuilder | None = None,
    ) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = prompt_builder or PairwiseRankingPromptBuilder()

    def prepare(
        self,
        *,
        dossier: ProviderDossier,
        model: str,
        attempt: dict[str, Any],
        model_selection: dict[str, Any],
        execution_mode: str | None,
        repair_context: dict[str, Any] | None,
    ) -> PreparedPairwiseRankingAttempt:
        proof = self._budget_gate.evaluate(
            operation_id="pairwiseRanking",
            draft_run_step="pairwiseRanking",
            provider_input=dossier.provider_input(),
            execution_mode=execution_mode,
            model=model,
            model_role="review",
        )
        messages = self._prompts.build_from_provider_input(
            provider_input=proof.budgeted_input.payload,
            repair_context=repair_context,
        )
        request_payload = {
            "draftRunStep": "pairwiseRanking",
            "attempt": attempt,
            "messages": messages,
            **model_selection,
            **proof.request_payload_fields(),
            "providerDossier": dossier.to_payload(),
        }
        return PreparedPairwiseRankingAttempt(messages, request_payload)


__all__ = ("PairwiseRankingDossierAttemptBuilder", "PreparedPairwiseRankingAttempt")
