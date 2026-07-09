"""Owner: drafting.application.reliability

Used by: DraftRun reliability event extraction.
Does not own: DraftRun quality verdicts, operation-envelope parsing, provider execution, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import OperationReliabilityEvent
from backend.app.shared.llm_operations.incidents import infer_incident_type_value


class ChildAiRunReliabilityEventComponent:
    """Creates reliability events for child AiRuns not represented by stage summaries."""

    def missing_events(
        self,
        *,
        run_id: str,
        ai_runs: list[dict[str, Any]],
        existing: list[OperationReliabilityEvent],
        execution_mode: str | None,
    ) -> list[OperationReliabilityEvent]:
        existing_ids = {event.operation_id for event in existing if event.operation_id.startswith("aiRun:")}
        events: list[OperationReliabilityEvent] = []
        for run in ai_runs:
            ai_run_id = str(run.get("id") or "")
            operation_id = f"aiRun:{ai_run_id}"
            if not ai_run_id or operation_id in existing_ids:
                continue
            events.append(self._event(run_id, run, operation_id, execution_mode))
        return events

    def _event(
        self,
        run_id: str,
        run: dict[str, Any],
        operation_id: str,
        execution_mode: str | None,
    ) -> OperationReliabilityEvent:
        error = str(run.get("error") or "")
        fallback = bool(run.get("fallbackUsed") or run.get("fallback_used"))
        retry_path = "fallbackRecovered" if fallback else "retryRecovered" if error else "clean"
        return OperationReliabilityEvent(
            run_id=run_id,
            step_key=str(run.get("step") or "unknown"),
            operation_id=operation_id,
            operation_kind="aiRun",
            provider=_optional_str(run.get("provider")),
            model=_optional_str(run.get("model")),
            model_role=None,
            execution_mode=execution_mode,
            attempt_count=1,
            retry_path=retry_path,
            result_impact="fallbackRecovered" if fallback else "retryRecovered" if error else "none",
            outcome="fallbackRecovered" if fallback else "retryRecovered" if error else "clean",
            incident_types=(_incident_from_error(error),) if error else (),
            source="childAiRun",
        )


def _incident_from_error(error: str) -> str:
    return infer_incident_type_value(error)


def _optional_str(value: Any) -> str | None:
    return str(value) if value not in {None, ""} else None
