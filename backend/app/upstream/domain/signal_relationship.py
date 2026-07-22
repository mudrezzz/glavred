"""Owner: upstream.domain

Used by: relationship policy, utility report, and signal presentation.
Does not own: pair selection, classification policy, provider calls, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.upstream.domain.signal_utility_types import SignalRelationshipKind


@dataclass(frozen=True)
class SignalRelationship:
    other_signal_id: str
    kind: SignalRelationshipKind
    summary: str
    evidence_refs: tuple[dict[str, str], ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "otherSignalId": self.other_signal_id,
            "kind": self.kind.value,
            "summary": self.summary,
            "evidenceRefs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class SignalRelationshipReport:
    status: str
    canonical_signal_id: str
    relations: tuple[SignalRelationship, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": 1,
            "status": self.status,
            "canonicalSignalId": self.canonical_signal_id,
            "relations": [item.to_payload() for item in self.relations],
        }


__all__ = ("SignalRelationship", "SignalRelationshipReport")
