"""Owner: drafting.application.quality

Used by: DraftRun quality/fidelity reporting and diagnostics.
Does not own: validation execution, final-quality gate logic, provider retries, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any


class QualityFidelityVerdictPolicy:
    """Maps technical, provider-recovery, and editorial signals to canonical verdicts."""

    def technical_status(
        self,
        run_status: str,
        steps: list[dict[str, Any]],
        final_draft: dict[str, Any] | None,
    ) -> str:
        if run_status == "failed" or any(step.get("status") == "failed" for step in steps):
            return "failed"
        if any(step.get("status") == "running" for step in steps):
            return "stale"
        complete = _artifact(steps, "complete")
        if complete.get("status") == "blocked" or final_draft is None:
            return "blocked"
        return "succeeded"

    def provider_recovery_status(self, stage_summaries: list[dict[str, Any]]) -> str:
        impacts = {str(summary.get("resultImpact")) for summary in stage_summaries}
        retry_paths = {str(summary.get("retryPath")) for summary in stage_summaries}
        if "stepFailed" in impacts:
            return "failed"
        if "stepDegraded" in impacts:
            return "degraded"
        if "fallbackRecovered" in retry_paths:
            return "fallbackRecovered"
        if "backupRecovered" in retry_paths:
            return "backupRecovered"
        if "retryRecovered" in retry_paths:
            return "retryRecovered"
        return "clean"

    def editorial_status(
        self,
        *,
        technical_status: str,
        issue_lifecycle: dict[str, Any],
        evidence: dict[str, Any],
        final_gate: dict[str, Any],
        final_draft: dict[str, Any] | None,
    ) -> str:
        if technical_status in {"failed", "blocked"} or not final_draft:
            return "blocked" if technical_status == "blocked" else "needsHumanReview"
        if issue_lifecycle.get("openCriticalCount", 0) or final_gate.get("status") == "critical":
            return "needsHumanReview"
        body = str(final_draft.get("body") or final_draft.get("text") or "")
        if len(body) > 10240:
            return "publishableWithCaution"
        if final_gate.get("status") == "warning" or issue_lifecycle.get("openWarningCount", 0):
            return "publishableWithCaution"
        if evidence.get("coverageVerdict") == "missing" or evidence.get("fidelityImpact") == "blocked":
            return "needsHumanReview"
        if evidence.get("coverageVerdict") in {"partial", "weak"}:
            return "publishableWithCaution"
        return "publishable"

    def overall_verdict(self, technical_status: str, provider_status: str, editorial_status: str) -> str:
        if technical_status == "failed" or provider_status == "failed":
            return "failed"
        if editorial_status in {"needsHumanReview", "blocked"}:
            return "needsAttention"
        if provider_status in {"fallbackRecovered", "degraded"}:
            return "degradedSuccess"
        if provider_status in {"retryRecovered", "backupRecovered"}:
            return "recoveredSuccess"
        return "cleanSuccess" if editorial_status == "publishable" else "degradedSuccess"


def _artifact(steps: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return next((_dict(step.get("artifact")) for step in steps if step.get("key") == key), {})


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
