"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import complete_drafting_json
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.revision.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.drafting.application.revision.draft_pairwise_ranking_prompts import (
    PAIRWISE_RANKING_KEYS,
    PAIRWISE_RANKING_TEMPERATURE,
    PairwiseRankingPromptBuilder,
)
from backend.app.drafting.application.revision.draft_pairwise_ranking_payloads import PairwiseRankingPayloadMapper
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.drafting.application.artifacts.draft_article_memory_service import context_pack_from_payload
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_ranking_revision import PairwiseRankingReport, RankingDecision
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftPairwiseRankingService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
        fallback_ranker: DeterministicPairwiseRanker | None = None,
        prompt_builder: PairwiseRankingPromptBuilder | None = None,
        payload_mapper: PairwiseRankingPayloadMapper | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._fallback = fallback_ranker or DeterministicPairwiseRanker()
        self._prompt_builder = prompt_builder or PairwiseRankingPromptBuilder()
        self._payloads = payload_mapper or PairwiseRankingPayloadMapper()

    def rank(
        self,
        *,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> PairwiseRankingReport:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return self._fallback_report(draft_artifact, validation_report, [], "provider-unconfigured")
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.REVIEW)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, primary_selection, draft_artifact, validation_report, context_artifact, rule_pack, material_plan, repair_context)
            attempts.append(result["attempt"])
            if result["accepted"]:
                report = self._payloads.report_from_payload(result["payload"], attempts, [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")])
                if report.decision.winner_candidate_id:
                    return report
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "winnerCandidateId, reason, comparisons[]"}
        return self._fallback_report(draft_artifact, validation_report, attempts, "pairwise-ranking-provider-failed")

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.REVIEW, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        context_pack = context_pack_from_payload(context_artifact, DraftModelRole.REVIEW)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        messages = self._prompt_builder.build_messages(
            draft_artifact=draft_artifact,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {"draftRunStep": "pairwiseRanking", "attempt": attempt_payload, "contextPack": context_pack, "messages": messages, **selection.to_payload()}
        try:
            result = complete_drafting_json(self._openrouter_adapter,
                settings=self._settings,
                messages=messages,
                expected_keys=PAIRWISE_RANKING_KEYS,
                temperature=PAIRWISE_RANKING_TEMPERATURE,
                model=attempt.model,
            )
            self._payloads.validate_pairwise_payload(result.payload, draft_artifact)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "pairwiseRanking", "attempt": attempt_payload, "result": result.payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {
                "accepted": True,
                "payload": result.payload,
                    "attempt": self._payloads.attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                    editorial_dimension_scores=self._payloads.dimension_scores(result.payload),
                ),
            }
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, self._safe_error(exc))

    def _attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload={"draftRunStep": "pairwiseRanking", "attempt": {"label": attempt.label, "model": attempt.model}, "result": {}},
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {"accepted": False, "payload": {}, "attempt": self._payloads.attempt_record(attempt, run.id, "error", selection, error)}

    def _fallback_report(self, draft_artifact: dict[str, Any], validation_report: dict[str, Any], attempts: list[dict[str, Any]], warning: str) -> PairwiseRankingReport:
        fallback = self._fallback.rank(draft_artifact=draft_artifact, validation_report=validation_report)
        decision = RankingDecision(
            winner_candidate_id=fallback.decision.winner_candidate_id,
            reason=fallback.decision.reason,
            source="deterministicFallback",
            fallback_used=True,
            warnings=[*fallback.decision.warnings, warning],
        )
        return PairwiseRankingReport(
            decision=decision,
            comparisons=fallback.comparisons,
            attempts=[*attempts, {"label": "deterministic-fallback", "model": "deterministic", "status": "fallback", "backup": False, "validation": warning}],
            ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
        )

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"
