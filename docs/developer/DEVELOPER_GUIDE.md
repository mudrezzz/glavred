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

Run browser visual smoke checks for operational UI guardrails:

```bash
npm run test:visual
```

Run structural design-system checks for cabinet layout contracts:

```bash
npm run test:design
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
- Local-first external source shell inside author memory: source list, reviewed queue,
  grouping, candidate filters, archive-safe bulk actions, latest bulk undo, and archive
  records.
- Evidence-backed author-position assertions inferred from demo notes.
- Structured editorial setup inside `Редакционная модель`: project profile, atomic
  editorial rules, compact topic/fabula lists, explicit matrix save/cancel behavior,
  and a deterministic validation panel on every internal tab.
- Editable `Редакционная модель`, reviewed signals/radars, plan item, post brief, and
  post draft.
- Human approval gates for content plan, post brief, final text, and release readiness.
- Deterministic style, anti-AI, fact-check, and policy checks for the draft.
- Manual release package with Telegram/LinkedIn targets, checklist, text copy, and
  Markdown download.
- Local analytics prep with manual metrics and captured editorial learning notes.
- Local-first workspace persistence through browser `localStorage`.
- Topbar-triggered context chat overlay with deterministic section-aware chat replies
  and suggestions. The chat can open safe draft flows for rules, topics, and fabulas,
  but does not persist chat state or call AI providers.

The app does not yet include real source ingestion, AI calls, publishing integrations,
autoposting, or real metrics ingestion.

## Wiki Documentation Workflow

The GitHub Wiki is generated from `docs/wiki/`. Keep the source in the main
repository so wiki changes are reviewed, tested, and versioned with the product.

`npm run docs:screenshots` starts Vite on a dedicated local port, opens the app in
Playwright, resets browser `localStorage`, walks through the demo flow, and writes PNG
files to `docs/wiki/assets/screenshots/`.

`npm run test:visual` starts Vite on a dedicated local port and runs Playwright layout
assertions for high-risk operational screens. The current guardrail checks that
`Память автора -> Источники` rows do not overflow or collapse source titles into narrow
columns, that row actions stay inside the row, that autosave/status toast appears only
after an explicit action and disappears automatically, that the context chat overlay
opens from the topbar and keeps visible layer separation, and that `Сигналы` renders
radars and found signals as framed rows with stable chips and no horizontal overflow.
For `Сигналы`, visual smoke also verifies the section header, main/side column gap,
action-button spacing, side-panel action spacing, radar edit-form overflow, and signal
title width. These checks are intentionally stricter than ordinary smoke tests because
the screen is dense and small spacing regressions make it unreadable.

`npm run test:design` starts Vite and checks shared cabinet design-system invariants:
major section headers reuse known patterns, header metric blocks align to the right
edge, cards and panels keep internal padding, main/right columns do not overlap,
dense workspace grids keep a measurable gutter, action groups keep a measurable gap,
tab counters use the shared badge pattern, and radar edit sections align with base
form fields.
It also compares `Signals -> Radars` geometry before and after expanding/collapsing a
radar row, checks the Signals header on a wide desktop viewport, and measures vertical
form rhythm in the radar editor. A disclosure state that shifts the workspace, a
metric group drifting from the right edge, or a label/control pair with no visible gap
is a design-system failure.
The checks also require existing radar edit mode to render inside the edited
`data-testid="radar-row"` and require radar rule/source value controls to use multiline
`textarea` fields. Creating a new radar may use a temporary top-of-list draft, but
editing an existing radar must stay in-place.
Use it whenever a slice changes a large operational screen, not only when screenshots
change.

Cabinet action taxonomy is intentional:

- secondary white buttons are ordinary work actions, such as adding a radar/topic,
  editing, opening, cancelling or navigating;
- primary red buttons are validation, approval, save/commit and HITL lifecycle
  actions.

Entity list toolbars should use the compact count-left/action-right pattern. Entity
rows should reserve stable metadata slots and render fallbacks for optional values
instead of leaving layout holes.
Expandable rows must keep the same horizontal geometry in collapsed and expanded
states. If a row needs more detail, add vertical content inside the existing frame; do
not let disclosure change the main/side grid, toolbar width, or row width.

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
- `RadarDefinition` for local-first radar settings: source type, scope, acceptance
  policy, trigger mode, status, last run, and notes.
- `RadarSearchRule` and `RadarSearchSource` for structured radar configuration.
  Rules are atomic and support `and`, `or`, and `negate`; sources are optional and can
  represent archive, URL, MCP, API, search keywords, manual source, social profile,
  document, or open web.
- `SourceSignal` now supports review metadata: `radarId`, `reviewStatus`,
  `suggestedTopicId`, `suggestedFabulaId`, `suggestedValue`, `duplicateRisk`, and
  `authorCorrection`.
  `suggestedTopicId`, `suggestedFabulaId`, and `suggestedValue` are temporary
  compatibility fields. The `Найденные сигналы` UI treats signals as raw material and
  does not expose topic/fabula matching; Slice 1.6 moves matching to `PostCandidate`.
  New signal-facing fields are `evidence` and `searchNote`.
- `Topic`, `Fabula`, `WeightRange`, and `TopicFabulaMatrixEntry` as implemented
  structured editorial entities. `ContentDesignRecord` and `PlatformProfile` remain
  future entities.
- `ValidatorResult` as a common score/status/evidence contract across setup,
  planning, drafting, release, and archive uniqueness.
- `ContextChatSession` for a future right-side assistant synchronized with the active
  section.

Do not model these as one large prompt or one freeform settings textarea. The product
requires small entities, explicit rules, validator scores, and evidence links.

## Architecture Boundaries

The implemented flow is:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> InsightCard -> BroadcastContentPlan -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

Planning architecture is being corrected after Slice 1.4. The broadcast grid is the
current compatibility layer, but the intended flow is:

`AuthorMemory/Archive/ExternalSources -> Сигналы -> Кандидаты постов -> BroadcastContentPlan -> approved PostBrief`

Use these boundaries:

- Domain objects and pure transitions live in `src/domain/`.
- Application services normalize author notes into memory events, infer
  evidence-backed author-position assertions, and turn the demo signal into an insight
  card, a broadcast content grid, a post brief, a deterministic draft, editorial
  checks, editor notes, a release package, and an editorial learning scaffold.
- Infrastructure adapters handle browser `localStorage` through a `WorkspaceStore`
  interface.
- React components render the workflow and call application services; they must not own
  domain rules.
- `WorkspaceState.contentPlanItems` is the broadcast grid. `contentPlanItem` remains a
  compatibility field for the currently selected/approved slot used by post brief,
  release, and analytics services.
- `Сигналы` owns local-first radar settings and reviewed source material. `sourceSignals`
  is the new signal list; `sourceSignal` remains the compatibility field for the
  currently selected approved signal used by insight, plan, brief, release, and
  analytics services.
- Future `PostCandidate` services should assemble signal/topic/fabula/audience/value/
  goal combinations before a calendar slot becomes an approved post concept.
- The author-memory UI may use browser-only helpers for local link previews, derived
  titles, search filters, summary counts, and voice-input capability detection. These
  helpers must not fetch external metadata or bypass local-first storage.

Do not call browser storage from domain code. Do not add backend persistence, auth,
real source ingestion, or AI provider calls until their slices are planned.

Do not deepen `План` as a standalone generator of posts. The next planning slices must
first add the signal workspace and post candidate assemblies so the calendar shows
material readiness rather than invented slots.

Signal review transitions are pure domain helpers:

- `approveSignal(signal)` marks material ready for insight generation.
- `rejectSignal(signal)` removes it from active consideration.
- `archiveSignal(signal)` keeps it as non-active context.
- `correctSignal(signal, patch)` stores author corrections. In the UI, correction also
  creates a targeted `AuthorNote` so the author-memory layer learns from review
  choices.

`LocalWorkspaceStore.normalizeWorkspace` fills missing `radars` and `sourceSignals`
from the demo workspace and maps old `activeSection: "radar"` browser state to
`activeSection: "signals"`.

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

## Topic And Fabula Runtime Layer

Slice 1.1 decomposes part of the old `EditorialModel` into runtime entities while
keeping legacy fields for compatibility.

Implemented entities:

- `Topic`: title, description, purpose, audience value, author stance, rules,
  forbidden angles, advisory `WeightRange`, and active/paused status.
- `Fabula`: title, description, dramaturgy, structure, proof requirements, rules,
  advisory `WeightRange`, and active/paused status.
- `TopicFabulaMatrixEntry`: `topicId`, `fabulaId`, and `enabled`.

Rules:

- `createDefaultTopicFabulaMatrix` enables all topic/fabula pairs by default.
- `completeTopicFabulaMatrix` fills missing entries during storage normalization.
- `normalizeWeightRange` clamps values to `0..100` and keeps `min <= max`.
- `getTopicFabulaWarnings` reports active topics or fabulas that have no active
  compatible pair.
- Deterministic insight/planning/briefing services use the first active compatible
  topic/fabula when the workspace passes these entities in. Calls without them keep
  the legacy rubric/fabula fallback.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing `topics`, `fabulas`, and
  `topicFabulaMatrix` from the demo workspace so old browser state continues to load.

## Editorial Model UX Rules

Slice 1.1.1 adds `ProjectProfile`, `EditorialRule`, and lightweight setup validation
contracts around the Slice 1.1 topic/fabula layer. Slice 1.1.2 adds explicit
validation-run state so the UI can show a saved validation snapshot instead of
recalculating setup feedback live. Slice 1.2 replaces the ad-hoc setup check with a
shared validator baseline.

Runtime rules:

- `WorkspaceState.projectProfile` stores the project name, description, and setup
  status. The seeded demo project is `TG-блог AI Product Manager`.
- `WorkspaceState.editorialRules` stores atomic rules grouped by author, audience,
  positioning, style voice, style language, style rhythm, anti-AI pattern, goal, and
  forbidden topic.
- `WorkspaceState.editorialSetupRevision` increments after committed editorial setup
  changes.
- `WorkspaceState.editorialValidationRun` stores the last manual validation snapshot:
  run id, revision, checked timestamp, `ValidatorRun.results`, aggregate status,
  aggregate score, and a compatibility `EditorialValidationSummary`.
- Legacy `EditorialModel.rubrics` and `EditorialModel.fabula` remain available for
  downstream service compatibility, but the UI no longer exposes them as setup fields.
- `runEditorialSetupValidators(workspace)` is the deterministic Slice 1.2 validator
  runner. It returns `ValidatorRun` with `ValidatorResult[]`.
- `createEditorialValidationRun(workspace)` wraps the runner with aggregate status,
  aggregate score, and summary compatibility for the current UI/storage boundary.
- `validateEditorialSetup(workspace)` remains as a summary helper for compatibility.
- Implemented setup validators:
  `author-position-clarity`, `anti-ai-style-coverage`, `audience-value-fit`,
  `goal-consistency`, and `topic-fabula-coverage`.
- Topic/fabula CRUD is explicit:
  - `createTopicDraft()` and `createFabulaDraft()` create local draft entities.
  - `addTopic()` and `addFabula()` commit normalized entities.
  - `deleteTopic()` and `deleteFabula()` remove entities and their matrix links.
  - `completeTopicFabulaMatrix()` fills newly missing links with `enabled: true`.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing project/rule fields from the
  demo workspace so older local browser states continue to load.

Frontend rules are now ADR-backed:

- Reuse existing product interaction patterns before inventing local controls.
- Treat editorial settings as structured rules, not large textareas.
- Use read/edit/save/cancel for important entity edits.
- Use a single main column plus a right-side validation panel for editorial setup.
- Do not render anonymous domain text as a hero.
- Use compact list-first catalogs with details on demand.
- Use single-column lists for operational entity catalogs; avoid two-column card
  grids for editable/reviewable entities such as sources, topics, fabulas, future
  platforms, formats, and CDR/PDR records.
- Add real-browser visual smoke checks when changing operational catalog layout,
  because DOM tests do not catch collapsed text columns or overflowing actions.
- Render operational cabinet lists as framed rows/cards. Metadata, expanded details,
  and actions must stay inside the same entity container; status chips must not wrap by
  letters or become tall badges. See ADR `cabinet-lists-require-framed-rows-and-visual-coverage`.
- Keep autosave/status toast event-driven and temporary; do not use a permanent bottom
  overlay for local workspace status.
- Implement context chat as a topbar-triggered, tabbed overlay. Do not add a permanent
  third column or floating page button beside existing right-side panels.
- Give overlay drawers visible but restrained layer separation: subtle directional
  shadow and edge separation, not a full modal backdrop.
- Keep validation visible as a first-class UX surface.
- Run editorial setup validation only after explicit `Проверить`; show stale state
  after saved setup changes.
- Keep editorial entity layouts contained: wrap long labels, use one shared detail
  scroll area, and make matrix topic columns sticky during horizontal scroll.

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
