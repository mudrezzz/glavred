# ADR: Architecture Drift Is Prevented by Agent and Smoke Guardrails

## Status

Accepted

## Context

The Slice 1.5 refactoring chain reduced `App.tsx`, feature entrypoints, domain
compatibility files, app hooks, and demo fixtures into smaller role-owned modules.
That work can regress if future product slices treat architecture rules as a one-time
agreement instead of a required development workflow.

The next product slice, post candidate assemblies, will touch feature, domain, and
application boundaries. Before that work resumes, the project needs explicit
guardrails that make architecture drift visible before code is merged.

## Decision

An architecture rule is accepted only when it is documented and enforceable. New
architecture rules must be reflected in ADRs and the system architecture overview,
and must be backed by at least one of:

- an automated smoke check such as `npm run test:architecture`;
- a mandatory agent workflow checklist when automation would be too brittle.

New product slices must do an architecture preflight before implementation. The
preflight checks the planned files against current file-size limits, module ownership,
feature dependency direction, design-system ownership, and near-limit warnings.

Tracked large files keep hard line-count limits. Files at or above 85% of their limit
produce a warning and must not receive new behavior unless the same slice includes a
refactor step that moves behavior into a role-owned module. Export-count guardrails are
warning-level at first so the current codebase is observable without blocking cleanup
slices.

`src/features/*` modules must not import other features directly or through a root
features barrel. Cross-feature sharing belongs in `src/shared/*`, `src/application/*`,
`src/domain/*`, or app-level composition.

Agent skills are part of the delivery system. Slice implementation, roadmap planning,
architecture design, regression strategy, frontend design-system, and onboarding
skills must require the relevant architecture checks before selecting or completing a
slice.

## Consequences

- Future product slices start with explicit `Architecture impact` in `ROADMAP.md`.
- Near-limit files are visible even when the hard architecture gate still passes.
- Adding behavior to a near-limit file requires decomposition in the same slice.
- New architecture rules cannot live only in conversation; they need ADR/SAO coverage
  plus automation or a workflow checklist.
- `npm run test:architecture` remains mandatory for refactor, domain, application,
  app, and frontend slices.

## Alternatives considered

- **Keep architecture rules only in ADRs.** Rejected because future slices can miss
  passive documentation during implementation.
- **Make every warning a hard failure immediately.** Rejected because export-count and
  near-limit cleanup should be staged without blocking unrelated process work.
- **Rely only on agent checklists.** Rejected because file-size and dependency drift are
  cheap to detect automatically.
