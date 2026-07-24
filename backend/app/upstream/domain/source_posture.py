"""Owner: upstream.domain

Used by: source-posture classification and utility consistency policies.
Does not own: provider evaluation, URL reading, persistence, or UI presentation.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.upstream.domain.signal_utility_types import (
    SignalClaimSupport,
    SignalSourcePosture,
)


@dataclass(frozen=True)
class SourcePostureAssessment:
    ownership: SignalSourcePosture
    claim_support: SignalClaimSupport
    reason_codes: tuple[str, ...]
    source_domains: tuple[str, ...]
    owner_keys: tuple[str, ...]

    @property
    def effective_posture(self) -> SignalSourcePosture:
        if self.claim_support == SignalClaimSupport.CORROBORATED:
            return SignalSourcePosture.CORROBORATED
        return self.ownership

    def to_payload(self) -> dict[str, Any]:
        return {
            "sourcePosture": self.effective_posture.value,
            "ownershipPosture": self.ownership.value,
            "claimSupport": self.claim_support.value,
            "reasonCodes": list(self.reason_codes),
            "sourceDomains": list(self.source_domains),
            "ownerKeys": list(self.owner_keys),
        }


__all__ = ("SourcePostureAssessment",)
