---
name: regression-and-test-strategy
description: Use when deciding which tests to add or run for a slice, when a change may affect existing functionality, or when planning/running full regression. Covers unit, integration, smoke, and e2e testing.
---

# Regression and Test Strategy Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Choose and execute the right validation scope for the current change.

Run all selected Glavred tests through
`.agents/skills/remote-docker-testing/SKILL.md`. Local execution may diagnose a
bootstrap failure but cannot satisfy acceptance.

## Test layers

Consider:

- Unit tests for isolated logic.
- Integration tests for collaboration between components.
- Smoke tests for critical startup and happy-path behavior.
- E2E tests for important user-facing flows.

## Process

1. Inspect the current slice or change.
2. Identify affected components.
3. Identify existing tests.
   - For complex pipeline slices, read the relevant AS IS/TO BE sources before
     choosing tests. DraftRun proof starts from
     `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`; RadarRun proof starts from
     `docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md`; broader upstream proof uses
     `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md`.
   - Build the test plan from the lifecycle
     `AS IS -> Change Intent -> TO BE -> DoD -> Implementation -> AS IS Update`.
     The Definition of Done and test list must prove preserved AS IS invariants,
     changed TO BE targets, structured trace evidence, and the final AS IS update
     outcome.
4. Add or update tests for changed behavior.
   - On Windows/PowerShell, avoid deriving localized expected strings from mojibake
     terminal output. Prefer stable ASCII ids/statuses, semantic DOM queries, or
     UTF-8-aware reads for Russian UI text assertions.
   - Keep `src/App.test.tsx` for app shell/navigation only.
   - Put feature user-flow coverage in the owning feature as `*AppFlow.test.tsx`.
   - Put domain/application/storage coverage beside the owning domain/application/
     infrastructure module.
   - Use `src/test-support` only for small repeated navigation/setup helpers, not
     hidden business assertions.
   - For backend work, put route contract tests beside API ownership, use-case tests
     beside application services, policy tests beside domain modules, and adapter
     tests beside infrastructure modules.
5. Select validation scope:
   - targeted tests for local changes
   - smoke tests for user-visible flows
   - integration tests for cross-component changes
   - full regression when risk is broad
   - `npm run test:architecture` for every refactor, domain, application, app, or
     frontend slice
   - backend unit/contract tests for backend slices when the command exists
   - for persisted workspace or portfolio UI changes, an authenticated browser test
     against real FastAPI and temporary SQLite; assert `/api/users/me` returns `200`
     after login and fail on `localFallback`, CORS, or backend unavailability
6. Run the selected commands if available.
7. Report results clearly.

## Full regression triggers

Run or recommend full regression when:

- core domain behavior changed
- shared infrastructure changed
- public APIs changed
- persistence or migration logic changed
- authentication, authorization, payments, security, or data integrity paths changed
- demo-critical flows changed
- many modules were touched

## Mandatory Architecture Validation

Run `npm run test:architecture` before completing any slice that touches:

- architecture docs or ADRs;
- domain or application logic;
- `src/app`;
- `src/features`;
- shared frontend primitives or visible frontend behavior;
- refactoring, module ownership, or import boundaries.
- backend architecture, environment contracts, provider adapters, API routes, or
  backend tests.

Review warning-level near-limit and export-count output even when the command passes.
If the architecture smoke reports a near-limit test file touched by the current slice,
split that test by feature/workflow ownership before adding more scenarios.

Backend validation should include missing OpenRouter configuration, provider error
mapping, deterministic fallback, route contracts, and forbidden dependency direction
when those surfaces exist.

## Completion checklist

Before finishing:

- Test coverage matches the slice.
- Relevant tests were run.
- Any skipped tests are explained.
- Failures are either fixed or documented as blockers.
- `ROADMAP.md` reflects test-related follow-up work.
