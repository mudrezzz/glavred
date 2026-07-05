"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.disabled_public_search_adapter import DisabledPublicSearchAdapter
from backend.app.drafting.application.evidence.public_evidence_ports import (
    DisabledPublicUrlReader,
    PublicSearchAdapter,
    PublicUrlReadResult,
    PublicUrlReader,
)
from backend.app.drafting.application.evidence.public_evidence_query_builder import build_public_evidence_search_task
from backend.app.drafting.application.evidence.public_evidence_budgeting import budget_public_evidence_tasks, trim_public_evidence_items
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.domain.draft_public_evidence import (
    PublicEvidenceAllowedUse,
    PublicEvidenceAttempt,
    PublicEvidenceAttemptStatus,
    PublicEvidenceBatch,
    PublicEvidenceItem,
    PublicEvidenceWarning,
)


class PublicEvidenceRetrievalService:
    def __init__(
        self,
        *,
        url_reader: PublicUrlReader | None = None,
        search_adapter: PublicSearchAdapter | None = None,
    ) -> None:
        self._url_reader = url_reader or DisabledPublicUrlReader()
        self._search_adapter = search_adapter or DisabledPublicSearchAdapter()

    def retrieve(
        self,
        *,
        source_intent_artifact: dict[str, Any],
        context_artifact: dict[str, Any] | None = None,
        progress: DraftRunStepOperationSink | None = None,
    ) -> PublicEvidenceBatch:
        attempts: list[PublicEvidenceAttempt] = []
        items: list[PublicEvidenceItem] = []
        warnings: list[PublicEvidenceWarning] = []
        ai_run_ids: list[str] = []
        metadata: dict[str, Any] = {"searchProvider": "notConfigured"}
        tasks, skipped_attempts, skipped_warnings, budget_trace = budget_public_evidence_tasks(_tasks(source_intent_artifact), context_artifact)
        attempts.extend(skipped_attempts)
        warnings.extend(skipped_warnings)
        metadata["budgetTrace"] = budget_trace
        for task in tasks:
            kind = str(task.get("kind") or "")
            target = str(task.get("target") or task.get("instruction") or "").strip()
            task_id = _optional_str(task.get("id"))
            item_id = _optional_str(task.get("sourceIntentItemId"))
            if kind == "readUrl":
                operation_id = _attempt_id("url", task_id, item_id)
                progress.start_operation(operation_id, kind="readUrl", label=f"Read URL: {target}", target=target) if progress else None
                attempt, item, warning = self._read_url(target, task_id=task_id, source_intent_item_id=item_id)
                attempts.append(attempt)
                if item:
                    items.append(item)
                if warning:
                    warnings.append(warning)
                    progress.fail_operation(operation_id, warning.message) if progress else None
                else:
                    progress.complete_operation(operation_id) if progress else None
            elif kind in {"findPublicSources", "verifyClaim"}:
                search_task = build_public_evidence_search_task(
                    task,
                    source_intent_artifact=source_intent_artifact,
                    context_artifact=context_artifact,
                )
                operation_id = _attempt_id("search", task_id, item_id)
                progress.start_operation(
                    operation_id,
                    kind=kind,
                    label=_search_label(kind, search_task.query),
                    target=search_task.query,
                ) if progress else None
                search_result = self._search_adapter.search(search_task)
                attempts.extend(search_result.attempts)
                items.extend(search_result.items)
                warnings.extend(search_result.warnings)
                ai_run_ids.extend(run_id for run_id in search_result.ai_run_ids if run_id not in ai_run_ids)
                metadata.update(search_result.metadata)
                ai_run_id = search_result.ai_run_ids[-1] if search_result.ai_run_ids else None
                if _has_failed_search(search_result.attempts):
                    error = _first_attempt_error(search_result.attempts) or "Public search did not produce usable evidence."
                    progress.fail_operation(operation_id, error, ai_run_id=ai_run_id) if progress else None
                else:
                    progress.complete_operation(operation_id, ai_run_id=ai_run_id) if progress else None
            elif kind:
                operation_id = _attempt_id("skip", task_id, item_id)
                progress.start_operation(operation_id, kind=kind, label=f"Skip retrieval: {kind}", target=target) if progress else None
                attempts.append(PublicEvidenceAttempt(
                    id=operation_id,
                    task_id=task_id,
                    source_intent_item_id=item_id,
                    kind=kind,
                    target=target,
                    status=PublicEvidenceAttemptStatus.SKIPPED,
                    notes=["Research task does not require public retrieval in v1."],
                ))
                progress.complete_operation(operation_id, notes=["Task does not require public retrieval in v1."]) if progress else None
        items, trim_warnings, trim_metadata = trim_public_evidence_items(items, context_artifact)
        warnings.extend(trim_warnings)
        metadata.update(trim_metadata)
        if not attempts:
            warnings.append(PublicEvidenceWarning(code="no-public-retrieval-tasks", message="No URL or public search tasks were available."))
        metadata.update({"itemCount": len(items), "attemptCount": len(attempts)})
        return PublicEvidenceBatch(
            source="publicEvidenceRetrievalV1",
            attempts=attempts,
            items=items,
            warnings=warnings,
            metadata=metadata,
            ai_run_ids=ai_run_ids,
        )

    def _read_url(
        self,
        target: str,
        *,
        task_id: str | None,
        source_intent_item_id: str | None,
    ) -> tuple[PublicEvidenceAttempt, PublicEvidenceItem | None, PublicEvidenceWarning | None]:
        attempt_id = _attempt_id("url", task_id, source_intent_item_id)
        try:
            result = self._url_reader.read(target)
            item = PublicEvidenceItem(
                id=f"public-evidence-{attempt_id}",
                attempt_id=attempt_id,
                source_url=result.final_url or result.url,
                source_title=result.title or result.url,
                snippet=_truncate(result.text, 700),
                text_summary=_truncate(result.text, 1200),
                provenance="urlRead",
                confidence="medium",
                allowed_use=PublicEvidenceAllowedUse.NEEDS_QUALIFICATION,
                extraction_notes=["URL was read directly; claims require later ledger merge and validation."],
            )
            return (PublicEvidenceAttempt(
                id=attempt_id,
                task_id=task_id,
                source_intent_item_id=source_intent_item_id,
                kind="readUrl",
                target=target,
                status=PublicEvidenceAttemptStatus.SUCCEEDED,
                notes=["URL read succeeded."],
            ), item, None)
        except Exception as exc:
            error = _safe_error(exc)
            return (PublicEvidenceAttempt(
                id=attempt_id,
                task_id=task_id,
                source_intent_item_id=source_intent_item_id,
                kind="readUrl",
                target=target,
                status=PublicEvidenceAttemptStatus.FAILED,
                notes=["URL read failed; no evidence item was created."],
                error=error,
            ), None, PublicEvidenceWarning(code="url-read-failed", message=error, target=target))


def _tasks(source_intent_artifact: dict[str, Any]) -> list[dict[str, Any]]:
    research_plan = source_intent_artifact.get("researchPlan")
    if not isinstance(research_plan, dict):
        return []
    tasks = research_plan.get("verificationTasks")
    return [task for task in tasks if isinstance(task, dict)] if isinstance(tasks, list) else []


def _attempt_id(prefix: str, task_id: str | None, source_intent_item_id: str | None) -> str:
    suffix = task_id or source_intent_item_id or "unlinked"
    return f"{prefix}-{suffix}"


def _optional_str(value: Any) -> str | None:
    return str(value) if value else None


def _truncate(value: str, limit: int) -> str:
    cleaned = " ".join(value.split())
    return cleaned[:limit].rstrip()


def _safe_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {str(error)[:180]}"


def _search_label(kind: str, query: str) -> str:
    prefix = "Search public sources" if kind == "findPublicSources" else "Verify claim"
    return f"{prefix}: {query[:90]}"


def _has_failed_search(attempts: list[PublicEvidenceAttempt]) -> bool:
    return bool(attempts) and all(attempt.status == PublicEvidenceAttemptStatus.FAILED for attempt in attempts)


def _first_attempt_error(attempts: list[PublicEvidenceAttempt]) -> str | None:
    for attempt in attempts:
        if attempt.error:
            return attempt.error
    return None


__all__ = (
    'PublicEvidenceRetrievalService',
)
