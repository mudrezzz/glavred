"""Owner: upstream.application

Used by: upstream radar external run service.
Does not own: API routing, SQLite persistence, provider transport, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from urllib.parse import urlparse


class UpstreamSearchTriagePolicy:
    def canonical_url(self, url: str) -> str:
        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower().removeprefix("www.")
        path = parsed.path.rstrip("/")
        return f"{scheme}://{netloc}{path}"

    def result_domain(self, url: str) -> str:
        return urlparse(self.canonical_url(url)).netloc

    def score_search_result(self, *, title: str, snippet: str, query: str) -> int:
        haystack = f"{title} {snippet}".lower()
        query_terms = {term for term in query.lower().split() if len(term) > 3}
        score = sum(1 for term in query_terms if term in haystack)
        score += self._keyword_bonus(
            haystack,
            {"case", "кейс", "example", "пример", "implementation", "внедрение"},
        )
        score += self._keyword_bonus(
            haystack,
            {"benchmark", "paper", "study", "исследование", "метрики", "github"},
        )
        score -= self._keyword_bonus(
            haystack,
            {"buy now", "pricing", "лучшее решение", "закажите", "vendor"},
        )
        return max(0, score)

    def select_results_for_read(
        self, raw_results: list[dict], max_reads: int
    ) -> tuple[list[dict], list[dict]]:
        selected: list[dict] = []
        rejected: list[dict] = []
        seen_keys: set[str] = set()
        seen_domains: set[str] = set()
        for result in sorted(raw_results, key=lambda item: int(item.get("score") or 0), reverse=True):
            key = str(result.get("duplicateKey") or result.get("url") or "")
            domain = str(result.get("domain") or "")
            if key in seen_keys:
                rejected.append(self._decision(result, "duplicate-url"))
                continue
            seen_keys.add(key)
            if len(selected) >= max_reads:
                rejected.append(self._decision(result, "url-read-budget"))
                continue
            if domain in seen_domains and len(selected) > 0:
                rejected.append(self._decision(result, "domain-diversity"))
                continue
            seen_domains.add(domain)
            selected.append(self._decision(result, "best-diverse-result"))
        return selected, rejected

    def _decision(self, result: dict, reason: str) -> dict:
        return {
            "rawResultId": result.get("id"),
            "url": result.get("url"),
            "reason": reason,
            "score": result.get("score", 0),
        }

    def _keyword_bonus(self, haystack: str, keywords: set[str]) -> int:
        return sum(1 for keyword in keywords if keyword in haystack)


_TRIAGE = UpstreamSearchTriagePolicy()


def canonical_url(url: str) -> str:
    return _TRIAGE.canonical_url(url)


def result_domain(url: str) -> str:
    return _TRIAGE.result_domain(url)


def score_search_result(*, title: str, snippet: str, query: str) -> int:
    return _TRIAGE.score_search_result(title=title, snippet=snippet, query=query)


def select_results_for_read(raw_results: list[dict], max_reads: int) -> tuple[list[dict], list[dict]]:
    return _TRIAGE.select_results_for_read(raw_results, max_reads)


__all__ = (
    "UpstreamSearchTriagePolicy",
    "canonical_url",
    "result_domain",
    "score_search_result",
    "select_results_for_read",
)
