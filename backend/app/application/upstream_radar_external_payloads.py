from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.application.upstream_radar_search_triage import canonical_url, result_domain, score_search_result


def budget_for_mode(mode: str) -> dict[str, int]:
    base = {"maxOperations": 10, "maxInternalItems": 0, "maxExternalQueries": 3, "maxUrlReads": 2, "maxFoundMaterials": 2}
    if mode == "smoke":
        base.update({"maxOperations": 4, "maxExternalQueries": 1, "maxUrlReads": 1, "maxFoundMaterials": 1})
    elif mode == "full":
        base.update({"maxOperations": 16, "maxExternalQueries": 5, "maxUrlReads": 4, "maxFoundMaterials": 4})
    return {**base, "usedOperations": 0, "usedInternalItems": 0, "usedExternalQueries": 0, "usedUrlReads": 0, "usedFoundMaterials": 0}


def raw_result(run_id: str, query: dict[str, Any], citation: Any, index: int) -> dict[str, Any]:
    url = canonical_url(str(citation.url))
    return {
        "id": f"{run_id}-raw-{query['id']}-{index + 1}",
        "sourceHandleId": query["sourceHandleId"],
        "queryId": query["id"],
        "title": citation.title or url,
        "url": url,
        "snippet": citation.snippet or "",
        "domain": result_domain(url),
        "score": score_search_result(title=citation.title or "", snippet=citation.snippet or "", query=query["query"]),
        "duplicateKey": url,
        "provider": "openrouter:web_search",
    }


def material_from_read(*, material_id: str, run_id: str, source_handle_id: str, title: str, read: PublicUrlReadResult, provenance: str) -> dict[str, Any]:
    return {
        "id": material_id,
        "radarRunId": run_id,
        "sourceHandleId": source_handle_id,
        "type": "searchResult",
        "title": read.title or title or read.url,
        "locator": read.final_url or read.url,
        "snippet": truncate(read.text, 360),
        "summary": truncate(read.text, 1200),
        "capturedAt": now_iso(),
        "status": "found",
        "warnings": [],
        "provenanceLabel": provenance,
    }


def material_from_raw(*, material_id: str, run_id: str, raw: dict[str, Any], warning: str) -> dict[str, Any]:
    return {
        "id": material_id,
        "radarRunId": run_id,
        "sourceHandleId": raw["sourceHandleId"],
        "type": "searchResult",
        "title": raw["title"],
        "locator": raw["url"],
        "snippet": truncate(raw["snippet"], 360),
        "summary": truncate(raw["snippet"], 1200),
        "capturedAt": now_iso(),
        "status": "found",
        "warnings": [warning, "search-result-only"],
        "provenanceLabel": f"{raw['provider']} / {raw['domain']}",
    }


def operation(*, operation_id: str, run_id: str, source_handle_id: str, kind: str, label: str, status: str, started_at: str, target: str, found_material_ids: list[str] | None = None, skipped_reason: str | None = None, error: str | None = None) -> dict[str, Any]:
    payload = {
        "id": operation_id,
        "runId": run_id,
        "sourceHandleId": source_handle_id,
        "kind": kind,
        "label": label,
        "status": status,
        "startedAt": started_at,
        "completedAt": now_iso() if status != "running" else None,
        "target": target,
        "foundMaterialIds": found_material_ids or [],
    }
    if skipped_reason:
        payload["skippedReason"] = skipped_reason
    if error:
        payload["error"] = error
    return payload


def warnings_for(raw_results: list[dict[str, Any]], found_materials: list[dict[str, Any]]) -> list[str]:
    if not raw_results:
        return ["no-raw-search-results"]
    if not found_materials:
        return ["no-readable-found-materials"]
    return []


def safe_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {str(error)[:180]}"


def stable_slug(value: str) -> str:
    return "".join(char if char.isalnum() else "-" for char in value.lower()).strip("-")[:64] or "item"


def truncate(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit].rstrip()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()
