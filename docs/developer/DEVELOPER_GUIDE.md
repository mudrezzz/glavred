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
- The five MVP modules: editorial bible, sources and insights, content plan, post
  brief, draft and review.

The baseline does not yet include persistence, source ingestion, AI calls, publishing
integrations, or analytics.
