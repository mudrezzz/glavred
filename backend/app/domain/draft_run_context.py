from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DraftRunContext:
    work_item: dict[str, Any] | None = None
    plan_slot: dict[str, Any] | None = None
    candidate: dict[str, Any] | None = None
    source_signal: dict[str, Any] | None = None
    topic: dict[str, Any] | None = None
    fabula: dict[str, Any] | None = None
    project_profile: dict[str, Any] = field(default_factory=dict)
    editorial_model: dict[str, Any] = field(default_factory=dict)
    publisher_rules: list[dict[str, Any]] = field(default_factory=list)
    author_position_evidence: list[dict[str, Any]] = field(default_factory=list)
    missing_context: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class DraftRunContextSummary:
    brief: dict[str, Any]
    work_item: dict[str, Any] | None
    plan_slot: dict[str, Any] | None
    candidate: dict[str, Any] | None
    source_signal: dict[str, Any] | None
    topic: dict[str, Any] | None
    fabula: dict[str, Any] | None
    publisher_rules: dict[str, Any]
    author_position_evidence: dict[str, Any]
    missing_context: list[dict[str, Any]]

    def to_payload(self) -> dict[str, Any]:
        return {
            "brief": self.brief,
            "workItem": self.work_item,
            "planSlot": self.plan_slot,
            "candidate": self.candidate,
            "sourceSignal": self.source_signal,
            "topic": self.topic,
            "fabula": self.fabula,
            "publisherRules": self.publisher_rules,
            "authorPositionEvidence": self.author_position_evidence,
            "missingContext": self.missing_context,
        }
