from __future__ import annotations

from pathlib import Path

from backend.app.application.roadmap_tracker import (
    add_slice,
    document_from_jsonl,
    document_to_jsonl,
    next_slice,
    parse_roadmap_markdown,
    render_roadmap_markdown,
    update_slice_status,
    validate_document,
)
from backend.app.infrastructure.sqlite_roadmap_repository import SQLiteRoadmapRepository


SAMPLE_ROADMAP = """# Roadmap

Intro.

### Iteration 2.17: SaaS

- Status: In Progress

## Slice Backlog

### Slice 2.17.3.3: Project Dashboard App Shell Alignment

- Status: Done
- Goal: Align dashboard shell.

### Slice 2.17.4: Multi-Platform Publication Variants

- Status: Ready
- Goal: Generate platform variants.

## Completed Slices

- Slice 2.17.3.3: Project Dashboard App Shell Alignment. Completed 2026-06-30.

## Blocked Items

- None.

## Open Questions

- None.

## Next Recommended Task

Implement `Slice 2.17.4: Multi-Platform Publication Variants`.
"""


def test_parse_render_and_export_roundtrip() -> None:
    document = parse_roadmap_markdown(SAMPLE_ROADMAP)

    assert next_slice(document).id == "2.17.4"
    assert document.slices[0].completed_at == "2026-06-30"

    jsonl = document_to_jsonl(document)
    restored = document_from_jsonl(jsonl)
    rendered = render_roadmap_markdown(restored)

    assert "GENERATED FROM docs/roadmap/slices.export.jsonl" in rendered
    assert "### Slice 2.17.4: Multi-Platform Publication Variants" in rendered
    assert validate_document(restored, rendered_markdown=rendered) == []


def test_add_slice_update_status_and_next() -> None:
    document = parse_roadmap_markdown(SAMPLE_ROADMAP)
    document = add_slice(
        document,
        slice_id="2.17.3.4",
        title="Roadmap Tracker Source of Truth",
        after_id="2.17.3.3",
        status="Ready",
        goal="Move roadmap editing behind tracker commands.",
        user_value="Agents stop hand-editing a huge Markdown backlog.",
        scope="SQLite tracker; JSONL export; generated report",
    )

    assert next_slice(document).id == "2.17.3.4"

    document = update_slice_status(
        document,
        slice_id="2.17.3.4",
        status="Done",
        completed_at="2026-07-01",
    )

    assert next_slice(document).id == "2.17.4"
    assert "Completed: 2026-07-01" in document.slices[1].body_markdown


def test_sqlite_repository_roundtrip(tmp_path: Path) -> None:
    document = parse_roadmap_markdown(SAMPLE_ROADMAP)
    repository = SQLiteRoadmapRepository(tmp_path / "roadmap.sqlite")

    repository.save(document)
    restored = repository.load()

    assert restored.slices[0].id == "2.17.3.3"
    assert restored.slices[1].status == "Ready"


def test_check_reports_stale_render() -> None:
    document = parse_roadmap_markdown(SAMPLE_ROADMAP)

    errors = validate_document(document, rendered_markdown="stale")

    assert "ROADMAP.md is stale; run python -m backend.app.roadmap render" in errors


def test_import_normalizes_legacy_done_status_with_date() -> None:
    legacy = SAMPLE_ROADMAP.replace("- Status: Ready", "- Status: Done (2026-06-24)")

    document = parse_roadmap_markdown(legacy)
    imported = document.slices[1]

    assert imported.status == "Done"
    assert imported.completed_at == "2026-06-24"
    assert "- Status: Done" in imported.body_markdown
    assert "- Completed: 2026-06-24" in imported.body_markdown
