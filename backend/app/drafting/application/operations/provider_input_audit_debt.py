"""Owner: drafting.application.operations

Used by: ProviderInputAudit to classify intentionally deferred provider-input gates.
Does not own: repair implementation, roadmap status changes, provider calls, or prompts.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from backend.app.drafting.application.operations.provider_input_audit_contracts import ProviderInputBudgetDebt

DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS: dict[str, ProviderInputBudgetDebt] = {
    "pairwiseRanking": ProviderInputBudgetDebt(
        operation_id="pairwiseRanking",
        owner="backend.app.drafting.application.revision",
        reason="ranking/revision dossier migration is intentionally deferred after planning gate rollout",
        risk="large candidate/report payloads can exceed provider input budget until revision dossier slice",
        repair_slice="2.17.4.6.1.3.9",
    ),
    "llmValidation": ProviderInputBudgetDebt(
        operation_id="llmValidation",
        owner="backend.app.drafting.application.validation",
        reason="review dossier migration is deferred to validation quality/read-model slice",
        risk="LLM validation can still pass broad candidate/rule/evidence reports",
        repair_slice="2.17.4.6.1.3.9",
    ),
    "finalQualityGateReview": ProviderInputBudgetDebt(
        operation_id="finalQualityGateReview",
        owner="backend.app.drafting.application.final_quality",
        reason="final-gate dossier belongs with final quality repair path cleanup",
        risk="final gate can still pass broad validation/final trace",
        repair_slice="2.17.4.6.1.3.9",
    ),
}


__all__ = ("DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS",)
