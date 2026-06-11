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

Refresh wiki screenshots:

```bash
npm run docs:screenshots
```

Publish GitHub Wiki from `docs/wiki/`:

```bash
npm run docs:wiki:publish
```

## Source Layout

- `src/domain/`: framework-independent domain model.
- `src/application/`: deterministic application services for author memory inference,
  insight, planning, briefing, drafting, editorial checks, release packaging, and
  analytics prep.
- `src/infrastructure/`: browser storage adapter.
- `src/fixtures/`: demo workspace data.
- `src/App.tsx`: production React editorial cabinet shell and screens.
- `src/test/`: test setup.
- `ui-design-systems/`: design handoff and reference UI, not production code.
- `docs/`: documentation.
- `docs/wiki/`: source files for the GitHub Wiki, including screenshot assets.
- `demo/`: demo notes and future demo assets.

## Requirements Status

The primary product brief is `glavred.md`. It is filled and should drive future
architecture and implementation decisions.

Use the design handoff for visual and conceptual reference, but treat it as secondary
to the brief. Keep product logic in `src/domain/` or future domain/application modules
before wiring it into React views.

## Current Baseline

The current app implements:

- Author memory feed with titleless thought capture, link-reaction previews,
  targeted manual corrections, search/filtering, lazy display, edit/delete actions,
  memory summary, and browser speech-recognition fallback.
- Local-first external source shell inside author memory: source cards, reviewed queue,
  grouping, candidate filters, archive-safe bulk actions, latest bulk undo, and archive
  records.
- Evidence-backed author-position assertions inferred from demo notes.
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

## Wiki Documentation Workflow

The GitHub Wiki is generated from `docs/wiki/`. Keep the source in the main
repository so wiki changes are reviewed, tested, and versioned with the product.

`npm run docs:screenshots` starts Vite on a dedicated local port, opens the app in
Playwright, resets browser `localStorage`, walks through the demo flow, and writes PNG
files to `docs/wiki/assets/screenshots/`.

`npm run docs:wiki:publish` copies `docs/wiki/` into the separate GitHub Wiki
repository at `https://github.com/mudrezzz/glavred.wiki.git` and pushes it. The main
repository must be public before publishing the wiki in the current GitHub setup.

GitHub creates the backing `*.wiki.git` repository only after the first wiki page is
saved through the web UI. For the first publish, open
`https://github.com/mudrezzz/glavred/wiki`, click `Create the first page`, save a
temporary `Home` page, and then rerun `npm run docs:wiki:publish`.

When user-visible UI changes, update the matching wiki page and refresh screenshots in
the same slice.

## Revised Product Direction

The next product circle re-centers Glavred around:

`AuthorMemory -> AuthorPositionModel -> EditorialSystem -> ContentProduction`

The existing production flow remains valid, but it is downstream. Future development
should first capture the author's raw thoughts, reactions, corrections, and archive
material, then turn them into structured, evidence-backed entities that constrain the
content pipeline.

New conceptual entities:

- `AuthorNote` and `AuthorMemoryEvent` for loose thoughts, links, reactions,
  corrections, local note attachments, archive annotations, and learning events.
- `AuthorNote.targetType`, `targetId`, and `targetTitle` are optional metadata used
  only when a manual correction targets an inferred assertion or evidence item.
- `AuthorAttachment` and `AuthorNote.attachments` store small local demo files attached
  through `+ Файл`. Attachments are supporting material, not automatically analyzed
  evidence.
- `AuthorPositionAssertion` for transparent claims about how the author thinks or
  writes, with evidence.
- `AuthorExternalSource`, `ImportedMemoryCandidate`, `ImportCandidateGroup`,
  `BulkImportAction`, and `ArchiveRecord` for the local import-review shell. Only
  `acceptedToMemory` candidates become `AuthorNote`; unreviewed and archive-only
  candidates do not affect `AuthorPositionAssertion`.
- `Topic`, `Fabula`, `TopicFabulaMatrix`, `ContentDesignRecord`, and
  `PlatformProfile` as structured editorial entities.
- `ValidatorResult` as a common score/status/evidence contract across setup,
  planning, drafting, release, and archive uniqueness.
- `ContextChatSession` for a future right-side assistant synchronized with the active
  section.

Do not model these as one large prompt or one freeform settings textarea. The product
requires small entities, explicit rules, validator scores, and evidence links.

## Architecture Boundaries

The implemented flow is:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

Use these boundaries:

- Domain objects and pure transitions live in `src/domain/`.
- Application services normalize author notes into memory events, infer
  evidence-backed author-position assertions, and turn the demo signal into an insight
  card, a plan item, a post brief, a deterministic draft, editorial checks, editor
  notes, a release package, and an editorial learning scaffold.
- Infrastructure adapters handle browser `localStorage` through a `WorkspaceStore`
  interface.
- React components render the workflow and call application services; they must not own
  domain rules.
- The author-memory UI may use browser-only helpers for local link previews, derived
  titles, search filters, summary counts, and voice-input capability detection. These
  helpers must not fetch external metadata or bypass local-first storage.

Do not call browser storage from domain code. Do not add backend persistence, auth,
real source ingestion, or AI provider calls until their slices are planned.

File attachments are local-first and size-limited to 1 MB per attachment in the browser
demo. They are stored as metadata plus `dataUrl`. Real PDF/DOCX parsing, OCR, image
understanding, text extraction, chunking, and AI analysis belong to a later
attachment-analysis slice after storage and provider boundaries are ready.

## External Source Import Runtime Shell

Slice 1.0.5 implements the first local-first UI shell for external source import. It
adds runtime contracts and deterministic transitions, but still does not add real
Telegram/social/blog APIs, OAuth, crawlers, backend workers, scheduled ingestion, or
AI analysis.

Runtime import entities:

- `AuthorExternalSource`: source settings for Telegram, social profiles, blogs,
  documents, article archives, and manual uploads.
- `ImportedMemoryCandidate`: imported item waiting for author review.
- `ImportCandidateGroup`: grouped candidates for large imports.
- `BulkImportAction`: reversible bulk decision such as `Добавить все` or archive
  selected items.
- `ArchiveRecord`: accepted historical material.
- `Provenance`: source, original URL/file reference, import date, acceptance date,
  acceptance mode, and author reason.
- `EvidencePolicy`: `canSupportAssertions`, `archiveOnly`, or `ignored`.

Rules:

- Unreviewed candidates must not change `AuthorPositionAssertion`.
- Large archives default to archive-safe acceptance, not active memory.
- Bulk-accepted records must remain distinguishable from manually reviewed evidence.
- `acceptCandidateToMemory` may create an `AuthorNote`; `acceptedToArchive` and
  `bulkAcceptedToArchive` create only `ArchiveRecord`.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing import fields from the demo
  workspace so old browser states continue to load.
- Real Telegram/social/blog APIs, OAuth, crawlers, backend workers, scheduled
  ingestion, and AI analysis are later slices.

## AI Provider Architecture Baseline

Slice 0.8 defines the first AI boundary without adding runtime provider calls. The
first replacement target is drafting from an approved `PostBrief`.

After the June 2026 product revision, this boundary remains valid but is no longer the
next implementation priority. AI-assisted drafting should wait until author memory,
author position, topic/fabula entities, and validator contracts are strong enough to
constrain generation.

Rules for future AI-assisted drafting:

- React components must not call AI providers, SDKs, prompt builders, or provider
  network clients directly.
- Domain modules must stay provider-free and should not import provider request,
  response, error, or metadata types.
- Application services own the orchestration decision: use a provider adapter when it
  is available and allowed, or use the deterministic `createPostDraft` fallback.
- Infrastructure adapters own provider-specific calls, authentication, SDK imports,
  response normalization, and provider error mapping.
- Local-first deterministic behavior remains the default for demo, tests, offline
  development, and provider failure.

The conceptual drafting boundary is:

`approved PostBrief + EditorialModel + optional EditorialLearningNote -> DraftGenerationRequest -> DraftingProvider -> DraftGenerationResult -> PostDraft`

Conceptual interfaces for the next implementation slice:

- `AiProviderAdapter`: provider-specific adapter behind an application boundary.
- `DraftGenerationRequest`: brief, editorial model, optional learning note, locale,
  constraints, and caller context.
- `DraftGenerationResult`: draft title/body, notes, risks, and provider metadata that
  can be mapped into `PostDraft`.
- `PromptTemplate`: layered prompt definition for system/context, editorial model,
  brief, output contract, and HITL reminder.
- `ProviderRunMetadata`: normalized run information such as provider, model, run id,
  latency, token estimates, and fallback mode.
- `ProviderError`: normalized error object handled by application services.
- `AiFallbackPolicy`: fallback rules for disabled providers, missing configuration,
  provider errors, invalid results, or local demo mode.

Prompt architecture for drafting:

1. System/context layer: careful editorial assistant.
2. Editorial model layer: author, audience, position, style rules, rubrics, forbidden
   topics, and goals.
3. Brief layer: thesis, conflict, evidence, examples, CTA, risks, and sources.
4. Output contract layer: draft body, notes, risks, and metadata.
5. Human approval reminder: AI proposes a draft, but never approves final text.

Slice 0.8 intentionally adds no provider SDKs, API keys, environment variables,
backend, streaming, billing, or real provider calls.

## Validation Strategy

Current tests cover:

- Author memory event creation, assertion inference, evidence links, persistence, and
  UI smoke behavior.
- Domain transitions and approval rules.
- Deterministic scoring, planning, briefing, drafting, editorial check, and release
  packaging services, plus analytics prep.
- Local workspace save/load behavior.
- UI smoke coverage for the signal to captured learning note flow.

Run `npm test` and `npm run smoke` before completing the slice.
