"""Owner: drafting.application.quality

Used by: DraftRun quality/fidelity reporting.
Does not own: validation rule execution, final-gate assessment, provider recovery, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any


class QualityFidelityIssueComponent:
    """Classifies warning/critical findings as open, suppressed, accepted risk, or resolved."""

    def summary(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        final_gate = self.final_gate(steps)
        lifecycle = [self._finding_lifecycle(item, final_gate) for item in self._findings(steps, final_gate)]
        return {
            "openCriticalCount": sum(1 for item in lifecycle if item["severity"] == "critical" and item["status"] == "open"),
            "openWarningCount": sum(1 for item in lifecycle if item["severity"] == "warning" and item["status"] == "open"),
            "resolvedCount": sum(1 for item in lifecycle if item["status"] == "resolved"),
            "suppressedCount": sum(1 for item in lifecycle if item["status"] == "suppressed"),
            "acceptedRiskCount": sum(1 for item in lifecycle if item["status"] == "acceptedRisk"),
            "items": lifecycle[:20],
        }

    def final_gate(self, steps: list[dict[str, Any]]) -> dict[str, Any]:
        validation = _artifact(steps, "validation")
        ranking = _dict(validation.get("rankingRevision"))
        return _dict(ranking.get("finalQualityGate"))

    def _findings(self, steps: list[dict[str, Any]], final_gate: dict[str, Any]) -> list[dict[str, Any]]:
        validation = _artifact(steps, "validation")
        findings: list[dict[str, Any]] = []
        for report in _list(validation.get("candidateReports")):
            findings.extend(_dict(item) for item in _list(_dict(report).get("findings")))
        llm = _dict(validation.get("llmValidationReport"))
        for report in _list(llm.get("candidateReports")):
            findings.extend(_dict(item) for item in _list(_dict(report).get("findings")))
        independent = _dict(final_gate.get("independentReview"))
        findings.extend(_dict(item) for item in _list(independent.get("findings")))
        return findings

    def _finding_lifecycle(self, finding: dict[str, Any], final_gate: dict[str, Any]) -> dict[str, Any]:
        severity = str(finding.get("severity") or finding.get("status") or "warning")
        if severity not in {"critical", "warning"}:
            severity = "warning"
        validator_id = str(finding.get("validatorId") or "unknown")
        suppressed = finding.get("suppressedReason") or _dict(finding.get("metadata")).get("suppressedReason")
        if suppressed:
            status = "suppressed"
        elif final_gate.get("acceptedRepair"):
            status = "resolved"
        elif validator_id.startswith("evidence.attribution") and final_gate.get("status") in {"passed", "warning"}:
            status = "acceptedRisk"
        else:
            status = "open"
        return {
            "validatorId": validator_id,
            "severity": severity,
            "status": status,
            "message": str(finding.get("message") or "")[:180],
        }


def _artifact(steps: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return next((_dict(step.get("artifact")) for step in steps if step.get("key") == key), {})


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
