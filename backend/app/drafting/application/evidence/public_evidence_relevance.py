"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import re
from dataclasses import dataclass
from typing import Protocol

from backend.app.drafting.application.evidence.public_evidence_ports import PublicEvidenceSearchTask


class CitationLike(Protocol):
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class CitationRelevanceResult:
    accepted: list[CitationLike]
    rejected: list[dict[str, str]]








_STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "как", "для", "или", "где",
    "что", "это", "его", "при", "над", "под", "без", "про", "тема", "найти",
    "проверить", "публичные", "источники", "минимум", "данные",
}


class PublicEvidenceRelevancePolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def filter_relevant_citations(
        citations: list[CitationLike],
        *,
        task: PublicEvidenceSearchTask,
    ) -> CitationRelevanceResult:
        query_terms = _terms(" ".join([task.query, task.instruction]))
        accepted: list[OpenRouterWebSearchCitation] = []
        rejected: list[dict[str, str]] = []
        for citation in citations:
            text = " ".join([citation.title, citation.snippet, citation.url])
            overlap = sorted(query_terms.intersection(_terms(text)))
            if _is_relevant(overlap, text, task.query):
                accepted.append(citation)
            else:
                rejected.append({
                    "title": citation.title,
                    "url": citation.url,
                    "reason": "search-result-drift",
                    "matchedTerms": ", ".join(overlap),
                })
        return CitationRelevanceResult(accepted=accepted, rejected=rejected)

    @staticmethod
    def _is_relevant(overlap: list[str], text: str, query: str) -> bool:
        if len(overlap) >= 2:
            return True
        lowered_text = text.lower()
        lowered_query = query.lower()
        return "ai" in lowered_query and ("ai" in lowered_text or "artificial intelligence" in lowered_text)

    @staticmethod
    def _terms(value: str) -> set[str]:
        return {
            term
            for term in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9][a-zA-Zа-яА-ЯёЁ0-9-]{2,}", value.lower())
            if term not in _STOPWORDS and not term.startswith("target-")
        }

filter_relevant_citations = PublicEvidenceRelevancePolicy.filter_relevant_citations
_is_relevant = PublicEvidenceRelevancePolicy._is_relevant
_terms = PublicEvidenceRelevancePolicy._terms


__all__ = (
    'CitationLike',
    'CitationRelevanceResult',
    'filter_relevant_citations',
    'PublicEvidenceRelevancePolicy',
)
