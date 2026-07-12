"""Owner: drafting.application.quality

Used by: DraftRun quality issue lifecycle reporting.
Does not own: validator execution, final-gate decisions, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityIssueScope:
    scope: str
    applies_to_final_draft: bool
    resolved_reason: str | None = None


class QualityIssueScopePolicy:
    """Determines whether one issue still applies to the delivered candidate."""

    def classify(self, *, candidate_id: str | None, final_candidate_id: str | None) -> QualityIssueScope:
        if candidate_id and final_candidate_id:
            if candidate_id == final_candidate_id:
                return QualityIssueScope("finalDraft", True)
            return QualityIssueScope("nonFinalCandidate", False, "candidate-not-delivered")
        return QualityIssueScope("unknown", True)


__all__ = ("QualityIssueScope", "QualityIssueScopePolicy")
