"""Owner: upstream.domain

Used by: upstream search campaign planning and RadarRun trace serialization.
Does not own: provider transport, API routing, UI rendering, or signal scoring.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SearchIntent:
    id: str
    intent_type: str
    family: str
    evidence_type: str
    label: str
    source_handle_id: str
    source_handle_title: str
    rationale: str
    priority: int
    query_terms: list[str] = field(default_factory=list)
    query_language: str = "ru"

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "intentType": self.intent_type,
            "family": self.family,
            "evidenceType": self.evidence_type,
            "label": self.label,
            "sourceHandleId": self.source_handle_id,
            "sourceHandleTitle": self.source_handle_title,
            "rationale": self.rationale,
            "priority": self.priority,
            "queryTerms": self.query_terms,
            "queryLanguage": self.query_language,
        }


@dataclass(frozen=True)
class SearchQuery:
    id: str
    intent_id: str
    source_handle_id: str
    intent: str
    family: str
    evidence_type: str
    priority: int
    label: str
    query: str
    rationale: str
    query_language: str = "ru"

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "intentId": self.intent_id,
            "sourceHandleId": self.source_handle_id,
            "intent": self.intent,
            "family": self.family,
            "evidenceType": self.evidence_type,
            "priority": self.priority,
            "label": self.label,
            "query": self.query,
            "rationale": self.rationale,
            "queryLanguage": self.query_language,
        }


@dataclass(frozen=True)
class SkippedSearchIntent:
    id: str
    reason: str
    rationale: str
    source_handle_id: str | None = None
    intent_id: str | None = None
    intent_type: str | None = None
    family: str | None = None
    query_language: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "reason": self.reason,
            "rationale": self.rationale,
        }
        if self.source_handle_id:
            payload["sourceHandleId"] = self.source_handle_id
        if self.intent_id:
            payload["intentId"] = self.intent_id
        if self.intent_type:
            payload["intentType"] = self.intent_type
        if self.family:
            payload["family"] = self.family
        if self.query_language:
            payload["queryLanguage"] = self.query_language
        return payload


@dataclass(frozen=True)
class SearchCampaignTrace:
    planner_version: str
    input_summary: dict[str, Any]
    intent_coverage: list[dict[str, Any]]
    budget_limits: dict[str, Any]
    source_eligibility: list[dict[str, Any]]
    skipped_reasons: list[str]
    ownership_boundary: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "plannerVersion": self.planner_version,
            "inputSummary": self.input_summary,
            "intentCoverage": self.intent_coverage,
            "budgetLimits": self.budget_limits,
            "sourceEligibility": self.source_eligibility,
            "skippedReasons": self.skipped_reasons,
            "ownershipBoundary": self.ownership_boundary,
        }


@dataclass(frozen=True)
class SearchPlan:
    strategy: str
    language: str
    intents: list[SearchIntent]
    queries: list[SearchQuery]
    skipped_intents: list[SkippedSearchIntent]
    source_strategy: dict[str, Any]
    trace: SearchCampaignTrace
    language_context: dict[str, Any] = field(default_factory=dict)
    language_coverage_gaps: list[dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        skipped_reasons = _unique([item.reason for item in self.skipped_intents])
        return {
            "strategy": self.strategy,
            "language": self.language,
            "queries": [item.to_payload() for item in self.queries],
            "skippedIntents": skipped_reasons,
            "intents": [item.to_payload() for item in self.intents],
            "sourceStrategy": self.source_strategy,
            "trace": self.trace.to_payload(),
            "skippedIntentDetails": [item.to_payload() for item in self.skipped_intents],
            "languageContext": self.language_context,
            "languageCoverageGaps": self.language_coverage_gaps,
        }


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))
