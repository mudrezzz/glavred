"""Owner: upstream.application

Used by: deterministic search triage before duplicate grouping and read allocation.
Does not own: provider search, result ranking, URL reading, or utility scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import replace
import re
from typing import Any

from backend.app.upstream.domain.search_result_contracts import SearchResultCandidate


class SearchEvidenceTargetFitPolicy:
    """Separates query discovery lineage from actual evidence suitability."""

    _BENCHMARK = {
        "benchmark", "research", "study", "paper", "report", "methodology", "dataset",
        "исследование", "отчет", "отчёт", "методология", "выборка",
    }
    _VENDOR = {
        "pricing", "request a demo", "our platform", "our solution", "customer story",
        "case study", "купить", "цены", "наша платформа", "наше решение",
    }
    _MECHANISM = {
        "implementation", "workflow", "architecture", "integration", "process",
        "внедрение", "процесс", "интеграция", "механизм", "архитектура",
    }
    _OUTCOME = {
        "result", "metric", "reduction", "increase", "downtime", "availability",
        "результат", "метрика", "снижение", "рост", "простой", "доступность",
    }

    def apply(
        self,
        candidates: list[SearchResultCandidate],
        *,
        search_plan: dict[str, Any],
    ) -> list[SearchResultCandidate]:
        profile = (
            search_plan.get("requirementProfile")
            if isinstance(search_plan.get("requirementProfile"), dict)
            else {}
        )
        requirements = {
            str(item.get("id")): item
            for item in profile.get("requirements", [])
            if isinstance(item, dict) and item.get("id")
        }
        return [
            replace(
                candidate,
                supported_requirement_ids=tuple(
                    requirement_id
                    for requirement_id in candidate.requirement_ids
                    if self._supports(candidate, requirements.get(requirement_id))
                ),
            )
            for candidate in candidates
        ]

    def _supports(
        self,
        candidate: SearchResultCandidate,
        requirement: dict[str, Any] | None,
    ) -> bool:
        if not requirement or requirement.get("role") == "exclusion":
            return False
        families = {str(item) for item in requirement.get("queryFamilies", []) if item}
        evidence_types = {str(item) for item in requirement.get("evidenceTypes", []) if item}
        if families and candidate.family not in families:
            return False
        if evidence_types and candidate.evidence_type not in evidence_types:
            return False

        dimension = str(requirement.get("dimension") or "")
        text = f"{candidate.title} {candidate.snippet}".casefold()
        if dimension == "sourceCredibility":
            return (
                candidate.family == "benchmarkPaper"
                and self._contains(text, self._BENCHMARK)
                and not self._contains(text, self._VENDOR)
            )
        if dimension in {"mechanism", "actionability"}:
            return self._contains(text, self._MECHANISM)
        if dimension in {"observableOutcome", "result", "evidenceStrength"}:
            return self._contains(text, self._OUTCOME) or bool(re.search(r"\b\d+(?:[.,]\d+)?%?\b", text))
        if dimension in {"productiveTension", "limitations"}:
            return any(token in text for token in ("risk", "limitation", "failure", "constraint", "риск", "огранич", "ошиб", "провал"))
        return True

    def _contains(self, text: str, terms: set[str]) -> bool:
        return any(term in text for term in terms)


__all__ = ("SearchEvidenceTargetFitPolicy",)
