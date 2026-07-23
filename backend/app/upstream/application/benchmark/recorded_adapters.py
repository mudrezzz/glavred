"""Owner: upstream.application

Used by: recorded upstream Radar benchmark runner.
Does not own: live provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_web_search_adapter import (
    OpenRouterWebSearchCitation,
    OpenRouterWebSearchResult,
)


class RecordedRadarFixture:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    @classmethod
    def load(cls, fixture_name: str) -> "RecordedRadarFixture":
        fixture = resources.files(__package__).joinpath("fixtures", fixture_name)
        return cls(json.loads(fixture.read_text(encoding="utf-8")))

    def citations_for_query(self, query: str) -> list[OpenRouterWebSearchCitation]:
        return self.citations_for_family(self._family_for_query(query))

    def citations_for_family(self, family: str) -> list[OpenRouterWebSearchCitation]:
        records = self._payload.get("searchResultsByFamily", {}).get(family, [])
        return [
            OpenRouterWebSearchCitation(
                title=str(item.get("title") or item.get("url") or ""),
                url=str(item.get("url") or ""),
                snippet=str(item.get("snippet") or ""),
            )
            for item in records
            if isinstance(item, dict)
        ]

    def read(self, url: str) -> PublicUrlReadResult:
        reads = self._payload.get("urlReads", {})
        record = reads.get(url) if isinstance(reads, dict) else None
        if not isinstance(record, dict):
            raise RuntimeError(f"Recorded fixture has no URL read for {url}")
        return PublicUrlReadResult(
            url=url,
            final_url=str(record.get("finalUrl") or url),
            title=str(record.get("title") or url),
            text=str(record.get("text") or ""),
        )

    def source_signals(
        self,
        *,
        run_id: str,
        radar_id: str,
        found_materials: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        records = self._payload.get("sourceSignals", [])
        result: list[dict[str, Any]] = []
        for index, item in enumerate(records):
            if not isinstance(item, dict) or not found_materials:
                continue
            material = found_materials[min(index, len(found_materials) - 1)]
            fragments = [fragment for fragment in material.get("contentFragments", []) if isinstance(fragment, dict)]
            if not fragments:
                continue
            result.append({
                "id": str(item.get("id") or f"recorded-signal-{index + 1}"),
                "radarRunId": run_id,
                "radarId": radar_id,
                "title": str(item.get("title") or f"Recorded signal {index + 1}"),
                "evidenceRefs": [{"materialId": material["id"], "fragmentId": fragments[0]["id"]}],
                "utilityReport": {"recommendation": str(item.get("recommendation") or "inconclusive")},
            })
        return result

    def _family_for_query(self, query: str) -> str:
        lower = query.lower()
        if "case study" in lower or "implementation example" in lower:
            return "caseExample"
        if "benchmark" in lower or "paper" in lower or "metrics" in lower:
            return "benchmarkPaper"
        if "risks" in lower or "limitations" in lower or "lessons learned" in lower:
            return "limitationCritique"
        if "github" in lower or "open source" in lower:
            return "ossTooling"
        return "broadDiscovery"


class RecordedRadarSearchAdapter:
    def __init__(self, fixture: RecordedRadarFixture) -> None:
        self._fixture = fixture

    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        query = str(kwargs.get("query") or "")
        family = self._family_for_call(query)
        citations = self._fixture.citations_for_family(family)
        return OpenRouterWebSearchResult(
            content=f"Recorded {family} search results for {query}",
            citations=citations,
            raw_response={"id": "recorded-search", "query": query, "family": family, "citationCount": len(citations)},
        )

    def _family_for_call(self, query: str) -> str:
        return self._fixture._family_for_query(query)


class RecordedUrlReader:
    def __init__(self, fixture: RecordedRadarFixture) -> None:
        self._fixture = fixture

    def read(self, url: str) -> PublicUrlReadResult:
        return self._fixture.read(url)


__all__ = ("RecordedRadarFixture", "RecordedRadarSearchAdapter", "RecordedUrlReader")
