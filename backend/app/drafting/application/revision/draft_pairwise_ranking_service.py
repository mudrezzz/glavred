"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.revision.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.drafting.application.revision.draft_pairwise_ranking_prompts import (
    PAIRWISE_RANKING_KEYS,
    PAIRWISE_RANKING_TEMPERATURE,
    PairwiseRankingPromptBuilder,
)
from backend.app.drafting.application.revision.draft_pairwise_ranking_payloads import PairwiseRankingPayloadMapper
from backend.app.drafting.application.revision.pairwise_comparison_identity import (
    PairwisePayloadValidationError,
)
from backend.app.drafting.application.revision.pairwise_ranking_fallback_factory import PairwiseRankingFallbackFactory
from backend.app.drafting.application.revision.draft_pairwise_ranking_dossier_attempt import PairwiseRankingDossierAttemptBuilder
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_ranking_revision import PairwiseRankingReport
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier
from backend.app.drafting.application.dossiers.provider_dossier_context_snapshot import ProviderDossierContextSnapshotFactory
from backend.app.drafting.application.dossiers.provider_dossier_factories import RankingDossierFactory


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
        self._fallback_reports = PairwiseRankingFallbackFactory(self._fallback)
        self._prompt_builder = prompt_builder or PairwiseRankingPromptBuilder()
        self._payloads = payload_mapper or PairwiseRankingPayloadMapper()
        self._attempt_builder = PairwiseRankingDossierAttemptBuilder(prompt_builder=self._prompt_builder)

    def rank(
        self,
        *,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        provider_dossier: ProviderDossier | None = None,
    ) -> PairwiseRankingReport:
        if provider_dossier is None:
            access = ProviderDossierContextSnapshotFactory().access(
                draft_artifact=draft_artifact,
                validation_report=validation_report,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                review_context={"candidates": draft_artifact.get("candidates", []), "validationReport": validation_report},
            )
            provider_dossier = RankingDossierFactory(access).build()
        if provider_dossier is None or provider_dossier.readiness_status is DossierReadinessStatus.BLOCKED:
            reason = "dossier-context-unavailable" if provider_dossier is None else "ranking-dossier-blocked"
            return self._fallback_reports.build(draft_artifact=draft_artifact, validation_report=validation_report, attempts=[], warning=reason)
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return self._fallback_reports.build(draft_artifact=draft_artifact, validation_report=validation_report, attempts=[], warning="provider-unconfigured")
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.REVIEW)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, primary_selection, draft_artifact, validation_report, provider_dossier, repair_context)
            attempts.append(result["attempt"])
            if result["accepted"]:
                report = self._payloads.report_from_payload(
                    result["payload"],
                    attempts,
                    [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
                    result["comparisonIdentity"],
                )
                if report.decision.winner_candidate_id:
                    return report
            repair_context = {
                "errorType": "schemaFailure",
                "validationDetails": result.get("validationDetails") or {},
                "requiredShape": "winnerCandidateId, reason, comparisons[], editorialDimensionScores[]",
            }
        return self._fallback_reports.build(draft_artifact=draft_artifact, validation_report=validation_report, attempts=attempts, warning="pairwise-ranking-provider-failed")

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        provider_dossier: ProviderDossier,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.REVIEW, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        prepared = self._attempt_builder.prepare(
            dossier=provider_dossier,
            model=attempt.model,
            attempt=attempt_payload,
            model_selection=selection.to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            repair_context=repair_context if attempt.repair else None,
        )
        messages = prepared.messages
        request_payload = prepared.request_payload
        if prepared.blocked_reason:
            return self._attempt_error(attempt, request_payload, prepared.blocked_reason, {
                "code": prepared.blocked_reason,
                "messageCharCount": request_payload.get("messageCharCount"),
            })
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=PAIRWISE_RANKING_KEYS,
                temperature=PAIRWISE_RANKING_TEMPERATURE,
                model=attempt.model,
            )
            visible_candidates = request_payload.get("providerInput", {}).get("candidates", [])
            candidate_ids = [str(item.get("id")) for item in visible_candidates if isinstance(item, dict) and item.get("id")]
            comparison_identity = self._payloads.validate_pairwise_payload(result.payload, candidate_ids)
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
                "comparisonIdentity": comparison_identity,
                "attempt": self._payloads.attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                    editorial_dimension_scores=self._payloads.dimension_scores(result.payload),
                ),
            }
        except PairwisePayloadValidationError as exc:
            return self._attempt_error(attempt, request_payload, "schemaFailure", exc.to_payload())
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, self._safe_error(exc))

    def _attempt_error(
        self,
        attempt: JsonStepAttempt,
        request_payload: dict[str, Any],
        error: str,
        validation_details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload={
                "draftRunStep": "pairwiseRanking",
                "attempt": {"label": attempt.label, "model": attempt.model},
                "result": {},
                "validationDetails": validation_details or {},
            },
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {
            "accepted": False,
            "payload": {},
            "validationDetails": validation_details or {},
            "attempt": self._payloads.attempt_record(attempt, run.id, "error", selection, error),
        }

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"
