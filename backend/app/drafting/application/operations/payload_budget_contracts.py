"""Owner: drafting.application.operations

Used by: DraftRun payload budget policy, compactors, and runtime migration helpers.
Does not own: provider calls, prompt text, operation routing, or incident decisions.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.drafting.domain.provider_input_semantics import SemanticInputContract
from backend.app.shared.llm_operations import LlmOperationIncident


@dataclass(frozen=True)
class PayloadBudgetProfile:
    operation_id: str
    operation_kind: str
    execution_mode: str
    max_prompt_chars: int
    approx_token_budget: int
    max_rules: int
    max_claims: int
    max_evidence_items: int
    max_candidates: int
    max_source_snippets: int
    max_prior_drafts: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "operationId": self.operation_id,
            "operationKind": self.operation_kind,
            "executionMode": self.execution_mode,
            "maxPromptChars": self.max_prompt_chars,
            "approxTokenBudget": self.approx_token_budget,
            "maxRules": self.max_rules,
            "maxClaims": self.max_claims,
            "maxEvidenceItems": self.max_evidence_items,
            "maxCandidates": self.max_candidates,
            "maxSourceSnippets": self.max_source_snippets,
            "maxPriorDrafts": self.max_prior_drafts,
        }


@dataclass(frozen=True)
class PayloadBudgetResult:
    compact_payload: dict[str, Any]
    input_stats: dict[str, Any]
    payload_stats: dict[str, Any]
    trimmed_counts: dict[str, int] = field(default_factory=dict)
    suppressed_fields: tuple[str, ...] = ()
    quality_risk: str = "none"
    incident: LlmOperationIncident | None = None

    @property
    def payload_budget(self) -> dict[str, Any]:
        return dict(self.payload_stats.get("payloadBudget") or {})


@dataclass(frozen=True)
class PayloadCompactionResult:
    payload: dict[str, Any]
    trimmed_counts: dict[str, int]
    suppressed_fields: tuple[str, ...] = ()
