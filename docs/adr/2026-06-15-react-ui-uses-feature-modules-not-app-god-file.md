# ADR: React UI Uses Feature Modules, Not an App.tsx God File

## Status

Accepted.

## Context

`src/App.tsx` has grown into a React god file: about 6813 lines and roughly 120
top-level declarations, including most product screens, editors, panels, format
helpers, local UI orchestration, and feature-specific rendering logic.

This made fast product iteration possible early on, but it is now unsafe:

- feature work can accidentally change unrelated screens;
- visual fixes are harder to isolate and test;
- domain/application rules can leak into JSX;
- new screens are likely to be added by copying more code into `App.tsx`;
- refactoring risk increases with every slice.

The product is now broad enough that the React layer needs explicit module boundaries
before adding post candidate assemblies, calendar planning, real validators, or AI
provider integration.

## Decision

React UI must be organized by application role and feature module.

Target structure:

- `src/app/`: composition root, shell, topbar/sidebar, navigation, and workspace
  controller.
- `src/features/author-memory/`: author memory feed, assertions, imports, archive UI.
- `src/features/editorial-model/`: project profile, rules, topics, fabulas, matrix, and
  setup validation UI.
- `src/features/signals/`: radar setup, found signals, signal review, and future post
  candidate entry points.
- `src/features/plan/`: broadcast grid and calendar planning UI.
- `src/features/briefing/`: post brief and approved post-fabula workflow.
- `src/features/editing/`: draft, editorial checks, notes, and final text approval.
- `src/features/release/`: manual release package and export UI.
- `src/features/analytics/`: manual metrics and editorial learning notes.
- `src/features/context-chat/`: context assistant overlay and suggestions.
- `src/shared/ui/`: reusable cabinet primitives, panels, rows, buttons, tabs, badges,
  fields, and layout helpers.
- `src/shared/format/`: labels, dates, status text, and formatting helpers.

Dependency direction:

`features -> shared/application/domain`

There must be no direct `feature -> feature` dependency. Cross-feature behavior should
move through application services, domain contracts, shared UI primitives, or the app
composition layer.

`App.tsx` is the composition root only. It may wire the shell, state controller, and
feature entry components, but it must not contain new large `*View`, `*Editor`,
`*Panel`, `*Card`, `*Header`, `*Sidebar`, `*Topbar`, or `*Overlay` implementations.

Domain/application logic must not be written inside JSX. React components render state,
collect user intent, and call application/domain services.

## Consequences

- New major product screens cannot be added directly to `App.tsx`.
- Refactoring will happen through small extraction slices that preserve current
  behavior and tests.
- Architecture smoke tests will prevent `App.tsx` from growing past the current
  baseline.
- After every extraction slice, the allowed `App.tsx` line/declaration limits must be
  lowered.
- Shared UI primitives should be extracted when two or more features need the same
  cabinet pattern.

## Alternatives Considered

- Continue developing in `App.tsx`: rejected because the file is already too large to
  maintain safely.
- Perform one large rewrite: rejected because it risks breaking the current local-first
  demo flow and would be hard to review.
- Extract only shared CSS: rejected because the main problem is ownership and module
  boundaries, not only visual styling.
