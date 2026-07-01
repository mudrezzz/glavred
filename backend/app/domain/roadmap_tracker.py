from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


RoadmapStatus = Literal["Backlog", "Ready", "In Progress", "Blocked", "Done", "Deferred"]

VALID_ROADMAP_STATUSES: set[str] = {
    "Backlog",
    "Ready",
    "In Progress",
    "Blocked",
    "Done",
    "Deferred",
}


@dataclass(frozen=True)
class IterationRecord:
    id: str
    title: str
    status: str
    goal: str
    ordering: int
    payload: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass(frozen=True)
class SliceRecord:
    id: str
    iteration_id: str
    title: str
    status: str
    ordering: int
    body_markdown: str
    completed_at: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""


@dataclass(frozen=True)
class RoadmapMeta:
    product_preamble_markdown: str
    blocked_items_markdown: str
    open_questions_markdown: str
    next_recommended_task: str
    updated_at: str = ""


@dataclass(frozen=True)
class RoadmapDocument:
    meta: RoadmapMeta
    iterations: list[IterationRecord]
    slices: list[SliceRecord]


def validate_status(status: str) -> None:
    if status not in VALID_ROADMAP_STATUSES:
        valid = ", ".join(sorted(VALID_ROADMAP_STATUSES))
        raise ValueError(f"Invalid roadmap status {status!r}; expected one of: {valid}")
