"""Owner: drafting.application.quality

Used by: DraftRun quality/fidelity reporting.
Does not own: provider recovery classification, validation issue lifecycle, or evidence retrieval.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any


class QualityFidelityEvidenceComponent:
    """Summarizes whether accepted evidence was available and interpreted."""

    def summary(self, steps: list[dict[str, Any]], stage_summaries: list[dict[str, Any]]) -> dict[str, Any]:
        public_evidence = _artifact(steps, "publicEvidence")
        rule_pack = _artifact(steps, "rulePack")
        found = len(_list(public_evidence.get("items")))
        attempts = _list(public_evidence.get("attempts"))
        rejected = sum(len(_list(_dict(_dict(item).get("metadata")).get("rejectedCitations"))) for item in attempts)
        interpretation = _dict(rule_pack.get("evidenceInterpretation"))
        interpreted = sum(
            len(_list(interpretation.get(key)))
            for key in ("implications", "usableExamples", "limits", "warnings")
        )
        fallback_interpreted = sum(
            1
            for item in stage_summaries
            if item.get("stepKey") == "rulePack" and item.get("retryPath") == "fallbackRecovered"
        )
        return {
            "foundEvidenceCount": found,
            "acceptedEvidenceCount": found,
            "interpretedEvidenceCount": interpreted,
            "fallbackInterpretedEvidenceCount": fallback_interpreted,
            "rejectedEvidenceCount": rejected,
            "coverageVerdict": self._coverage(found, interpreted, fallback_interpreted),
        }

    def _coverage(self, accepted: int, interpreted: int, fallback_interpreted: int) -> str:
        if accepted == 0:
            return "missing"
        if fallback_interpreted:
            return "weak"
        if interpreted == 0:
            return "partial"
        return "sufficient"


def _artifact(steps: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return next((_dict(step.get("artifact")) for step in steps if step.get("key") == key), {})


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
