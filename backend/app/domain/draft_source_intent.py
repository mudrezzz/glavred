from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SourceIntentItemKind(StrEnum):
    URL = "url"
    NAMED_SOURCE = "namedSource"
    RESEARCH_REQUEST = "researchRequest"
    PROOF_NEED = "proofNeed"
    FRAMING_HINT = "framingHint"
    EXCLUSION = "exclusion"
    UNKNOWN = "unknown"


class ResearchPlanTaskKind(StrEnum):
    READ_URL = "readUrl"
    FIND_PUBLIC_SOURCES = "findPublicSources"
    VERIFY_CLAIM = "verifyClaim"
    RESPECT_EXCLUSION = "respectExclusion"
    USE_AS_FRAMING = "useAsFraming"


@dataclass(frozen=True)
class SourceIntentItem:
    id: str
    raw: str
    kind: SourceIntentItemKind
    instruction: str
    confidence: str
    notes: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "raw": self.raw,
            "kind": self.kind.value,
            "instruction": self.instruction,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class SourceIntent:
    items: list[SourceIntentItem]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "items": [item.to_payload() for item in self.items],
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ResearchPlanTask:
    id: str
    kind: ResearchPlanTaskKind
    source_intent_item_id: str | None
    instruction: str
    target: str
    priority: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "sourceIntentItemId": self.source_intent_item_id,
            "instruction": self.instruction,
            "target": self.target,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class ResearchPlan:
    research_questions: list[str]
    source_targets: list[str]
    verification_tasks: list[ResearchPlanTask]
    query_candidates: list[str]
    exclusions: list[str]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "researchQuestions": self.research_questions,
            "sourceTargets": self.source_targets,
            "verificationTasks": [task.to_payload() for task in self.verification_tasks],
            "queryCandidates": self.query_candidates,
            "exclusions": self.exclusions,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def research_plan_from_payload(payload: dict[str, Any]) -> ResearchPlan:
    return ResearchPlan(
        research_questions=_list(payload.get("researchQuestions")),
        source_targets=_list(payload.get("sourceTargets")),
        verification_tasks=[
            ResearchPlanTask(
                id=str(item.get("id") or f"task-{index + 1}"),
                kind=_task_kind(item.get("kind")),
                source_intent_item_id=str(item.get("sourceIntentItemId")) if item.get("sourceIntentItemId") else None,
                instruction=str(item.get("instruction") or ""),
                target=str(item.get("target") or ""),
                priority=str(item.get("priority") or "medium"),
            )
            for index, item in enumerate(_dicts(payload.get("verificationTasks")))
        ],
        query_candidates=_list(payload.get("queryCandidates")),
        exclusions=_list(payload.get("exclusions")),
        warnings=_list(payload.get("warnings")),
        metadata=_dict(payload.get("metadata")),
    )


def _task_kind(value: Any) -> ResearchPlanTaskKind:
    try:
        return ResearchPlanTaskKind(str(value))
    except ValueError:
        return ResearchPlanTaskKind.FIND_PUBLIC_SOURCES


def _list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
