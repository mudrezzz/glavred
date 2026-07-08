"""Owner: drafting.application.reliability

Used by: DraftRun reliability event extraction.
Does not own: quality/fidelity report construction, provider calls, persistence, or remediation policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import OperationReliabilityEvent


class QualityFidelityReliabilitySignalExtractor:
    """Converts non-provider quality/fidelity warnings into reliability events."""

    def events(
        self,
        *,
        run_id: str,
        quality_fidelity: dict[str, Any],
        execution_mode: str | None,
    ) -> list[OperationReliabilityEvent]:
        events: list[OperationReliabilityEvent] = []
        events.extend(self._issue_events(run_id, quality_fidelity, execution_mode))
        events.extend(self._evidence_events(run_id, quality_fidelity, execution_mode))
        return events

    def _issue_events(
        self,
        run_id: str,
        quality_fidelity: dict[str, Any],
        execution_mode: str | None,
    ) -> list[OperationReliabilityEvent]:
        issue_lifecycle = _dict(quality_fidelity.get("issueLifecycle"))
        events: list[OperationReliabilityEvent] = []
        if int(issue_lifecycle.get("openCriticalCount") or 0) > 0:
            events.append(self._event(run_id, "qualityFidelity:openCritical", "openCritical", execution_mode))
        if int(issue_lifecycle.get("openWarningCount") or 0) > 0 or quality_fidelity.get("editorialStatus") == "publishableWithCaution":
            events.append(self._event(run_id, "qualityFidelity:finalGateWarning", "finalGateWarning", execution_mode))
        return events

    def _evidence_events(
        self,
        run_id: str,
        quality_fidelity: dict[str, Any],
        execution_mode: str | None,
    ) -> list[OperationReliabilityEvent]:
        evidence = _dict(quality_fidelity.get("evidenceFidelity"))
        if evidence.get("coverageVerdict") not in {"weak", "missing"}:
            return []
        return [
            self._event(
                run_id,
                "qualityFidelity:evidenceFidelity",
                "degraded",
                execution_mode,
                incident_type=f"evidence-{evidence.get('coverageVerdict')}",
            )
        ]

    def _event(
        self,
        run_id: str,
        operation_id: str,
        outcome: str,
        execution_mode: str | None,
        *,
        incident_type: str | None = None,
    ) -> OperationReliabilityEvent:
        return OperationReliabilityEvent(
            run_id=run_id,
            step_key="validation" if "finalGate" in operation_id or "openCritical" in operation_id else "quality",
            operation_id=operation_id,
            operation_kind="qualityFidelity",
            provider=None,
            model=None,
            model_role=None,
            execution_mode=execution_mode,
            attempt_count=0,
            retry_path="qualitySignal",
            result_impact="stepDegraded",
            outcome=outcome,  # type: ignore[arg-type]
            incident_types=(incident_type or outcome,),
            source="qualityFidelity",
        )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
