# ADR: App flow tests follow feature ownership

## Status

Accepted

## Context

`src/App.test.tsx` grew into a shared regression file for unrelated workflows:
signals, author memory, editorial model, planning, editing, release, analytics, and
context chat. This repeated the earlier `App.tsx` problem in the test layer: one file
became the default place for every new product slice, even after production code was
split into role-owned modules.

Large test files make future changes harder to review, hide feature ownership, and
encourage broad helpers that know too much about the product. Test architecture must
therefore follow the same ownership model as production architecture.

## Decision

`src/App.test.tsx` is limited to app shell and navigation smoke coverage. Feature
workflows live in feature-owned app-flow tests:

- `src/features/signals/SignalsAppFlow.test.tsx`
- `src/features/author-memory/AuthorMemoryAppFlow.test.tsx`
- `src/features/editorial-model/EditorialModelAppFlow.test.tsx`
- `src/features/plan/PlanAppFlow.test.tsx`
- `src/features/editing/EditorialWorkbenchAppFlow.test.tsx`
- `src/features/release/ReleaseAppFlow.test.tsx`
- `src/features/analytics/AnalyticsAppFlow.test.tsx`
- `src/features/context-chat/ContextChatAppFlow.test.tsx`

Shared test helpers live under `src/test-support`, but only for repeated user-flow
navigation and setup. They must not contain hidden business assertions or become a
large page-object framework.

`npm run test:architecture` enforces:

- a hard line-count limit for `src/App.test.tsx`;
- hard line-count limits for feature app-flow tests and key `src/test-support` files;
- warning-level near-limit summaries for large test files;
- explicit blockers for feature-flow helper names in `src/App.test.tsx`.

Future slices must add or update tests beside the module that owns the behavior. A
new cross-feature scenario must choose the closest owning feature or introduce a
small, explicitly named app-flow test file rather than expanding `App.test.tsx`.

## Consequences

- Test files become easier to review together with the product module they exercise.
- `App.test.tsx` can no longer quietly become a second god file.
- Full regression still runs through Vitest, but the files are grouped by ownership.
- Existing large test files outside `App.test.tsx` are now visible in architecture
  smoke near-limit output and should be split before more behavior is added to them.

## Alternatives considered

- Keep all app-flow regression in `App.test.tsx`.
  Rejected because it recreates the god-file problem and is already near the previous
  hard limit.
- Move all tests into a single `src/app-flows` directory.
  Rejected because it separates tests from feature ownership and makes future slices
  less likely to update the right tests.
- Build a full page-object test framework.
  Rejected for now because the product is still evolving quickly; small flow drivers
  are enough and easier to keep honest.
