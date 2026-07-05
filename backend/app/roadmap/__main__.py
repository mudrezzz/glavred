from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.app.roadmap.tracker import (
    add_slice,
    document_from_jsonl,
    document_to_jsonl,
    find_slice,
    next_slice,
    parse_roadmap_markdown,
    render_roadmap_markdown,
    update_slice_status,
    validate_document,
)
from backend.app.infrastructure.sqlite_roadmap_repository import SQLiteRoadmapRepository

ROOT = Path.cwd()
ROADMAP_PATH = ROOT / "ROADMAP.md"
EXPORT_PATH = ROOT / "docs" / "roadmap" / "slices.export.jsonl"
DB_PATH = ROOT / "var" / "roadmap" / "roadmap.sqlite"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(f"roadmap: error: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m backend.app.roadmap")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List slices")
    list_parser.add_argument("--status", action="append", help="Filter by status")
    list_parser.set_defaults(handler=_handle_list)

    next_parser = subparsers.add_parser("next", help="Show next Ready slice")
    next_parser.set_defaults(handler=_handle_next)

    show_parser = subparsers.add_parser("show", help="Show one slice")
    show_parser.add_argument("slice_id")
    show_parser.set_defaults(handler=_handle_show)

    add_parser = subparsers.add_parser("add-slice", help="Add a slice after an existing slice")
    add_parser.add_argument("slice_id")
    add_parser.add_argument("title")
    add_parser.add_argument("--after", required=True)
    add_parser.add_argument("--status", default="Backlog")
    add_parser.add_argument("--goal", required=True)
    add_parser.add_argument("--user-value", default="")
    add_parser.add_argument("--scope", default="")
    add_parser.add_argument("--completed-at")
    add_parser.set_defaults(handler=_handle_add_slice)

    status_parser = subparsers.add_parser("update-status", help="Update slice status")
    status_parser.add_argument("slice_id")
    status_parser.add_argument("status")
    status_parser.add_argument("--completed-at")
    status_parser.set_defaults(handler=_handle_update_status)

    import_parser = subparsers.add_parser("import", help="Import ROADMAP.md into local SQLite")
    import_parser.set_defaults(handler=_handle_import)

    export_parser = subparsers.add_parser("export", help="Export local tracker state to JSONL")
    export_parser.set_defaults(handler=_handle_export)

    render_parser = subparsers.add_parser("render", help="Render ROADMAP.md from tracker state")
    render_parser.set_defaults(handler=_handle_render)

    check_parser = subparsers.add_parser("check", help="Validate tracker/export/render consistency")
    check_parser.set_defaults(handler=_handle_check)

    return parser


def _handle_list(args: argparse.Namespace) -> int:
    document = _load_document()
    statuses = set(args.status or [])
    for record in document.slices:
        if statuses and record.status not in statuses:
            continue
        print(f"{record.id}\t{record.status}\t{record.title}")
    return 0


def _handle_next(_: argparse.Namespace) -> int:
    record = next_slice(_load_document())
    if record is None:
        print("No Ready slice")
        return 2
    print(f"{record.id}\t{record.title}")
    return 0


def _handle_show(args: argparse.Namespace) -> int:
    record = find_slice(_load_document(), args.slice_id)
    print(f"Slice {record.id}: {record.title}")
    print(record.body_markdown)
    return 0


def _handle_add_slice(args: argparse.Namespace) -> int:
    document = add_slice(
        _load_document(),
        slice_id=args.slice_id,
        title=args.title,
        after_id=args.after,
        status=args.status,
        goal=args.goal,
        user_value=args.user_value,
        scope=args.scope,
        completed_at=args.completed_at,
    )
    _save_document(document)
    print(f"Added slice {args.slice_id}")
    return 0


def _handle_update_status(args: argparse.Namespace) -> int:
    document = update_slice_status(
        _load_document(),
        slice_id=args.slice_id,
        status=args.status,
        completed_at=args.completed_at,
    )
    _save_document(document)
    print(f"Updated slice {args.slice_id} to {args.status}")
    return 0


def _handle_import(_: argparse.Namespace) -> int:
    if not ROADMAP_PATH.exists():
        raise FileNotFoundError(f"ROADMAP.md not found at {ROADMAP_PATH}")
    document = parse_roadmap_markdown(ROADMAP_PATH.read_text(encoding="utf-8"))
    _repository().save(document)
    print(f"Imported ROADMAP.md into {DB_PATH}")
    return 0


def _handle_export(_: argparse.Namespace) -> int:
    document = _load_document(prefer_db=True)
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(document_to_jsonl(document), encoding="utf-8")
    print(f"Exported {len(document.slices)} slices to {EXPORT_PATH}")
    return 0


def _handle_render(_: argparse.Namespace) -> int:
    document = _load_document()
    ROADMAP_PATH.write_text(render_roadmap_markdown(document), encoding="utf-8")
    print(f"Rendered ROADMAP.md from tracker state")
    return 0


def _handle_check(_: argparse.Namespace) -> int:
    document = _load_document()
    rendered = ROADMAP_PATH.read_text(encoding="utf-8") if ROADMAP_PATH.exists() else None
    errors = validate_document(document, rendered_markdown=rendered)
    if EXPORT_PATH.exists():
        exported_document = document_from_jsonl(EXPORT_PATH.read_text(encoding="utf-8"))
        if document_to_jsonl(exported_document) != document_to_jsonl(document):
            errors.append("docs/roadmap/slices.export.jsonl is stale; run python -m backend.app.roadmap export")
    else:
        errors.append("docs/roadmap/slices.export.jsonl is missing; run python -m backend.app.roadmap export")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Roadmap tracker check passed.")
    return 0


def _load_document(*, prefer_db: bool = False):
    repository = _repository()
    if prefer_db and repository.exists():
        return repository.load()
    if EXPORT_PATH.exists():
        return document_from_jsonl(EXPORT_PATH.read_text(encoding="utf-8"))
    if repository.exists():
        return repository.load()
    if ROADMAP_PATH.exists():
        return parse_roadmap_markdown(ROADMAP_PATH.read_text(encoding="utf-8"))
    raise FileNotFoundError("No roadmap source found")


def _save_document(document) -> None:
    _repository().save(document)
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(document_to_jsonl(document), encoding="utf-8")


def _repository() -> SQLiteRoadmapRepository:
    return SQLiteRoadmapRepository(DB_PATH)


if __name__ == "__main__":
    raise SystemExit(main())
