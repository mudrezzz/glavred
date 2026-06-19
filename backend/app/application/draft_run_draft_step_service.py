from typing import Any

from backend.app.application.draft_run_payloads import draft_to_payload
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


class LegacyDraftStepResult:
    def __init__(self, artifact_payload: dict[str, Any], final_draft: GeneratedDraft, ai_run_ids: list[str]) -> None:
        self.artifact_payload = artifact_payload
        self.final_draft = final_draft
        self.ai_run_ids = ai_run_ids


class LegacyDraftStepService:
    def __init__(self, deterministic_draft_service: Any) -> None:
        self._deterministic_draft_service = deterministic_draft_service

    def create(self, *, request: DraftGenerationRequest, **kwargs: Any) -> LegacyDraftStepResult:
        draft = self._deterministic_draft_service.create_draft(request)
        return LegacyDraftStepResult(
            artifact_payload={"draft": draft_to_payload(draft)},
            final_draft=draft,
            ai_run_ids=[],
        )
