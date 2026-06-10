# ROADMAP.md

## Product Vision

Glavred is an AI-native editorial office for expert authors who want a repeatable
personal media system without losing their own position.

The central promise is not "AI writes better". The central promise is:

> The author captures raw thoughts, reactions, corrections, and released work; Glavred
> turns that material into a transparent author position model; the production pipeline
> uses that model to plan, validate, draft, release, and learn.

The durable product loop is:

`Author Memory -> Author Position Model -> Editorial System -> Content Production -> Release -> Learning`

The already implemented production loop remains valuable:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

It is now treated as a downstream production layer, not the product center.

## Source Requirements

Primary requirements document:

- `glavred.md`

Current status:

- `glavred.md` is filled and remains the historical source requirements document.
- The June 2026 product revision centers the project on `AuthorMemory` and
  `AuthorPositionModel`; see `docs/architecture/AUTHOR_POSITION_CONCEPT.md`.
- The `ui-design-systems/` handoff contains product/design context and remains a
  secondary source.
- Product-facing terminology keeps **Редакционная модель** / `EditorialModel`, but this
  aggregate should evolve into structured author-position entities.

## Status Legend

- `Backlog`: known but not ready or not prioritized
- `Ready`: ready to implement
- `In Progress`: currently being worked on
- `Blocked`: cannot proceed without clarification or dependency
- `Done`: completed and validated
- `Deferred`: intentionally postponed because a prior product layer is missing

## Current Iteration

### Iteration 2: Author Position Operating System

Goal:

- Re-center Glavred around author memory, author position, structured editorial
  entities, validators, and context chat before adding real AI drafting.

Status:

- `Ready`

## Slice Backlog

### Slice 0.1: Bootstrap Project Structure

- Status: Done
- Goal: Create initial React/Vite/TypeScript project structure, docs, tests, demo, and
  Git baseline.
- Validation: `npm test`, `npm run smoke`, and `npm audit --audit-level=moderate`
  passed.

### Slice 0.2: Brief-Backed Bootstrap Update

- Status: Done
- Goal: Accept `glavred.md` as the primary requirements source and update the baseline
  from the filled brief.
- Validation: `npm test`, `npm run smoke`, and `npm audit --audit-level=moderate`
  passed.

### Slice 0.3: Architecture Baseline for the First Product Perimeter

- Status: Done
- Goal: Define the first local-first flow from source signal to approved post brief.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.4: First Working Flow to Approved Post Brief

- Status: Done
- Goal: Implement the first working editorial cabinet from signal to approved post
  brief with local-first persistence.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.5: Draft and Editorial Checks

- Status: Done
- Goal: Extend approved briefs into deterministic drafts, editorial checks, and
  approved final text.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.6: Manual Export and Release Prep

- Status: Done
- Goal: Prepare approved final text for manual release through copy and Markdown
  export.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.7: Analytics Prep and Editorial Learning Notes

- Status: Done
- Goal: Turn analytics into local manual metrics and captured editorial learning after
  manual export.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.8: AI Provider Architecture Baseline

- Status: Done
- Goal: Document provider-agnostic AI boundaries and deterministic fallback.
- Note: This remains valid, but implementation is deferred until author position and
  validators are stronger.
- Validation: `npm test` and `npm run smoke` passed.

### Slice 0.9: Author Position Product Reframe

- Status: Done
- Goal: Reframe project documents around author memory, author position, structured
  editorial entities, validators, and context chat.
- User value: Future implementation starts from the stronger product premise: AI must
  help the author preserve and apply their own position, not generate generic content.
- Scope:
  - Add author position concept documentation.
  - Add ADR for centering the product on author memory and position.
  - Update README, architecture overview, developer guide, user guide, demo docs, and
    roadmap.
  - Defer AI drafting adapter implementation.
- Out of scope:
  - Runtime TypeScript changes.
  - UI changes.
  - AI provider integration.
  - Backend, auth, team work, and real ingestion.
- Tests:
  - Documentation-only regression: `npm test` passed; `npm run smoke` passed.
- Docs:
  - This slice is docs-only and updates the project direction.
- Demo impact:
  - Current demo behavior remains unchanged.
  - Next demo should expose author memory and author position controls above the
    current production layer.
- Acceptance criteria:
  - Product docs identify `AuthorMemory` and `AuthorPositionModel` as the center. Done.
  - Roadmap no longer points to AI drafting adapter as the next implementation. Done.
  - AI provider integration is deferred until author-position constraints exist. Done.
  - Current working production flow remains documented. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - The existing UI still reflects the old signal-first model until the next
    implementation slice.

### Slice 1.0: Author Memory Feed and Position Evidence Baseline

- Status: Done
- Goal: Add the first working author memory layer above the existing production flow.
- User value: The author can capture loose thoughts and reactions, and the product can
  start showing how those notes become evidence for author position.
- Scope:
  - Add runtime contracts for `AuthorNote`, `AuthorMemoryEvent`,
    `AuthorPositionAssertion`, and evidence links.
  - Add local-first persistence fields with backward-compatible workspace
    normalization.
  - Add a new active section for author memory as an internal feed.
  - Support at least three note types: raw thought, link reaction, and manual
    correction.
  - Add deterministic classification from notes into draft author-position assertions.
  - Show evidence links from assertions back to source notes.
  - Keep current production flow working.
- Out of scope:
  - Real AI classification.
  - Context chat.
  - Topic/fabula matrix.
  - Archive import.
  - Backend and multi-workspace sync.
- Implementation notes:
  - Keep note capture loose and low-friction.
  - Keep assertions structured and editable.
  - Treat every author correction as potential future memory input, but implement only
    the minimal correction type in this slice.
- Tests:
  - Unit tests for note creation and deterministic classification. Done.
  - Unit tests for evidence linking. Done.
  - Storage tests for old workspace normalization and author memory persistence. Done.
  - UI smoke tests for creating notes and seeing evidence-backed assertions. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Docs:
  - Update README, architecture overview, developer guide, user guide, demo docs, and
    roadmap.
- Demo impact:
  - Demo starts with the author memory feed before radar/production.
  - Permanent demo example is the TG-blog of an AI Product Manager building AI-B2B
    products.
- Acceptance criteria:
  - User can add author notes and link reactions. Done.
  - System shows first evidence-backed author-position assertions. Done.
  - State survives reload. Done.
  - Existing signal-to-learning production flow still works. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - Deterministic classification may feel simplistic; UI copy should make clear this is
    the first baseline before AI assistance.

### Slice 1.0.1: Author Memory UX Hardening

- Status: Done
- Goal: Make author memory fast, forgiving, and believable as the product's main
  entry point.
- User value: The author can capture thoughts with less friction, understand what the
  system inferred, correct it in place, and manage a growing feed without losing
  context.
- Scope:
  - Add a short instruction under `Авторская память` explaining how to use memory.
  - Make note title optional through a `+ Заголовок` reveal action with remove/hide
    behavior.
  - Add local link previews for URLs in the composer and note feed.
  - Split `Ручная корректировка` into a separate correction flow:
    - target an inferred author-position block or concrete evidence item;
    - hide unrelated fields such as link/title;
    - let the user write only the correction;
    - show a conflict-resolution prompt when the correction contradicts existing
      evidence.
  - Add `Корректировать` actions to every inferred assertion and evidence item.
  - Add search and type filters above the memory feed.
  - Add lazy feed display with `Показать еще` for large note sets.
  - Collapse long notes with `Показать полностью` / `Свернуть`.
  - Add edit and delete actions for notes with evidence-aware confirmation.
  - Add a memory summary: total notes, notes by type, this month, this year.
  - Add a voice-input affordance for notes with browser capability fallback.
- Out of scope:
  - Real AI classification.
  - Real link metadata fetching through backend.
  - Import-source settings, migration, and ingestion from Telegram/social/blog/docs.
  - Audio storage, transcription backend, and voice model integration.
  - Topic/fabula entities and validator framework.
- Implementation notes:
  - Keep the flow local-first and deterministic.
  - Link previews can initially use parsed URL/domain metadata because browser-only
    fetching is limited by CORS.
  - Voice input can use browser speech recognition when available and show a disabled
    fallback otherwise.
  - Corrections should become author-memory notes themselves, not hidden UI state.
  - Search belongs directly above the feed, after the composer and before note cards.
- Tests:
  - UI tests for optional title, adding a note without a title, and title reveal/hide. Done.
  - UI tests for link preview in composer and persisted note feed. Done.
  - UI tests for manual correction mode and correction actions from assertions/evidence. Done.
  - UI tests for search/filter, lazy loading, long-note expansion, edit, and delete. Done.
  - UI tests for memory summary and voice-input affordance fallback. Done.
  - Storage regression for preserving author-memory target metadata. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Docs:
  - Update README, user guide, developer guide, demo docs, and roadmap.
- Demo impact:
  - The AI Product Manager demo should feel like a lived-in memory feed, not a static
    fixture.
  - Demo notes should be searchable, partially collapsed when long, and correctable
    through evidence-backed assertions.
- Acceptance criteria:
  - The author can add a quick thought without a title. Done.
  - Link notes show a recognizable preview before and after saving. Done.
  - Manual correction is targeted at what the system inferred, not modeled as a
    generic note form. Done.
  - The feed remains usable with many notes through search, filters, lazy loading, and
    collapsed long text. Done.
  - Notes can be edited and deleted without breaking assertions or storage. Done.
  - Voice affordance is visible but does not promise unavailable transcription
    backends. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - Correction conflict handling can become too complex; keep it to a small HITL
    choice rather than building a full merge engine.
  - Browser speech recognition support varies; the fallback state must be explicit.

### Slice 1.0.2: Author Memory External Sources and Import Design

- Status: Backlog
- Goal: Design how external author material enters author memory without turning import
  into an opaque dump of data.
- User value: The author can see where their prior thoughts may come from, choose
  trusted sources, understand import status, and keep imported material explainable as
  evidence for author position.
- Scope:
  - Define import-source concepts for Telegram channel, social network, blog/site,
    article archive, document/report, and manual file upload.
  - Design source settings UX: source type, name, URL/file reference, import mode,
    status, last checked/imported time, and user notes.
  - Define migration/import states: `planned`, `connected`, `needsReview`,
    `imported`, `paused`, `failed`.
  - Define how imported items become `AuthorNote` or archive records.
  - Define deduplication and evidence rules so imported material does not flood the
    author-position model.
  - Define review workflow before imported material starts influencing assertions.
  - Decide what can be local-first in the browser and what requires future backend or
    manual export/import.
  - Add an implementation-ready roadmap for the first minimal import surface.
- Out of scope:
  - Real Telegram/social/blog API integrations.
  - OAuth, backend workers, crawler infrastructure, and scheduled ingestion.
  - Bulk document parsing beyond conceptual contracts.
  - Automatic author-position updates from unreviewed imported material.
- Implementation notes:
  - Treat this as a product/architecture slice unless the design becomes small enough
    for a minimal local UI shell.
  - Imported material must preserve provenance: source, captured date, original link,
    and why it was accepted as evidence.
  - User review remains mandatory before imported material strengthens assertions.
- Tests:
  - If docs-only: `npm test` and `npm run smoke` as regression.
  - If a UI shell is included: UI tests for source settings, source status, and no-op
    local persistence.
- Docs:
  - Update architecture overview, developer guide, user guide, demo docs, and roadmap.
  - Add ADR if the slice decides local-first/manual-import boundaries.
- Demo impact:
  - Demo should show possible AI Product Manager source channels without pretending
    that real ingestion is already connected.
- Acceptance criteria:
  - Import is separated from day-to-day author-memory capture.
  - Source provenance, review, deduplication, and influence on assertions are described.
  - The next implementation step for imports is small and explicit.
  - `npm test` and `npm run smoke` pass.
- Risks:
  - Real integrations can quickly dominate the product; keep the first implementation
    focused on source configuration and reviewed import, not automation.

### Slice 1.1: Topics and Fabulas as Editorial Entities

- Status: Backlog
- Goal: Replace coarse rubric/fabula settings with editable topic and fabula cards.
- Scope:
  - Add `Topic`, `Fabula`, `WeightRange`, and `TopicFabulaMatrix`.
  - Show topic cards with rules, purpose, audience value, and author stance.
  - Show fabula cards with dramaturgy, structure, and proof requirements.
  - Add default all-enabled compatibility matrix with manual toggles.
  - Route content-plan suggestions through topic/fabula compatibility.
- Tests:
  - Unit tests for weight ranges and compatibility.
  - UI smoke tests for editing topic/fabula cards.

### Slice 1.2: Validator Framework Baseline

- Status: Backlog
- Goal: Introduce generic validator results across author position, topics, fabulas,
  and production artifacts.
- Scope:
  - Add `ValidatorDefinition`, `ValidatorResult`, score/status/evidence model.
  - Add first validators for author position clarity, anti-AI style, audience value,
    and goal consistency.
  - Show compact red/yellow/green indicators with evidence drill-down.

### Slice 1.3: Context Chat Wizard Skeleton

- Status: Backlog
- Goal: Add right-side section-aware chat skeleton for guided setup.
- Scope:
  - Add chat shell synchronized with active section.
  - Use deterministic suggestions first.
  - Convert accepted suggestions into structured entities.
  - Keep AI provider calls out of scope until provider integration is re-opened.

### Slice 1.4: Content Plan as Broadcast Grid

- Status: Backlog
- Goal: Make the content plan reflect topic, fabula, platform, format, and tempo
  weights.
- Scope:
  - Add advisory weight conflict detection.
  - Let manual grid edits override abstract weights.
  - Surface conflicts when the grid no longer satisfies declared strategy.

### Slice 1.5: Archive and Uniqueness Baseline

- Status: Backlog
- Goal: Treat released and imported posts as author memory and uniqueness material.
- Scope:
  - Add archive records.
  - Link archive posts to author-position evidence.
  - Add deterministic uniqueness checks against archive titles/body snippets.

### Deferred: AI Drafting Adapter Skeleton

- Status: Deferred
- Goal: Add a runtime provider-agnostic drafting adapter skeleton without real provider
  calls.
- Reason deferred:
  - AI drafting should be constrained by author memory, author position, topic/fabula
    entities, and validators first.
- Re-open when:
  - `AuthorMemory`, first `AuthorPositionModel`, topics/fabulas, and validator
    baseline are implemented.

## Completed Slices

- Slice 0.1: Bootstrap Project Structure. Completed 2026-06-03.
- Slice 0.2: Brief-Backed Bootstrap Update. Completed 2026-06-03.
- Slice 0.3: Architecture Baseline for the First Product Perimeter. Completed
  2026-06-03.
- Slice 0.4: First Working Flow to Approved Post Brief. Completed 2026-06-03.
- Slice 0.5: Draft and Editorial Checks. Completed 2026-06-03.
- Slice 0.6: Manual Export and Release Prep. Completed 2026-06-04.
- Slice 0.7: Analytics Prep and Editorial Learning Notes. Completed 2026-06-04.
- Slice 0.8: AI Provider Architecture Baseline. Completed 2026-06-04.
- Slice 0.9: Author Position Product Reframe. Completed 2026-06-10.
- Slice 1.0: Author Memory Feed and Position Evidence Baseline. Completed
  2026-06-10.
- Slice 1.0.1: Author Memory UX Hardening. Completed 2026-06-10.

## Blocked Items

- None.

## Open Questions

- Which author memory event types beyond raw thoughts, link reactions, and corrections
  should be first-class?
- Should topic/fabula/platform weights initially be advisory only, or hard validation
  constraints?
- How much of the context chat should ship before real AI provider calls?
- What is the minimum useful archive import for uniqueness and author-position
  evidence?
- Which hosted deployment target should be used after local-first development?

## Next Recommended Task

Start `Slice 1.0.2: Author Memory External Sources and Import Design`.
