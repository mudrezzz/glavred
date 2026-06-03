# Developer Guide

## Stack

- React 18
- Vite
- TypeScript
- Vitest
- Testing Library

## Commands

Install dependencies:

```bash
npm install
```

Start local development:

```bash
npm run dev
```

Run tests:

```bash
npm test
```

Run build smoke test:

```bash
npm run smoke
```

## Source Layout

- `src/domain/`: framework-independent domain model.
- `src/App.tsx`: temporary brief-backed baseline application shell.
- `src/test/`: test setup.
- `ui-design-systems/`: design handoff and reference UI, not production code.
- `docs/`: documentation.
- `demo/`: demo notes and future demo assets.

## Requirements Status

The primary product brief is `glavred.md`. It is filled and should drive future
architecture and implementation decisions.

Use the design handoff for visual and conceptual reference, but treat it as secondary
to the brief. Keep product logic in `src/domain/` or future domain/application modules
before wiring it into React views.

## Current Baseline

The baseline models:

- The editorial loop from radar to learning.
- Human approval gates for content plan, post brief, and final editorial checks.
- The five MVP modules: editorial model, sources and insights, content plan, post
  brief, draft and review.

The baseline does not yet include persistence, source ingestion, AI calls, publishing
integrations, or analytics.

## Slice 0.4 Architecture Target

The next implementation slice should build the first working flow:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief`

Use these boundaries:

- Domain objects and pure transitions live in `src/domain/`.
- Application services turn the demo signal into an insight card, a plan item, and a
  post brief.
- Infrastructure adapters handle browser `localStorage` through a `WorkspaceStore`
  interface.
- React components render the workflow and call application services; they must not own
  domain rules.

Do not add backend persistence, auth, real source ingestion, or AI provider calls in
Slice 0.4. Deterministic services and fixtures are the accepted first implementation
strategy.

## Slice 0.4 Validation Strategy

Add tests for:

- Domain transitions and approval rules.
- Deterministic scoring, planning, and briefing services.
- Local workspace save/load behavior.
- UI smoke coverage for the signal to approved post brief flow.

Run `npm test` and `npm run smoke` before completing the slice.
