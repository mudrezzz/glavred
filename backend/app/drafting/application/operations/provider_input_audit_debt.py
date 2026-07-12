"""Owner: drafting.application.operations

Used by: ProviderInputAudit to classify intentionally deferred provider-input gates.
Does not own: repair implementation, roadmap status changes, provider calls, or prompts.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from backend.app.drafting.application.operations.provider_input_audit_contracts import ProviderInputBudgetDebt

DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS: dict[str, ProviderInputBudgetDebt] = {}


__all__ = ("DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS",)
