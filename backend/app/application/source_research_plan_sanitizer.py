from typing import Any


def sanitize_research_plan_for_source_intent(
    *,
    plan_payload: dict[str, Any],
    source_intent_payload: dict[str, Any],
) -> dict[str, Any]:
    items = {str(item.get("id")): item for item in _dicts(source_intent_payload.get("items"))}
    warnings = [str(item) for item in _list(plan_payload.get("warnings"))]
    tasks: list[dict[str, Any]] = []
    for task in _dicts(plan_payload.get("verificationTasks")):
        fixed = dict(task)
        kind = str(fixed.get("kind") or "")
        source_item = items.get(str(fixed.get("sourceIntentItemId") or ""))
        if kind == "readUrl" and not _is_url(str(fixed.get("target") or fixed.get("instruction") or "")):
            if source_item and source_item.get("kind") == "url" and _is_url(str(source_item.get("instruction") or "")):
                fixed["target"] = str(source_item.get("instruction"))
            else:
                fixed["kind"] = "findPublicSources"
                fixed["metadata"] = {**_dict(fixed.get("metadata")), "sanitizedFrom": "readUrl", "reason": "linked-source-intent-is-not-url"}
                warnings.append(f"Research task {fixed.get('id') or 'unknown'} changed from readUrl to findPublicSources because target is not an HTTP URL.")
        tasks.append(fixed)
    return {**plan_payload, "verificationTasks": tasks, "warnings": _dedupe(warnings)}


def _is_url(value: str) -> bool:
    return value.strip().lower().startswith(("http://", "https://"))


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
