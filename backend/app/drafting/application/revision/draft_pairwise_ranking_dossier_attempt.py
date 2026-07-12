"""Owner: drafting.application.revision

Used by: pairwise ranking provider attempts.
Does not own: dossier assembly, ranking decisions, provider transport, or fallback policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.drafting.application.operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.drafting.application.revision.draft_pairwise_ranking_prompts import PairwiseRankingPromptBuilder
from backend.app.drafting.domain.provider_dossier import ProviderDossier


@dataclass(frozen=True)
class PreparedPairwiseRankingAttempt:
    messages: list[dict[str, str]]
    request_payload: dict[str, Any]
    blocked_reason: str | None = None


class PairwiseRankingDossierAttemptBuilder:
    def __init__(
        self,
        budget_gate: ProviderInputBudgetGate | None = None,
        prompt_builder: PairwiseRankingPromptBuilder | None = None,
        message_budget_guard: ProviderMessageBudgetGuard | None = None,
    ) -> None:
        self._budget_gate = budget_gate or ProviderInputBudgetGate()
        self._prompts = prompt_builder or PairwiseRankingPromptBuilder()
        self._message_budget = message_budget_guard or ProviderMessageBudgetGuard()

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
        input_with_repair = dossier.provider_input()
        if repair_context:
            input_with_repair["repairContext"] = repair_context
        proof = self._budget_gate.evaluate(
            operation_id="pairwiseRanking",
            draft_run_step="pairwiseRanking",
            provider_input=input_with_repair,
            execution_mode=execution_mode,
            model=model,
            model_role="review",
        )
        budgeted_input = dict(proof.budgeted_input.payload)
        budgeted_repair = budgeted_input.pop("repairContext", None)
        messages = self._prompts.build_from_provider_input(provider_input=budgeted_input, repair_context=budgeted_repair)
        repair_chars = len(json.dumps(budgeted_repair, ensure_ascii=False, sort_keys=True)) if budgeted_repair else 0
        message_proof = self._message_budget.evaluate(
            messages=messages,
            request_fields=proof.request_payload_fields(),
            repair_context_char_count=repair_chars,
        )
        request_payload = {
            "draftRunStep": "pairwiseRanking",
            "attempt": attempt,
            "messages": messages,
            **model_selection,
            **message_proof.request_fields,
            "providerInput": budgeted_input,
            "providerDossier": dossier.to_payload(),
        }
        return PreparedPairwiseRankingAttempt(messages, request_payload, message_proof.blocked_reason)


__all__ = ("PairwiseRankingDossierAttemptBuilder", "PreparedPairwiseRankingAttempt")
