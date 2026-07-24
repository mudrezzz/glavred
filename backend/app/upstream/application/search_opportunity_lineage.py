"""Owner: upstream.application

Used by: search opportunity reporting to resolve persisted evidence lineage.
Does not own: opportunity status, search execution, scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter
from typing import Any


class SearchOpportunityLineageBuilder:
    def build(
        self,
        *,
        run: dict[str, Any],
        requirements: dict[str, dict[str, Any]],
        queries: dict[str, dict[str, Any]],
        raw_results: list[dict[str, Any]],
        found_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, int]]:
        raw_by_id = {str(item.get("id")): item for item in raw_results if item.get("id")}
        read_plan = (
            (run.get("searchTriage") or {}).get("readPlan") or {}
            if isinstance(run.get("searchTriage"), dict)
            else {}
        )
        selected_decisions = {
            str(item.get("rawResultId") or ""): item
            for item in read_plan.get("decisions", [])
            if isinstance(item, dict) and item.get("status") == "selected"
        }
        material_by_id = {str(item.get("id")): item for item in found_materials if item.get("id")}
        fragment_ids = {
            str(fragment.get("id"))
            for material in found_materials
            for fragment in material.get("contentFragments", [])
            if isinstance(fragment, dict) and fragment.get("id")
        }
        unresolved = Counter({
            "requirement": 0,
            "query": 0,
            "rawResult": 0,
            "readDecision": 0,
            "material": 0,
            "fragment": 0,
            "signal": 0,
        })
        lineage = [
            self._material_lineage(
                material,
                requirements=requirements,
                queries=queries,
                raw_by_id=raw_by_id,
                selected_decisions=selected_decisions,
                unresolved=unresolved,
            )
            for material in found_materials
        ]
        lineage.extend(
            self._signal_lineage(
                signal,
                material_by_id=material_by_id,
                fragment_ids=fragment_ids,
                unresolved=unresolved,
            )
            for signal in source_signals
        )
        return lineage, dict(unresolved)

    def _material_lineage(
        self,
        material: dict[str, Any],
        *,
        requirements: dict[str, dict[str, Any]],
        queries: dict[str, dict[str, Any]],
        raw_by_id: dict[str, dict[str, Any]],
        selected_decisions: dict[str, dict[str, Any]],
        unresolved: Counter,
    ) -> dict[str, Any]:
        trace = material.get("discoveryTrace") if isinstance(material.get("discoveryTrace"), dict) else {}
        discovered = self._ids(trace, "discoveredRequirementIds", "requirementIds")
        supported = self._ids(trace, "supportedRequirementIds", "requirementIds")
        query_ids = [str(item) for item in trace.get("queryIds", []) if item]
        raw_result_ids = [str(item) for item in trace.get("rawResultIds", []) if item]
        unresolved["requirement"] += sum(item not in requirements for item in {*discovered, *supported})
        unresolved["query"] += sum(item not in queries for item in query_ids)
        unresolved["rawResult"] += sum(item not in raw_by_id for item in raw_result_ids)
        unresolved["readDecision"] += int(
            bool(raw_result_ids) and not any(item in selected_decisions for item in raw_result_ids)
        )
        return {
            "kind": "material",
            "materialId": material.get("id"),
            "requirementIds": discovered,
            "discoveredRequirementIds": discovered,
            "supportedRequirementIds": supported,
            "queryIds": query_ids,
            "rawResultIds": raw_result_ids,
            "readDecisionRawResultIds": [
                item for item in raw_result_ids if item in selected_decisions
            ],
        }

    def _signal_lineage(
        self,
        signal: dict[str, Any],
        *,
        material_by_id: dict[str, dict[str, Any]],
        fragment_ids: set[str],
        unresolved: Counter,
    ) -> dict[str, Any]:
        refs = [item for item in signal.get("evidenceRefs", []) if isinstance(item, dict)]
        material_ids = [str(item.get("materialId")) for item in refs if item.get("materialId")]
        requirement_ids = sorted({
            requirement_id
            for material_id in material_ids
            for requirement_id in self._ids(
                material_by_id.get(material_id, {}).get("discoveryTrace") or {},
                "supportedRequirementIds",
                "requirementIds",
            )
        })
        unresolved["material"] += sum(item not in material_by_id for item in material_ids)
        unresolved["fragment"] += sum(
            str(item.get("fragmentId")) not in fragment_ids
            for item in refs
            if item.get("fragmentId")
        )
        return {
            "kind": "signal",
            "signalId": signal.get("id"),
            "requirementIds": requirement_ids,
            "materialIds": material_ids,
            "fragmentIds": [str(item.get("fragmentId")) for item in refs if item.get("fragmentId")],
            "recommendation": (signal.get("utilityReport") or {}).get("recommendation"),
        }

    def _ids(self, payload: dict[str, Any], primary: str, legacy: str) -> list[str]:
        values = payload.get(primary) if primary in payload else payload.get(legacy)
        return [str(item) for item in values or [] if item]


__all__ = ("SearchOpportunityLineageBuilder",)
