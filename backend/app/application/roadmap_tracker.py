from __future__ import annotations

import json
import re
from dataclasses import asdict, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

from backend.app.domain.roadmap_tracker import (
    IterationRecord,
    RoadmapDocument,
    RoadmapMeta,
    SliceRecord,
    validate_status,
)

GENERATED_NOTICE = "<!-- GENERATED FROM docs/roadmap/slices.export.jsonl. DO NOT EDIT MANUALLY. -->"
DEFAULT_ITERATION_ID = "roadmap"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def document_to_jsonl(document: RoadmapDocument) -> str:
    records: list[dict[str, object]] = [
        {
            "recordType": "meta",
            "id": "roadmap-meta",
            "updatedAt": document.meta.updated_at or utc_now_iso(),
            "payload": asdict(document.meta),
        }
    ]
    records.extend(
        {
            "recordType": "iteration",
            "id": iteration.id,
            "updatedAt": iteration.updated_at or utc_now_iso(),
            "payload": asdict(iteration),
        }
        for iteration in sorted(document.iterations, key=lambda item: item.ordering)
    )
    records.extend(
        {
            "recordType": "slice",
            "id": slice_record.id,
            "updatedAt": slice_record.updated_at or utc_now_iso(),
            "payload": asdict(slice_record),
        }
        for slice_record in sorted(document.slices, key=lambda item: item.ordering)
    )
    return "\n".join(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records) + "\n"


def document_from_jsonl(jsonl: str) -> RoadmapDocument:
    meta: RoadmapMeta | None = None
    iterations: list[IterationRecord] = []
    slices: list[SliceRecord] = []
    seen: set[tuple[str, str]] = set()
    for line_number, line in enumerate(jsonl.splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        record_type = record.get("recordType")
        record_id = record.get("id")
        if not isinstance(record_type, str) or not isinstance(record_id, str):
            raise ValueError(f"Invalid JSONL record on line {line_number}: missing recordType/id")
        key = (record_type, record_id)
        if key in seen:
            raise ValueError(f"Duplicate roadmap record {record_type}:{record_id}")
        seen.add(key)
        payload = record.get("payload")
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid JSONL record on line {line_number}: payload must be object")
        if record_type == "meta":
            meta = RoadmapMeta(**payload)
        elif record_type == "iteration":
            iterations.append(IterationRecord(**payload))
        elif record_type == "slice":
            slices.append(SliceRecord(**payload))
        else:
            raise ValueError(f"Unknown roadmap recordType {record_type!r} on line {line_number}")
    if meta is None:
        raise ValueError("Roadmap export does not contain roadmap-meta record")
    return RoadmapDocument(
        meta=meta,
        iterations=sorted(iterations, key=lambda item: item.ordering),
        slices=sorted(slices, key=lambda item: item.ordering),
    )


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
        body = _replace_or_append_field(record.body_markdown, "Status", status)
        if status == "Done":
            body = _replace_or_append_field(body, "Completed", completed_at or date.today().isoformat())
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
            body = _replace_or_append_field(body, "Status", status)
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


def _extract_field(markdown: str, field_name: str) -> str | None:
    match = re.search(rf"^- {re.escape(field_name)}:\s*(.+)$", markdown, re.MULTILINE)
    return match.group(1).strip() if match else None


def _normalize_imported_status(status: str) -> tuple[str, str | None]:
    match = re.fullmatch(r"Done\s*\((?P<date>\d{4}-\d{2}-\d{2})\)", status)
    if match:
        return "Done", match.group("date")
    return status, None


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
    record = next_slice(document)
    if record is None:
        return "No Ready slice is currently available."
    return f"Implement `Slice {record.id}: {record.title}`."


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


def _replace_or_append_field(markdown: str, field_name: str, value: str) -> str:
    pattern = rf"^- {re.escape(field_name)}:\s*.+$"
    replacement = f"- {field_name}: {value}"
    if re.search(pattern, markdown, flags=re.MULTILINE):
        return re.sub(pattern, replacement, markdown, count=1, flags=re.MULTILINE)
    return f"{markdown.rstrip()}\n{replacement}"
