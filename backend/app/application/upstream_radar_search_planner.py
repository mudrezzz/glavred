from __future__ import annotations

from typing import Any


def build_search_plan(*, radar: dict[str, Any], handles: list[dict[str, Any]], budget: dict[str, int], workspace: dict[str, Any]) -> dict[str, Any]:
    language = _workspace_language(workspace)
    queries: list[dict[str, str]] = []
    skipped: list[str] = []
    max_queries = max(1, int(budget.get("maxExternalQueries", 1)))
    for handle in handles:
        if str(handle.get("status") or "active") != "active":
            skipped.append(f"{handle.get('id')}:source-inactive")
            continue
        if not _can_search(handle):
            continue
        base = _base_query(radar, handle)
        for intent, label, suffix in _intent_templates(language):
            if len(queries) >= max_queries:
                skipped.append("budget-max-external-queries")
                break
            query = _clean_query(f"{base} {suffix}")
            queries.append({
                "id": f"query-{len(queries) + 1}",
                "sourceHandleId": str(handle.get("id") or ""),
                "intent": intent,
                "label": label,
                "query": query,
                "rationale": f"Ищем {label.lower()} для радара «{radar.get('title') or radar.get('id')}».",
            })
    return {
        "strategy": "deterministic-search-campaign-v1",
        "language": language,
        "queries": queries,
        "skippedIntents": _unique(skipped),
    }


def _can_search(handle: dict[str, Any]) -> bool:
    capabilities = handle.get("capabilities") if isinstance(handle.get("capabilities"), dict) else {}
    return bool(capabilities.get("canSearch")) or str(handle.get("type") or "") in {"openWebQuery", "socialProfile"}


def _base_query(radar: dict[str, Any], handle: dict[str, Any]) -> str:
    parts = [
        str(handle.get("locator") or ""),
        str(handle.get("title") or ""),
        str(radar.get("title") or ""),
        str(radar.get("scope") or ""),
    ]
    rules = radar.get("rules") if isinstance(radar.get("rules"), list) else []
    parts.extend(str(rule.get("statement") or "") for rule in rules if isinstance(rule, dict))
    return _clean_query(" ".join(part for part in parts if part))


def _intent_templates(language: str) -> list[tuple[str, str, str]]:
    if language == "ru":
        return [
            ("caseStudy", "кейсы применения", "кейс внедрения пример практика"),
            ("benchmark", "исследования и цифры", "исследование benchmark метрики результаты"),
            ("tooling", "инструменты и OSS", "github open source framework инструмент"),
            ("limitations", "ограничения и провалы", "риски ограничения провал lessons learned"),
        ]
    return [
        ("caseStudy", "case studies", "case study implementation example"),
        ("benchmark", "benchmarks and papers", "benchmark paper metrics results"),
        ("tooling", "tools and OSS", "github open source framework tool"),
        ("limitations", "limitations and failures", "risks limitations failure lessons learned"),
    ]


def _workspace_language(workspace: dict[str, Any]) -> str:
    profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
    language = str(profile.get("language") or workspace.get("language") or "ru").lower()
    return "en" if language.startswith("en") else "ru"


def _clean_query(value: str) -> str:
    return " ".join(value.split())[:240]


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))
