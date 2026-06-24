import re
from dataclasses import dataclass
from typing import Protocol

from backend.app.application.public_evidence_ports import PublicEvidenceSearchTask


class CitationLike(Protocol):
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class CitationRelevanceResult:
    accepted: list[CitationLike]
    rejected: list[dict[str, str]]


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


def _is_relevant(overlap: list[str], text: str, query: str) -> bool:
    if len(overlap) >= 2:
        return True
    lowered_text = text.lower()
    lowered_query = query.lower()
    return "ai" in lowered_query and ("ai" in lowered_text or "artificial intelligence" in lowered_text)


def _terms(value: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9][a-zA-Zа-яА-ЯёЁ0-9-]{2,}", value.lower())
        if term not in _STOPWORDS and not term.startswith("target-")
    }


_STOPWORDS = {
    "the", "and", "for", "with", "from", "this", "that", "как", "для", "или", "где",
    "что", "это", "его", "при", "над", "под", "без", "про", "тема", "найти",
    "проверить", "публичные", "источники", "минимум", "данные",
}
