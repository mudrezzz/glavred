"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService to build deterministic search-triage trace.
Does not own: provider search, URL reading, persistence, benchmark grading, or downstream signals.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from backend.app.upstream.application.radar_language_context import RadarLanguageContextFactory
from backend.app.upstream.application.search_duplicate_policy import SearchDuplicateGroupingPolicy
from backend.app.upstream.application.search_read_allocator import SearchReadBudgetAllocator
from backend.app.upstream.application.search_result_normalization import SearchResultNormalizer
from backend.app.upstream.application.search_result_scoring import SearchResultQualityPolicy
from backend.app.upstream.domain.search_triage_contracts import SearchTriageReport, SearchTriageResult
from backend.app.upstream.domain.radar_language import RadarLanguageContext, SourceLanguageAssessment


class SearchResultTriageService:
    POLICY_VERSION = "deterministic-search-triage-v2"

    def __init__(
        self,
        *,
        normalizer: SearchResultNormalizer | None = None,
        duplicate_policy: SearchDuplicateGroupingPolicy | None = None,
        quality_policy: SearchResultQualityPolicy | None = None,
        read_allocator: SearchReadBudgetAllocator | None = None,
        language_factory: RadarLanguageContextFactory | None = None,
    ) -> None:
        self._normalizer = normalizer or SearchResultNormalizer()
        self._duplicate_policy = duplicate_policy or SearchDuplicateGroupingPolicy()
        self._quality_policy = quality_policy or SearchResultQualityPolicy()
        self._read_allocator = read_allocator or SearchReadBudgetAllocator()
        self._language_factory = language_factory or RadarLanguageContextFactory()

    def triage(
        self,
        *,
        raw_results: list[dict[str, Any]],
        search_plan: dict[str, Any],
        workspace: dict[str, Any],
        radar: dict[str, Any],
        max_reads: int,
        language_context: RadarLanguageContext | None = None,
    ) -> SearchTriageResult:
        language_context = language_context or self._language_factory.build(
            project_context=None,
            workspace=workspace,
            radar=radar,
        )
        queries = {
            str(item.get("id")): item
            for item in search_plan.get("queries", [])
            if isinstance(item, dict) and item.get("id")
        }
        normalized = [
            self._normalizer.normalize(raw, query=queries.get(str(raw.get("queryId"))))
            for raw in raw_results
        ]
        candidates = [self._apply_language_policy(item, language_context) for item in normalized]
        project_context = self._project_context(workspace=workspace, radar=radar)
        scores = {
            candidate.id: self._quality_policy.assess(candidate, project_context=project_context)
            for candidate in candidates
        }
        duplicate_groups = self._duplicate_policy.group(candidates, scores)
        required_families = self._required_families(search_plan)
        required_requirement_ids = self._required_requirement_ids(search_plan)
        read_plan = self._read_allocator.allocate(
            candidates=candidates,
            scores=scores,
            duplicate_groups=duplicate_groups,
            max_reads=max_reads,
            required_families=required_families,
            required_requirement_ids=required_requirement_ids,
        )
        report = SearchTriageReport(
            policy_version=self.POLICY_VERSION,
            candidates=tuple(candidates),
            scores=scores,
            duplicate_groups=tuple(duplicate_groups),
            read_plan=read_plan,
            decision_counts=self._read_allocator.decision_counts(read_plan),
            language_context=language_context.to_payload(),
        )
        candidate_by_raw = {item.raw_result_id: item for item in candidates}
        score_by_raw = {item.raw_result_id: scores[item.id] for item in candidates}
        group_by_raw = {
            raw_id: group
            for group in duplicate_groups
            for raw_id in group.raw_result_ids
        }
        enriched_raw = tuple(
            {
                **raw,
                "title": candidate_by_raw[str(raw.get("id"))].title,
                "url": candidate_by_raw[str(raw.get("id"))].canonical_url or candidate_by_raw[str(raw.get("id"))].url,
                "snippet": candidate_by_raw[str(raw.get("id"))].snippet,
                "domain": candidate_by_raw[str(raw.get("id"))].domain,
                "duplicateKey": candidate_by_raw[str(raw.get("id"))].canonical_url,
                "candidateId": candidate_by_raw[str(raw.get("id"))].id,
                "duplicateGroupId": group_by_raw.get(str(raw.get("id"))).id if group_by_raw.get(str(raw.get("id"))) else None,
                "score": score_by_raw[str(raw.get("id"))].total,
                "dimensionScores": score_by_raw[str(raw.get("id"))].to_payload(),
                "sourceLanguage": candidate_by_raw[str(raw.get("id"))].to_payload()["sourceLanguage"],
                "requirementIds": list(candidate_by_raw[str(raw.get("id"))].requirement_ids),
            }
            for raw in raw_results
        )
        decisions = [item.to_payload() for item in read_plan.decisions]
        selected_order = {
            candidate_id: index for index, candidate_id in enumerate(read_plan.selected_candidate_ids)
        }
        selected = tuple(
            sorted(
                (item for item in decisions if item["status"] == "selected"),
                key=lambda item: selected_order[str(item["candidateId"])],
            )
        )
        rejected = tuple(item for item in decisions if item["status"] != "selected")
        return SearchTriageResult(
            report=report,
            raw_results=enriched_raw,
            selected_for_read=selected,
            rejected_before_read=rejected,
        )

    def _apply_language_policy(self, candidate, context: RadarLanguageContext):
        assessment = SourceLanguageAssessment(
            language=candidate.source_language,
            confidence=candidate.source_language_confidence,
            mixed=candidate.source_language_mixed,
            reason_codes=candidate.source_language_reason_codes,
        )
        allowed, reason = context.allows(assessment)
        return replace(
            candidate,
            source_language_allowed=allowed,
            source_language_eligibility_reason=reason,
        )

    def _required_families(self, search_plan: dict[str, Any]) -> list[str]:
        required_ids = set(self._required_requirement_ids(search_plan))
        intents = [
            item for item in search_plan.get("intents", [])
            if isinstance(item, dict) and (not required_ids or required_ids.intersection(item.get("requirementIds") or []))
        ]
        ordered = sorted(intents, key=lambda item: (int(item.get("priority") or 999), str(item.get("family") or "")))
        families = [str(item.get("family") or "") for item in ordered]
        if not families:
            families = [
                str(item.get("family") or "")
                for item in search_plan.get("queries", [])
                if isinstance(item, dict)
            ]
        return list(dict.fromkeys(item for item in families if item))

    def _required_requirement_ids(self, search_plan: dict[str, Any]) -> list[str]:
        profile = search_plan.get("requirementProfile") if isinstance(search_plan.get("requirementProfile"), dict) else {}
        return [
            str(item.get("id"))
            for item in profile.get("requirements", [])
            if isinstance(item, dict) and item.get("role") == "required" and item.get("id")
        ]

    def _project_context(self, *, workspace: dict[str, Any], radar: dict[str, Any]) -> str:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        values = [
            profile.get("name"),
            profile.get("description"),
            radar.get("title"),
            radar.get("scope"),
        ]
        values.extend(
            item.get("statement")
            for item in radar.get("rules", [])
            if isinstance(item, dict)
        )
        values.extend(
            item.get("title")
            for key in ("topics", "fabulas")
            for item in workspace.get(key, [])
            if isinstance(item, dict)
        )
        return " ".join(str(item) for item in values if item)[:6000]


__all__ = ("SearchResultTriageService",)
