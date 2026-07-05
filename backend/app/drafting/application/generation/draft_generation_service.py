"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Protocol

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.generation.draft_generation_audit import build_draft_request_trace, build_draft_result_trace
from backend.app.drafting.application.generation.draft_prompt_builder import build_draft_prompt_messages
from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_draft_adapter import OpenRouterDraftAdapter
from backend.app.settings import BackendSettings


class DraftGenerationResult(Protocol):
    draft: GeneratedDraft
    raw_response: dict[str, object]


class DraftGenerationService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterDraftAdapter,
        deterministic_draft_service: DeterministicDraftService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_draft_service = deterministic_draft_service

    def generate(self, request: DraftGenerationRequest) -> tuple[GeneratedDraft, AiRun]:
        openrouter_status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if openrouter_status.configured else AiRunProvider.DETERMINISTIC
        model = self._settings.openrouter_default_model if openrouter_status.configured else None
        messages = build_draft_prompt_messages(request)
        request_payload = build_draft_request_trace(
            request,
            provider=provider,
            model=model,
            messages=messages,
        )
        if not openrouter_status.configured:
            draft = self._deterministic_draft_service.create_draft(request)
            return draft, self._create_fallback_run(
                request_payload=request_payload,
                draft=draft,
                provider=AiRunProvider.DETERMINISTIC,
                model=None,
                error="OpenRouter is not configured",
            )

        try:
            result = self._openrouter_adapter.generate(self._settings, request, messages)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=self._settings.openrouter_default_model,
                request_payload=request_payload,
                result_payload=build_draft_result_trace(
                    result.draft,
                    provider_response=result.raw_response,
                ),
                fallback_used=False,
            )
            return result.draft, run
        except Exception as exc:
            draft = self._deterministic_draft_service.create_draft(request)
            return draft, self._create_fallback_run(
                request_payload=request_payload,
                draft=draft,
                provider=AiRunProvider.OPENROUTER,
                model=self._settings.openrouter_default_model,
                error=self._safe_error(exc),
            )

    def _create_fallback_run(
        self,
        *,
        request_payload: dict[str, object],
        draft: GeneratedDraft,
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> AiRun:
        return self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_draft_result_trace(
                draft,
                provider_response=None,
                fallback="deterministic",
            ),
            fallback_used=True,
            error=error,
        )

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"
