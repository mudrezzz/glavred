"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


def final_decision(candidate: dict[str, Any] | None, source: str, reason: str) -> dict[str, Any]:
    return {"finalCandidateId": (candidate or {}).get("id"), "source": source, "reason": reason}


def not_run_payload(reason: str) -> dict[str, Any]:
    return {"status": "not-run", "reason": reason, "acceptedRepair": False, "finalDecision": {"source": "none", "reason": reason}}


def strings(value: Any) -> list[str]:
    return [str(item) for item in value if str(item).strip()] if isinstance(value, list) else []


def last(values: list[str]) -> str | None:
    return values[-1] if values else None


def worst_status(*values: Any) -> str:
    usable = [str(value or "passed") for value in values if str(value or "") != "not-run"]
    return max(usable or ["passed"], key=lambda item: {"passed": 0, "clean": 0, "warning": 1, "critical": 2}.get(item, 0))


def gate_improved(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if severity(after.get("status")) < severity(before.get("status")):
        return True
    before_findings = len(list_value(dict_value(before.get("independentReview")).get("findings")))
    after_findings = len(list_value(dict_value(after.get("independentReview")).get("findings")))
    return after_findings < before_findings


def severity(value: Any) -> int:
    return {"passed": 0, "clean": 0, "warning": 1, "critical": 2}.get(str(value or "passed"), 0)


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def dedupe(values: list[str]) -> list[str]:
    return unique([value for value in values if value.strip()])


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


class FinalQualityGatePayloads:
    """Owns trace-safe payload helpers for the final quality gate."""

    final_decision = staticmethod(final_decision)
    not_run_payload = staticmethod(not_run_payload)
    strings = staticmethod(strings)
    last = staticmethod(last)
    worst_status = staticmethod(worst_status)
    gate_improved = staticmethod(gate_improved)
    severity = staticmethod(severity)
    unique = staticmethod(unique)
    dedupe = staticmethod(dedupe)
    dict_value = staticmethod(dict_value)
    list_value = staticmethod(list_value)
