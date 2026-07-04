"""Owner: drafting.application.operations

Used by: DraftRun provider-heavy services before building LLM provider messages.
Does not own: artifact storage, provider adapters, prompt text, model selection.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
import math
from typing import Any, Mapping

from backend.app.drafting.application.operations.payload_budget_contracts import (
    PayloadBudgetProfile,
    PayloadBudgetResult,
    SemanticInputContract,
)
from backend.app.drafting.application.operations.payload_budget_profiles import PayloadBudgetProfileRegistry
from backend.app.drafting.application.operations.payload_compactors import DraftRunPayloadCompactor, PayloadBudgetCounters
from backend.app.drafting.application.operations.payload_semantic_contracts import SemanticInputContractRegistry
from backend.app.shared.llm_operations import LlmOperationIncident, LlmOperationIncidentSeverity, LlmOperationIncidentType

HARD_PAYLOAD_CHAR_CAP_MULTIPLIER = 1.25
CONTEXT_OVER_BUDGET_INCIDENT = "contextOverBudget"
PAYLOAD_TOO_LARGE_INCIDENT = "payloadTooLarge"


class DraftRunPayloadBudgetPolicy:
    def __init__(
        self,
        *,
        profiles: PayloadBudgetProfileRegistry | None = None,
        contracts: SemanticInputContractRegistry | None = None,
        compactor: DraftRunPayloadCompactor | None = None,
    ) -> None:
        self._profiles = profiles or PayloadBudgetProfileRegistry()
        self._contracts = contracts or SemanticInputContractRegistry()
        self._compactor = compactor or DraftRunPayloadCompactor()

    def profile_for(self, operation_id: str, execution_mode: str | None = None) -> PayloadBudgetProfile:
        return self._profiles.profile_for(operation_id, execution_mode)

    def compact(
        self,
        operation_id: str,
        payload: Mapping[str, Any],
        *,
        execution_mode: str | None = None,
        model: str | None = None,
        model_role: str | None = None,
        generation_params: Mapping[str, Any] | None = None,
    ) -> PayloadBudgetResult:
        profile = self.profile_for(operation_id, execution_mode)
        contract = self._contracts.contract_for(operation_id)
        compaction = self._compactor.compact(payload, profile=profile, contract=contract)
        prompt_char_estimate = len(json.dumps(compaction.payload, ensure_ascii=False, sort_keys=True))
        # Approximation is intentionally simple and trace-facing; exact tokenizer
        # selection is provider/model-specific and belongs outside this policy.
        approx_tokens = math.ceil(prompt_char_estimate / 4)
        sent_counts = PayloadBudgetCounters.sent_counts(compaction.payload)
        quality_risk = self._quality_risk(contract, compaction.payload, compaction.trimmed_counts, prompt_char_estimate, profile.max_prompt_chars)
        payload_budget = {
            "profileId": profile.operation_id,
            "operationKind": profile.operation_kind,
            "executionMode": profile.execution_mode,
            "limits": profile.to_payload(),
            "sentCounts": sent_counts,
            "trimmedCounts": compaction.trimmed_counts,
            "suppressedFields": list(compaction.suppressed_fields),
            "semanticInputs": contract.to_payload(),
            "qualityRisk": quality_risk,
            "promptCharEstimate": prompt_char_estimate,
            "approxTokenEstimate": approx_tokens,
        }
        input_stats = {
            "promptCharEstimate": prompt_char_estimate,
            "approxTokenEstimate": approx_tokens,
            "ruleCount": sent_counts["rules"],
            "evidenceCount": sent_counts["evidenceItems"],
            "claimCount": sent_counts["claims"],
            "sourceCount": sent_counts["sourceSnippets"],
            "candidateCount": sent_counts["candidates"],
            "model": model,
            "modelRole": model_role,
            "generationParams": dict(generation_params or {}),
        }
        payload_stats = {"payloadBudget": payload_budget}
        return PayloadBudgetResult(
            compact_payload=compaction.payload,
            input_stats=input_stats,
            payload_stats=payload_stats,
            trimmed_counts=compaction.trimmed_counts,
            suppressed_fields=compaction.suppressed_fields,
            quality_risk=quality_risk,
            incident=self._budget_incident(profile, prompt_char_estimate, payload_stats),
        )

    def _quality_risk(
        self,
        contract: SemanticInputContract,
        payload: Mapping[str, Any],
        trimmed_counts: Mapping[str, int],
        prompt_chars: int,
        max_prompt_chars: int,
    ) -> str:
        missing_must_have = [field_name for field_name in contract.must_have if field_name not in payload or payload.get(field_name) in (None, {}, [])]
        if missing_must_have or prompt_chars > max_prompt_chars:
            return "high"
        if any(value > 0 for value in trimmed_counts.values()):
            return "medium"
        return "none"

    def _budget_incident(self, profile: PayloadBudgetProfile, prompt_char_estimate: int, payload_stats: Mapping[str, Any]) -> LlmOperationIncident | None:
        # payloadTooLarge is reserved for hard cap breaches that should be treated as
        # unsafe provider input, not normal trimming pressure.
        if prompt_char_estimate > int(profile.max_prompt_chars * HARD_PAYLOAD_CHAR_CAP_MULTIPLIER):
            return LlmOperationIncident(
                incident_type=LlmOperationIncidentType.PAYLOAD_TOO_LARGE,
                incident_severity=LlmOperationIncidentSeverity.ERROR,
                probable_cause="compacted-provider-payload-exceeds-hard-cap",
                needs_follow_up=True,
                payload_stats=payload_stats,
            )
        # contextOverBudget means the curated prompt exceeded its normal profile; the
        # operation can still run but diagnostics should review quality/cost risk.
        if prompt_char_estimate > profile.max_prompt_chars:
            return LlmOperationIncident(
                incident_type=LlmOperationIncidentType.CONTEXT_OVER_BUDGET,
                incident_severity=LlmOperationIncidentSeverity.WARNING,
                probable_cause="compacted-provider-payload-exceeds-profile-budget",
                needs_follow_up=True,
                payload_stats=payload_stats,
            )
        return None
