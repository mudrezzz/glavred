"""Owner: drafting.application.reliability

Used by: DraftRun reliability extraction replay for legacy embedded quality summaries.
Does not own: quality/fidelity verdicts, AiRun persistence, remediation policy, or provider execution.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from backend.app.drafting.application.reliability.contracts import OperationReliabilityEvent
from backend.app.shared.llm_operations.incidents import infer_incident_type_value


class LegacyStageIncidentRefinementComponent:
    """Refines legacy stage `unknownProviderFailure` from matching child AiRun errors."""

    def refine(
        self,
        events: list[OperationReliabilityEvent],
        ai_runs: list[dict[str, Any]],
    ) -> list[OperationReliabilityEvent]:
        return [self._event(event, ai_runs) for event in events]

    def _event(
        self,
        event: OperationReliabilityEvent,
        ai_runs: list[dict[str, Any]],
    ) -> OperationReliabilityEvent:
        if event.incident_types != ("unknownProviderFailure",):
            return event
        if event.source != "qualityFidelity.stageSummaries":
            return event
        inferred = self._incident_from_matching_ai_run(event, ai_runs)
        if inferred and inferred != "unknownProviderFailure":
            return replace(event, incident_types=(inferred,))
        return event

    def _incident_from_matching_ai_run(
        self,
        event: OperationReliabilityEvent,
        ai_runs: list[dict[str, Any]],
    ) -> str | None:
        for run in ai_runs:
            error = str(run.get("error") or "")
            if not error:
                continue
            request_payload = _dict(run.get("requestPayload"))
            step = str(request_payload.get("draftRunStep") or run.get("step") or "")
            candidate_id = str(request_payload.get("candidateId") or "")
            if step and step != event.operation_kind:
                continue
            if candidate_id and candidate_id not in event.operation_id:
                continue
            return infer_incident_type_value(error)
        return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
