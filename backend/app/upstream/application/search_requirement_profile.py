"""Owner: upstream.application

Used by: SearchIntentPlanner before query allocation.
Does not own: provider execution, result scoring, project utility scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from hashlib import sha256
import re
from typing import Any

from backend.app.upstream.domain.search_requirements import (
    RadarSearchRequirementProfile,
    SearchApplicabilityDecision,
    SearchRequirement,
)


class RadarSearchRequirementProfileFactory:
    MAX_FILTERS = 24
    MAX_STATEMENT_CHARS = 320
    MAX_TERMS = 12
    MAX_TERM_CHARS = 48

    _SEARCH_DIMENSIONS: dict[str, tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]] = {
        "topics": (("caseExample", "broadDiscovery"), ("caseExample", "overview"), ()),
        "topicAffinity": (("caseExample", "broadDiscovery"), ("caseExample", "overview"), ()),
        "industrialContext": (("caseExample", "broadDiscovery"), ("caseExample", "overview"), ()),
        "mechanism": (("caseExample", "ossTooling"), ("caseExample", "ossTooling"), ("implementation", "workflow")),
        "observableOutcome": (("benchmarkPaper", "caseExample"), ("benchmarkPaper", "caseExample"), ("metrics", "results")),
        "result": (("benchmarkPaper", "caseExample"), ("benchmarkPaper", "caseExample"), ("metrics", "results")),
        "sourceCredibility": (("benchmarkPaper",), ("benchmarkPaper",), ("independent report", "study")),
        "evidenceStrength": (("benchmarkPaper", "caseExample"), ("benchmarkPaper", "caseExample"), ("evidence", "data")),
        "actionability": (("caseExample", "ossTooling"), ("caseExample", "ossTooling"), ("implementation", "practice")),
        "novelty": (("broadDiscovery", "freshness"), ("overview", "freshness"), ("recent", "new")),
        "freshness": (("freshness",), ("freshness",), ("recent", "2026")),
        "promotionalNoise": ((), (), ("pricing", "buy now", "promotion")),
        "genericAiNoise": ((), (), ("generic AI news", "model leaderboard")),
        "productiveTension": (("limitationCritique",), ("limitationCritique",), ("limitations", "failure modes", "critique")),
        "limitations": (("limitationCritique",), ("limitationCritique",), ("limitations", "failure modes")),
    }
    _SCORING_ONLY = {
        "author", "authorFit", "audience", "audienceValue", "positioning", "positioningContribution",
        "goals", "goalContribution", "forbiddenTopics", "style", "channel", "platform", "fabula",
    }
    _ROLE_BY_MODE = {
        "mustMatch": "required",
        "shouldMatch": "optional",
        "mustNotMatch": "exclusion",
        "seekTension": "tension",
    }
    _PRIORITY_BY_ROLE = {"required": 100, "tension": 55, "optional": 25, "exclusion": 0}

    def build(self, radar: dict[str, Any]) -> RadarSearchRequirementProfile:
        filters = [
            item for item in radar.get("filters", [])
            if isinstance(item, dict) and item.get("enabled", True)
        ]
        requirements: list[SearchRequirement] = []
        not_applicable: list[SearchApplicabilityDecision] = []
        trimmed = max(0, len(filters) - self.MAX_FILTERS)
        for index, item in enumerate(filters[: self.MAX_FILTERS]):
            filter_id = str(item.get("id") or self._stable_filter_id(radar, item, index))
            dimension = str(item.get("dimension") or "unknown")
            mode = str(item.get("mode") or "shouldMatch")
            mapping = self._SEARCH_DIMENSIONS.get(dimension)
            if mapping is None:
                reason = "project-setting-is-scoring-only" if dimension in self._SCORING_ONLY else "dimension-has-no-search-evidence-contract"
                not_applicable.append(SearchApplicabilityDecision(filter_id, dimension, mode, reason))
                continue
            role = self._ROLE_BY_MODE.get(mode, "optional")
            families, evidence_types, default_terms = mapping
            statement = self._bounded(str(item.get("instruction") or item.get("statement") or item.get("title") or dimension))
            requirements.append(
                SearchRequirement(
                    id=f"search-requirement-{filter_id}",
                    filter_id=filter_id,
                    dimension=dimension,
                    mode=mode,
                    role=role,
                    title=str(item.get("title") or self._title(dimension)),
                    statement=statement,
                    priority=self._PRIORITY_BY_ROLE[role],
                    query_families=families,
                    evidence_types=evidence_types,
                    terms=self._terms(statement, default_terms),
                    source_hints=tuple(str(value)[:80] for value in item.get("sourceHints", [])[:4] if value),
                )
            )

        if not filters:
            statement = self._bounded(str(radar.get("scope") or radar.get("title") or "Radar scope"))
            requirements.append(
                SearchRequirement(
                    id=f"search-requirement-{radar.get('id', 'radar')}-scope",
                    filter_id=f"{radar.get('id', 'radar')}-scope",
                    dimension="topics",
                    mode="mustMatch",
                    role="required",
                    title="Область радара",
                    statement=statement,
                    priority=100,
                    query_families=("caseExample", "broadDiscovery"),
                    evidence_types=("caseExample", "overview"),
                    terms=self._terms(statement, ()),
                )
            )

        requirements.sort(key=lambda item: (-item.priority, item.filter_id, item.id))
        return RadarSearchRequirementProfile(
            radar_id=str(radar.get("id") or ""),
            requirements=tuple(requirements),
            not_search_applicable=tuple(sorted(not_applicable, key=lambda item: item.filter_id)),
            retained_counts={"filters": min(len(filters), self.MAX_FILTERS), "requirements": len(requirements)},
            trimmed_counts={"filters": trimmed},
        )

    def _stable_filter_id(self, radar: dict[str, Any], item: dict[str, Any], index: int) -> str:
        seed = f"{radar.get('id')}|{item.get('dimension')}|{item.get('mode')}|{item.get('instruction')}|{index}"
        return sha256(seed.encode("utf-8")).hexdigest()[:12]

    def _bounded(self, value: str) -> str:
        return " ".join(value.split())[: self.MAX_STATEMENT_CHARS].rstrip()

    def _terms(self, statement: str, defaults: tuple[str, ...]) -> tuple[str, ...]:
        words = re.findall(r"[\w-]{3,}", statement, flags=re.UNICODE)
        ignored = {"signal", "must", "should", "сигнал", "должен", "нужно", "быть", "для", "или"}
        values = [*defaults, *(word for word in words if word.casefold() not in ignored)]
        return tuple(dict.fromkeys(value[: self.MAX_TERM_CHARS] for value in values if value))[: self.MAX_TERMS]

    def _title(self, dimension: str) -> str:
        return {
            "topics": "Тематика",
            "mechanism": "Механизм внедрения",
            "observableOutcome": "Наблюдаемый результат",
            "sourceCredibility": "Надёжность источника",
            "actionability": "Практическая применимость",
            "novelty": "Новизна",
            "promotionalNoise": "Рекламный шум",
            "productiveTension": "Продуктивное противоречие",
        }.get(dimension, dimension)


__all__ = ("RadarSearchRequirementProfileFactory",)
