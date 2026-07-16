from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class AiRunCapability(StrEnum):
    DRAFT_GENERATION = "draftGeneration"
    VISUAL_GENERATION = "visualGeneration"
    MEME_SEARCH = "memeSearch"
    DOCUMENT_IMPORT = "documentImport"
    SIGNAL_EXTRACTION = "signalExtraction"


class AiRunProvider(StrEnum):
    OPENROUTER = "openrouter"
    DETERMINISTIC = "deterministic"
    NONE = "none"


class AiRunStatus(StrEnum):
    RECORDED = "recorded"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class AiRun:
    id: str
    capability: AiRunCapability
    status: AiRunStatus
    provider: AiRunProvider
    model: str | None
    request_payload: dict[str, Any]
    result_payload: dict[str, Any] | None
    error: str | None
    fallback_used: bool
    created_at: datetime
    updated_at: datetime
