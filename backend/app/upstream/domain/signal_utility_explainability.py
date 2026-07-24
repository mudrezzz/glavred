"""Owner: upstream.domain

Used by: signal utility decision and presentation contracts.
Does not own: criterion calculation, source resolution, provider calls, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.upstream.domain.signal_utility_types import (
    SignalCriterionEffect,
    SignalCriterionOrigin,
    SignalUtilityStatus,
)


@dataclass(frozen=True)
class SignalUtilityCriterionResult:
    criterion_id: str
    origin: SignalCriterionOrigin
    dimension: str
    title: str
    statement: str
    mode: str
    status: SignalUtilityStatus
    verdict: str
    effect: SignalCriterionEffect
    summary: str
    setting_refs: tuple[str, ...] = ()
    evidence_refs: tuple[dict[str, str], ...] = ()
    uncertainty: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "criterionId": self.criterion_id,
            "origin": self.origin.value,
            "dimension": self.dimension,
            "title": self.title,
            "statement": self.statement,
            "mode": self.mode,
            "status": self.status.value,
            "verdict": self.verdict,
            "effect": self.effect.value,
            "summary": self.summary,
            "settingRefs": list(self.setting_refs),
            "evidenceRefs": list(self.evidence_refs),
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class SignalQualityCheck:
    check_id: str
    title: str
    status: str
    verdict: str
    effect: SignalCriterionEffect
    summary: str
    classification: str | None = None
    applicable: bool = True
    evidence_refs: tuple[dict[str, str], ...] = ()
    details: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "checkId": self.check_id,
            "title": self.title,
            "status": self.status,
            "verdict": self.verdict,
            "effect": self.effect.value,
            "summary": self.summary,
            "classification": self.classification,
            "applicable": self.applicable,
            "evidenceRefs": list(self.evidence_refs),
            "details": dict(self.details or {}),
        }


__all__ = ("SignalQualityCheck", "SignalUtilityCriterionResult")
