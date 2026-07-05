"""Roadmap tracker mutation and validation service functions."""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Iterable

from backend.app.domain.roadmap_tracker import RoadmapDocument, SliceRecord, validate_status
from backend.app.roadmap.tracker_clock import utc_now_iso
from backend.app.roadmap.tracker_parsing import replace_or_append_field
from backend.app.roadmap.tracker_rendering import render_roadmap_markdown


def add_slice(
    document: RoadmapDocument,
    *,
    slice_id: str,
    title: str,
    after_id: str,
    status: str,
    goal: str,
    user_value: str,
    scope: str,
    completed_at: str | None = None,
) -> RoadmapDocument:
    validate_status(status)
    if any(record.id == slice_id for record in document.slices):
        raise ValueError(f"Slice {slice_id} already exists")
    after = _find_slice(document.slices, after_id)
    body = _build_slice_body(
        status=status,
        goal=goal,
        user_value=user_value,
        scope=scope,
        completed_at=completed_at,
    )
    inserted = SliceRecord(
        id=slice_id,
        iteration_id=after.iteration_id,
        title=title,
        status=status,
        ordering=after.ordering + 1,
        body_markdown=body,
        completed_at=completed_at,
        updated_at=utc_now_iso(),
    )
    slices: list[SliceRecord] = []
    for record in document.slices:
        if record.ordering > after.ordering:
            slices.append(replace(record, ordering=record.ordering + 1))
        else:
            slices.append(record)
    slices.append(inserted)
    return replace(document, slices=sorted(slices, key=lambda item: item.ordering))


def update_slice_status(
    document: RoadmapDocument,
    *,
    slice_id: str,
    status: str,
    completed_at: str | None = None,
) -> RoadmapDocument:
    validate_status(status)
    if status == "Done" and completed_at is None:
        completed_at = date.today().isoformat()
    updated: list[SliceRecord] = []
    for record in document.slices:
        if record.id != slice_id:
            updated.append(record)
            continue
        body = replace_or_append_field(record.body_markdown, "Status", status)
        if status == "Done":
            body = replace_or_append_field(body, "Completed", completed_at or date.today().isoformat())
        updated.append(
            replace(
                record,
                status=status,
                body_markdown=body,
                completed_at=completed_at if status == "Done" else None,
                updated_at=utc_now_iso(),
            )
        )
    if all(record.id != slice_id for record in document.slices):
        raise ValueError(f"Slice {slice_id} not found")
    return replace(document, slices=updated)


def next_slice(document: RoadmapDocument) -> SliceRecord | None:
    return next((record for record in sorted(document.slices, key=lambda item: item.ordering) if record.status == "Ready"), None)


def validate_document(document: RoadmapDocument, rendered_markdown: str | None = None) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for record in document.slices:
        if record.id in seen:
            errors.append(f"Duplicate slice id: {record.id}")
        seen.add(record.id)
        try:
            validate_status(record.status)
        except ValueError as exc:
            errors.append(str(exc))
        if record.status == "Done" and not record.completed_at:
            errors.append(f"Done slice {record.id} is missing completedAt")
    if next_slice(document) is None:
        errors.append("Roadmap has no Ready slice")
    if rendered_markdown is not None and rendered_markdown != render_roadmap_markdown(document):
        errors.append("ROADMAP.md is stale; run python -m backend.app.roadmap render")
    return errors


def find_slice(document: RoadmapDocument, slice_id: str) -> SliceRecord:
    return _find_slice(document.slices, slice_id)


def _find_slice(records: Iterable[SliceRecord], slice_id: str) -> SliceRecord:
    for record in records:
        if record.id == slice_id:
            return record
    raise ValueError(f"Slice {slice_id} not found")


def _build_slice_body(
    *,
    status: str,
    goal: str,
    user_value: str,
    scope: str,
    completed_at: str | None,
) -> str:
    completed_line = f"\n- Completed: {completed_at}" if completed_at else ""
    return "\n".join(
        [
            f"- Status: {status}",
            f"- Goal: {goal}",
            f"- User value: {user_value}",
            "- Scope:",
            *[f"  - {line}" for line in scope.split("; ") if line],
            "- Out of scope:",
            "  - Product runtime behavior changes.",
            "- Architecture impact:",
            "  - Moves roadmap editing behind a tracker/export/render workflow.",
            "- Tests:",
            "  - Roadmap CLI import/export/render/check coverage.",
            "- Docs:",
            "  - README, ADR, contributor guide, developer guide, AGENTS, and roadmap docs.",
            "- Acceptance criteria:",
            "  - Agents can use CLI commands instead of manually editing ROADMAP.md.",
            "  - ROADMAP.md renders from docs/roadmap/slices.export.jsonl.",
            "  - Roadmap changes remain reviewable in git diff.",
            completed_line.strip(),
        ]
    ).strip()
