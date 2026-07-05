"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


class DraftRevisionGoalEvaluator:
    def evaluate(
        self,
        *,
        repair_goals: list[str],
        validation_before: dict[str, Any],
        validation_after: dict[str, Any],
        base_candidate_id: str | None,
        revised_candidate_id: str | None,
    ) -> dict[str, list[str]]:
        before = _candidate_report(validation_before, base_candidate_id)
        after = _candidate_report(validation_after, revised_candidate_id)
        resolved: list[str] = []
        unresolved: list[str] = []
        for goal in repair_goals:
            if _goal_resolved(goal, before, after):
                resolved.append(goal)
            else:
                unresolved.append(goal)
        return {"resolved": resolved, "unresolved": unresolved}


def _goal_resolved(goal: str, before: dict[str, Any], after: dict[str, Any]) -> bool:
    validator = goal.split(":", 1)[0].strip()
    if validator == "evidence.attribution":
        return _missing_attribution_count(after) < _missing_attribution_count(before)
    if validator.startswith("llm.source-grounding"):
        return _missing_attribution_count(after) < _missing_attribution_count(before)
    if validator:
        return _finding_count(after, validator) < _finding_count(before, validator)
    return _warning_count(after) < _warning_count(before)


def _candidate_report(report: dict[str, Any], candidate_id: str | None) -> dict[str, Any]:
    for item in _list(report.get("candidateReports")):
        row = _dict(item)
        if row.get("candidateId") == candidate_id:
            return row
    return {}


def _finding_count(report: dict[str, Any], validator_prefix: str) -> int:
    return sum(1 for finding in _findings(report) if str(finding.get("validatorId") or "").startswith(validator_prefix))


def _warning_count(report: dict[str, Any]) -> int:
    return _int(report.get("criticalCount")) + _int(report.get("warningCount"))


def _missing_attribution_count(report: dict[str, Any]) -> int:
    missing: set[str] = set()
    for finding in _findings(report):
        if finding.get("validatorId") == "evidence.attribution":
            metadata = _dict(finding.get("metadata"))
            missing.update(str(item) for item in _list(metadata.get("missingClaimIds")) if str(item).strip())
    return len(missing)


def _findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [_dict(item) for item in _list(report.get("findings"))]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0
