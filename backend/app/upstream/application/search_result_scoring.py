"""Owner: upstream.application

Used by: deterministic RadarRun triage to assess normalized search results.
Does not own: provider calls, duplicate grouping, read execution, persistence, or editorial approval.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import re

from backend.app.upstream.domain.search_triage_contracts import (
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchResultQualityPolicy:
    QUALITY_FLOOR = 45
    _CASE_TERMS = {
        "case", "study", "implementation", "implemented", "deployment", "example",
        "кейс", "внедрение", "пример", "эксплуатация",
    }
    _PAPER_TERMS = {
        "benchmark", "paper", "study", "research", "metrics", "results", "doi",
        "исследование", "метрики", "результаты", "отчет", "отчёт",
    }
    _LIMITATION_TERMS = {
        "risk", "risks", "limitation", "limitations", "failure", "failed", "lessons",
        "constraint", "constraints", "риск", "ограничение", "ошибка", "провал",
    }
    _TOOLING_TERMS = {"github", "open source", "framework", "tool", "library", "oss"}
    _INDUSTRIAL_TERMS = {
        "industrial", "maintenance", "asset", "reliability", "manufacturing", "eam",
        "тоир", "оборудование", "надежность", "надёжность", "производство",
    }
    _NOISE_TERMS = {
        "buy now", "pricing", "price list", "vendor pricing", "request a demo",
        "generic ai news", "model leaderboard", "sponsored", "заказать", "цены",
        "прайс", "купить",
    }
    _PROMOTIONAL_TERMS = {"leading", "best solution", "revolutionary", "game-changing", "industry-leading"}
    _STOP_WORDS = {
        "with", "from", "that", "this", "into", "find", "public", "source", "material",
        "для", "или", "как", "это", "где", "есть", "найти", "искать",
    }

    def assess(
        self,
        candidate: SearchResultCandidate,
        *,
        project_context: str,
    ) -> SearchResultDimensionScores:
        if not candidate.valid:
            return SearchResultDimensionScores(0, 0, 0, 0, 0, 100, 0, (candidate.invalid_reason or "invalid",), "Результат не содержит допустимый URL.")

        haystack = f"{candidate.title} {candidate.snippet}".casefold()
        haystack_terms = self._terms(haystack)
        query_terms = self._terms(candidate.query) - self._STOP_WORDS
        project_terms = self._terms(project_context) - self._STOP_WORDS
        query_overlap = len(query_terms & haystack_terms)
        project_overlap = len(project_terms & haystack_terms)
        reasons: list[str] = []

        relevance = self._bounded(35 + min(query_overlap, 6) * 10)
        if query_overlap:
            reasons.append("query-term-match")

        family_terms = self._family_terms(candidate.family)
        family_matches = self._phrase_matches(haystack, family_terms)
        evidence_fit = self._bounded(35 + min(family_matches, 4) * 15)
        if family_matches:
            reasons.append("evidence-family-match")

        industrial_matches = self._phrase_matches(haystack, self._INDUSTRIAL_TERMS)
        project_fit = self._bounded(30 + min(project_overlap, 4) * 8 + min(industrial_matches, 3) * 12)
        if industrial_matches:
            reasons.append("industrial-context")

        source_quality = 50
        if candidate.url.startswith("https://"):
            source_quality += 5
        if any(marker in candidate.domain for marker in (".gov", ".edu", "doi.org", "github.com")):
            source_quality += 25
            reasons.append("strong-source-signal")
        if any(marker in haystack for marker in ("methodology", "dataset", "references", "методология", "данные")):
            source_quality += 10
        source_quality = self._bounded(source_quality)

        detail_signals = sum(
            bool(re.search(pattern, haystack))
            for pattern in (r"\b\d+(?:[.,]\d+)?%", r"\b\d{4}\b", r"\bweek", r"\bmonth", r"\bmetric", r"\bdata")
        )
        novelty = self._bounded(45 + min(detail_signals, 4) * 10 + (5 if len(candidate.snippet) >= 240 else 0))
        if detail_signals:
            reasons.append("specific-detail")

        noise_hits = self._phrase_matches(haystack, self._NOISE_TERMS)
        promotional_hits = self._phrase_matches(haystack, self._PROMOTIONAL_TERMS)
        noise_risk = self._bounded(noise_hits * 35 + promotional_hits * 12)
        if noise_hits:
            reasons.append("known-noise")
        elif promotional_hits:
            reasons.append("promotional-language")

        weighted = (
            0.30 * relevance
            + 0.20 * evidence_fit
            + 0.20 * project_fit
            + 0.15 * source_quality
            + 0.15 * novelty
        )
        noise_penalty = min(30, round(noise_risk * 0.30))
        total = self._bounded(round(weighted) - noise_penalty)
        explanation = self._explanation(candidate, total, reasons)
        return SearchResultDimensionScores(
            relevance=relevance,
            evidence_fit=evidence_fit,
            project_fit=project_fit,
            source_quality=source_quality,
            novelty=novelty,
            noise_risk=noise_risk,
            total=total,
            reason_codes=tuple(reasons or ["neutral-signals"]),
            explanation=explanation,
        )

    def _family_terms(self, family: str) -> set[str]:
        return {
            "caseExample": self._CASE_TERMS,
            "benchmarkPaper": self._PAPER_TERMS,
            "limitationCritique": self._LIMITATION_TERMS,
            "ossTooling": self._TOOLING_TERMS,
            "freshness": {"2026", "recent", "latest", "свежие", "обновление"},
            "broadDiscovery": self._INDUSTRIAL_TERMS,
        }.get(family, self._INDUSTRIAL_TERMS)

    def _terms(self, value: str) -> set[str]:
        return {term for term in re.findall(r"[\w]+", value.casefold(), flags=re.UNICODE) if len(term) > 2}

    def _phrase_matches(self, haystack: str, terms: set[str]) -> int:
        return sum(1 for term in terms if term in haystack)

    def _bounded(self, value: int) -> int:
        return max(0, min(100, value))

    def _explanation(self, candidate: SearchResultCandidate, total: int, reasons: list[str]) -> str:
        reason_text = ", ".join(reasons or ["нейтральные сигналы"])
        return f"{candidate.family}: итог {total}; сигналы: {reason_text}."[:320]


__all__ = ("SearchResultQualityPolicy",)
