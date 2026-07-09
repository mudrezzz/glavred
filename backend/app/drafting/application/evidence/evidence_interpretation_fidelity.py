"""Owner: drafting.application.evidence

Used by: Evidence interpretation services and DraftRun quality/fidelity reporting.
Does not own: provider retries, source retrieval, validation, final quality, or UI layout.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INTERPRETATION_KEYS = (
    "implications",
    "tensions",
    "usableExamples",
    "limits",
    "forbiddenOverclaims",
    "authorPositionLinks",
    "readerValueHooks",
    "recommendedUseByPlan",
    "rejectedEvidenceUses",
    "warnings",
)


@dataclass(frozen=True)
class EvidenceInterpretationFidelity:
    """Trace-safe judgement of whether interpreted evidence is trustworthy."""

    accepted_evidence_count: int
    interpreted_evidence_count: int
    fallback_used: bool
    coverage_verdict: str
    fidelity_impact: str
    accepted_risk: bool
    needs_follow_up: bool
    reason_codes: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "acceptedEvidenceCount": self.accepted_evidence_count,
            "interpretedEvidenceCount": self.interpreted_evidence_count,
            "fallbackUsed": self.fallback_used,
            "coverageVerdict": self.coverage_verdict,
            "fidelityImpact": self.fidelity_impact,
            "acceptedRisk": self.accepted_risk,
            "needsFollowUp": self.needs_follow_up,
            "reasonCodes": list(self.reason_codes),
        }


class EvidenceInterpretationFidelityPolicy:
    """Classifies evidence interpretation fidelity without changing provider behavior."""

    def evaluate(
        self,
        *,
        context_artifact: dict[str, Any],
        evidence_interpretation: dict[str, Any],
        attempts: list[dict[str, Any]],
        fallback_used: bool,
    ) -> EvidenceInterpretationFidelity:
        accepted_count = self._accepted_evidence_count(context_artifact)
        interpreted_count = self._interpreted_evidence_count(evidence_interpretation)
        reason_codes = self._reason_codes(
            accepted_count=accepted_count,
            interpreted_count=interpreted_count,
            attempts=attempts,
            fallback_used=fallback_used,
        )
        coverage_verdict = self._coverage_verdict(
            accepted_count=accepted_count,
            interpreted_count=interpreted_count,
            fallback_used=fallback_used,
        )
        fidelity_impact = self._fidelity_impact(coverage_verdict, reason_codes)
        return EvidenceInterpretationFidelity(
            accepted_evidence_count=accepted_count,
            interpreted_evidence_count=interpreted_count,
            fallback_used=fallback_used,
            coverage_verdict=coverage_verdict,
            fidelity_impact=fidelity_impact,
            accepted_risk=fidelity_impact in {"diagnostic", "weak"},
            needs_follow_up=fidelity_impact != "none",
            reason_codes=tuple(reason_codes),
        )

    def _coverage_verdict(self, *, accepted_count: int, interpreted_count: int, fallback_used: bool) -> str:
        if accepted_count == 0:
            return "missing"
        if fallback_used:
            return "weak"
        if interpreted_count == 0:
            return "partial"
        return "sufficient"

    def _fidelity_impact(self, coverage_verdict: str, reason_codes: list[str]) -> str:
        if coverage_verdict == "missing":
            return "blocked"
        if coverage_verdict in {"partial", "weak"}:
            return "weak"
        if any(code in {"backup-accepted", "provider-timeout-recovered", "provider-malformed-json-recovered"} for code in reason_codes):
            return "diagnostic"
        return "none"

    def _reason_codes(
        self,
        *,
        accepted_count: int,
        interpreted_count: int,
        attempts: list[dict[str, Any]],
        fallback_used: bool,
    ) -> list[str]:
        codes: list[str] = []
        if accepted_count == 0:
            codes.append("no-accepted-evidence")
        if interpreted_count == 0:
            codes.append("weak-interpreted-evidence")
        if fallback_used:
            codes.append("deterministic-fallback")
        if any(self._status(item) == "timeout" or self._incident_type(item) == "providerTimeout" for item in attempts) and not fallback_used:
            codes.append("provider-timeout-recovered")
        if any(self._incident_type(item) == "malformedJson" for item in attempts) and not fallback_used:
            codes.append("provider-malformed-json-recovered")
        if any(bool(item.get("backup")) and self._status(item) in {"accepted", "backupaccepted"} for item in attempts):
            codes.append("backup-accepted")
        if self._accepted_attempt_index(attempts) > 0 and not fallback_used:
            codes.append("retry-recovered")
        return _unique(codes)

    def _accepted_evidence_count(self, context_artifact: dict[str, Any]) -> int:
        public_items = _records(_record(context_artifact.get("publicEvidence")).get("items"))
        claims = [
            item
            for item in _records(_record(context_artifact.get("sourceLedger")).get("claims"))
            if item.get("type") == "externalEvidenceClaim"
        ]
        return max(len(public_items), len(claims))

    def _interpreted_evidence_count(self, evidence_interpretation: dict[str, Any]) -> int:
        return sum(len(_records(evidence_interpretation.get(key))) for key in INTERPRETATION_KEYS)

    def _accepted_attempt_index(self, attempts: list[dict[str, Any]]) -> int:
        return next((index for index, item in enumerate(attempts) if self._status(item) in {"accepted", "repaired", "backupaccepted"}), -1)

    def _incident_type(self, attempt: dict[str, Any]) -> str:
        return str(_record(attempt.get("incident")).get("incidentType") or "")

    def _status(self, attempt: dict[str, Any]) -> str:
        return str(attempt.get("status") or "").replace("-", "").lower()


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


__all__ = (
    "EvidenceInterpretationFidelity",
    "EvidenceInterpretationFidelityPolicy",
)
