from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


@dataclass(frozen=True)
class ValidationRankingResult:
    artifact_payload: dict[str, Any]
    ai_run_ids: list[str]
    final_draft: GeneratedDraft | None = None


class DraftValidationRankingBridge:
    def __init__(self, ranking_revision_service: DraftRankingRevisionService | None = None) -> None:
        self._ranking_revision = ranking_revision_service

    def apply(
        self,
        *,
        request: DraftGenerationRequest | None,
        artifact_payload: dict[str, Any],
        ai_run_ids: list[str],
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> ValidationRankingResult:
        if not self._ranking_revision or request is None:
            return ValidationRankingResult(artifact_payload, ai_run_ids)
        result = self._ranking_revision.run(
            request=request,
            draft_artifact=draft_artifact,
            validation_report=artifact_payload,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        return ValidationRankingResult(
            {**artifact_payload, "rankingRevision": result.artifact_payload},
            [*ai_run_ids, *result.ai_run_ids],
            result.final_draft,
        )
