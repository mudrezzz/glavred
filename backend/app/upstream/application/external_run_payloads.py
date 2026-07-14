"""Owner: upstream.application

Used by: RadarRun search/read operation runners and external run orchestration.
Does not own: provider transport, triage decisions, budgets, persistence, or DraftRun.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.upstream.application.search_result_normalization import SearchResultNormalizer


class UpstreamRadarPayloadFactory:
    def __init__(self) -> None:
        self._normalizer = SearchResultNormalizer()

    def raw_result(self, run_id: str, query: dict[str, Any], citation: Any, index: int) -> dict[str, Any]:
        original_url = str(citation.url or "")
        url, invalid_reason = self._normalizer.canonical_url(original_url)
        title = self._normalizer.bounded_text(str(citation.title or url), self._normalizer.TITLE_LIMIT)
        snippet = self._normalizer.bounded_text(str(citation.snippet or ""), self._normalizer.SNIPPET_LIMIT)
        return {
            "id": f"{run_id}-raw-{query['id']}-{index + 1}",
            "sourceHandleId": query["sourceHandleId"],
            "queryId": query["id"],
            "intentId": query.get("intentId"),
            "family": query.get("family"),
            "evidenceType": query.get("evidenceType"),
            "query": self._normalizer.bounded_text(str(query.get("query") or ""), 1000),
            "title": title,
            "url": url,
            "snippet": snippet,
            "domain": self._normalizer.normalize(
                {"id": f"{run_id}-raw-{query['id']}-{index + 1}", "url": url, "title": title, "snippet": snippet},
                query=query,
            ).domain,
            "duplicateKey": url,
            "provider": "openrouter:web_search",
            **({"invalidReason": invalid_reason} if invalid_reason else {}),
        }

    def material_from_read(
        self,
        *,
        material_id: str,
        run_id: str,
        source_handle_id: str,
        title: str,
        read: PublicUrlReadResult,
        provenance: str,
        discovery_trace: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._material(
            material_id=material_id,
            run_id=run_id,
            source_handle_id=source_handle_id,
            title=read.title or title or read.url,
            locator=read.final_url or read.url,
            text=read.text,
            status="found",
            warnings=[],
            provenance=provenance,
            discovery_trace=discovery_trace,
        )

    def material_from_raw(
        self,
        *,
        material_id: str,
        run_id: str,
        raw: dict[str, Any],
        warning: str,
        discovery_trace: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._material(
            material_id=material_id,
            run_id=run_id,
            source_handle_id=str(raw["sourceHandleId"]),
            title=str(raw["title"]),
            locator=str(raw["url"]),
            text=str(raw.get("snippet") or ""),
            status="metadataOnly",
            warnings=[warning, "search-result-only"],
            provenance=f"{raw['provider']} / {raw['domain']}",
            discovery_trace=discovery_trace,
        )

    def operation(self, **values: Any) -> dict[str, Any]:
        payload = {
            "id": values["operation_id"],
            "runId": values["run_id"],
            "sourceHandleId": values["source_handle_id"],
            "kind": values["kind"],
            "label": values["label"],
            "status": values["status"],
            "startedAt": values["started_at"],
            "completedAt": self.now_iso() if values["status"] != "running" else None,
            "target": values["target"],
            "foundMaterialIds": values.get("found_material_ids") or [],
        }
        for source, target in (("skipped_reason", "skippedReason"), ("error", "error")):
            if values.get(source):
                payload[target] = values[source]
        if values.get("trace"):
            payload.update(values["trace"])
        return payload

    def warnings_for(self, raw_results: list[dict[str, Any]], materials: list[dict[str, Any]]) -> list[str]:
        if not raw_results:
            return ["no-raw-search-results"]
        if not materials or not any(item.get("status") != "metadataOnly" for item in materials):
            return ["no-readable-found-materials"]
        return []

    def safe_error(self, error: Exception) -> str:
        return f"{error.__class__.__name__}: {str(error)[:180]}"

    def stable_slug(self, value: str) -> str:
        return "".join(char if char.isalnum() else "-" for char in value.lower()).strip("-")[:64] or "item"

    def now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _material(self, **values: Any) -> dict[str, Any]:
        text = " ".join(str(values["text"]).split())
        payload = {
            "id": values["material_id"],
            "radarRunId": values["run_id"],
            "sourceHandleId": values["source_handle_id"],
            "type": "searchResult",
            "title": values["title"],
            "locator": values["locator"],
            "snippet": text[:360].rstrip(),
            "summary": text[:1200].rstrip(),
            "capturedAt": self.now_iso(),
            "status": values["status"],
            "warnings": values["warnings"],
            "provenanceLabel": values["provenance"],
        }
        if values.get("discovery_trace"):
            payload["discoveryTrace"] = values["discovery_trace"]
        return payload


_FACTORY = UpstreamRadarPayloadFactory()
raw_result = _FACTORY.raw_result
material_from_read = _FACTORY.material_from_read
material_from_raw = _FACTORY.material_from_raw
operation = _FACTORY.operation
warnings_for = _FACTORY.warnings_for
safe_error = _FACTORY.safe_error
stable_slug = _FACTORY.stable_slug
now_iso = _FACTORY.now_iso


__all__ = (
    "UpstreamRadarPayloadFactory",
    "material_from_raw",
    "material_from_read",
    "now_iso",
    "operation",
    "raw_result",
    "safe_error",
    "stable_slug",
    "warnings_for",
)
