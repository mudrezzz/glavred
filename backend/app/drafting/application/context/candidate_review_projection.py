"""Owner: drafting.application.context

Used by: review and ranking dossier context reads.
Does not own: candidate selection, validation decisions, prompt construction, or budgets.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class CandidateReviewProjectionBuilder:
    """Builds equal, deterministic candidate views for multi-candidate ranking."""

    def build(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        body = str(candidate.get("body") or "")
        paragraphs = [item.strip() for item in body.splitlines() if item.strip()]
        return {
            **self._select(candidate, ("id", "title", "rhetoricalPlanId")),
            "bodyExcerpt": body[:480],
            "bodyWindows": self._body_windows(body),
            "bodyChars": len(body),
            "paragraphCount": len(paragraphs),
            "usedEvidence": self._bounded_list(candidate.get("usedEvidence"), 6, 180),
            "ruleCoverage": self._bounded_list(candidate.get("ruleCoverage"), 6, 180),
            "risks": self._bounded_list(candidate.get("risks"), 2, 240),
            "weaknesses": self._bounded_list(candidate.get("weaknesses"), 2, 240),
        }

    def _body_windows(self, body: str) -> dict[str, str]:
        if len(body) <= 3000:
            return {"full": body}
        middle_start = max(0, (len(body) // 2) - 500)
        return {
            "opening": body[:1000],
            "middle": body[middle_start:middle_start + 1000],
            "ending": body[-1000:],
        }

    def _bounded_list(self, value: Any, limit: int, text_limit: int) -> list[Any]:
        if not isinstance(value, list):
            return []
        return [self._bounded(item, text_limit) for item in value[:limit]]

    def _bounded(self, value: Any, text_limit: int) -> Any:
        if isinstance(value, str):
            return value[:text_limit]
        if isinstance(value, Mapping):
            return {
                str(key): self._bounded(child, text_limit)
                for key, child in list(value.items())[:10]
            }
        return value

    def _select(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}


__all__ = ("CandidateReviewProjectionBuilder",)
