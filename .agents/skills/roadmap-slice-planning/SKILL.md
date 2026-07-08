---
name: roadmap-slice-planning
description: Use when turning requirements, user ideas, or architecture into tracker-backed roadmap iterations, slices, backlog items, and next actions. Optimizes for small complete increments and concentric product growth.
---

# Roadmap Slice Planning Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Maintain the tracker-backed roadmap as the project control center. `ROADMAP.md` is a generated report; the committed source artifact is `docs/roadmap/slices.export.jsonl`.

## Process

1. Read the requirements source.
2. Read current tracker state with `python -m backend.app.roadmap next/list/show`; use `ROADMAP.md` as a generated report fallback.
3. Read architecture docs if present.
4. Identify the smallest useful product perimeter.
5. Break work into iterations.
6. Break iterations into small slices.
7. Ensure every slice has:
   - user value
   - implementation scope
   - architecture impact
   - documentation impact
   - test expectations
   - demo impact when applicable
   - clear completion criteria

## Slice format

Use this format in the slice `body_markdown` stored by the tracker/export:

```markdown
### Slice <number>: <title>

- Status: Backlog | Ready | In Progress | Blocked | Done
- Goal:
- User value:
- Scope:
- Out of scope:
- Implementation notes:
- Architecture impact:
- Tests:
- Docs:
- Demo impact:
- Acceptance criteria:
- Risks:
```

## Planning rules

- Prefer small working increments.
- Avoid large vague tasks.
- Avoid module-by-module waterfall plans.
- Ensure each iteration can leave the product demonstrable.
- Keep blocked questions explicit.
- Always identify the next recommended task.
- For Glavred drafting/backend roadmap work, preserve the documented drafting quality
  order: source ledger and post contract come before validator/revision loops. If a
  slice skips ahead, record the reason and architecture impact explicitly.
- For any DraftRun or drafting-pipeline slice, read
  `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` before planning. If the planned
  slice changes step order, artifacts, roles, context packs, validation, ranking,
  revision, fallback, or trace semantics, include updating that Markdown file and
  regenerating `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf` in the slice scope.

## Completion checklist

Before finishing:

- The tracker is updated with CLI commands or JSONL changes.
- `python -m backend.app.roadmap render` and `python -m backend.app.roadmap export` were run.
- The next task is clearly marked.
- Slices are small enough to implement independently.
- Testing and docs are included in each slice.
