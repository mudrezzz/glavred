"""Owner: drafting.application.steps

Used by: migration slices adapting legacy DraftRun step result dataclasses.
Does not own: provider calls, prompt construction, workflow sequencing, artifact semantics.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import cast

from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.domain.draft_generation import GeneratedDraft
from backend.app.drafting.application.steps.contracts import DraftStepOutcome


class DraftPlanningStepOutcomeAdapter:
    @staticmethod
    def from_legacy(result: DraftPlanningStepResult) -> DraftStepOutcome:
        return DraftStepOutcome.succeeded(
            artifact_payload=result.artifact_payload,
            ai_run_id=result.ai_run_id,
            ai_run_ids=result.ai_run_ids,
        )

    @staticmethod
    def to_legacy(outcome: DraftStepOutcome) -> DraftPlanningStepResult:
        primary_ai_run_id = outcome.ai_run_ids[0] if outcome.ai_run_ids else None
        return DraftPlanningStepResult(
            artifact_payload=outcome.artifact_payload,
            ai_run_id=primary_ai_run_id,
            ai_run_ids=list(outcome.ai_run_ids) or None,
        )


class DraftCandidateStepOutcomeAdapter:
    FINAL_DRAFT_KEY = "final_draft"

    @staticmethod
    def from_legacy(result: DraftCandidateGenerationResult) -> DraftStepOutcome:
        return DraftStepOutcome.succeeded(
            artifact_payload=result.artifact_payload,
            ai_run_ids=result.ai_run_ids,
            result_payload={DraftCandidateStepOutcomeAdapter.FINAL_DRAFT_KEY: result.final_draft},
        )

    @staticmethod
    def to_legacy(outcome: DraftStepOutcome) -> DraftCandidateGenerationResult:
        return DraftCandidateGenerationResult(
            artifact_payload=outcome.artifact_payload,
            final_draft=cast(
                GeneratedDraft | None,
                outcome.result_payload.get(DraftCandidateStepOutcomeAdapter.FINAL_DRAFT_KEY),
            ),
            ai_run_ids=list(outcome.ai_run_ids),
        )
