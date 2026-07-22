"""Owner: shared.llm_operations

Used by: drafting and upstream provider attempt builders that verify serialized messages.
Does not own: domain-specific compaction, prompt wording, provider transport, or retry policy.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ProviderMessageBudgetResult:
    request_fields: dict[str, Any]
    blocked_reason: str | None


class ProviderMessageBudgetGuard:
    """Reconciles direct input proof with the messages actually sent to a provider."""

    def evaluate(
        self,
        *,
        messages: list[dict[str, str]],
        request_fields: Mapping[str, Any],
        repair_context_char_count: int = 0,
    ) -> ProviderMessageBudgetResult:
        fields = dict(request_fields)
        payload_budget = dict(fields.get("payloadBudget") or {})
        input_stats = dict(fields.get("inputStats") or {})
        payload_stats = dict(fields.get("payloadStats") or {})
        provider_input_chars = int(payload_budget.get("providerInputCharEstimate") or payload_budget.get("promptCharEstimate") or 0)
        message_chars = len(json.dumps(messages, ensure_ascii=False, sort_keys=True))
        limits = dict(payload_budget.get("limits") or {})
        max_chars = int(limits.get("maxMessageChars") or limits.get("maxPromptChars") or 0)

        payload_budget.update(
            {
                "providerInputCharEstimate": provider_input_chars,
                "promptCharEstimate": message_chars,
                "approxTokenEstimate": math.ceil(message_chars / 4),
                "messageCharCount": message_chars,
                "repairContextCharCount": repair_context_char_count,
            }
        )
        input_stats.update(
            {
                "providerInputCharEstimate": provider_input_chars,
                "promptCharEstimate": message_chars,
                "approxTokenEstimate": math.ceil(message_chars / 4),
                "messageCharCount": message_chars,
                "repairContextCharCount": repair_context_char_count,
            }
        )
        blocked_reason = None
        if max_chars and message_chars > max_chars:
            blocked_reason = "provider-message-budget-exceeded"
            payload_budget["qualityRisk"] = "high"
            payload_budget["incident"] = {
                "incidentType": "contextOverBudget",
                "incidentSeverity": "error",
                "probableCause": "serialized-provider-messages-exceed-profile-budget",
                "needsFollowUp": True,
            }
        payload_stats["payloadBudget"] = payload_budget
        fields.update(
            {
                "payloadBudget": payload_budget,
                "inputStats": input_stats,
                "payloadStats": payload_stats,
                "messageCharCount": message_chars,
                "repairContextCharCount": repair_context_char_count,
                "providerInputCharEstimate": provider_input_chars,
                "promptCharEstimate": message_chars,
            }
        )
        return ProviderMessageBudgetResult(fields, blocked_reason)


__all__ = ("ProviderMessageBudgetGuard", "ProviderMessageBudgetResult")
