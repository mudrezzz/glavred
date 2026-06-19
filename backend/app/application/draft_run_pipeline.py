from typing import Any, Protocol

from backend.app.application.draft_run_payloads import draft_to_payload, request_from_payload
from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.domain.draft_run import (
    DraftRun,
    DraftRunStatus,
    DraftRunStepKey,
    DraftRunStepStatus,
)


class DraftRunPipelineRepository(Protocol):
    def get(self, run_id: str) -> DraftRun | None: ...

    def set_run_status(
        self,
        run_id: str,
        status: DraftRunStatus,
        *,
        error: str | None = None,
        final_draft: dict[str, Any] | None = None,
        ai_run_ids: list[str] | None = None,
    ) -> None: ...

    def set_step_status(
        self,
        run_id: str,
        key: DraftRunStepKey,
        status: DraftRunStepStatus,
        *,
        artifact_payload: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None: ...


class DraftRunPipeline:
    def __init__(
        self,
        repository: DraftRunPipelineRepository,
        deterministic_draft_service: DeterministicDraftService,
    ) -> None:
        self._repository = repository
        self._deterministic_draft_service = deterministic_draft_service

    def execute(self, run_id: str) -> DraftRun:
        run = self._repository.get(run_id)
        if run is None:
            raise ValueError(f"DraftRun {run_id} not found")
        self._repository.set_run_status(run_id, DraftRunStatus.RUNNING)
        try:
            request = request_from_payload(run.request_payload)
            self._complete_step(
                run_id,
                DraftRunStepKey.CONTEXT,
                {
                    "briefTitle": request.brief.title,
                    "audience": request.brief.audience or request.editorial_model.audience,
                    "evidenceCount": len(request.brief.evidence),
                    "sourceCount": len(request.brief.sources),
                },
            )
            self._complete_step(
                run_id,
                DraftRunStepKey.RULE_PACK,
                {
                    "styleRules": request.editorial_model.style_rules,
                    "forbiddenTopics": request.editorial_model.forbidden_topics,
                    "goals": request.editorial_model.goals,
                },
            )
            self._complete_step(
                run_id,
                DraftRunStepKey.MATERIAL_PLAN,
                {
                    "evidence": request.brief.evidence,
                    "examples": request.brief.examples,
                    "sources": request.brief.sources,
                },
            )
            self._complete_step(
                run_id,
                DraftRunStepKey.STRATEGY,
                {
                    "thesis": request.brief.thesis,
                    "conflict": request.brief.conflict,
                    "cta": request.brief.cta,
                },
            )
            draft_payload = draft_to_payload(self._deterministic_draft_service.create_draft(request))
            self._complete_step(run_id, DraftRunStepKey.DRAFT, {"draft": draft_payload})
            self._complete_step(
                run_id,
                DraftRunStepKey.VALIDATION,
                {
                    "status": "placeholder-passed",
                    "checks": ["structure", "audience", "rules"],
                },
            )
            self._complete_step(run_id, DraftRunStepKey.COMPLETE, {"status": "succeeded"})
            self._repository.set_run_status(
                run_id,
                DraftRunStatus.SUCCEEDED,
                final_draft=draft_payload,
            )
        except Exception as exc:
            self._repository.set_run_status(
                run_id,
                DraftRunStatus.FAILED,
                error=(str(exc)[:500] or "Draft run failed"),
            )
        loaded = self._repository.get(run_id)
        if loaded is None:
            raise ValueError(f"DraftRun {run_id} disappeared")
        return loaded

    def _complete_step(
        self,
        run_id: str,
        key: DraftRunStepKey,
        artifact_payload: dict[str, Any],
    ) -> None:
        self._repository.set_step_status(run_id, key, DraftRunStepStatus.RUNNING)
        self._repository.set_step_status(
            run_id,
            key,
            DraftRunStepStatus.SUCCEEDED,
            artifact_payload=artifact_payload,
        )
