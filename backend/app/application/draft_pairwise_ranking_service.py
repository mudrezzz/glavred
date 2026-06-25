from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.application.draft_pairwise_ranking_prompts import (
    PAIRWISE_RANKING_KEYS,
    PAIRWISE_RANKING_TEMPERATURE,
    build_pairwise_ranking_messages,
)
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_ranking_revision import PairwiseComparison, PairwiseRankingReport, RankingDecision
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
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._fallback = fallback_ranker or DeterministicPairwiseRanker()

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
        for attempt in build_json_step_attempts(
            primary_model=self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, draft_artifact, validation_report, context_artifact, rule_pack, material_plan, repair_context)
            attempts.append(result["attempt"])
            if result["accepted"]:
                report = _report_from_payload(result["payload"], draft_artifact, attempts, [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")])
                if report.decision.winner_candidate_id:
                    return report
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "winnerCandidateId, reason, comparisons[]"}
        return self._fallback_report(draft_artifact, validation_report, attempts, "pairwise-ranking-provider-failed")

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup}
        messages = build_pairwise_ranking_messages(
            draft_artifact=draft_artifact,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {"draftRunStep": "pairwiseRanking", "attempt": attempt_payload, "messages": messages}
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=PAIRWISE_RANKING_KEYS,
                temperature=PAIRWISE_RANKING_TEMPERATURE,
                model=attempt.model,
            )
            _validate_payload(result.payload, draft_artifact)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "pairwiseRanking", "attempt": attempt_payload, "result": result.payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {"accepted": True, "payload": result.payload, "attempt": _attempt_record(attempt, run.id, "accepted")}
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
        return {"accepted": False, "payload": {}, "attempt": _attempt_record(attempt, run.id, "error", error)}

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


def _report_from_payload(payload: dict[str, Any], draft_artifact: dict[str, Any], attempts: list[dict[str, Any]], ai_run_ids: list[str]) -> PairwiseRankingReport:
    return PairwiseRankingReport(
        decision=RankingDecision(
            winner_candidate_id=str(payload.get("winnerCandidateId") or ""),
            reason=str(payload.get("reason") or "Selected by provider pairwise ranking."),
            source="openrouter",
        ),
        comparisons=[
            PairwiseComparison(
                left_candidate_id=str(item.get("leftCandidateId") or ""),
                right_candidate_id=str(item.get("rightCandidateId") or ""),
                winner_candidate_id=str(item.get("winnerCandidateId") or ""),
                reason=str(item.get("reason") or ""),
                decisive_factors=[str(value) for value in item.get("decisiveFactors", []) if str(value).strip()] if isinstance(item.get("decisiveFactors"), list) else [],
            )
            for item in payload.get("comparisons", [])
            if isinstance(item, dict)
        ],
        attempts=attempts,
        ai_run_ids=ai_run_ids,
    )


def _validate_payload(payload: dict[str, Any], draft_artifact: dict[str, Any]) -> None:
    candidate_ids = {str(candidate.get("id")) for candidate in draft_artifact.get("candidates", []) if isinstance(candidate, dict)}
    winner = str(payload.get("winnerCandidateId") or "")
    if winner not in candidate_ids:
        raise ValueError("Pairwise ranking winnerCandidateId is not a known candidate")
    if not isinstance(payload.get("comparisons"), list):
        raise ValueError("Pairwise ranking comparisons is not a list")


def _attempt_record(attempt: JsonStepAttempt, ai_run_id: str, status: str, validation: Any | None = None) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup}
    if validation:
        record["validation"] = validation
    return record
