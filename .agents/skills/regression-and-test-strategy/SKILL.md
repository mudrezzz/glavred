---
name: regression-and-test-strategy
description: Use when deciding which tests to add or run for a slice, when a change may affect existing functionality, or when planning/running full regression. Covers unit, integration, smoke, and e2e testing.
---

# Regression and Test Strategy Skill

## Goal

Choose and execute the right validation scope for the current change.

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
4. Add or update tests for changed behavior.
   - Keep `src/App.test.tsx` for app shell/navigation only.
   - Put feature user-flow coverage in the owning feature as `*AppFlow.test.tsx`.
   - Put domain/application/storage coverage beside the owning domain/application/
     infrastructure module.
   - Use `src/test-support` only for small repeated navigation/setup helpers, not
     hidden business assertions.
5. Select validation scope:
   - targeted tests for local changes
   - smoke tests for user-visible flows
   - integration tests for cross-component changes
- full regression when risk is broad
   - `npm run test:architecture` for every refactor, domain, application, app, or
     frontend slice
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

Review warning-level near-limit and export-count output even when the command passes.
If the architecture smoke reports a near-limit test file touched by the current slice,
split that test by feature/workflow ownership before adding more scenarios.

## Completion checklist

Before finishing:

- Test coverage matches the slice.
- Relevant tests were run.
- Any skipped tests are explained.
- Failures are either fixed or documented as blockers.
- `ROADMAP.md` reflects test-related follow-up work.
