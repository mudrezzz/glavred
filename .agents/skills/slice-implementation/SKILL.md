---
name: slice-implementation
description: Use when implementing a selected tracker-backed roadmap slice. Keeps the increment small, updates tests, docs, demo, and roadmap, and preserves a working product after the slice.
---

# Slice Implementation Skill

## Goal

Implement one small, complete, tested, documented product increment.

## Process

1. Read `AGENTS.md`.
2. Read tracker state with `python -m backend.app.roadmap next/list/show` and use generated `ROADMAP.md` for narrative context.
3. Identify the active or next slice.
4. Read relevant requirements, architecture docs, ADRs, and existing code.
5. Run an architecture preflight before implementation:
   - check the files you expect to touch against `scripts/architecture-smoke.mjs`
     limits;
   - inspect `npm run test:architecture` output when practical before adding
     behavior to large tracked files;
   - identify module ownership and dependency direction for the slice;
   - confirm whether the `ROADMAP.md` entry includes `Architecture impact`.
6. Confirm the slice scope.
7. Implement only the selected slice.
8. Add or update tests.
9. Update documentation.
10. Update demo if user-visible behavior changed.
11. Run relevant validation, including final `npm run test:architecture`.
12. Update the tracker, then run `python -m backend.app.roadmap render` and `python -m backend.app.roadmap export`.

## Implementation rules

- Keep changes localized.
- Preserve existing functionality.
- Follow OOP and single-responsibility principles.
- Comment non-obvious code and tests.
- Do not expand scope unless required for the slice to work.
- Record follow-up work in the tracker/export instead of silently doing it.
- Do not add new behavior to a near-limit file unless the same slice includes a
  refactor step into a role-owned module and keeps the architecture smoke hard limits
  green.
- Do not bypass module ownership through feature barrels or feature-to-feature imports.
- Do not add feature-flow scenarios to `src/App.test.tsx`; keep it limited to app
  shell/navigation smoke coverage. Add feature workflows beside the owning feature as
  `*AppFlow.test.tsx`, and use `src/test-support` only for small repeated navigation
  helpers.
- Do not add test behavior to a near-limit test file unless the same slice splits the
  test by feature/workflow ownership and keeps `npm run test:architecture` green.
- For backend slices, do not add boilerplate-only modules, unused abstractions, or broad
  scaffolding. Add only the route, use case, domain policy, adapter, setting, or test
  required by the current slice.
- Backend API handlers must stay thin. Put orchestration in application services and
  provider/library calls in infrastructure adapters.
- Backend domain modules must not import OpenRouter, provider SDKs, HTTP clients,
  database sessions, queues, file systems, or `langgraph-document-ai-platform`.
- If a backend slice changes environment variables, update `.env.example`,
  developer docs, and architecture smoke checks. Never commit real `.env` secrets.
- For drafting/backend slices, read ADRs
  `2026-06-19-drafting-uses-queued-agentic-runs` and
  `2026-06-20-drafting-quality-requires-source-ledger-and-post-contract` before
  editing. Do not jump from draft candidates directly to a validator/revision loop:
  source ledger, feasibility gate, and post contract must exist first unless
  the tracker record explicitly records a safe exception.
- For DraftRun pipeline slices, also read
  `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` before implementation. If behavior
  changes, update that Markdown file and regenerate
  `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf` with
  `python scripts/generate-draft-run-pipeline-pdf.py` before completing the slice.

## Completion checklist

Before finishing:

- Slice behavior works.
- Tests were added or updated.
- Relevant tests were run.
- `npm run test:architecture` was run and any near-limit warnings were considered.
- For backend slices, backend tests were run when a backend test command exists, and
  architecture smoke covers new backend ownership rules.
- Docs were updated.
- Demo was updated if needed.
- Tracker status was updated and `ROADMAP.md`/`docs/roadmap/slices.export.jsonl` were regenerated.
- Remaining risks and next tasks are documented.
