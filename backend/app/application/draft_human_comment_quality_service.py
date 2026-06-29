import json
import re
from typing import Any, Protocol

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.application.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.application.draft_provider_error_utils import raw_response_excerpt, safe_provider_error
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_human_revision import HumanCommentRevisionQualityCheck, human_comment_revision_quality_not_run
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings

QUALITY_CHECK_KEYS = {
    "status",
    "commentComplianceStatus",
    "sourceIntegrityStatus",
    "publicProseStatus",
    "internalJargonLeaks",
    "regressionWarnings",
    "matchedCommentIntents",
    "missedCommentIntents",
    "summary",
}

INTERNAL_JARGON_TERMS = ["SourceLedger", "publicEvidence", "validators", "PostContract", "RuleRegistry"]
SOURCE_MARKER_CANDIDATES = [
    "B2BNotes",
    "WebProNews",
    "RAND",
    "RAND Corporation",
    "NSSG",
    "NSSG Insights",
    "Gartner",
    "McKinsey",
    "Forrester",
]


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


class DraftHumanCommentQualityService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter

    def check(
        self,
        *,
        base_version: dict[str, Any],
        revised_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
    ) -> HumanCommentRevisionQualityCheck:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return human_comment_revision_quality_not_run(reason="OpenRouter is not configured")

        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.REVIEW)
        primary_model = primary_selection.model or self._settings.openrouter_default_model

        for attempt in build_json_step_attempts(
            primary_model=primary_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                base_version=base_version,
                revised_version=revised_version,
                editor_comment=editor_comment,
                trace_context=trace_context,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                return _apply_deterministic_overlay(
                    _normalize_quality_payload(result["payload"], attempts),
                    base_body=str(base_version.get("body") or ""),
                    revised_body=str(revised_version.get("body") or ""),
                )
            repair_context = {
                "previousAttempt": result["attempt"],
                "requiredShape": ", ".join(sorted(QUALITY_CHECK_KEYS)),
            }

        return human_comment_revision_quality_not_run(
            reason="Human comment revision quality check failed after all JSON attempts",
            attempts=attempts,
        )

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        base_version: dict[str, Any],
        revised_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(
            role=DraftModelRole.REVIEW,
            model=attempt.model,
            backup=attempt.backup,
            primary_selection=primary_selection,
        )
        generation_params = generation_params_for_attempt(
            self._settings,
            primary_profile=GenerationParamProfile.JSON_REPAIR,
            attempt=attempt,
        )
        attempt_payload = {
            "label": attempt.label,
            "model": attempt.model,
            "repair": attempt.repair,
            "backup": attempt.backup,
            **selection.to_payload(),
        }
        messages = build_human_comment_quality_messages(
            base_version=base_version,
            revised_version=revised_version,
            editor_comment=editor_comment,
            trace_context=trace_context,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {
            "draftRunStep": "humanCommentRevisionQualityCheck",
            "attempt": attempt_payload,
            "baseVersion": _compact_version(base_version),
            "revisedVersion": _compact_version(revised_version),
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
                expected_keys=QUALITY_CHECK_KEYS,
                temperature=generation_params.temperature,
                top_p=generation_params.top_p,
                model=attempt.model,
            )
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={
                    "draftRunStep": "humanCommentRevisionQualityCheck",
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
                "draftRunStep": "humanCommentRevisionQualityCheck",
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


def build_human_comment_quality_messages(
    *,
    base_version: dict[str, Any],
    revised_version: dict[str, Any],
    editor_comment: str,
    trace_context: dict[str, Any],
    repair_context: dict[str, Any] | None,
) -> list[dict[str, str]]:
    system = (
        "You are Glavred's post-run human revision quality reviewer. Return strict JSON only. "
        "Evaluate whether the revised public post followed the editor comment without losing source markers, "
        "without adding internal pipeline jargon, and without becoming worse public prose."
    )
    payload = {
        "task": "Assess one human-comment revision. This is diagnostic: do not rewrite the post.",
        "requiredJson": {
            "status": "passed | warning | critical",
            "commentComplianceStatus": "passed | warning | critical",
            "sourceIntegrityStatus": "passed | warning | critical",
            "publicProseStatus": "passed | warning | critical",
            "internalJargonLeaks": ["string"],
            "regressionWarnings": ["string"],
            "matchedCommentIntents": ["string"],
            "missedCommentIntents": ["string"],
            "summary": "string",
        },
        "baseVersion": _compact_version(base_version),
        "revisedVersion": _compact_version(revised_version),
        "editorComment": editor_comment,
        "machineTraceContext": trace_context,
        "repairContext": repair_context,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _normalize_quality_payload(payload: dict[str, Any], attempts: list[dict[str, Any]]) -> HumanCommentRevisionQualityCheck:
    status = _status(payload.get("status"))
    comment_status = _status(payload.get("commentComplianceStatus"))
    source_status = _status(payload.get("sourceIntegrityStatus"))
    prose_status = _status(payload.get("publicProseStatus"))
    worst_status = _worst_status([status, comment_status, source_status, prose_status])
    return HumanCommentRevisionQualityCheck(
        status=worst_status,
        comment_compliance_status=comment_status,
        source_integrity_status=source_status,
        public_prose_status=prose_status,
        internal_jargon_leaks=_strings(payload.get("internalJargonLeaks")),
        regression_warnings=_strings(payload.get("regressionWarnings")),
        matched_comment_intents=_strings(payload.get("matchedCommentIntents")),
        missed_comment_intents=_strings(payload.get("missedCommentIntents")),
        summary=str(payload.get("summary") or "").strip(),
        attempts=attempts,
    )


def _apply_deterministic_overlay(
    check: HumanCommentRevisionQualityCheck,
    *,
    base_body: str,
    revised_body: str,
) -> HumanCommentRevisionQualityCheck:
    leaks = list(dict.fromkeys([*check.internal_jargon_leaks, *[term for term in INTERNAL_JARGON_TERMS if term in revised_body]]))
    lost_markers = [
        marker
        for marker in SOURCE_MARKER_CANDIDATES
        if _contains_marker(base_body, marker) and not _contains_marker(revised_body, marker)
    ]
    regression_warnings = list(check.regression_warnings)
    if lost_markers:
        regression_warnings.append(f"Lost visible source markers: {', '.join(lost_markers)}")
    source_status = _worse(check.source_integrity_status, "warning" if lost_markers else "passed")
    prose_status = _worse(check.public_prose_status, "warning" if leaks else "passed")
    status = _worst_status([check.status, check.comment_compliance_status, source_status, prose_status])
    return HumanCommentRevisionQualityCheck(
        status=status,
        comment_compliance_status=check.comment_compliance_status,
        source_integrity_status=source_status,
        public_prose_status=prose_status,
        internal_jargon_leaks=leaks,
        regression_warnings=regression_warnings,
        matched_comment_intents=check.matched_comment_intents,
        missed_comment_intents=check.missed_comment_intents,
        summary=check.summary,
        attempts=check.attempts,
    )


def _compact_version(version: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": version.get("id"),
        "versionNumber": version.get("versionNumber"),
        "title": version.get("title"),
        "body": version.get("body"),
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


def _status(value: Any) -> str:
    normalized = str(value or "").strip()
    return normalized if normalized in {"passed", "warning", "critical", "notRun"} else "warning"


def _worst_status(values: list[str]) -> str:
    rank = {"passed": 0, "notRun": 0, "warning": 1, "critical": 2}
    return max(values, key=lambda item: rank.get(item, 1))


def _worse(left: str, right: str) -> str:
    return _worst_status([left, right])


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _contains_marker(body: str, marker: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(marker)}(?!\w)", body, flags=re.IGNORECASE) is not None
