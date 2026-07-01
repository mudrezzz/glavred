# ADR: Roadmap Tracker Source of Truth

- Status: Accepted
- Date: 2026-07-01

## Context

`ROADMAP.md` has grown into a large report. It is useful for human reading, but it is
awkward as the source of truth for agent workflows: every slice update requires editing
a large Markdown file, diffs are noisy, and simple queries such as "next Ready slice"
require parsing prose.

SQLite is useful as a local working database, but a raw SQLite file is not reviewable
in Git.

## Decision

Use a small roadmap tracker with three artifacts:

- `var/roadmap/roadmap.sqlite`: local generated working database for agents and CLI
  commands. It is ignored by Git.
- `docs/roadmap/slices.export.jsonl`: committed canonical review artifact. One line
  is one roadmap record.
- `ROADMAP.md`: committed generated Markdown report with a "do not edit manually"
  header.

Agents and contributors change roadmap state through:

```bash
python -m backend.app.roadmap ...
```

Required pre-commit workflow for roadmap changes:

```bash
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
git diff --check
```

## Consequences

- `ROADMAP.md` remains readable for humans and external contributors.
- Git review should focus on `docs/roadmap/slices.export.jsonl`.
- The local SQLite DB can be rebuilt from the committed export/report and must not be
  committed.
- Older historical slices may remain stored as preserved Markdown bodies while new
  slices gradually use more structured fields.
- Project and skill instructions must treat `ROADMAP.md` as a generated report, not a
  hand-edited source.

