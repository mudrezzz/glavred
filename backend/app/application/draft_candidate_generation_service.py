from datetime import UTC, datetime
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.application.draft_candidate_audit import build_candidate_request_trace, build_candidate_result_trace
from backend.app.application.draft_candidate_direction_service import DraftCandidateDirectionService
from backend.app.application.draft_candidate_prompts import CANDIDATE_KEYS, CANDIDATE_TEMPERATURE, build_draft_candidate_messages
from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.application.draft_candidate_selection_service import DraftCandidateSelectionService
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_material_plan_service import OpenRouterJsonStepAdapter
from backend.app.application.draft_model_role_resolver import select_model_for_role, unconfigured_model_selection
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_candidates import DraftCandidate, DraftCandidateDirection, candidate_from_payload
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftCandidateGenerationService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        direction_service: DraftCandidateDirectionService,
        deterministic_candidate_service: DeterministicDraftCandidateService,
        selection_service: DraftCandidateSelectionService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._direction_service = direction_service
        self._deterministic_candidate_service = deterministic_candidate_service
        self._selection_service = selection_service

    def create(
        self,
        *,
        request: DraftGenerationRequest,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        rhetorical_plans: dict[str, Any] | None = None,
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftCandidateGenerationResult:
        directions = self._direction_service.create_directions(
            context_summary=context_summary,
            rule_pack=rule_pack,
            draft_strategy=draft_strategy,
            rhetorical_plans=rhetorical_plans,
        )
        candidate_payloads: list[dict[str, Any]] = []
        ai_run_ids: list[str] = []
        fallback_used = False
        for direction in directions:
            operation_id = f"draft-candidate-{direction.id}"
            if progress:
                progress.start_operation(
                    operation_id,
                    kind="draftCandidate",
                    label=f"Generate candidate: {direction.title}",
                    target=direction.rhetorical_plan_id or direction.id,
                )
            payload, ai_run_id = self._create_one(request, context_summary, rule_pack, material_plan, draft_strategy, direction)
            candidate_payloads.append(payload)
            if ai_run_id:
                ai_run_ids.append(ai_run_id)
            if progress:
                notes = [f"source={payload.get('source')}", f"fallback={payload.get('fallbackUsed')}"]
                progress.complete_operation(operation_id, ai_run_id=ai_run_id, notes=notes)
            fallback_used = fallback_used or bool(payload.get("fallbackUsed"))
        selection = self._selection_service.select(candidate_payloads).to_payload()
        selected_id = selection.get("selectedCandidateId")
        selected = _selected_candidate(candidate_payloads, selected_id) if selected_id else None
        artifact = {
            "source": _artifact_source(candidate_payloads),
            "fallbackUsed": fallback_used,
            "aiRunIds": ai_run_ids,
            "rhetoricalPlanSet": rhetorical_plans,
            "directions": [direction.to_payload() for direction in directions],
            "candidates": candidate_payloads,
            "selection": selection,
        }
        return DraftCandidateGenerationResult(
            artifact_payload=artifact,
            final_draft=_candidate_to_draft(request, selected) if selected else None,
            ai_run_ids=ai_run_ids,
        )

    def _create_one(
        self,
        request: DraftGenerationRequest,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        direction: DraftCandidateDirection,
    ) -> tuple[dict[str, Any], str | None]:
        messages = build_draft_candidate_messages(
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            direction=direction,
        )
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        selection = select_model_for_role(self._settings, DraftModelRole.WRITER) if status.configured else unconfigured_model_selection(DraftModelRole.WRITER)
        model = selection.model
        request_payload = build_candidate_request_trace(
            provider=provider,
            model=model,
            messages=messages,
            context_summary=context_summary,
            direction=direction,
            model_selection=selection.to_payload(),
        )
        if not status.configured:
            return self._fallback(request, direction, rule_pack, material_plan, request_payload, provider, model, "OpenRouter is not configured")
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=CANDIDATE_KEYS,
                temperature=CANDIDATE_TEMPERATURE,
                model=model,
            )
            candidate = candidate_from_payload(f"candidate-{direction.id}-{request.brief.id}", direction, result.payload)
            if not candidate.body.strip():
                raise ValueError("OpenRouter draft candidate body is empty")
            return self._complete_candidate(candidate, "openrouter", request_payload, result.raw_response, model, False, None, model_selection=selection.to_payload())
        except Exception as exc:
            return self._fallback(request, direction, rule_pack, material_plan, request_payload, AiRunProvider.OPENROUTER, model, self._safe_error(exc))

    def _fallback(
        self,
        request: DraftGenerationRequest,
        direction: DraftCandidateDirection,
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        request_payload: dict[str, Any],
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> tuple[dict[str, Any], str | None]:
        candidate = self._deterministic_candidate_service.create_candidate(
            request=request,
            direction=direction,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        model_selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return self._complete_candidate(candidate, "deterministicFallback", request_payload, None, model, True, error, provider=provider, model_selection=model_selection)

    def _complete_candidate(
        self,
        candidate: DraftCandidate,
        source: str,
        request_payload: dict[str, Any],
        provider_response: dict[str, Any] | None,
        model: str | None,
        fallback_used: bool,
        error: str | None,
        *,
        provider: AiRunProvider = AiRunProvider.OPENROUTER,
        model_selection: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], str]:
        payload = candidate.to_payload(source=source, ai_run_id=None, fallback_used=fallback_used)
        if model_selection:
            payload.update(model_selection)
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_candidate_result_trace(
                candidate_payload=payload,
                provider_response=provider_response,
                fallback="deterministic" if fallback_used else None,
            ),
            fallback_used=fallback_used,
            error=error,
        )
        final_payload = candidate.to_payload(source=source, ai_run_id=run.id, fallback_used=fallback_used)
        if model_selection:
            final_payload.update(model_selection)
        return final_payload, run.id

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _selected_candidate(candidates: list[dict[str, Any]], selected_id: Any) -> dict[str, Any]:
    return next(candidate for candidate in candidates if candidate["id"] == selected_id)


def _candidate_to_draft(request: DraftGenerationRequest, candidate: dict[str, Any]) -> GeneratedDraft:
    return GeneratedDraft(
        id=f"draft-{request.brief.id}",
        brief_id=request.brief.id,
        title=str(candidate["title"]),
        body=str(candidate["body"]),
        version=1,
        status="draft",
        updated_at=datetime.now(UTC).isoformat(),
    )


def _artifact_source(candidates: list[dict[str, Any]]) -> str:
    sources = {str(candidate.get("source")) for candidate in candidates}
    return sources.pop() if len(sources) == 1 else "mixed"
