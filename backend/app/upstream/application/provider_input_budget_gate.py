"""Owner: upstream.application

Used by: upstream provider operations before constructing and sending provider messages.
Does not own: provider transport, query planning, prompt wording, or DraftRun payload policies.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile


@dataclass(frozen=True)
class UpstreamProviderInputBudgetResult:
    request_fields: dict[str, Any]
    blocked_reason: str | None
    provider_input_chars: int
    approx_tokens: int


class UpstreamProviderInputBudgetGate:
    def evaluate(
        self,
        *,
        provider_input: Mapping[str, Any],
        query_text: str,
        profile: UpstreamProviderBudgetProfile,
        run_budget: Mapping[str, Any],
    ) -> UpstreamProviderInputBudgetResult:
        provider_input_payload = dict(provider_input)
        input_chars = len(json.dumps(provider_input_payload, ensure_ascii=False, sort_keys=True))
        approx_tokens = math.ceil(input_chars / 4)
        current_run_chars = int(run_budget.get("usedProviderInputChars") or 0)
        current_run_tokens = int(run_budget.get("usedProviderInputTokens") or 0)
        reasons: list[str] = []
        if len(query_text) > profile.max_query_chars:
            reasons.append("query-char-limit")
        if input_chars > profile.max_provider_input_chars:
            reasons.append("provider-input-char-limit")
        if approx_tokens > profile.max_approx_tokens:
            reasons.append("provider-input-token-limit")
        if current_run_chars + input_chars > profile.max_run_input_chars:
            reasons.append("radar-run-input-char-limit")
        if current_run_tokens + approx_tokens > profile.max_run_approx_tokens:
            reasons.append("radar-run-input-token-limit")

        blocked_reason = "provider-input-over-budget" if reasons else None
        payload_budget: dict[str, Any] = {
            "profileId": profile.id,
            "operationId": profile.operation_id,
            "executionMode": profile.execution_mode,
            "status": "blocked" if blocked_reason else "directlyBudgeted",
            "limits": {
                "maxQueryChars": profile.max_query_chars,
                "maxProviderInputChars": profile.max_provider_input_chars,
                "maxMessageChars": profile.max_message_chars,
                "maxApproxTokens": profile.max_approx_tokens,
                "maxRunInputChars": profile.max_run_input_chars,
                "maxRunApproxTokens": profile.max_run_approx_tokens,
            },
            "providerInputCharEstimate": input_chars,
            "promptCharEstimate": input_chars,
            "approxTokenEstimate": approx_tokens,
            "qualityRisk": "high" if blocked_reason else "none",
            "budgetIncidents": list(reasons),
        }
        if blocked_reason:
            payload_budget["incident"] = {
                "incidentType": "payloadTooLarge",
                "incidentSeverity": "error",
                "probableCause": ",".join(reasons),
                "needsFollowUp": True,
            }
        fields = {
            "providerInput": provider_input_payload,
            "payloadBudget": payload_budget,
            "inputStats": {
                "queryCharCount": len(query_text),
                "providerInputCharEstimate": input_chars,
                "approxTokenEstimate": approx_tokens,
                "runInputCharsBefore": current_run_chars,
                "runInputTokensBefore": current_run_tokens,
            },
            "payloadStats": {
                "sentItemCount": 1,
                "trimmedItemCount": 0,
                "suppressedFields": [],
            },
        }
        return UpstreamProviderInputBudgetResult(fields, blocked_reason, input_chars, approx_tokens)


__all__ = ("UpstreamProviderInputBudgetGate", "UpstreamProviderInputBudgetResult")
