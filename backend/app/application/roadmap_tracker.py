"""Compatibility shim for roadmap tracker application behavior."""

from backend.app.roadmap.tracker import (
    add_slice,
    document_from_jsonl,
    document_to_jsonl,
    find_slice,
    next_slice,
    parse_roadmap_markdown,
    render_roadmap_markdown,
    update_slice_status,
    utc_now_iso,
    validate_document,
)

__all__ = (
    "utc_now_iso",
    "parse_roadmap_markdown",
    "render_roadmap_markdown",
    "document_to_jsonl",
    "document_from_jsonl",
    "add_slice",
    "update_slice_status",
    "next_slice",
    "validate_document",
    "find_slice",
)
