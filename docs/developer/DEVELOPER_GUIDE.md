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

Run React architecture guardrails:

```bash
npm run test:architecture
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

## Product and Refactor Slice Preflight

Before implementing a product, refactor, domain, application, app, or frontend slice:

1. Read the active `ROADMAP.md` slice and confirm it has `Architecture impact`.
2. Check the planned files against the current large-file limits in
   `scripts/architecture-smoke.mjs`.
3. Treat files reported as near-limit by `npm run test:architecture` as closed for new
   behavior unless the same slice includes a refactor step into a role-owned module.
4. Confirm module ownership before editing:
   - app shell and high-level wiring stay in `src/app/`;
   - feature UI stays under its own `src/features/<feature>/` folder;
   - shared visual primitives go to `src/shared/ui`;
   - shared business behavior goes to `src/application` or `src/domain`.
5. For frontend work, check existing design-system primitives before adding a new UI
   pattern.
6. Run `npm run test:architecture` before completing the slice. For visible frontend
   changes, also run `npm run test:design` and `npm run test:visual`.

Architecture rules are accepted only when they are documented in ADR/SAO and backed by
an automated check or mandatory workflow checklist. Warning-level near-limit and
export-count output should be reviewed even when the command exits successfully.

## Source Layout

- `src/domain/`: framework-independent domain model.
- `src/application/`: deterministic application services for author memory inference,
  insight, planning, briefing, drafting, editorial checks, release packaging, and
  analytics prep.
- `src/infrastructure/`: browser storage adapter.
- `src/fixtures/`: demo workspace data.
- `src/App.tsx`: React composition root. It connects the app shell, workspace
  controller, context chat, and feature entrypoints, but must not own feature UI,
  persistence, autosave, reset, navigation shell, or app-level orchestration.
- `src/app/`: app shell, topbar/sidebar, navigation, context-chat overlay/scope, and
  workspace controller.
- `src/features/signals`: feature-owned `Signals` workspace. It receives workspace
  data and callbacks from the app controller and does not own persistence.
- `src/features/editorial-model`: feature-owned editorial setup workspace. It owns
  project profile UI, publisher rules, topics, fabulas, matrix, and setup validation
  rendering, but receives workspace data and callbacks from the app controller.
- `src/features/author-memory`: feature-owned author memory workspace. It owns the
  memory feed, composer, assertions/evidence correction UI, import sources, import
  queue, archive, attachments, and local import/archive UI orchestration, but receives
  workspace data and callbacks from the app controller and does not own persistence.
- `src/features/plan`: feature-owned broadcast grid and plan slot UI.
- `src/features/briefing`: feature-owned post brief / concrete post-fabula workflow.
- `src/features/editing`: feature-owned draft, editorial checks, editor notes, and
  final-text approval UI.
- `src/features/release`: feature-owned manual export package, checklist, copy, and
  Markdown export UI.
- `src/features/analytics`: feature-owned manual metrics and editorial learning note
  UI.
- Future `src/features/*`: feature-owned screens such as context chat when it is
  extracted from the app layer.
- `src/shared/ui`: shared cabinet primitives such as `Icon` and `WeightRangeEditor`.
- `src/shared/ui/WorkflowPrimitives.tsx`: shared production-flow primitives such as
  HITL gates, field rows/lists, placeholders, and empty states.
- `src/shared/format`: formatting helpers.
- `src/shared/format/production.ts`: shared production-flow labels, dates, and text
  helpers.
- `src/test/`: test setup.
- `src/test-support/`: small repeated app-flow navigation/setup helpers. Do not place
  business assertions or page-object frameworks here.
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
For `План`, the same command checks canonical tabs, filter-card placement before the
broadcast list, row overflow, action spacing, and readable warning contrast. A
centered floating list action, a slot card in the side panel, or low-contrast warning
text is a design-system failure.
The broadcast grid filter toolbar must also expose the calendar view tab, and visual
smoke checks that the calendar opens, shows candidate counts per date, and renders the
same row cards for the selected date.
For `Редактура`, design smoke opens both `Посты` and `Рабочий стол`: the section header
must reuse project-profile padding, header metrics must align to the right edge, the
queue side panel must use shared compact `.summary-item` metric cards, and the
selected-post workbench must not reintroduce a redundant top post header.
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
  `suggestedTopicId`, `suggestedFabulaId`, and `suggestedValue` are compatibility
  fields for older signal fixtures. The `Найденные сигналы` UI treats signals as raw
  material and does not expose topic/fabula matching; `PostCandidate` is now the first
  matching layer.
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

The implemented flow still contains compatibility release artifacts:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> PostCandidate -> InsightCard -> BroadcastContentPlan -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

The target production boundary is:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> PostCandidate -> InsightCard -> BroadcastContentPlan -> EditorialWorkItem -> approved PostBrief -> approved PostDraft -> Visual -> ReadyPost -> PublicationLogEntry -> EditorialLearningNote`

`FinalText` and `ReleasePackage` should be treated as compatibility/manual-export
artifacts until their cleanup slices. Do not add new user-facing preparation behavior
to `Выпуск`.

Planning architecture is being corrected after Slice 1.4. The broadcast grid is the
current compatibility layer, but the intended flow is:

`AuthorMemory/Archive/ExternalSources -> Сигналы -> Кандидаты постов -> BroadcastContentPlan -> approved PostBrief`

React UI now has an explicit architecture baseline. `App.tsx` is a composition root
and must stay small. App shell, navigation, context-chat overlay, shared icon, weight
range editor, workspace controller, signals, editorial-model, author-memory, plan,
briefing, editing, release, and analytics features have been extracted. New large
screens, editors, panels, cards, headers, overlays, and formatting helpers should be
added to `src/app/`, `src/features/<feature>/`, `src/shared/ui`, or
`src/shared/format`, not directly to `App.tsx`.

Run `npm run test:architecture` before completing any UI slice. The current guardrail
blocks `App.tsx` and `App.test.tsx` growth past the accepted baseline, checks required
app/shared extraction files, author-memory, signals, editorial-model, plan, briefing,
editing, release, and analytics feature entries, and verifies that `App.tsx` no longer
imports `LocalWorkspaceStore` or contains extracted feature internals. After Slice
1.10.6.3 the limits are `App.tsx <= 350`, `App.test.tsx <= 300`, and large App UI
declarations `<= 1`. `App.test.tsx` is shell/navigation-only; feature user flows live
beside the owning feature as `*AppFlow.test.tsx`.

After Slice 1.5.15, architecture smoke also tracks large-file baselines outside
`App.tsx`. These are temporary ceilings:

- `src/features/author-memory/AuthorMemoryView.tsx`
- `src/domain/editorialWorkspace.ts`
- `src/features/editorial-model/EditorialModelView.tsx`
- `src/fixtures/demoWorkspace.ts`
- `src/features/signals/SignalsView.tsx`
- `src/application/editorialServices.ts`
- `src/domain/editorial-model/transitions.ts`
- `src/fixtures/demoImports.ts`

Do not add product behavior to these files unless the same slice lowers the relevant
limit by extracting cohesive modules. As of the refactoring chain through Slice 1.5.23,
`editorialWorkspace.ts`, `editorialServices.ts`, and `demoWorkspace.ts` are compatibility
facades/factories rather than owners of all domain, service, or demo logic. Source comments
should explain ownership, invariants, compatibility fields, deterministic stubs, and future
provider/backend boundaries; avoid comments that only describe obvious JSX or assignments.

After Slice 1.5.24, feature entrypoints must stay thin. `AuthorMemoryView`,
`EditorialModelView`, and `SignalsView` should compose feature-local modules, not absorb
every tab, dialog, row, editor, side panel, and helper. Use the existing split as the
default destination for new code:

- Author memory import/source/archive UI belongs in `ExternalSourcesView`,
  `ImportQueueView`, `CandidateCard`, `ArchiveView`, or `BulkActionDialog`.
- Editorial model setup UI belongs in `ProjectProfileHeader`, `PublisherRulesView`,
  `TopicsTab`, `FabulasTab`, or `MatrixTab`.
- Signals setup UI belongs in `RadarEditor`; signals summary belongs in
  `SignalsSidePanel`.

After Slice 1.5.25, `AuthorMemoryView` is also only a feature composition root.
Memory feed, composer, note edit/delete, correction conflict, and filtered-note state
belong in `useMemoryFeedController`; import queue, archive restore/delete, selected
candidates, bulk confirmation, and undo state belong in `useImportReviewController`.
Rendering is split into `MemoryFeedTab`, `MemorySidePanel`, and `MemoryDialogs`.

After Slice 1.5.26, `SignalsView` is also only a feature composition root. Signals tab,
expanded row, radar draft, signal draft, filter, summary, and derived-list state belongs
in `useSignalsController`. Rendering is split into `SignalsHeader`, `SignalsTabs`,
`RadarsTab`, `RadarCard`, `FoundSignalsTab`, `SourceSignalCard`, and
`PostCandidatesPreviewTab`. `RadarEditor` remains the radar form editor, not the owner
of tab/list state.

After Slice 1.6, `PostCandidatesPreviewTab` is the real candidates tab composition root,
not a placeholder. Candidate derivation belongs in `usePostCandidatesController`,
candidate rendering belongs in `PostCandidateCard`, deterministic assembly belongs in
`src/application/postCandidateService.ts`, and candidate approval/downstream reset
belongs in `src/app/usePostCandidateWorkspaceActions.ts`.

After Slice 1.7, large operational entity lists must use the shared cabinet list
pattern: `filter card -> search -> list/group toggle -> framed rows -> bottom-left
actions`. `Кандидаты постов` follows the same UX rule as
`Память автора -> Очередь разбора`: filters and grouping live in
`PostCandidatesToolbar`, grouped rendering in `PostCandidateGroupList`, inline editing
in `PostCandidateEditForm`, and local filter/group helpers in `postCandidateFilters`.
Do not add new large-list hero/summary blocks above the filter card. Primary row
actions are red only for the main approval/save step; secondary row actions stay white.

After Slice 1.8.1, `План` follows the same cabinet-list contract. Broadcast slots must
start with a filter card, full-width search, list/group tabs, and framed rows in
`.broadcast-main`; slot cards must not render in `.broadcast-aside`. Expanded and edit
states must keep readonly candidate context visible: source signal, topic, fabula,
audience, value, and goal. Plan edit fields may change schedule/slot metadata, but
must not hide the candidate/source context that explains what is being scheduled.

After Slice 1.8.2, the broadcast grid has a third view mode: `Календарь`. It must reuse
the planning mini-calendar period model (`week | month | quarter`), count the currently
filtered plan items by date, and render date-specific candidates with the same
`BroadcastGridRow` component used by the list/group views. Do not build separate
calendar-only candidate cards unless a later slice explicitly changes the row contract.

Planning settings use the mini-calendar as the visible source of publish-slot choices.
Clicking a day selects/unselects an explicit `publishSlots` date. Period changes switch
the visible horizon: week, month, or quarter. `publishingDays` and `publishingTimes`
remain normalized fallback/default fields for older workspaces and generated slots,
but new UX should not reintroduce abstract weekday toggle bars as the primary control.

After Slice 1.7.1, `PostCandidate` does not own `format`. Fabula is the candidate's
editorial shape; broadcast grid settings and `ContentPlanItem` own plan formats.
Candidate edit context must show readonly source signal and topic, and may edit
`fabulaId` with a compatibility warning instead of silently hiding matrix risk.

After Slice 1.5.27, `ImportQueueView` is also only the author-memory import-queue
composition root. Filter controls and view-mode switching belong in
`ImportQueueToolbar`; selected-count and bulk actions belong in `ImportQueueBulkBar`;
group/list/empty rendering belongs in `ImportCandidateGroupList`, `ImportCandidateList`,
and `ImportQueueEmptyState`. Keep import transitions in the existing controller and
domain helpers; queue view modules must not own persistence.

After Slice 1.5.28, `useWorkspaceController` is also only an app-level public facade.
Do not add new persistence, context-chat, radar/signal, production-flow, or browser
export action groups directly to it. Use the role-owned app hooks instead:

- `useWorkspacePersistence` owns load/save/reset/toast and workspace patch helpers.
- `useContextChatController` owns chat open/tab/messages/suggestions/intents.
- `useSignalsWorkspaceActions` owns radar and signal workspace mutations.
- `useProductionFlowActions` owns insight, plan, brief, draft, release, and analytics
  callbacks.
- `releaseExport` owns clipboard and Markdown download browser edges.

Domain transitions follow the same rule. `src/domain/editorial-model/transitions.ts`
is a compatibility barrel. Rule transitions go to `rules.ts`, setup validators to
`validation.ts`, and topic/fabula/matrix operations to `catalog.ts`. This applies OOP/SRP
through explicit ownership and stable module boundaries rather than class-heavy React.

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
- Approved posts use `EditorialWorkItem` identity rather than expanding singleton
  production state. The current `postBrief`, `postDraft`, `finalText`,
  `releasePackage`, and `editorialLearningNote` fields remain compatibility fields.
  Slice 1.10 creates or updates the selected work item and prepares its initial
  `PostBrief` when a plan slot is approved; future production actions should accept an
  explicit work-item id so editing one post does not overwrite another queued post.
- `Редактура` owns the production queue from approved slot to ready post. Its UX rule
  is `section header -> Посты / Рабочий стол tabs -> filter card -> search ->
  list/group toggle -> framed rows -> selected-post workbench`. The selected-post
  workbench owns post preparation: `Фабула`, `Драфт`, `Визуал`, and
  `readyForRelease`. Visual modes must pass through the review contract:
  brief, prepare deterministic or adapter-backed variants, select one variant,
  then approve. `memeRemix` is the exception inside that contract: it prepares and
  selects a meme reference before preparing final remix variants. `noVisual` is the
  only direct visual completion path.
- `Выпуск` owns delivery history for ready posts. It should show publication log
  records, statuses, external links, platform errors, and retry notes. It must not
  edit text, visual, brief, candidate, or slot artifacts.
- `WorkspaceState.contentPlanSettings` is normalized on load. It owns period, tempo,
  publishing days/times, candidate limits, default platform, and signal-selection
  policy. Saving settings clears generated plan slots and downstream production
  artifacts so the grid is rebuilt explicitly.
- `Сигналы` owns local-first radar settings and reviewed source material. `sourceSignals`
  is the new signal list; `sourceSignal` remains the compatibility field for the
  currently selected approved signal used by insight, plan, brief, release, and
  analytics services.
- `PostCandidate` services assemble signal/topic/fabula/audience/value/goal/platform
  combinations before insight creation. Approving a candidate sets
  `WorkspaceState.postCandidate`, switches the current `sourceSignal` to the candidate's
  source, and clears stale downstream insight, selected plan item, brief, draft,
  release, and analytics artifacts. Editing or rejecting a candidate updates only
  candidate review state and must not create or clear downstream artifacts. A rejected
  candidate cannot become the current approved concept.
- The author-memory UI may use browser-only helpers for local link previews, derived
  titles, search filters, summary counts, and voice-input capability detection. These
  helpers must not fetch external metadata or bypass local-first storage.

Do not call browser storage from domain code. Do not add backend persistence, auth,
real source ingestion, or AI provider calls until their slices are planned.

Do not deepen `План` as a standalone generator of posts. Planning settings may create
the publish-window frame, but content ideas must continue to come from approved
signals, post candidates, topics, and fabulas. Calendar binding and AI planning need
separate roadmap slices.

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

Slice 1.5.8 extends `RadarDefinition` with `sourceDiscoveryMode` and `filters`.
Domain/application code owns `evaluateSignalAgainstRadarFilters(signal, radar,
workspace)`. React may render the filter editor and evaluation badges, but it must not
duplicate filter scoring rules. `notes` remains a legacy storage field for old
workspaces and must not be reintroduced as a visible radar editor field.

Radar source configuration rules:

- `specifiedOnly` requires at least one source before save.
- `specifiedAndAdditional` means explicit sources are mandatory context, but future
  search adapters may also discover additional sources.
- `autonomous` is valid without sources.
- `style` is not a radar filter dimension.
- failed filter evaluations mark a signal for review; they do not delete or hide it.

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
- Feature-owned app-flow coverage for signals, author memory, editorial model,
  context chat, plan, editing, release, and analytics.
- App shell/navigation coverage in `src/App.test.tsx`.

Run `npm test` and `npm run smoke` before completing the slice.
For new UI behavior, put tests beside the owner:

- app shell only: `src/App.test.tsx`;
- feature workflows: `src/features/<feature>/*AppFlow.test.tsx`;
- component-level feature behavior: the feature component test;
- domain/application/infrastructure behavior: the owning module test.

If `npm run test:architecture` reports a touched test file as near-limit, split that
test by feature/workflow ownership before adding more scenarios.
