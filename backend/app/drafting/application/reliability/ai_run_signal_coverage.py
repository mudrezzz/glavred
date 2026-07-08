"""Owner: drafting.application.reliability

Used by: DraftRun reliability signal coverage reports.
Does not own: operation-envelope coverage, budget coverage, event extraction, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from backend.app.domain.ai_run import AiRun
from backend.app.drafting.application.reliability.contracts import ReliabilitySignalCoverageRecord
from backend.app.drafting.application.reliability.signal_coverage_utils import _incident_from_error


class ChildAiRunSignalCoverageComponent:
    """Audits child AiRun records and child-provider failures."""

    def records(
        self,
        *,
        run_id: str,
        ai_runs: list[AiRun],
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        records: list[ReliabilitySignalCoverageRecord] = []
        for ai_run in ai_runs:
            records.extend(self._records_for_ai_run(run_id, ai_run, operation_ids))
        return records

    def _records_for_ai_run(
        self,
        run_id: str,
        ai_run: AiRun,
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        operation_id = f"aiRun:{ai_run.id}"
        step_key = str(ai_run.request_payload.get("draftRunStep") or "unknown")
        covered = operation_id in operation_ids
        records = [
            ReliabilitySignalCoverageRecord(
                run_id=run_id,
                step_key=step_key,
                path=f"aiRun:{ai_run.id}",
                signal_type="childAiRun",
                coverage_status="covered" if covered else "ignored",
                reason="countedAsAiRunEvent" if covered else "missingAiRunEvent",
                operation_id=operation_id,
                ai_run_id=ai_run.id,
            )
        ]
        if ai_run.error:
            records.append(
                ReliabilitySignalCoverageRecord(
                    run_id=run_id,
                    step_key=step_key,
                    path=f"aiRun:{ai_run.id}.error",
                    signal_type="childAiRunError",
                    coverage_status="covered" if covered else "ignored",
                    reason="countedAsAiRunProviderIncident" if covered else "missingAiRunEvent",
                    operation_id=operation_id,
                    incident_type=_incident_from_error(ai_run.error),
                    ai_run_id=ai_run.id,
                )
            )
        if ai_run.fallback_used:
            records.append(
                ReliabilitySignalCoverageRecord(
                    run_id=run_id,
                    step_key=step_key,
                    path=f"aiRun:{ai_run.id}.fallbackUsed",
                    signal_type="fallback",
                    coverage_status="covered" if covered else "ignored",
                    reason="countedAsAiRunFallback" if covered else "missingAiRunEvent",
                    operation_id=operation_id,
                    incident_type="deterministicFallback",
                    ai_run_id=ai_run.id,
                )
            )
        return records
