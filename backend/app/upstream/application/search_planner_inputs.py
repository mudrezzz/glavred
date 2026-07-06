"""Owner: upstream.application

Used by: SearchIntentPlanner to extract campaign inputs from workspace snapshots.
Does not own: provider transport, API routing, UI rendering, signal scoring, or candidate assembly.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

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

    def base_query(self, *, radar: dict[str, Any], handle: dict[str, Any], workspace: dict[str, Any]) -> str:
        parts = [
            str(handle.get("locator") or ""),
            str(handle.get("title") or ""),
            str(radar.get("title") or ""),
            str(radar.get("scope") or ""),
        ]
        rules = radar.get("rules") if isinstance(radar.get("rules"), list) else []
        parts.extend(str(rule.get("statement") or "") for rule in rules if isinstance(rule, dict))
        parts.extend(self._entity_names(workspace.get("topics"), limit=2))
        parts.extend(self._entity_names(workspace.get("fabulas"), limit=2))
        parts.extend(self._publisher_rules(workspace))
        return self.clean_query(" ".join(part for part in parts if part))

    def query_terms(self, base_query: str, suffix: str) -> list[str]:
        return self.clean_query(f"{base_query} {suffix}").split()[:16]

    def clean_query(self, value: str) -> str:
        return " ".join(value.split())[:240]

    def _entity_names(self, items: Any, *, limit: int) -> list[str]:
        if not isinstance(items, list):
            return []
        names: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            value = item.get("title") or item.get("name") or item.get("label")
            if value:
                names.append(str(value))
            if len(names) >= limit:
                break
        return names

    def _publisher_rules(self, workspace: dict[str, Any]) -> list[str]:
        rules = workspace.get("publisherRules") if isinstance(workspace.get("publisherRules"), list) else []
        values: list[str] = []
        for rule in rules[:2]:
            if isinstance(rule, dict):
                values.append(str(rule.get("statement") or rule.get("title") or ""))
            elif rule:
                values.append(str(rule))
        return [item for item in values if item]


__all__ = ("SearchPlannerInputPolicy",)
