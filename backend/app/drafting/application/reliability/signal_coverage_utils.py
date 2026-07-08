"""Owner: drafting.application.reliability

Used by: reliability signal coverage components.
Does not own: event extraction, remediation policy, provider execution, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import ReliabilitySignalCoverageRecord


def _record(
    run_id: str,
    step_key: str,
    path: str,
    signal_type: str,
    operation_id: str,
    operation_ids: set[str],
    *,
    incident_type: str | None = None,
    reason: str,
) -> ReliabilitySignalCoverageRecord:
    covered = operation_id in operation_ids
    return ReliabilitySignalCoverageRecord(
        run_id=run_id,
        step_key=step_key,
        path=path,
        signal_type=signal_type,
        coverage_status="covered" if covered else "ignored",
        reason=reason if covered else "noMatchingOperationSummary",
        operation_id=operation_id,
        incident_type=incident_type,
        ai_run_id=None,
    )


def _walk_dicts(value: dict[str, Any], path: str = "") -> list[tuple[str, dict[str, Any]]]:
    items = [(path, value)]
    for key, child in value.items():
        if isinstance(child, dict):
            items.extend(_walk_dicts(child, f"{path}.{key}" if path else str(key)))
        elif isinstance(child, list):
            for index, list_child in enumerate(child):
                if isinstance(list_child, dict):
                    items.extend(_walk_dicts(list_child, f"{path}.{key}[{index}]" if path else f"{key}[{index}]"))
    return items


def _dedupe_records(records: list[ReliabilitySignalCoverageRecord]) -> list[ReliabilitySignalCoverageRecord]:
    seen: set[tuple[str, str, str, str, str | None]] = set()
    result: list[ReliabilitySignalCoverageRecord] = []
    for record in records:
        key = (record.run_id, record.step_key, record.path, record.signal_type, record.incident_type)
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return result


def _incident_from_error(error: str) -> str:
    lowered = error.lower()
    if "timeout" in lowered:
        return "providerTimeout"
    if "json" in lowered:
        return "malformedJson"
    if "schema" in lowered or "validation" in lowered:
        return "schemaFailure"
    if "4xx" in lowered or "401" in lowered or "403" in lowered:
        return "provider4xx"
    if "5xx" in lowered or "500" in lowered:
        return "provider5xx"
    return "unknownProviderFailure"


def _status(value: dict[str, Any]) -> str:
    return str(value.get("status") or "").replace("-", "").lower()


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _optional_str(value: Any) -> str | None:
    return str(value) if value not in {None, ""} else None
