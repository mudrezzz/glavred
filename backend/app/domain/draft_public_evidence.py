from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PublicEvidenceAttemptStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    NOT_CONFIGURED = "notConfigured"
    SKIPPED = "skipped"


class PublicEvidenceAllowedUse(StrEnum):
    CAN_STATE = "canState"
    CAN_USE_AS_FRAMING = "canUseAsFraming"
    NEEDS_QUALIFICATION = "needsQualification"
    DO_NOT_STATE = "doNotState"


@dataclass(frozen=True)
class PublicEvidenceAttempt:
    id: str
    task_id: str | None
    source_intent_item_id: str | None
    kind: str
    target: str
    status: PublicEvidenceAttemptStatus
    notes: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "taskId": self.task_id,
            "sourceIntentItemId": self.source_intent_item_id,
            "kind": self.kind,
            "target": self.target,
            "status": self.status.value,
            "notes": self.notes,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class PublicEvidenceItem:
    id: str
    attempt_id: str
    source_url: str | None
    source_title: str
    snippet: str
    text_summary: str
    provenance: str
    confidence: str
    allowed_use: PublicEvidenceAllowedUse
    extraction_notes: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "attemptId": self.attempt_id,
            "sourceUrl": self.source_url,
            "sourceTitle": self.source_title,
            "snippet": self.snippet,
            "textSummary": self.text_summary,
            "provenance": self.provenance,
            "confidence": self.confidence,
            "allowedUse": self.allowed_use.value,
            "extractionNotes": self.extraction_notes,
        }


@dataclass(frozen=True)
class PublicEvidenceWarning:
    code: str
    message: str
    target: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "target": self.target}


@dataclass(frozen=True)
class PublicEvidenceBatch:
    source: str
    attempts: list[PublicEvidenceAttempt]
    items: list[PublicEvidenceItem]
    warnings: list[PublicEvidenceWarning] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    ai_run_ids: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "attempts": [attempt.to_payload() for attempt in self.attempts],
            "items": [item.to_payload() for item in self.items],
            "warnings": [warning.to_payload() for warning in self.warnings],
            "metadata": self.metadata,
            "aiRunIds": self.ai_run_ids,
        }
