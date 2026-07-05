"""Roadmap tracker JSONL import/export."""

from __future__ import annotations

import json
from dataclasses import asdict

from backend.app.domain.roadmap_tracker import (
    IterationRecord,
    RoadmapDocument,
    RoadmapMeta,
    SliceRecord,
)
from backend.app.roadmap.tracker_clock import utc_now_iso


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
