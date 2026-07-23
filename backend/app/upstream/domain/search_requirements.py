"""Owner: upstream.domain

Used by: deterministic radar filter projection, query allocation, and coverage trace.
Does not own: provider transport, result triage, signal scoring, persistence, or UI.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


SearchRequirementRole = Literal["required", "optional", "exclusion", "tension"]


@dataclass(frozen=True)
class SearchRequirement:
    id: str
    filter_id: str
    dimension: str
    mode: str
    role: SearchRequirementRole
    title: str
    statement: str
    priority: int
    query_families: tuple[str, ...]
    evidence_types: tuple[str, ...]
    terms: tuple[str, ...] = ()
    source_hints: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filterId": self.filter_id,
            "dimension": self.dimension,
            "mode": self.mode,
            "role": self.role,
            "title": self.title,
            "statement": self.statement,
            "priority": self.priority,
            "queryFamilies": list(self.query_families),
            "evidenceTypes": list(self.evidence_types),
            "terms": list(self.terms),
            "sourceHints": list(self.source_hints),
        }


@dataclass(frozen=True)
class SearchApplicabilityDecision:
    filter_id: str
    dimension: str
    mode: str
    reason: str

    def to_payload(self) -> dict[str, str]:
        return {
            "filterId": self.filter_id,
            "dimension": self.dimension,
            "mode": self.mode,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RadarSearchRequirementProfile:
    radar_id: str
    requirements: tuple[SearchRequirement, ...]
    not_search_applicable: tuple[SearchApplicabilityDecision, ...]
    version: str = "radar-search-requirements-v1"
    retained_counts: dict[str, int] = field(default_factory=dict)
    trimmed_counts: dict[str, int] = field(default_factory=dict)
    suppressed_fields: tuple[str, ...] = (
        "workspace",
        "fabulas",
        "contentPlanItems",
        "publications",
        "providerEnvelopes",
        "trace",
    )

    def required_ids(self) -> tuple[str, ...]:
        return tuple(item.id for item in self.requirements if item.role == "required")

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "radarId": self.radar_id,
            "requirements": [item.to_payload() for item in self.requirements],
            "notSearchApplicable": [item.to_payload() for item in self.not_search_applicable],
            "retainedCounts": dict(self.retained_counts),
            "trimmedCounts": dict(self.trimmed_counts),
            "suppressedFields": list(self.suppressed_fields),
        }


__all__ = (
    "RadarSearchRequirementProfile",
    "SearchApplicabilityDecision",
    "SearchRequirement",
    "SearchRequirementRole",
)
