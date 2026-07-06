"""Owner: upstream.application

Used by: SearchIntentPlanner to derive deterministic query families.
Does not own: provider transport, API routing, UI rendering, or signal scoring.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchQueryFamily:
    family: str
    intent_type: str
    evidence_type: str
    label: str
    suffix: str
    priority: int


class SearchQueryFamilyPolicy:
    def families(self, *, language: str, include_freshness: bool) -> list[SearchQueryFamily]:
        families = self._base_families(language)
        if include_freshness:
            families.append(self._freshness_family(language, priority=len(families) + 1))
        return families

    def _base_families(self, language: str) -> list[SearchQueryFamily]:
        if language == "ru":
            return [
                SearchQueryFamily("broadDiscovery", "broadDiscovery", "overview", "широкий поиск", "обзор практика тренды", 1),
                SearchQueryFamily("caseExample", "caseStudy", "caseExample", "кейсы и примеры", "кейс внедрения пример практика", 2),
                SearchQueryFamily("benchmarkPaper", "benchmark", "benchmarkPaper", "исследования и цифры", "исследование benchmark метрики результаты", 3),
                SearchQueryFamily("ossTooling", "tooling", "ossTooling", "инструменты и OSS", "github open source framework инструмент", 4),
                SearchQueryFamily("limitationCritique", "limitations", "limitationCritique", "ограничения и критика", "риски ограничения провал lessons learned", 5),
            ]
        return [
            SearchQueryFamily("broadDiscovery", "broadDiscovery", "overview", "broad discovery", "overview practice trends", 1),
            SearchQueryFamily("caseExample", "caseStudy", "caseExample", "case studies", "case study implementation example", 2),
            SearchQueryFamily("benchmarkPaper", "benchmark", "benchmarkPaper", "benchmarks and papers", "benchmark paper metrics results", 3),
            SearchQueryFamily("ossTooling", "tooling", "ossTooling", "tools and OSS", "github open source framework tool", 4),
            SearchQueryFamily("limitationCritique", "limitations", "limitationCritique", "limitations and critique", "risks limitations failure lessons learned", 5),
        ]

    def _freshness_family(self, language: str, *, priority: int) -> SearchQueryFamily:
        if language == "ru":
            return SearchQueryFamily("freshness", "freshness", "freshness", "свежие изменения", "2026 свежие данные новости обновления", priority)
        return SearchQueryFamily("freshness", "freshness", "freshness", "freshness", "2026 recent news updates", priority)


__all__ = ("SearchQueryFamily", "SearchQueryFamilyPolicy")
