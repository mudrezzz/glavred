"""Owner: upstream.application

Used by: SearchIntentPlanner to extract campaign inputs from workspace snapshots.
Does not own: provider transport, API routing, UI rendering, signal scoring, or candidate assembly.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import re
from typing import Any


class SearchPlannerInputPolicy:
    def source_eligibility(self, handle: dict[str, Any]) -> dict[str, Any]:
        status = str(handle.get("status") or "active")
        handle_id = str(handle.get("id") or "")
        capabilities = handle.get("capabilities") if isinstance(handle.get("capabilities"), dict) else {}
        can_search = bool(capabilities.get("canSearch")) or str(handle.get("type") or "") in {"openWebQuery", "socialProfile"}
        can_read = bool(capabilities.get("canReadUrl")) or str(handle.get("type") or "") == "externalUrl"
        if status != "active":
            return {"sourceHandleId": handle_id, "status": status, "strategy": "skipped", "reason": "source-inactive"}
        if can_search:
            return {"sourceHandleId": handle_id, "status": status, "strategy": "providerSearch", "reason": None}
        if can_read:
            return {"sourceHandleId": handle_id, "status": status, "strategy": "directRead", "reason": None}
        return {"sourceHandleId": handle_id, "status": status, "strategy": "skipped", "reason": "source-not-searchable"}

    def workspace_language(self, workspace: dict[str, Any]) -> str:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        language = str(profile.get("language") or workspace.get("language") or "ru").lower()
        return "en" if language.startswith("en") else "ru"

    def research_depth(self, *, radar: dict[str, Any], workspace: dict[str, Any]) -> str:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        for container in (radar, profile, workspace):
            value = container.get("researchDepth") if isinstance(container, dict) else None
            if value:
                return str(value)
        return "standard"

    def needs_freshness(self, *, radar: dict[str, Any], workspace: dict[str, Any], research_depth: str) -> bool:
        if research_depth == "full":
            return True
        haystack = " ".join(
            [
                str(radar.get("title") or ""),
                str(radar.get("scope") or ""),
                " ".join(str(rule.get("statement") or "") for rule in radar.get("rules", []) if isinstance(rule, dict)),
                str(workspace.get("benchmarkRole") or ""),
            ]
        ).lower()
        return any(marker in haystack for marker in ("fresh", "recent", "news", "trend", "2026", "свеж", "новост", "тренд"))

    def base_query(
        self,
        *,
        radar: dict[str, Any],
        handle: dict[str, Any],
        requirement_terms: list[str] | None = None,
    ) -> str:
        parts = [
            str(handle.get("locator") or ""),
            str(handle.get("title") or ""),
            str(radar.get("title") or ""),
            str(radar.get("scope") or ""),
        ]
        parts.extend(requirement_terms or [])
        return self.clean_query(" ".join(part for part in parts if part))

    def query_terms(self, base_query: str, suffix: str) -> list[str]:
        return self.clean_query(f"{base_query} {suffix}").split()[:16]

    def query_for_language(self, *, base_query: str, suffix: str, language: str) -> str:
        tokens = base_query.split()
        if language == "ru":
            selected = [item for item in tokens if re.search(r"[\u0400-\u052f]", item)]
        else:
            selected = [item for item in tokens if re.search(r"[a-zA-Z]", item) and not re.search(r"[\u0400-\u052f]", item)]
        return self.clean_query(" ".join([*selected[:12], suffix]))

    def clean_query(self, value: str) -> str:
        retained: list[str] = []
        seen: set[str] = set()
        for token in value.split():
            normalized = re.sub(r"[^\w]+", "", token, flags=re.UNICODE).casefold()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            retained.append(token)
        return " ".join(retained)[:240]

__all__ = ("SearchPlannerInputPolicy",)
