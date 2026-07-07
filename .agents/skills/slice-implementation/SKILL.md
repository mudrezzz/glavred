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
- On Windows/PowerShell, do not trust terminal-rendered Cyrillic when it appears as
  mojibake (`Р...`, `С...`, `вЂ...`). Treat it as a console encoding artifact until
  proven otherwise. Do not rewrite localized UI/test strings from mojibake output;
  use stable ASCII anchors, JSON/AST-aware reads, browser/UI assertions, or an
  explicit UTF-8-aware read path before editing localized text.
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
- Before backend runtime work, read `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`,
  `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`, and
  `docs/developer/BACKEND_MODULE_TEMPLATE.md`, plus
  `docs/adr/2026-07-03-backend-bounded-contexts-and-operation-contracts.md`.
- New DraftRun backend modules must live under `backend/app/drafting`; new upstream
  radar/search/signal modules must live under `backend/app/upstream`. Do not add new
  flat `backend/app/application/draft_*.py`, `backend/app/domain/draft_*.py`, or
  `backend/app/application/upstream_radar_*.py` files unless the slice explicitly
  records a temporary debt exception.
- Treat old DraftRun paths as active compatibility facade, migrated thin shim, or
  remaining explicit debt. Do not add behavior to a migrated thin shim; move behavior
  to the canonical package owner under `backend/app/drafting`.
- For broad backend refactors or when package quality is questioned, run
  `.agents/skills/backend-architecture-audit/SKILL.md` before implementing. Known
  debt must be separated from new unclassified smells before the slice scope is
  chosen.
- Provider-heavy backend work must pass the Provider-Heavy Review Checklist in
  `docs/developer/BACKEND_MODULE_TEMPLATE.md`: shared operation governance,
  incidents, payload budget, timeout/runtime budget, safe errors, and no raw
  provider `.complete_json(` calls in bounded application modules.
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
