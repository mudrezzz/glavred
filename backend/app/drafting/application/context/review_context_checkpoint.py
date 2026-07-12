"""Owner: drafting.application.context

Used by: validation, ranking, revision, and final-quality orchestration.
Does not own: repository access, provider calls, dossier policy, or final decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink


class ReviewContextCheckpointPublisher:
    """Persists the exact current review state before a dependent provider call."""

    def publish(
        self,
        progress: DraftRunStepOperationSink | None,
        *,
        stage: str,
        candidates: list[dict[str, Any]] | None = None,
        current_candidate: dict[str, Any] | None = None,
        validation_report: dict[str, Any] | None = None,
        revision_instruction: dict[str, Any] | None = None,
        final_quality_contract: dict[str, Any] | None = None,
        deterministic_gate: dict[str, Any] | None = None,
        repair_history: dict[str, Any] | None = None,
    ) -> None:
        if progress is None:
            return
        payload: dict[str, Any] = {"stage": stage}
        for key, value in (
            ("candidates", candidates),
            ("currentCandidate", current_candidate),
            ("validationReport", validation_report),
            ("revisionInstruction", revision_instruction),
            ("finalQualityContract", final_quality_contract),
            ("deterministicGate", deterministic_gate),
            ("repairHistory", repair_history),
        ):
            if value is not None:
                payload[key] = value
        progress.merge_artifact({"reviewContext": payload})


__all__ = ("ReviewContextCheckpointPublisher",)
