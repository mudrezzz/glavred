import json
from dataclasses import dataclass
from typing import Any, Protocol

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.application.draft_human_comment_quality_service import DraftHumanCommentQualityService
from backend.app.application.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.application.draft_provider_error_utils import raw_response_excerpt, safe_provider_error
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_run import DraftRun
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings

HUMAN_COMMENT_REVISION_KEYS = {"title", "body", "revisionSummary"}


class OpenRouterJsonStepAdapter(Protocol):
    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> Any: ...


class DraftRunLookup(Protocol):
    def get(self, run_id: str) -> DraftRun | None: ...


@dataclass(frozen=True)
class HumanCommentRevisionResult:
    title: str
    body: str
    revision_summary: str
    ai_run_id: str | None
    selected_model: str | None
    attempts: list[dict[str, Any]]
    quality_check: dict[str, Any]


class HumanCommentRevisionUnavailable(RuntimeError):
    def __init__(self, message: str, *, attempts: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.attempts = attempts or []


class DraftHumanCommentRevisionService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        draft_run_repository: DraftRunLookup,
        quality_service: DraftHumanCommentQualityService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._draft_run_repository = draft_run_repository
        self._quality_service = quality_service

    def revise(
        self,
        *,
        draft_run_id: str | None,
        current_version: dict[str, Any],
        editor_comment: str,
    ) -> HumanCommentRevisionResult:
        comment = editor_comment.strip()
        if not comment:
            raise HumanCommentRevisionUnavailable("Editor comment is required")
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            raise HumanCommentRevisionUnavailable("OpenRouter is not configured")

        trace_context = self._compact_trace_context(draft_run_id)
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        primary_model = primary_selection.model or self._settings.openrouter_default_model

        for attempt in build_json_step_attempts(
            primary_model=primary_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                current_version=current_version,
                editor_comment=comment,
                trace_context=trace_context,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                payload = result["payload"]
                revised_version = {
                    "id": current_version.get("id"),
                    "versionNumber": current_version.get("versionNumber"),
                    "title": str(payload.get("title") or "").strip(),
                    "body": str(payload.get("body") or "").strip(),
                }
                quality_check = self._quality_service.check(
                    base_version=current_version,
                    revised_version=revised_version,
                    editor_comment=comment,
                    trace_context=trace_context,
                )
                return HumanCommentRevisionResult(
                    title=revised_version["title"],
                    body=revised_version["body"],
                    revision_summary=str(payload.get("revisionSummary") or "").strip(),
                    ai_run_id=result["attempt"].get("aiRunId"),
                    selected_model=result["attempt"].get("selectedModel"),
                    attempts=attempts,
                    quality_check=quality_check.to_payload(),
                )
            repair_context = {
                "previousAttempt": result["attempt"],
                "requiredShape": "title, body, revisionSummary"
            }

        raise HumanCommentRevisionUnavailable(
            "Human comment revision failed after all JSON attempts",
            attempts=attempts,
        )

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        current_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(
            role=DraftModelRole.WRITER,
            model=attempt.model,
            backup=attempt.backup,
            primary_selection=primary_selection,
        )
        generation_params = generation_params_for_attempt(
            self._settings,
            primary_profile=GenerationParamProfile.REVISION,
            attempt=attempt,
        )
        attempt_payload = {
            "label": attempt.label,
            "model": attempt.model,
            "repair": attempt.repair,
            "backup": attempt.backup,
            **selection.to_payload(),
        }
        messages = build_human_comment_revision_messages(
            current_version=current_version,
            editor_comment=editor_comment,
            trace_context=trace_context,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {
            "draftRunStep": "humanCommentRevision",
            "attempt": attempt_payload,
            "currentVersion": _compact_version(current_version),
            "editorComment": editor_comment,
            "traceContext": trace_context,
            "messages": messages,
            "generationParams": generation_params.to_payload(),
            **selection.to_payload(),
        }
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=HUMAN_COMMENT_REVISION_KEYS,
                temperature=generation_params.temperature,
                top_p=generation_params.top_p,
                model=attempt.model,
            )
            title = str(result.payload.get("title") or "").strip()
            body = str(result.payload.get("body") or "").strip()
            if not title or not body:
                raise ValueError("Human comment revision title/body is empty")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={
                    "draftRunStep": "humanCommentRevision",
                    "attempt": attempt_payload,
                    "result": result.payload,
                    "providerResponse": result.raw_response,
                },
                fallback_used=False,
            )
            return {"accepted": True, "payload": result.payload, "attempt": _attempt_record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            error = safe_provider_error(self._settings, exc)
            result_payload: dict[str, Any] = {
                "draftRunStep": "humanCommentRevision",
                "attempt": attempt_payload,
                "result": {},
            }
            excerpt = raw_response_excerpt(exc)
            if excerpt:
                result_payload["rawResponseExcerpt"] = excerpt
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=result_payload,
                fallback_used=False,
                error=error,
            )
            return {"accepted": False, "payload": {}, "attempt": _attempt_record(attempt, run.id, "error", selection.to_payload(), error)}

    def _compact_trace_context(self, draft_run_id: str | None) -> dict[str, Any]:
        if not draft_run_id:
            return {"draftRunId": None, "traceStatus": "unavailable"}
        run = self._draft_run_repository.get(draft_run_id)
        if not run:
            return {"draftRunId": draft_run_id, "traceStatus": "unavailable"}
        validation = _step_artifact(run, "validation")
        ranking_revision = _record(validation.get("rankingRevision"))
        return {
            "draftRunId": draft_run_id,
            "traceStatus": "available",
            "finalQualityGate": ranking_revision.get("finalQualityGate"),
            "revisionLoop": ranking_revision.get("revisionLoop"),
            "alternativeAngleTournament": validation.get("alternativeAngleTournament"),
            "validationSummary": _validation_summary(validation),
        }


def build_human_comment_revision_messages(
    *,
    current_version: dict[str, Any],
    editor_comment: str,
    trace_context: dict[str, Any],
    repair_context: dict[str, Any] | None,
) -> list[dict[str, str]]:
    system = (
        "You are Glavred's post-run human editor revision writer. Return strict JSON only. "
        "Revise the current public post according to the human editor comment. Preserve useful source markers, "
        "do not invent new claims, do not expose internal pipeline jargon such as SourceLedger, publicEvidence, "
        "validators, RuleRegistry, or PostContract, and keep the text publishable."
    )
    payload = {
        "task": "Create one improved draft version from a human editor comment.",
        "requiredJson": {"title": "string", "body": "string", "revisionSummary": "string"},
        "currentVersion": _compact_version(current_version),
        "editorComment": editor_comment,
        "machineTraceContext": trace_context,
        "repairContext": repair_context,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _step_artifact(run: DraftRun, key: str) -> dict[str, Any]:
    for step in run.steps:
        if step.key.value == key and isinstance(step.artifact_payload, dict):
            return step.artifact_payload
    return {}


def _validation_summary(validation: dict[str, Any]) -> dict[str, Any]:
    candidate_reports = validation.get("candidateReports")
    llm_report = _record(validation.get("llmValidationReport"))
    return {
        "deterministicCandidateCount": len(candidate_reports) if isinstance(candidate_reports, list) else 0,
        "llmCandidateCount": len(llm_report.get("candidateReports")) if isinstance(llm_report.get("candidateReports"), list) else 0,
        "status": validation.get("status") or llm_report.get("status"),
    }


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _compact_version(current_version: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": current_version.get("id"),
        "versionNumber": current_version.get("versionNumber"),
        "title": current_version.get("title"),
        "body": current_version.get("body"),
    }


def _attempt_record(
    attempt: JsonStepAttempt,
    ai_run_id: str,
    status: str,
    model_selection: dict[str, Any],
    validation: str | None = None,
) -> dict[str, Any]:
    record = {
        "label": attempt.label,
        "model": attempt.model,
        "status": status,
        "aiRunId": ai_run_id,
        "backup": attempt.backup,
        **model_selection,
    }
    if validation:
        record["validation"] = validation
    return record
