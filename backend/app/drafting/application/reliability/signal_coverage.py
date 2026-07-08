"""Owner: drafting.application.reliability

Used by: DraftRun provider reliability reports and diagnostics.
Does not own: provider execution, quality verdict policy, payload budget policy, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from backend.app.domain.ai_run import AiRun
from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.reliability.ai_run_signal_coverage import ChildAiRunSignalCoverageComponent
from backend.app.drafting.application.reliability.artifact_signal_coverage import ArtifactSignalCoverageComponent
from backend.app.drafting.application.reliability.contracts import (
    OperationReliabilityEvent,
    ReliabilitySignalCoverageRecord,
)


class ReliabilitySignalCoverageExtractor:
    """Coordinates raw structured-signal coverage without owning each signal rule."""

    def __init__(
        self,
        *,
        child_ai_runs: ChildAiRunSignalCoverageComponent | None = None,
        artifacts: ArtifactSignalCoverageComponent | None = None,
    ) -> None:
        self._child_ai_runs = child_ai_runs or ChildAiRunSignalCoverageComponent()
        self._artifacts = artifacts or ArtifactSignalCoverageComponent()

    def records(
        self,
        run: DraftRun,
        *,
        ai_runs: list[AiRun],
        events: list[OperationReliabilityEvent],
    ) -> list[ReliabilitySignalCoverageRecord]:
        operation_ids = {event.operation_id for event in events if event.run_id == run.id}
        records = self._child_ai_runs.records(run_id=run.id, ai_runs=ai_runs, operation_ids=operation_ids)
        for step in run.steps:
            records.extend(
                self._artifacts.records(
                    run_id=run.id,
                    step_key=step.key.value,
                    artifact=step.artifact_payload or {},
                    operation_ids=operation_ids,
                )
            )
        return records
