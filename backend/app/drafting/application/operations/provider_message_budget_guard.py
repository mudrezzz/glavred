"""Compatibility exports for the shared provider message budget guard.

Owner: drafting.application.operations
Used by: existing DraftRun provider attempt builders.
Does not own: message-size policy, provider transport, prompt wording, or compaction.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.shared.llm_operations.provider_message_budget_guard import (
    ProviderMessageBudgetGuard,
    ProviderMessageBudgetResult,
)


__all__ = ("ProviderMessageBudgetGuard", "ProviderMessageBudgetResult")
