"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService.
Does not own: API routing, SQLite persistence, provider transport, signal scoring, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any


class ExternalRunResultPolicy:
    def status(self, *, found_materials: list[dict[str, Any]], operations: list[dict[str, Any]], errors: list[str]) -> str:
        readable = [item for item in found_materials if item.get("status") != "metadataOnly"]
        failed_operations = [item for item in operations if item.get("status") == "failed"]
        if readable and not errors and not failed_operations:
            return "succeeded"
        if found_materials or operations:
            return "partial"
        return "failed"

    def unique(self, items: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in items if item))
