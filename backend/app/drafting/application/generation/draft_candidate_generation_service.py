"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from datetime import UTC, datetime
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.drafting.application.generation.draft_candidate_direction_service import DraftCandidateDirectionService
from backend.app.drafting.application.generation.draft_candidate_provider_service import DraftCandidateProviderService
from backend.app.drafting.application.generation.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.drafting.application.generation.draft_candidate_selection_service import DraftCandidateSelectionService
from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.domain.draft_candidates import DraftCandidateDirection
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
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
        self._provider_service = DraftCandidateProviderService(
            settings=settings,
            ai_run_service=ai_run_service,
            openrouter_validator=openrouter_validator,
            openrouter_adapter=openrouter_adapter,
            deterministic_candidate_service=deterministic_candidate_service,
        )

    def create(
        self,
        *,
        request: DraftGenerationRequest,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        rhetorical_plans: dict[str, Any] | None = None,
        context_pack: dict[str, Any] | None = None,
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftCandidateGenerationResult:
        directions = self._direction_service.create_directions(
            context_summary=context_summary,
            rule_pack=rule_pack,
            draft_strategy=draft_strategy,
            rhetorical_plans=rhetorical_plans,
        )
        budget = budget_from_context(context_summary)
        if len(directions) > budget.caps.max_draft_candidates:
            directions = directions[:budget.caps.max_draft_candidates]
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
            payload, candidate_ai_run_ids = self._provider_service.create_one(
                request=request,
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                direction=direction,
                context_pack=context_pack,
            )
            candidate_payloads.append(payload)
            ai_run_ids.extend(candidate_ai_run_ids)
            if progress:
                notes = [f"source={payload.get('source')}", f"fallback={payload.get('fallbackUsed')}"]
                progress.complete_operation(operation_id, ai_run_id=candidate_ai_run_ids[-1] if candidate_ai_run_ids else None, notes=notes)
            fallback_used = fallback_used or bool(payload.get("fallbackUsed"))
        selection = self._selection_service.select(candidate_payloads).to_payload()
        selected_id = selection.get("selectedCandidateId")
        selected = _selected_candidate(candidate_payloads, selected_id) if selected_id else None
        artifact = {
            "source": _artifact_source(candidate_payloads),
            "fallbackUsed": fallback_used,
            "aiRunIds": ai_run_ids,
            "rhetoricalPlanSet": rhetorical_plans,
            "draftRunBudget": budget.to_payload(),
            "directions": [direction.to_payload() for direction in directions],
            "candidates": candidate_payloads,
            "selection": selection,
        }
        return DraftCandidateGenerationResult(
            artifact_payload=artifact,
            final_draft=_candidate_to_draft(request, selected) if selected else None,
            ai_run_ids=ai_run_ids,
        )


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
