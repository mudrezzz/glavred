---
name: slice-implementation
description: Use when implementing a selected ROADMAP.md slice. Keeps the increment small, updates tests, docs, demo, and roadmap, and preserves a working product after the slice.
---

# Slice Implementation Skill

## Goal

Implement one small, complete, tested, documented product increment.

## Process

1. Read `AGENTS.md`.
2. Read `ROADMAP.md`.
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
12. Update `ROADMAP.md`.

## Implementation rules

- Keep changes localized.
- Preserve existing functionality.
- Follow OOP and single-responsibility principles.
- Comment non-obvious code and tests.
- Do not expand scope unless required for the slice to work.
- Record follow-up work in `ROADMAP.md` instead of silently doing it.
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
- `ROADMAP.md` status was updated.
- Remaining risks and next tasks are documented.
