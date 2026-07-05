"""Roadmap tracker Markdown parsing."""

from __future__ import annotations

import re

from backend.app.domain.roadmap_tracker import IterationRecord, RoadmapDocument, RoadmapMeta, SliceRecord
from backend.app.roadmap.tracker_clock import utc_now_iso
from backend.app.roadmap.tracker_constants import DEFAULT_ITERATION_ID, GENERATED_NOTICE


def parse_roadmap_markdown(markdown: str) -> RoadmapDocument:
    markdown = _strip_generated_notice(markdown)
    slice_backlog_index = _required_index(markdown, "\n## Slice Backlog")
    completed_index = _required_index(markdown, "\n## Completed Slices")
    blocked_index = _required_index(markdown, "\n## Blocked Items")
    open_questions_index = _required_index(markdown, "\n## Open Questions")
    next_index = _required_index(markdown, "\n## Next Recommended Task")

    preamble = markdown[:slice_backlog_index].rstrip()
    slice_backlog = markdown[slice_backlog_index:completed_index]
    blocked_items = markdown[blocked_index:open_questions_index].rstrip()
    open_questions = markdown[open_questions_index:next_index].rstrip()
    next_task = markdown[next_index:].strip()
    completed_dates = _parse_completed_dates(markdown[completed_index:blocked_index])
    iterations = [_parse_current_iteration(preamble)]
    slices = _parse_slices(slice_backlog, completed_dates)
    return RoadmapDocument(
        meta=RoadmapMeta(
            product_preamble_markdown=preamble,
            blocked_items_markdown=blocked_items,
            open_questions_markdown=open_questions,
            next_recommended_task=next_task,
            updated_at=utc_now_iso(),
        ),
        iterations=iterations,
        slices=slices,
    )


def _strip_generated_notice(markdown: str) -> str:
    if markdown.startswith(GENERATED_NOTICE):
        return markdown[len(GENERATED_NOTICE) :].lstrip("\n")
    return markdown


def _required_index(markdown: str, marker: str) -> int:
    index = markdown.find(marker)
    if index < 0:
        raise ValueError(f"ROADMAP.md is missing required section {marker.strip()!r}")
    return index


def _parse_current_iteration(preamble: str) -> IterationRecord:
    match = re.search(r"^### Iteration\s+([^:]+):\s*(.+)$", preamble, re.MULTILINE)
    if not match:
        return IterationRecord(
            id=DEFAULT_ITERATION_ID,
            title="Roadmap",
            status="Ready",
            goal="Imported roadmap slices",
            ordering=0,
            updated_at=utc_now_iso(),
        )
    iteration_number = match.group(1).strip()
    title = match.group(2).strip()
    block_start = match.end()
    next_heading = preamble.find("\n### ", block_start)
    block = preamble[block_start : next_heading if next_heading >= 0 else len(preamble)]
    status = _extract_field(block, "Status") or "Ready"
    goal_match = re.search(r"Goal:\n\n(?P<goal>(?:- .+\n?)+)", block)
    goal = goal_match.group("goal").strip() if goal_match else ""
    return IterationRecord(
        id=f"iteration-{iteration_number}",
        title=title,
        status=status.strip("`"),
        goal=goal,
        ordering=0,
        updated_at=utc_now_iso(),
    )


def _parse_completed_dates(completed_section: str) -> dict[str, str]:
    joined = re.sub(r"\n\s+", " ", completed_section)
    return {
        match.group("id").strip(): match.group("date")
        for match in re.finditer(
            r"- Slice (?P<id>[^:]+): .*? Completed (?P<date>\d{4}-\d{2}-\d{2})\.",
            joined,
        )
    }


def _parse_slices(slice_backlog: str, completed_dates: dict[str, str]) -> list[SliceRecord]:
    matches = list(re.finditer(r"^### Slice (?P<id>[^:]+): (?P<title>.+)$", slice_backlog, re.MULTILINE))
    records: list[SliceRecord] = []
    for ordering, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[ordering + 1].start() if ordering + 1 < len(matches) else len(slice_backlog)
        body = slice_backlog[body_start:body_end].strip()
        raw_status = (_extract_field(body, "Status") or "Backlog").strip("`")
        status, status_completed_at = _normalize_imported_status(raw_status)
        completed_at = (
            _extract_field(body, "Completed")
            or status_completed_at
            or completed_dates.get(match.group("id").strip())
        )
        if status == "Done" and not completed_at:
            completed_at = "unknown"
        if raw_status != status:
            body = replace_or_append_field(body, "Status", status)
        if status == "Done" and completed_at and "- Completed:" not in body:
            body = f"{body.rstrip()}\n- Completed: {completed_at}"
        records.append(
            SliceRecord(
                id=match.group("id").strip(),
                iteration_id=DEFAULT_ITERATION_ID,
                title=match.group("title").strip(),
                status=status,
                ordering=ordering,
                body_markdown=body,
                completed_at=completed_at,
                updated_at=utc_now_iso(),
            )
        )
    return records


def extract_field(markdown: str, field_name: str) -> str | None:
    return _extract_field(markdown, field_name)


def replace_or_append_field(markdown: str, field_name: str, value: str) -> str:
    pattern = rf"^- {re.escape(field_name)}:\s*.+$"
    replacement = f"- {field_name}: {value}"
    if re.search(pattern, markdown, flags=re.MULTILINE):
        return re.sub(pattern, replacement, markdown, count=1, flags=re.MULTILINE)
    return f"{markdown.rstrip()}\n{replacement}"


def _extract_field(markdown: str, field_name: str) -> str | None:
    match = re.search(rf"^- {re.escape(field_name)}:\s*(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else None


def _normalize_imported_status(status: str) -> tuple[str, str | None]:
    match = re.fullmatch(r"Done\s*\((?P<date>\d{4}-\d{2}-\d{2})\)", status)
    if match:
        return "Done", match.group("date")
    return status, None
