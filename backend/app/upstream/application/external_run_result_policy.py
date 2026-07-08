"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService.
Does not own: API routing, SQLite persistence, provider transport, signal scoring, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any


class ExternalRunResultPolicy:
    def status(self, *, found_ids: list[str], operations: list[dict[str, Any]], errors: list[str]) -> str:
        if found_ids and not errors:
            return "succeeded"
        if found_ids or operations:
            return "partial"
        return "failed"

    def unique(self, items: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in items if item))
