# ADR: Domain and feature modules have size and boundary guardrails

## Status

Accepted

## Context

The initial React god-file has been reduced to a small composition root, but the same
risk remains in other layers. Several files are still too large to be easy to review or
extend:

- `src/features/author-memory/AuthorMemoryView.tsx`
- `src/domain/editorialWorkspace.ts`
- `src/features/editorial-model/EditorialModelView.tsx`
- `src/fixtures/demoWorkspace.ts`
- `src/features/signals/SignalsView.tsx`
- `src/application/editorialServices.ts`

The project also had almost no source comments. That is acceptable for trivial code,
but not for domain invariants, legacy compatibility, deterministic stubs, and future
AI/backend boundaries.

## Decision

Large source files must be treated as temporary baselines, not acceptable end states.
Architecture smoke tests track the current line count of known large files and fail if
they grow. Each refactoring slice must lower the relevant limit.

The decomposition direction is:

- domain types and transitions split by bounded context;
- application services split by workflow responsibility;
- demo fixtures split by scenario/context;
- large feature entrypoints split into feature-local subcomponents;
- feature modules do not import other feature modules;
- app-level code owns orchestration, persistence, and feature composition.

Comments are required where they explain maintainability-critical knowledge:

- domain context ownership;
- invariants of transitions and validators;
- legacy compatibility fields;
- deterministic stub behavior;
- future provider/backend boundaries.

Comments must not restate obvious JSX, assignments, or prop passing.

## Consequences

- New product slices are deferred until the refactoring chain reduces the current large
  files.
- `npm run test:architecture` becomes the gate for file-size and boundary drift.
- Refactoring slices can be evaluated by measurable shrinkage instead of subjective
  cleanup.
- Contributors get explicit module ownership and comments where domain intent is not
  obvious.

## Alternatives considered

- **Leave large feature/domain files until they hurt more.** Rejected because they
  already slow review and make product work risky.
- **Split everything in one large refactor.** Rejected because broad moves without
  intermediate guardrails would be hard to review and easy to regress.
- **Add comments everywhere.** Rejected because noisy comments make code harder to
  scan; the useful target is boundary and invariant documentation.
