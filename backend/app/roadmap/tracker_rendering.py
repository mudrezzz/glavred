"""Roadmap tracker Markdown rendering."""

from __future__ import annotations

from typing import Iterable

from backend.app.domain.roadmap_tracker import RoadmapDocument, SliceRecord
from backend.app.roadmap.tracker_constants import GENERATED_NOTICE


def render_roadmap_markdown(document: RoadmapDocument) -> str:
    done_slices = [record for record in document.slices if record.status == "Done"]
    parts = [
        GENERATED_NOTICE,
        "",
        document.meta.product_preamble_markdown.rstrip(),
        "",
        "## Slice Backlog",
        "",
        *_render_slices(document.slices),
        "## Completed Slices",
        "",
        *_render_completed_slices(done_slices),
        "",
        document.meta.blocked_items_markdown.rstrip(),
        "",
        document.meta.open_questions_markdown.rstrip(),
        "",
        "## Next Recommended Task",
        "",
        _next_recommended_sentence(document),
        "",
    ]
    return "\n".join(parts)


def _render_slices(records: Iterable[SliceRecord]) -> list[str]:
    lines: list[str] = []
    for record in sorted(records, key=lambda item: item.ordering):
        lines.extend([f"### Slice {record.id}: {record.title}", "", record.body_markdown.rstrip(), ""])
    return lines


def _render_completed_slices(records: Iterable[SliceRecord]) -> list[str]:
    return [
        f"- Slice {record.id}: {record.title}. Completed {record.completed_at or 'unknown'}."
        for record in sorted(records, key=lambda item: item.ordering)
    ]


def _next_recommended_sentence(document: RoadmapDocument) -> str:
    record = next((record for record in sorted(document.slices, key=lambda item: item.ordering) if record.status == "Ready"), None)
    if record is None:
        return "No Ready slice is currently available."
    return f"Implement `Slice {record.id}: {record.title}`."
