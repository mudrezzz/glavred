"""Owner: upstream.application

Used by: RadarRun triage before allocating the bounded URL-read budget.
Does not own: URL fetching, document parsing, scoring, persistence, or provider calls.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from urllib.parse import urlsplit

from backend.app.upstream.domain.search_triage_contracts import SearchResultCandidate


class SearchResultReadabilityPolicy:
    _UNSUPPORTED_SUFFIXES = (".pdf",)

    def can_read(self, candidate: SearchResultCandidate) -> bool:
        path = urlsplit(candidate.url).path.casefold()
        return not path.endswith(self._UNSUPPORTED_SUFFIXES)

    def rejection_reason(self, candidate: SearchResultCandidate) -> str | None:
        return None if self.can_read(candidate) else "unsupported-read-format"


__all__ = ("SearchResultReadabilityPolicy",)
