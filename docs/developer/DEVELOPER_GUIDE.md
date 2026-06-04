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
- `src/application/`: deterministic application services for insight, planning,
  briefing, drafting, editorial checks, release packaging, and analytics prep.
- `src/infrastructure/`: browser storage adapter.
- `src/fixtures/`: demo workspace data.
- `src/App.tsx`: production React editorial cabinet shell and screens.
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

The current app implements:

- The first working flow from source signal to captured editorial learning note.
- Editable `Редакционная модель`, radar signal, plan item, post brief, and post draft.
- Human approval gates for content plan, post brief, final text, and release readiness.
- Deterministic style, anti-AI, fact-check, and policy checks for the draft.
- Manual release package with Telegram/LinkedIn targets, checklist, text copy, and
  Markdown download.
- Local analytics prep with manual metrics and captured editorial learning notes.
- Local-first workspace persistence through browser `localStorage`.

The app does not yet include real source ingestion, AI calls, publishing integrations,
autoposting, or real metrics ingestion.

## Architecture Boundaries

The implemented flow is:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

Use these boundaries:

- Domain objects and pure transitions live in `src/domain/`.
- Application services turn the demo signal into an insight card, a plan item, a post
  brief, a deterministic draft, editorial checks, editor notes, a release package, and
  an editorial learning scaffold.
- Infrastructure adapters handle browser `localStorage` through a `WorkspaceStore`
  interface.
- React components render the workflow and call application services; they must not own
  domain rules.

Do not call browser storage from domain code. Do not add backend persistence, auth,
real source ingestion, or AI provider calls until their slices are planned.

## Validation Strategy

Current tests cover:

- Domain transitions and approval rules.
- Deterministic scoring, planning, briefing, drafting, editorial check, and release
  packaging services, plus analytics prep.
- Local workspace save/load behavior.
- UI smoke coverage for the signal to captured learning note flow.

Run `npm test` and `npm run smoke` before completing the slice.
