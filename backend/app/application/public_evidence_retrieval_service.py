from dataclasses import dataclass
from typing import Any, Protocol

from backend.app.domain.draft_public_evidence import (
    PublicEvidenceAllowedUse,
    PublicEvidenceAttempt,
    PublicEvidenceAttemptStatus,
    PublicEvidenceBatch,
    PublicEvidenceItem,
    PublicEvidenceWarning,
)


@dataclass(frozen=True)
class PublicUrlReadResult:
    url: str
    title: str
    text: str
    final_url: str | None = None


class PublicUrlReader(Protocol):
    def read(self, url: str) -> PublicUrlReadResult: ...


class PublicSearchAdapter(Protocol):
    def search(self, target: str, *, task_id: str | None, source_intent_item_id: str | None) -> PublicEvidenceAttempt: ...


class DisabledPublicUrlReader:
    def read(self, url: str) -> PublicUrlReadResult:
        raise RuntimeError("Public URL reader is not configured")


class DisabledPublicSearchAdapter:
    def search(self, target: str, *, task_id: str | None, source_intent_item_id: str | None) -> PublicEvidenceAttempt:
        return PublicEvidenceAttempt(
            id=_attempt_id("search", task_id, source_intent_item_id),
            task_id=task_id,
            source_intent_item_id=source_intent_item_id,
            kind="search",
            target=target,
            status=PublicEvidenceAttemptStatus.NOT_CONFIGURED,
            notes=["Search provider is not configured; this planned task is not evidence."],
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

    def retrieve(self, *, source_intent_artifact: dict[str, Any]) -> PublicEvidenceBatch:
        attempts: list[PublicEvidenceAttempt] = []
        items: list[PublicEvidenceItem] = []
        warnings: list[PublicEvidenceWarning] = []
        for task in _tasks(source_intent_artifact):
            kind = str(task.get("kind") or "")
            target = str(task.get("target") or task.get("instruction") or "").strip()
            task_id = _optional_str(task.get("id"))
            item_id = _optional_str(task.get("sourceIntentItemId"))
            if kind == "readUrl":
                attempt, item, warning = self._read_url(target, task_id=task_id, source_intent_item_id=item_id)
                attempts.append(attempt)
                if item:
                    items.append(item)
                if warning:
                    warnings.append(warning)
            elif kind in {"findPublicSources", "verifyClaim"}:
                attempts.append(self._search_adapter.search(target, task_id=task_id, source_intent_item_id=item_id))
            elif kind:
                attempts.append(PublicEvidenceAttempt(
                    id=_attempt_id("skip", task_id, item_id),
                    task_id=task_id,
                    source_intent_item_id=item_id,
                    kind=kind,
                    target=target,
                    status=PublicEvidenceAttemptStatus.SKIPPED,
                    notes=["Research task does not require public retrieval in v1."],
                ))
        if not attempts:
            warnings.append(PublicEvidenceWarning(code="no-public-retrieval-tasks", message="No URL or public search tasks were available."))
        return PublicEvidenceBatch(
            source="publicEvidenceRetrievalV1",
            attempts=attempts,
            items=items,
            warnings=warnings,
            metadata={"searchProvider": "notConfigured", "itemCount": len(items), "attemptCount": len(attempts)},
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
