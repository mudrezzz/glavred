"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


class FinalQualityGatePayloadFactory:
    """Owns trace-safe payload helpers for the final quality gate."""

    def final_decision(self, candidate: dict[str, Any] | None, source: str, reason: str) -> dict[str, Any]:
        return {"finalCandidateId": (candidate or {}).get("id"), "source": source, "reason": reason}

    def not_run_payload(self, reason: str) -> dict[str, Any]:
        return {"status": "not-run", "reason": reason, "acceptedRepair": False, "finalDecision": {"source": "none", "reason": reason}}

    def strings(self, value: Any) -> list[str]:
        return [str(item) for item in value if str(item).strip()] if isinstance(value, list) else []

    def last(self, values: list[str]) -> str | None:
        return values[-1] if values else None

    def worst_status(self, *values: Any) -> str:
        usable = [str(value or "passed") for value in values if str(value or "") != "not-run"]
        return max(usable or ["passed"], key=lambda item: {"passed": 0, "clean": 0, "warning": 1, "critical": 2}.get(item, 0))

    def gate_improved(self, before: dict[str, Any], after: dict[str, Any]) -> bool:
        if self.severity(after.get("status")) < self.severity(before.get("status")):
            return True
        before_findings = len(self.list_value(self.dict_value(before.get("independentReview")).get("findings")))
        after_findings = len(self.list_value(self.dict_value(after.get("independentReview")).get("findings")))
        return after_findings < before_findings

    def severity(self, value: Any) -> int:
        return {"passed": 0, "clean": 0, "warning": 1, "critical": 2}.get(str(value or "passed"), 0)

    def unique(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def dedupe(self, values: list[str]) -> list[str]:
        return self.unique([value for value in values if value.strip()])

    def dict_value(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def list_value(self, value: Any) -> list[Any]:
        return value if isinstance(value, list) else []
