# System Architecture Overview

## Product Context

Glavred is an AI-native editorial office for personal and expert media. The product is
not a generic post generator and not a source-signal compiler. It helps an author
capture raw thoughts, reactions, corrections, archive material, and post-release
learning, turn them into a transparent author position model, and use that model to
plan, validate, draft, and release content.

The primary requirements source is `glavred.md`. The design handoff in
`ui-design-systems/` is a secondary visual and product reference. The June 2026 product
revision adds `AuthorMemory` and `AuthorPositionModel` as the conceptual center of the
system. The existing **Редакционная модель** / `EditorialModel` should evolve into a
set of structured, validator-backed editorial entities rather than remain a single
configuration block.

The revised product concept is documented in
`docs/architecture/AUTHOR_POSITION_CONCEPT.md`.

The external source and import-review concept is documented in
`docs/architecture/EXTERNAL_SOURCE_IMPORT_CONCEPT.md`.

The revised signal and broadcast planning concept is documented in
`docs/architecture/SIGNALS_AND_BROADCAST_PLANNING_CONCEPT.md`.

## Strategic Product Model

The durable model is:

`AuthorMemory -> AuthorPositionModel -> EditorialSystem -> Signals -> ContentProduction -> Release -> Learning`

- `AuthorMemory`: a lightweight internal feed of thoughts, reactions, links,
  corrections, small local attachments, archive notes, and post-release learning. It
  must allow loose stream-of-consciousness input.
- `AuthorPositionModel`: a transparent, evidence-backed digest of that memory:
  persona, style, audience, goals, metrics, topics, fabulas, platforms, formats,
  Content Design Records, and validators.
- `EditorialSystem`: structured rules, weights, compatibility matrices, and
  validation contracts that describe how the author publishes.
- `Signals`: radar findings and manually supplied material from author memory,
  archives, external sources, and manual input.
- `ContentProduction`: the downstream layer: approved signals, post candidates,
  broadcast slots, post briefs, drafts, checks, release, and analytics prep.

The main product risk is generic AI compilation. Glavred avoids it by making the
author's own position explicit, editable, evidence-backed, and continuously validated.

## Current Implemented Perimeter

The current implemented perimeter now starts with author memory and reaches a captured
editorial learning note:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> RadarDefinition -> reviewed SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

The source-to-release part remains useful as a production layer. It is no longer the
conceptual center of the product. Author memory, author-position assertions,
structured topics/fabulas, validator results, and reviewed signals now sit above that
flow; future slices should route post candidates and calendar slots through them.

Slice 1.5 adds the first local-first `Сигналы` workspace: demo radars, found signals,
manual review actions, and a read-only `Кандидаты постов` preview. The deeper planning
model still needs Slice 1.6 candidate assemblies before expanding the calendar UI.
Slice 1.5.8 refines radars into separate trigger rules, search sources, source
discovery mode, and editorial filters. Filters evaluate author, audience, positioning,
goals, forbidden topics, and topics; style remains a later drafting/review concern.
Filtered signals stay visible for human review instead of being deleted automatically.

Real AI provider calls, publication automation, backend sync, and real metrics
ingestion remain future slices. The near-term priority is not provider integration; it
is making the author's own position explicit enough that AI can later assist without
turning the product into generic content generation.

## Major Components

- `AuthorMemory`: captures raw author notes, reactions, links, archive annotations,
  manual corrections, rejected angles, draft revisions, and post-release learning
  events.
- `AuthorPositionModel`: aggregates memory into transparent rules and assertions about
  persona, style, audience, goals, topics, fabulas, platforms, and formats. Every
  assertion should have evidence.
- `ProjectProfile`: names the virtual publishing project and carries setup status and
  top-level context for the editorial cabinet.
- `EditorialRules`: stores atomic rules for author, audience, positioning, style,
  anti-AI patterns, goals, and forbidden topics. These are the validator-ready
  successor to large editorial settings textareas.
- `EditorialModel`: compatibility aggregate for author, audience, positioning, legacy
  fabula, legacy rubrics, style rules, forbidden topics, and blog goals. Legacy fields
  remain available to downstream services while the UI moves toward structured rules.
- `TopicCatalog`: stores editable topic cards with purpose, audience value, author
  stance, rules, forbidden angles, status, and advisory weight ranges for planning.
- `FabulaCatalog`: stores reusable post dramaturgy patterns with structure, conflict,
  proof requirements, rules, status, advisory weight ranges, and compatibility with
  topics.
- `ContentDesignRecords`: stores durable content decisions that apply across posts,
  similar to ADRs in software projects.
- `PlatformProfiles`: stores platform and format rules, local validator requirements,
  and planning weights.
- `ValidatorFramework`: evaluates entities and production artifacts, returning score,
  status, evidence, and fix guidance.
- `ContextChat`: topbar-triggered, tabbed overlay assistant synchronized with the active
  product section and internal tab. The current implementation is deterministic,
  provider-free, supports local chat replies and suggestions, and can open safe draft
  flows for structured entities without saving changes automatically.
- `SignalsWorkspace`: reviews radar findings and manually supplied material before it
  can become a post concept.
- `EditorialRadar`: configurable source procedure inside `Сигналы`. Radar output is
  fuel for author memory and content production, not the only source of posts.
- Slice 1.5.1 correction: `EditorialRadar` owns atomic search rules and optional
  search sources. `SourceSignal` remains raw material with radar provenance, date,
  finding, evidence, search note, duplicate risk, and review status. Topic/fabula/
  audience/value matching starts in `PostCandidateAssembly`, not in the signal review
  UI.
- Slice 1.5.8 correction: `EditorialRadar` also owns source discovery mode and
  editorial filters. The deterministic filter service returns per-filter status, score,
  summary, and evidence on `SourceSignal`; React renders those results but does not
  implement scoring logic.
- `ExternalSourceSettings`: stores planned or connected source configurations for
  Telegram, social profiles, blogs, documents, article archives, and manual uploads.
- `ImportReviewQueue`: holds imported candidates before they affect author memory,
  archive, or author-position assertions.
- `ImportCandidateGroups`: groups large imports by source, date, tag, duplicate
  cluster, evidence risk, or status so the author can review patterns instead of
  every item.
- `BulkImportActions`: records reversible bulk choices such as `Добавить все`,
  accepting selected items into archive, or ignoring selected items as evidence.
- `ArchiveRecords`: stores accepted historical posts and long-form materials with
  provenance and evidence policy.
- `PostCandidateAssembly`: combines a reviewed signal with topic, fabula, audience,
  value, goal, platform, and format options before a post concept is approved.
- `InsightScoring`: turns a reviewed source signal into an insight card with relevance,
  urgency, banality risk, fact gaps, suggested topic, and suggested author position.
- `ContentPlanning`: describes broadcast demand and calendar status: tempo, period,
  publishing days/times, candidate count requirements, platform/date/topic/fabula/
  format, approval status, manual override state, and advisory conflicts.
- `Briefing`: turns an approved plan item into a post brief with thesis, conflict,
  author position, evidence, examples, structure, CTA, risks, sources, and approval
  status.
- `Drafting`: turns an approved post brief into an editable draft.
- `EditorialChecks`: models style, anti-AI, fact-check, and policy checks plus editor
  notes before final approval.
- `ReleasePackaging`: turns approved final text into platform targets, Markdown
  preview, release checklist, and manual export status.
- `AnalyticsPrep`: turns an exported release package into manual metric fields and an
  editorial learning note.
- `AIProviderBoundary`: defines how future provider-backed services can replace
  deterministic application services without leaking provider details into React or
  domain code.
- `LocalWorkspaceStore`: loads and saves the current workspace state in browser
  storage for the first implementation circles.

## Dependency Direction

Dependencies must point inward:

`React UI -> application services -> domain model`

Infrastructure adapters sit at the edge:

`React UI -> application services -> WorkspaceStore adapter -> localStorage`

Future provider integration follows the same rule:

`React UI -> application service -> provider boundary -> infrastructure provider adapter`

Domain code must not import React, browser APIs, storage APIs, future AI providers, or
network clients. React components render state and trigger application service methods.
Application services orchestrate domain operations, call adapters, and decide whether
to use deterministic fallback or provider-backed behavior.

## React UI Architecture

The React implementation has been extracted from the initial fast-exploration
god-file. As of Slice 1.5.14, `src/App.tsx` is a small composition root. Shell,
navigation, topbar/sidebar, context-chat overlay, shared icon, weight range editor,
persistence/autosave/reset, high-level workspace orchestration, `Author Memory`,
`Editorial Model`, `Signals`, and the production flow feature entrypoints now live
outside `App.tsx`. This is the new baseline for future feature work.

Target structure:

- `src/app/`: app shell, topbar/sidebar, navigation, context-chat overlay and scope,
  and workspace controller.
- `src/features/author-memory`: author memory feed, assertions, import queue, and
  archive UI.
- `src/features/editorial-model`: project profile, rules, topics, fabulas, matrix, and
  setup validation UI.
- `src/features/signals`: radar setup, found signals, signal review, and post
  candidate entry points.
- `src/features/plan`: broadcast grid, planning settings, and future calendar UI.
- `src/features/briefing`: post brief and concrete post-fabula approval workflow.
- `src/features/editing`: draft, editorial checks, editor notes, and final text
  approval.
- `src/features/release`: manual release package, checklist, copy, and Markdown export.
- `src/features/analytics`: manual metrics and editorial learning note UI.
- `src/features/context-chat`: collapsible context assistant overlay, deterministic
  suggestions, and future provider-backed chat adapter boundary.
- `src/shared/ui`: reusable cabinet primitives such as shell sections, panels, framed
  rows, tabs, badges, fields, action groups, metric cards, and empty states.
- `src/shared/format`: labels, dates, status text, source names, and other formatting
  helpers.

React dependency direction is:

`features -> shared/application/domain`

There is no feature -> feature dependency. If two features need the same visual
primitive, it belongs in `src/shared/ui`. If two features need the same business action,
it belongs in application/domain services. If app-level wiring is needed, it belongs in
`src/app/`.

`App.tsx` is a composition root only. It imports `useWorkspaceController`
from `src/app/useWorkspaceController.ts` and must not import `LocalWorkspaceStore`.
It may connect the app shell, workspace controller, and feature entry components, but
new large `*View`, `*Editor`, `*Panel`, `*Card`, `*Header`, `*Sidebar`, `*Topbar`, or
`*Overlay` implementations must not be added there. Domain/application logic must not
be written inside JSX.

Architecture smoke tests enforce the baseline:

- `src/App.tsx <= 350` lines after Slice 1.5.14.
- `src/App.test.tsx <= 850` lines.
- Large `App.tsx` UI declarations `<= 1`.
- Required app/shared extraction files, `src/features/author-memory/AuthorMemoryView.tsx`,
  `src/features/signals/SignalsView.tsx`, and
  `src/features/editorial-model/EditorialModelView.tsx` must exist.
- Production flow entrypoints must exist:
  `src/features/plan/PlanView.tsx`, `src/features/briefing/BriefView.tsx`,
  `src/features/editing/EditView.tsx`, `src/features/release/ReleaseView.tsx`, and
  `src/features/analytics/AnalyticsView.tsx`.
- `src/App.tsx` must not import or instantiate `LocalWorkspaceStore`.
- `src/App.tsx` must not contain signals feature internals such as `RadarEditor`,
  `SignalsSidePanel`, `RadarView`, or radar/signal label helpers.
- `src/App.tsx` must not contain editorial-model internals such as `TopicEditor`,
  `FabulaEditor`, `TopicFabulaMatrixView`, `EditorialValidationPanel`, or
  editorial setup helper factories.
- `src/App.tsx` must not contain author-memory internals such as `AuthorNoteCard`,
  `AssertionCard`, `ExternalSourcesView`, `ImportQueueView`, `ArchiveView`, or
  author-memory/import helper functions.
- `src/App.tsx` must not contain production-flow internals such as `PlanView`,
  `BriefView`, `EditView`, `ReleaseView`, `AnalyticsView`, `HitlGate`, `FieldInput`,
  `CheckCard`, or `FinalTextView` implementations.
- The React UI architecture ADR and this SAO section must exist.

Every extraction slice must lower these limits. The target after the extraction chain
is now met for `App.tsx`; future slices should keep it at composition-root size and
avoid moving feature behavior back into it.

### Large-file guardrails

The next architecture risk is no longer `App.tsx`; it is large domain, application,
fixture, and feature files. Architecture smoke now tracks current large-file baselines:

- `src/app/useWorkspaceController.ts <= 220`
- `src/app/useWorkspacePersistence.ts <= 170`
- `src/app/useContextChatController.ts <= 220`
- `src/app/useSignalsWorkspaceActions.ts <= 180`
- `src/app/useProductionFlowActions.ts <= 260`
- `src/app/releaseExport.ts <= 90`
- `src/features/author-memory/AuthorMemoryView.tsx <= 320`
- `src/features/author-memory/useMemoryFeedController.ts <= 280`
- `src/features/author-memory/useImportReviewController.ts <= 300`
- `src/features/author-memory/MemoryFeedTab.tsx <= 260`
- `src/features/author-memory/MemorySidePanel.tsx <= 140`
- `src/features/author-memory/MemoryDialogs.tsx <= 120`
- `src/domain/editorialWorkspace.ts <= 170`
- `src/features/editorial-model/EditorialModelView.tsx <= 220`
- `src/fixtures/demoWorkspace.ts <= 120`
- `src/features/signals/SignalsView.tsx <= 180`
- `src/features/signals/useSignalsController.ts <= 280`
- `src/features/signals/RadarsTab.tsx <= 220`
- `src/features/signals/RadarCard.tsx <= 240`
- `src/features/signals/FoundSignalsTab.tsx <= 220`
- `src/features/signals/SourceSignalCard.tsx <= 260`
- `src/features/signals/SignalsHeader.tsx <= 100`
- `src/features/signals/SignalsTabs.tsx <= 80`
- `src/features/signals/PostCandidatesPreviewTab.tsx <= 120`
- `src/application/editorialServices.ts <= 20`
- `src/domain/editorial-model/transitions.ts <= 20`
- `src/domain/editorial-model/rules.ts <= 50`
- `src/domain/editorial-model/validation.ts <= 460`
- `src/domain/editorial-model/catalog.ts <= 190`
- `src/features/author-memory/ImportViews.tsx <= 20`
- `src/features/author-memory/ImportQueueView.tsx <= 150`
- `src/features/author-memory/ImportQueueToolbar.tsx <= 120`
- `src/features/author-memory/ImportQueueBulkBar.tsx <= 130`
- `src/features/author-memory/ImportCandidateGroupList.tsx <= 140`
- `src/features/author-memory/ImportCandidateList.tsx <= 120`
- `src/features/author-memory/ImportQueueEmptyState.tsx <= 60`
- `src/features/editorial-model/EditorialModelParts.tsx <= 20`
- `src/features/editorial-model/TopicsTab.tsx <= 310`
- `src/features/editorial-model/FabulasTab.tsx <= 310`
- `src/features/signals/RadarEditor.tsx <= 270`
- `src/fixtures/demoImports.ts <= 410`

These are temporary ceilings, not acceptable target sizes. domain/application/fixtures/feature files must shrink through the 1.5.x refactoring chain. Product slices that add new user-facing UI are deferred until the large-file guardrails are lowered through bounded-context decomposition.

The refactoring direction is:

- domain types and transitions have moved from `editorialWorkspace.ts` into
  bounded-context modules;
- application services have moved from `editorialServices.ts` into workflow-specific
  services;
- demo data has moved from `demoWorkspace.ts` into scenario/context fixtures;
- large feature entrypoints have started moving internal tabs, panels, cards, forms, dialogs, and
  local helpers into feature-local files;
- feature modules still obey `no feature -> feature`.

Feature entrypoints stay thin. `AuthorMemoryView`, `EditorialModelView`, and
`SignalsView` are composition surfaces for their feature, not owners of every tab,
dialog, editor, row, side panel, and helper. Feature-local internals now live in
role-owned files such as:

- `src/features/author-memory/ExternalSourcesView.tsx`,
  `ImportQueueView.tsx`, `ImportQueueToolbar.tsx`, `ImportQueueBulkBar.tsx`,
  `ImportCandidateGroupList.tsx`, `ImportCandidateList.tsx`,
  `ImportQueueEmptyState.tsx`, `CandidateCard.tsx`, `ArchiveView.tsx`, and
  `BulkActionDialog.tsx`;
- `src/features/author-memory/useMemoryFeedController.ts`,
  `useImportReviewController.ts`, `MemoryFeedTab.tsx`, `MemorySidePanel.tsx`,
  and `MemoryDialogs.tsx`;
- `src/features/editorial-model/ProjectProfileHeader.tsx`,
  `PublisherRulesView.tsx`, `TopicsTab.tsx`, `FabulasTab.tsx`, and
  `MatrixTab.tsx`;
- `src/features/signals/useSignalsController.ts`, `SignalsHeader.tsx`,
  `SignalsTabs.tsx`, `RadarsTab.tsx`, `RadarCard.tsx`, `FoundSignalsTab.tsx`,
  `SourceSignalCard.tsx`, `PostCandidatesPreviewTab.tsx`, `RadarEditor.tsx`,
  and `SignalsSidePanel.tsx`.

Stateful feature orchestration belongs in feature-local hooks, not entrypoints.
After Slice 1.5.25, `AuthorMemoryView` composes the active memory tab, side panel,
and dialogs. Feed/composer/edit/delete/correction state lives in
`useMemoryFeedController`; import queue, archive, selection, bulk action, and undo
state lives in `useImportReviewController`.

After Slice 1.5.26, `SignalsView` composes the signals header, tabs, and active
workspace tab. Radar/signal expanded state, edit drafts, filters, summaries, and
derived lists live in `useSignalsController`; tab/entity rendering lives in
feature-local modules.

After Slice 1.5.27, `ImportQueueView` is also only a queue-tab composition root.
Queue filters and view mode live in `ImportQueueToolbar`; selection and bulk actions
live in `ImportQueueBulkBar`; list/group/empty rendering lives in
`ImportCandidateList`, `ImportCandidateGroupList`, and `ImportQueueEmptyState`.

After Slice 1.5.28, `useWorkspaceController` is only the app-level public facade.
Persistence/autosave/reset/toast live in `useWorkspacePersistence`; context-chat
state and suggestions live in `useContextChatController`; radar/signal mutations live
in `useSignalsWorkspaceActions`; downstream production callbacks live in
`useProductionFlowActions`; clipboard/download browser edges live in `releaseExport`.
New app-level action groups must be added to role-owned hooks, not back into the
controller facade.

Domain transitions are role-owned. `src/domain/editorial-model/transitions.ts`
is a compatibility barrel only; rules, setup validation, and topic/fabula catalog
transitions live in `rules.ts`, `validation.ts`, and `catalog.ts`. New transition
logic should be added to the role-owned file first, then re-exported only when
backward-compatible imports require it.

Source comments are required for domain ownership, invariants, legacy compatibility,
deterministic stubs, and future provider/backend boundaries. Comments should not
describe obvious JSX or restate simple assignments.

### Architecture drift prevention

Architecture rules are part of the delivery system, not only historical notes. A new
architecture rule is accepted only when it is recorded in an ADR, reflected in this
SAO, and backed by either an automated smoke check or an explicit mandatory agent
workflow checklist.

`npm run test:architecture` now reports both hard failures and warning-level drift
signals:

- hard line-count limits for `App.tsx`, `App.test.tsx`, and tracked large
  app/feature/domain/application/fixture files remain blocking;
- near-limit files are any tracked files at or above 85% of their limit and are listed
  at the end of a successful architecture smoke run;
- new behavior must not be added to a near-limit file unless the same slice includes a
  refactor step that moves behavior into a role-owned module;
- export-count warnings are observation-only for now and identify large tracked files
  whose public surface may need a facade or a split;
- `src/features/*` modules cannot import other features directly or through a root
  features barrel; cross-feature code belongs in `src/shared/*`,
  `src/application/*`, `src/domain/*`, or app-level composition.

Every product or refactor slice must include architecture preflight before
implementation. The preflight checks planned files against file-size limits, module
ownership, dependency direction, and design-system ownership. ROADMAP entries for new
product slices must include `Architecture impact`, and future agents must run
`npm run test:architecture` before completing refactor, domain, application, app, or
frontend slices.

The agent workflow is also enforced through `.agents/skills`: slice implementation,
roadmap planning, architecture design, regression strategy, frontend design-system,
and project onboarding now include the guardrails from ADR
`2026-06-16-architecture-drift-is-prevented-by-agent-and-smoke-guardrails`.

## Frontend UX Architecture

Slice 1.1.1 fixes the editorial setup UX and records reusable frontend decisions:

- Product screens reuse existing cabinet controls before adding new patterns.
- Editorial settings are structured rules, not freeform textareas.
- Important entities use read/edit/save/cancel instead of immediate hidden commits.
- Setup workflows use a single main column and a right-side validation panel.
- Page headers must come from explicit project/profile entities, not anonymous domain
  quotes.
- Topic and fabula catalogs use compact rows with details on demand.
- Validation is a first-class surface on every editorial setup tab.
- Editorial setup validation is explicit: the author clicks `Проверить`, then sees a
  validation snapshot. Saved setup changes mark that snapshot as stale until the next
  run.
- Editorial catalogs and matrices must contain realistic long content: wrap labels,
  use shared scroll areas for long details, and keep matrix row context visible with a
  sticky topic column during horizontal scroll.
- Disclosure-heavy lists must be layout-stable: expanding or collapsing an entity row
  adds vertical detail inside the same frame and must not move the header, tabs,
  main/right grid, toolbar, or row horizontally.
- Existing entity edit mode must open inside the selected entity row/card. Top-of-list
  draft forms are acceptable for new entities, but editing an existing entity cannot
  create a duplicate form detached from the row the author clicked.
- Structured search instructions, source descriptions, and other long rule-like values
  use multiline controls. One-line inputs are reserved for short titles, labels, and
  compact scalar settings.
- Dense editor forms must keep measurable vertical rhythm between fields and between
  labels and controls; grouped controls cannot collapse into neighboring labels.
- Context chat uses a collapsible overlay, not a permanent third column beside existing
  right-side panels. It must stay covered by visual smoke checks.

These rules are captured in ADRs under `docs/adr/` and should guide future validator
and context-chat implementation.

## Conceptual Domain Interfaces

Current implemented production contracts:

- `AuthorNote`: free author thought, link reaction, or manual correction.
- `AuthorAttachment`: optional local demo file attached to an author note, with file
  name, MIME type, size, data URL, creation date, and local-only marker.
- `AuthorMemoryEvent`: normalized memory event with detected author signals.
- `AuthorPositionAssertion`: evidence-backed inferred statement about persona, style,
  audience, topic, or principle.
- `EvidenceLink`: link from a position assertion back to source notes.
- `ProjectProfile`: name, description, and setup status for the current editorial
  project.
- `EditorialRule`: group, title, statement, active/paused status, and optional evidence
  note id.
- `ValidatorDefinition`: validator id, title, description, and supported target types.
- `ValidatorResult`: validator id, target, red/yellow/green status, score, summary,
  evidence, and suggested fixes.
- `ValidatorRun`: saved manual validation snapshot with run id, setup revision,
  checked timestamp, and validator results. UI marks it stale when the setup revision
  changes.
- `EditorialValidationSummary`: compatibility summary derived from the latest
  `ValidatorRun`.
- `EditorialModel`: compatibility aggregate for author, audience, positioning, fabula,
  rubrics, style rules, forbidden topics, goals.
- `Topic`: editable topic card with purpose, audience value, author stance, rules,
  forbidden angles, active/paused status, and advisory weight range.
- `Fabula`: editable dramaturgy card with structure, proof requirements, rules,
  active/paused status, and advisory weight range.
- `TopicFabulaMatrixEntry`: compatibility toggle between one topic and one fabula.
- Topic/fabula helpers create local drafts, commit new entities, delete entities, and
  keep matrix links normalized. Added entities get default enabled links; deleted
  entities remove their matrix links without rewriting existing production artifacts.
- `SourceSignal`: type, title, source, capturedAt, summary, rawNote.
- Future `RadarDefinition`: source, scope, acceptance policy, trigger mode, status,
  last run, and notes.
- Future `PostCandidate`: candidate assembly of signal, topic, fabula, audience,
  value, goal, platform, format, confidence, risks, and approval status.
- `InsightCard`: source signal, why it matters, audience relevance, author position,
  rubric, urgency, score, banality risk, fact gaps.
- `ContentPlanItem`: insight, platform, date, priority, format, expected effect,
  approval status, topic/fabula link, manual override state, and warning links.
- `ContentPlanSettings`: local-first tempo and format settings for the broadcast grid.
- `PlanWeightWarning`: advisory warning when the grid diverges from topic/fabula
  weights, matrix compatibility, or required slot fields.
- `PostBrief`: thesis, conflict, author position, evidence, examples, structure, CTA,
  risks, sources, approval status.
- `PostDraft`: brief, title, body, version, draft status, updated time.
- `EditorialCheck`: type, title, check status, summary, findings.
- `EditorNote`: agent, tone, text, target.
- `FinalText`: draft, title, body, approval status, approved time.
- `ReleasePackage`: final text, targets, Markdown, checklist, release status, updated
  time.
- `EditorialLearningNote`: release package, manual metrics, editorial conclusions,
  analytics status, updated time, captured time.
- `WorkspaceStore`: load and save current local workspace state.

Future author-position contracts:

- `ContentDesignRecord`: durable content rule with rationale, scope, status, evidence,
  and validator impact.
- `PlatformProfile`: platform, formats, format rules, weight range, and compatibility
  with fabulas.
- `ContextChatSession`: active section, messages, proposed structured changes, and
  approval state.
- `AuthorExternalSource`: source settings for Telegram, social, blog/site, document,
  article archive, or manual upload.
- `ImportedMemoryCandidate`: imported item waiting for review, grouping, or bulk
  action.
- `ImportCandidateGroup`: grouped candidate set used for large archives.
- `BulkImportSelection`: selected candidates by explicit ids or active filter.
- `BulkImportAction`: reversible record of a group operation.
- `ArchiveRecord`: accepted historical material with provenance and evidence policy.
- `Provenance`: source, original link or file reference, import date, acceptance date,
  acceptance mode, and author reason.
- `EvidencePolicy`: whether imported material can support assertions, is archive-only,
  or is ignored as evidence.

## Conceptual AI Provider Interfaces

These interfaces are documented for future implementation and are not runtime
TypeScript contracts in Slice 0.8:

- `AiProviderAdapter`: infrastructure-side adapter that performs provider-specific
  calls for one capability.
- `DraftGenerationRequest`: approved `PostBrief`, `EditorialModel` or future
  `AuthorPositionModel`, optional previous learning context, locale, output
  constraints, and caller context.
- `DraftGenerationResult`: title, draft body, notes, risks, provider metadata, and a
  shape that can be mapped into `PostDraft`.
- `PromptTemplate`: stable prompt layers and variables used by the application service
  before calling an adapter.
- `ProviderRunMetadata`: provider name, model name if known, run id if available,
  latency, token estimates when available, and fallback status.
- `ProviderError`: normalized error information that does not expose SDK-specific
  exceptions to React or domain code.
- `AiFallbackPolicy`: rules for when to use deterministic fallback, including disabled
  provider mode, missing configuration, provider error, invalid result, or local demo
  mode.

## Validator Architecture

Validators are a common product layer, not only draft checks.

Slice 1.2 implements the first setup-only validator runner:
`runEditorialSetupValidators(workspace)`. It is deterministic and provider-free.
The first validators are:

- `author-position-clarity`;
- `anti-ai-style-coverage`;
- `audience-value-fit`;
- `goal-consistency`;
- `topic-fabula-coverage`.

They should evaluate:

- author position;
- persona and alter ego;
- style and anti-AI quality;
- audience value;
- goal fit;
- topic rules;
- fabula rules;
- platform and format rules;
- Content Design Record compliance;
- uniqueness against archive;
- evidence quality and fact gaps.

Each validator result should include status, score, summary, evidence, and suggested
fixes. The UI should show compact colored indicators with progressive disclosure into
evidence and remediation.

## First Demo Data Flow

The permanent demo scenario is a Telegram blog by an AI Product Manager who shares
research experience building AI-B2B products:

1. The workspace opens on `AuthorMemory` with six seeded notes about workflow risk,
   evals as a product function, failed demo magic, GTM/adoption correction, enterprise
   trust, and confidence boundaries.
2. `createAuthorMemoryEvent` normalizes notes into memory events with detected signals.
3. `inferAuthorPositionAssertions` shows evidence-backed assertions about the author's
   persona, style, audience, topics, and product principle.
4. The author can add another thought, link reaction, file-backed note, or manual
   correction. Attached files are supporting material only; they are not parsed or
   analyzed in the current perimeter.
5. Future external source settings can describe the author's Telegram channel,
   interview notes, blog archive, and talks. Imported candidates must go through review
   or bulk archive acceptance before they influence memory or assertions.
6. `Сигналы` shows demo radars for author memory, archive, external sources, and
   manual research.
7. The author reviews found signals, then approves, archives, rejects, or corrects a
   signal before it becomes production material.
8. The approved signal becomes the compatibility `sourceSignal` for downstream flow.
9. `InsightScoring` produces an `InsightCard`.
10. `ContentPlanning` currently creates a Telegram broadcast grid prototype.
11. The author approves a slot and post brief through HITL gates.
12. `Drafting` creates an editable research-note draft.
13. `EditorialChecks` returns style, anti-AI, fact-check, and policy checks plus editor
   notes.
14. The author approves final text, prepares a manual Telegram release package, and
   captures analytics learning.

## Extension Points

- Author memory can ingest notes, links, archive posts, corrections, and analytics
  learning before production artifacts are created.
- External source import can add candidates to a review queue, but unreviewed material
  must not strengthen author-position assertions.
- Reviewed source material can become `SourceSignal`; unreviewed imports and archive
  records remain source material until the author or an acceptance policy promotes
  them.
- Post candidate assembly can later replace direct plan-slot generation while keeping
  current `contentPlanItems` as a compatibility layer.
- Bulk import can accept many historical items into archive, while preserving
  provenance, acceptance mode, and evidence policy.
- Source ingestion adapters can later replace manual signal entry.
- Validator adapters can later replace deterministic checks while preserving
  evidence-backed `ValidatorResult` contracts.
- Context chat can open draft flows for structured entities, but should not bypass
  explicit author review and save/cancel actions.
- AI provider adapters can later replace deterministic insight, planning, briefing,
  drafting, and check services after author position and validators exist.
- Backend persistence can replace `LocalWorkspaceStore` behind the same workspace store
  interface.
- Platform publication APIs can attach after the manual release package.
- Real analytics ingestion can replace manual metric entry behind the analytics prep
  shape.

## Testing Strategy

Current validation covers:

- Unit tests for author memory event creation and evidence-backed assertions.
- Unit tests for domain transitions and approval rules.
- Unit tests for deterministic scoring, planning, briefing, drafting, editorial check,
  release packaging, and analytics prep services.
- Integration tests for local workspace save/load.
- UI smoke tests for the source signal to captured editorial learning note flow.
- Manual demo acceptance for the founder-blog scenario.

For the author-position product circle, add:

- Unit tests for author note classification and evidence linking.
- Unit tests for topic/fabula weight ranges and compatibility matrix behavior.
- Unit tests for validator score/status aggregation.
- Integration tests for local persistence of author memory and position entities.
- UI smoke tests for the author memory feed, topic/fabula cards, and validator
  indicators.

For later AI-assisted drafting, add:

- Unit tests for deterministic fallback selection.
- Unit tests for a mock drafting adapter.
- Contract tests for `DraftGenerationResult -> PostDraft` mapping.
- Failure tests proving provider errors return deterministic fallback.
- UI smoke coverage proving an AI-assisted draft still follows the existing HITL flow.

## Known Trade-offs

- The current `EditorialModel` is too coarse for the revised concept. It should be
  migrated carefully into smaller entities without breaking the existing demo flow.
- Author memory must stay loose enough for stream-of-consciousness input, while the
  position model must be structured enough for validation.
- Validator indicators can become noisy if every rule is shown at once. The UI needs
  progressive disclosure from colored status to evidence.
- Local-first persistence avoids backend scope, but it is not suitable for multi-device
  or team collaboration.
- Provider selection is intentionally deferred. This keeps AI integration from being
  attached to an underdeveloped author-position model.

## Open Questions

- Which author memory event types should be implemented first: raw thoughts,
  link-reactions, radar corrections, archive annotations, or release learning?
- Should topic/fabula/platform weights initially be advisory only, or should they
  produce hard validation failures in the content plan?
- How much of the context chat should be implemented before real AI provider calls?
- Which hosted deployment target should be used after local-first development?
- Should the first backend persistence slice preserve the local workspace format or
  introduce a migration layer?
