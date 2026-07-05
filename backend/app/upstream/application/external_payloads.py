"""Owner: upstream.application

Used by: upstream radar external run service.
Does not own: API routing, SQLite persistence, provider transport, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.upstream.application.search_triage import (
    canonical_url,
    result_domain,
    score_search_result,
)


class UpstreamRadarPayloadFactory:
    def budget_for_mode(self, mode: str) -> dict[str, int]:
        base = {
            "maxOperations": 10,
            "maxInternalItems": 0,
            "maxExternalQueries": 3,
            "maxUrlReads": 2,
            "maxFoundMaterials": 2,
        }
        if mode == "smoke":
            base.update(
                {
                    "maxOperations": 4,
                    "maxExternalQueries": 1,
                    "maxUrlReads": 1,
                    "maxFoundMaterials": 1,
                }
            )
        elif mode == "full":
            base.update(
                {
                    "maxOperations": 16,
                    "maxExternalQueries": 5,
                    "maxUrlReads": 4,
                    "maxFoundMaterials": 4,
                }
            )
        return {
            **base,
            "usedOperations": 0,
            "usedInternalItems": 0,
            "usedExternalQueries": 0,
            "usedUrlReads": 0,
            "usedFoundMaterials": 0,
        }

    def raw_result(self, run_id: str, query: dict[str, Any], citation: Any, index: int) -> dict[str, Any]:
        url = canonical_url(str(citation.url))
        return {
            "id": f"{run_id}-raw-{query['id']}-{index + 1}",
            "sourceHandleId": query["sourceHandleId"],
            "queryId": query["id"],
            "title": citation.title or url,
            "url": url,
            "snippet": citation.snippet or "",
            "domain": result_domain(url),
            "score": score_search_result(
                title=citation.title or "",
                snippet=citation.snippet or "",
                query=query["query"],
            ),
            "duplicateKey": url,
            "provider": "openrouter:web_search",
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
    ) -> dict[str, Any]:
        return {
            "id": material_id,
            "radarRunId": run_id,
            "sourceHandleId": source_handle_id,
            "type": "searchResult",
            "title": read.title or title or read.url,
            "locator": read.final_url or read.url,
            "snippet": self.truncate(read.text, 360),
            "summary": self.truncate(read.text, 1200),
            "capturedAt": self.now_iso(),
            "status": "found",
            "warnings": [],
            "provenanceLabel": provenance,
        }

    def material_from_raw(
        self,
        *,
        material_id: str,
        run_id: str,
        raw: dict[str, Any],
        warning: str,
    ) -> dict[str, Any]:
        return {
            "id": material_id,
            "radarRunId": run_id,
            "sourceHandleId": raw["sourceHandleId"],
            "type": "searchResult",
            "title": raw["title"],
            "locator": raw["url"],
            "snippet": self.truncate(raw["snippet"], 360),
            "summary": self.truncate(raw["snippet"], 1200),
            "capturedAt": self.now_iso(),
            "status": "found",
            "warnings": [warning, "search-result-only"],
            "provenanceLabel": f"{raw['provider']} / {raw['domain']}",
        }

    def operation(
        self,
        *,
        operation_id: str,
        run_id: str,
        source_handle_id: str,
        kind: str,
        label: str,
        status: str,
        started_at: str,
        target: str,
        found_material_ids: list[str] | None = None,
        skipped_reason: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "id": operation_id,
            "runId": run_id,
            "sourceHandleId": source_handle_id,
            "kind": kind,
            "label": label,
            "status": status,
            "startedAt": started_at,
            "completedAt": self.now_iso() if status != "running" else None,
            "target": target,
            "foundMaterialIds": found_material_ids or [],
        }
        if skipped_reason:
            payload["skippedReason"] = skipped_reason
        if error:
            payload["error"] = error
        return payload

    def warnings_for(self, raw_results: list[dict[str, Any]], found_materials: list[dict[str, Any]]) -> list[str]:
        if not raw_results:
            return ["no-raw-search-results"]
        if not found_materials:
            return ["no-readable-found-materials"]
        return []

    def safe_error(self, error: Exception) -> str:
        return f"{error.__class__.__name__}: {str(error)[:180]}"

    def stable_slug(self, value: str) -> str:
        return "".join(char if char.isalnum() else "-" for char in value.lower()).strip("-")[:64] or "item"

    def truncate(self, value: str, limit: int) -> str:
        return " ".join(value.split())[:limit].rstrip()

    def now_iso(self) -> str:
        return datetime.now(UTC).isoformat()


_FACTORY = UpstreamRadarPayloadFactory()

budget_for_mode = _FACTORY.budget_for_mode
raw_result = _FACTORY.raw_result
material_from_read = _FACTORY.material_from_read
material_from_raw = _FACTORY.material_from_raw
operation = _FACTORY.operation
warnings_for = _FACTORY.warnings_for
safe_error = _FACTORY.safe_error
stable_slug = _FACTORY.stable_slug
truncate = _FACTORY.truncate
now_iso = _FACTORY.now_iso


__all__ = (
    "UpstreamRadarPayloadFactory",
    "budget_for_mode",
    "raw_result",
    "material_from_read",
    "material_from_raw",
    "operation",
    "warnings_for",
    "safe_error",
    "stable_slug",
    "truncate",
    "now_iso",
)
