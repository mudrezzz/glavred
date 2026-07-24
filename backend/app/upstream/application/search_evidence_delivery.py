"""Owner: upstream.application

Used by: post-scoring search opportunity coverage reporting.
Does not own: search planning, read allocation, utility scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.search_opportunity import SearchRequirementCoverage


class SearchEvidenceDeliveryPolicy:
    REVIEW_ELIGIBLE = {"recommended", "reviewWithCaution"}
    _STAGES = (
        "planned",
        "queryExecuted",
        "resultFound",
        "selectedForRead",
        "readableEvidence",
        "usedBySignal",
        "corroborated",
    )

    def build(
        self,
        *,
        run: dict[str, Any],
        requirements: dict[str, dict[str, Any]],
        queries: dict[str, dict[str, Any]],
        executed_query_ids: set[str],
        found_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]],
    ) -> tuple[SearchRequirementCoverage, ...]:
        raw_results = [item for item in run.get("rawResults", []) if isinstance(item, dict)]
        read_plan = (
            (run.get("searchTriage") or {}).get("readPlan") or {}
            if isinstance(run.get("searchTriage"), dict)
            else {}
        )
        decisions = [item for item in read_plan.get("decisions", []) if isinstance(item, dict)]
        result: list[SearchRequirementCoverage] = []
        for requirement_id, requirement in requirements.items():
            query_ids = tuple(
                query_id
                for query_id, query in queries.items()
                if requirement_id in query.get("requirementIds", [])
            )
            executed = tuple(item for item in query_ids if item in executed_query_ids)
            raw = [
                item for item in raw_results
                if requirement_id in self._ids(item, "discoveredRequirementIds", "requirementIds")
            ]
            supported_raw = [
                item for item in raw_results
                if requirement_id in self._ids(item, "supportedRequirementIds", "requirementIds")
            ]
            selected = [
                item for item in decisions
                if item.get("status") == "selected"
                and requirement_id in self._ids(item, "supportedRequirementIds", "requirementIds")
            ]
            selected_raw_ids = {str(item.get("rawResultId") or "") for item in selected}
            materials = [
                item for item in found_materials
                if item.get("status") != "metadataOnly"
                and requirement_id in self._ids(
                    item.get("discoveryTrace") or {},
                    "supportedRequirementIds",
                    "requirementIds",
                )
                and selected_raw_ids.intersection(
                    str(raw_id) for raw_id in (item.get("discoveryTrace") or {}).get("rawResultIds", [])
                )
            ]
            material_ids = {str(item.get("id") or "") for item in materials}
            used_signals = [
                item for item in source_signals
                if str((item.get("utilityReport") or {}).get("recommendation") or "") in self.REVIEW_ELIGIBLE
                and material_ids.intersection(
                    str(ref.get("materialId") or "")
                    for ref in item.get("evidenceRefs", [])
                    if isinstance(ref, dict)
                )
            ]
            fragment_ids = tuple(dict.fromkeys(
                str(ref.get("fragmentId") or "")
                for signal in used_signals
                for ref in signal.get("evidenceRefs", [])
                if isinstance(ref, dict)
                and str(ref.get("materialId") or "") in material_ids
                and ref.get("fragmentId")
            ))
            corroborating_material_ids = tuple(dict.fromkeys(
                material_id
                for signal in used_signals
                if self._claim_support(signal) == "corroborated"
                for material_id in (
                    str(ref.get("materialId") or "")
                    for ref in signal.get("evidenceRefs", [])
                    if isinstance(ref, dict)
                )
                if material_id
            ))
            stage = self._stage(
                executed=bool(executed),
                raw=bool(raw),
                selected=bool(selected),
                readable=bool(materials),
                used=bool(used_signals),
                corroborated=bool(corroborating_material_ids),
            )
            role = str(requirement.get("role") or "optional")
            delivered = bool(used_signals)
            result.append(
                SearchRequirementCoverage(
                    requirement_id=requirement_id,
                    role=role,
                    mode=str(requirement.get("mode") or "shouldMatch"),
                    title=str(requirement.get("title") or requirement_id),
                    furthest_stage=stage,
                    delivered=delivered,
                    stop_reason=self._stop_reason(
                        stage=stage,
                        requirement=requirement,
                        decisions=decisions,
                        supported_raw=bool(supported_raw),
                    ),
                    query_ids=query_ids,
                    raw_result_ids=tuple(str(item.get("id") or "") for item in raw),
                    supported_raw_result_ids=tuple(str(item.get("id") or "") for item in supported_raw),
                    read_decision_raw_result_ids=tuple(
                        str(item.get("rawResultId") or "") for item in selected
                    ),
                    material_ids=tuple(sorted(material_ids)),
                    fragment_ids=fragment_ids,
                    signal_ids=tuple(str(item.get("id") or "") for item in used_signals),
                    corroborating_material_ids=corroborating_material_ids,
                )
            )
        return tuple(result)

    def _ids(self, payload: dict[str, Any], primary: str, legacy: str) -> set[str]:
        values = payload.get(primary) if primary in payload else payload.get(legacy)
        return {str(item) for item in values or [] if item}

    def _claim_support(self, signal: dict[str, Any]) -> str:
        checks = (signal.get("utilityReport") or {}).get("qualityChecks") or []
        source = next(
            (item for item in checks if isinstance(item, dict) and item.get("checkId") == "source-posture"),
            {},
        )
        return str((source.get("details") or {}).get("claimSupport") or "")

    def _stage(
        self,
        *,
        executed: bool,
        raw: bool,
        selected: bool,
        readable: bool,
        used: bool,
        corroborated: bool,
    ) -> str:
        flags = (True, executed, raw, selected, readable, used, corroborated)
        return self._STAGES[max(index for index, value in enumerate(flags) if value)]

    def _stop_reason(
        self,
        *,
        stage: str,
        requirement: dict[str, Any],
        decisions: list[dict[str, Any]],
        supported_raw: bool,
    ) -> str | None:
        if stage == "corroborated":
            return None
        if stage == "planned":
            return "provider-search-not-executed"
        if stage == "queryExecuted":
            return "no-result-found"
        if stage == "resultFound" and not supported_raw:
            return "evidence-target-not-supported"
        if stage == "resultFound":
            reasons = [
                str(item.get("reason") or "")
                for item in decisions
                if item.get("status") != "selected"
                and set(self._ids(item, "supportedRequirementIds", "requirementIds"))
                & {str(requirement.get("id") or "")}
            ]
            return next(
                (item for item in ("below-quality-floor", "url-read-budget", "unsupported-read-format") if item in reasons),
                "not-selected-for-read",
            )
        if stage == "selectedForRead":
            return "read-failed"
        if stage == "readableEvidence":
            return "evidence-not-used-by-review-eligible-signal"
        if stage == "usedBySignal" and str(requirement.get("dimension") or "") == "sourceCredibility":
            return "corroboration-not-found"
        return None


__all__ = ("SearchEvidenceDeliveryPolicy",)
