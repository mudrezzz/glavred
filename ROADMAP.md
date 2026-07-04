<!-- GENERATED FROM docs/roadmap/slices.export.jsonl. DO NOT EDIT MANUALLY. -->

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

The next product layer turns this loop from a single local workspace into a SaaS-ready
portfolio:

`UserAccount -> BlogProject -> PublicationChannels -> Project-scoped Editorial System -> Platform Variants -> Learning`

`BlogProject` means one independent blog or media system, not just a technical
workspace. Author memory, editorial rules, topics, fabulas, sources, plan, drafts,
final decisions, and learning notes are project-scoped by default.

The already implemented production loop remains valuable as a compatibility layer:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

It is now treated as a downstream production layer, not the product center. The next
production correction moves the user-facing editorial chain to
`Фабула -> Драфт -> Визуал -> Готов к выпуску`; `FinalText` and `ReleasePackage`
remain compatibility artifacts until the release-log model replaces manual export.

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

### Iteration 3: SaaS Blog Portfolio and Multi-Platform Publishing

Goal:

- Add the product layer above the current workspace: authorized users, several
  independent blog projects per user, publication channels, multi-platform variants,
  and a three-blog benchmark portfolio.
- Preserve Glavred's core frame as an AI-native editorial office: the system manages
  author memory, editorial discipline, planning, drafting, validation, release, and
  learning per blog, not one generic post generator account.

Status:

- `Ready`

## Slice Backlog

### Slice 0.1: Bootstrap Project Structure

- Status: Done
- Goal: Create initial React/Vite/TypeScript project structure, docs, tests, demo, and
  Git baseline.
- Validation: `npm test`, `npm run smoke`, and `npm audit --audit-level=moderate`
  passed.
- Completed: 2026-06-03

### Slice 0.2: Brief-Backed Bootstrap Update

- Status: Done
- Goal: Accept `glavred.md` as the primary requirements source and update the baseline
  from the filled brief.
- Validation: `npm test`, `npm run smoke`, and `npm audit --audit-level=moderate`
  passed.
- Completed: 2026-06-03

### Slice 0.3: Architecture Baseline for the First Product Perimeter

- Status: Done
- Goal: Define the first local-first flow from source signal to approved post brief.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-03

### Slice 0.4: First Working Flow to Approved Post Brief

- Status: Done
- Goal: Implement the first working editorial cabinet from signal to approved post
  brief with local-first persistence.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-03

### Slice 0.5: Draft and Editorial Checks

- Status: Done
- Goal: Extend approved briefs into deterministic drafts, editorial checks, and
  approved final text.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-03

### Slice 0.6: Manual Export and Release Prep

- Status: Done
- Goal: Prepare approved final text for manual release through copy and Markdown
  export.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-04

### Slice 0.7: Analytics Prep and Editorial Learning Notes

- Status: Done
- Goal: Turn analytics into local manual metrics and captured editorial learning after
  manual export.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-04

### Slice 0.8: AI Provider Architecture Baseline

- Status: Done
- Goal: Document provider-agnostic AI boundaries and deterministic fallback.
- Note: This remains valid, but implementation is deferred until author position and
  validators are stronger.
- Validation: `npm test` and `npm run smoke` passed.
- Completed: 2026-06-04

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
- Completed: 2026-06-10

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
- Completed: 2026-06-10

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
- Completed: 2026-06-10

### Slice 1.0.2: Author Memory File Attachments

- Status: Done
- Goal: Add optional file attachments to manually captured author-memory notes.
- User value: The author can attach a document, screenshot, text file, or image to a
  thought or link reaction without turning it into a full external-import workflow.
- Scope:
  - Add `+ Файл` next to `+ Заголовок` in the author-memory composer.
  - Attach files to `Мысль` and `Реакция на ссылку`; keep `Ручная корректировка`
    focused on short targeted corrections.
  - Add `AuthorAttachment` and `AuthorNote.attachments`.
  - Store local demo attachments as metadata plus `dataUrl` with a strict size limit.
  - Show attachment preview in note cards: icon/type, filename, size, and local preview
    for images when possible.
  - Allow removing an attachment before saving.
  - Allow editing a note to remove or replace its attachment.
  - Keep attachment content out of deterministic author-position inference for this
    slice.
- Out of scope:
  - Real document parsing.
  - OCR, transcript extraction, PDF/DOCX analysis, image understanding, or AI analysis.
  - Backend file storage and cloud upload.
  - External source import and migration from Telegram/social/blog/docs.
- Implementation notes:
  - Suggested local-first file limit: 1 MB per attachment for the browser demo.
  - Oversized files should be rejected with clear UI copy and should not be persisted.
  - Attachments must preserve provenance fields: file name, MIME type, size, created
    date, and whether the content is locally stored as a demo `dataUrl`.
  - `createAuthorMemoryEvent` may add a generic `attached-material` signal, but
    assertion text should still be inferred only from note text and tags.
- Tests:
  - UI tests for `+ Файл` reveal/hide. Done.
  - UI tests for attaching a small file and seeing it in the saved note card. Done.
  - UI tests for rejecting an oversized file. Done.
  - UI tests for image/file preview and remove-before-save. Done.
  - UI tests for removing/replacing an attachment while editing a note. Done.
  - Storage tests for save/load/reset with attachment metadata. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Docs:
  - Update README, user guide, developer guide, demo docs, and roadmap.
- Demo impact:
  - Demo should show an AI Product Manager attaching a small research note or screenshot
    to a memory item as supporting material.
- Acceptance criteria:
  - The author can add a file to a thought or link reaction through `+ Файл`. Done.
  - Attachments survive reload in the local demo within the size limit. Done.
  - Oversized files are rejected clearly. Done.
  - Attachments are visible in the feed and editable/removable. Done.
  - UI does not claim that attached files are analyzed yet. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - Browser `localStorage` is not a real file store; size limits must stay explicit.
  - Data URLs can grow quickly; this remains demo-only until a real storage boundary is
    designed.
- Completed: 2026-06-10

### Slice 1.0.3: GitHub Wiki Screenshot Documentation Baseline

- Status: Done
- Goal: Create a public GitHub Wiki with real screenshots and user-facing
  explanations of the current product.
- User value: A user can understand what Glavred does through a visual walkthrough
  instead of reading only repository docs.
- Scope:
  - Convert `mudrezzz/glavred` to a public GitHub repository so Wiki can be used.
  - Add `docs/wiki/` as the source of truth for GitHub Wiki pages.
  - Add Playwright-based screenshot generation for the real local Vite interface.
  - Capture screenshots for author memory, composer controls, link preview,
    correction/evidence flow, approved brief, editorial final text, release, and
    analytics.
  - Publish `docs/wiki/` to `mudrezzz/glavred.wiki.git` after the first GitHub Wiki
    page is initialized through the web UI.
  - Link the wiki from README, user guide, developer guide, and demo docs.
- Out of scope:
  - Product runtime changes.
  - New user-facing features.
  - Real AI calls, backend, import, or analytics ingestion.
  - Automated GitHub Actions deployment for wiki updates.
- Implementation notes:
  - Keep wiki source in the main repository for review and versioning.
  - `npm run docs:screenshots` should reset browser local storage in Playwright and
    produce reproducible screenshots from the permanent AI Product Manager demo.
  - `npm run docs:wiki:publish` should publish the wiki source to the separate GitHub
    Wiki repository after GitHub creates the backing `*.wiki.git` remote.
  - Perform a quick secret/env sweep before changing repository visibility to public.
- Tests:
  - `npm test` passed.
  - `npm run smoke` passed.
  - `npm run docs:screenshots` passed.
  - `npm run docs:wiki:publish` passed after first-page Wiki initialization.
- Docs:
  - Add wiki pages under `docs/wiki/`.
  - Update README, user guide, developer guide, demo docs, and roadmap.
- Demo impact:
  - The current AI Product Manager demo is now documented with real screenshots.
  - The demo remains local-first and deterministic.
- Acceptance criteria:
  - `mudrezzz/glavred` is public. Done.
  - GitHub Wiki is published and available. Done.
  - Wiki pages use real screenshots from the current interface. Done.
  - Screenshots can be regenerated with `npm run docs:screenshots`. Done.
  - Existing tests and smoke build pass. Done.
- Risks:
  - Screenshots can drift when UI changes; future user-visible slices should refresh
    them.
  - GitHub Wiki backing repo is created lazily by GitHub and cannot be bootstrapped by
    REST/GraphQL/git push alone.
- Completed: 2026-06-11

### Slice 1.0.4: Author Memory External Sources and Import Design

- Status: Done
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
  - Design bulk actions for large archives:
    - select page;
    - select all by active filter;
    - group by source/date/tag/duplicate risk/evidence risk;
    - `Добавить все`;
    - archive-safe bulk accept;
    - undo latest bulk action.
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
  - Large historical imports default to archive-safe behavior, not immediate active
    memory or assertion influence.
- Tests:
  - Docs-only regression: `npm test` passed; `npm run smoke` passed.
- Docs:
  - Update architecture overview, developer guide, user guide, demo docs, and roadmap.
  - Add ADR for review-before-influence and archive-safe bulk import.
  - Add `docs/architecture/EXTERNAL_SOURCE_IMPORT_CONCEPT.md`.
  - Add a GitHub Wiki page for planned external sources.
- Demo impact:
  - Demo should show possible AI Product Manager source channels without pretending
    that real ingestion is already connected.
  - Demo import scenario includes a large Telegram archive, customer interview notes,
    blog essays, a talk document, and manual research uploads.
- Acceptance criteria:
  - Import is separated from day-to-day author-memory capture. Done.
  - Source provenance, review, deduplication, and influence on assertions are described. Done.
  - Bulk import and `Добавить все` are designed for large archives. Done.
  - Unreviewed and archive-only imports do not affect assertions by default. Done.
  - The next implementation step for imports is small and explicit. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - Real integrations can quickly dominate the product; keep the first implementation
    focused on source configuration and reviewed import, not automation.
  - Bulk import can hide low-quality material if summary and filters are weak; keep
    confirmation and evidence policy visible.
- Completed: 2026-06-11

### Slice 1.0.5: External Sources Local UI Shell

- Status: Done
- Goal: Add a local-first, mock-backed UI shell for external source settings and import
  review without real integrations.
- User value: The author can see how source settings, review queue, grouping, and
  `Добавить все` will work before backend/API integrations exist.
- Scope:
  - Add `Источники`, `Очередь разбора`, and `Архив` work areas inside `Память автора`
    or an adjacent memory workspace.
  - Add demo source cards for the AI Product Manager scenario.
  - Add mock imported candidates with source, date, tags, duplicate risk, suggested
    target, provenance, and evidence policy.
  - Add filters, grouping, individual review actions, selection, `Выбрать все по
    фильтру`, `Добавить все`, and undo for the latest bulk action.
  - Persist local source settings, candidates, archive records, and bulk action state
    in the existing workspace storage.
  - Keep unreviewed and archive-only records from changing current author-position
    assertions.
- Out of scope:
  - Real Telegram/social/blog integrations.
  - OAuth, crawler, backend workers, scheduled ingestion, and AI analysis.
  - Parsing actual uploaded archive files.
- Implementation notes:
  - Use deterministic mock candidates.
  - Default large-bulk destination should be archive.
  - Bulk confirmation must show count, filters, duplicate risk, destination, and
    evidence impact.
- Tests:
  - Unit tests for candidate review and bulk status transitions.
  - Storage tests for old workspace normalization and import state persistence.
  - UI tests for source cards, filters, grouping, select-all-by-filter, `Добавить все`,
    undo, and no assertion change from unreviewed/archive-only candidates.
  - `npm test`, `npm run smoke`, and screenshot/wiki refresh if UI is user-visible.
- Docs:
  - Update README, user guide, developer guide, demo docs, wiki, and roadmap.
- Demo impact:
  - Demo gains a visible import planning shell with AI Product Manager source examples.
- Acceptance criteria:
  - User can inspect source settings and mock candidates.
  - User can bulk-archive candidates through `Добавить все`.
  - User can undo the latest bulk action.
  - Imported/archive-only candidates do not change `Как система поняла автора`.
  - State survives reload.
- Validation:
  - Unit/domain tests for candidate review, archive records, grouping, bulk archive,
    and undo. Done.
  - Storage tests for old workspace normalization and import state persistence. Done.
  - UI tests for tabs, source cards, filters, `Добавить все`, undo, and accepting a
    candidate into memory. Done.
  - `npm test`, `npm run smoke`, `npm run docs:screenshots`, and
    `npm run docs:wiki:publish` passed.
- Completed: 2026-06-11

### Slice 1.0.5.1: External Sources UX Fixes

- Status: Done
- Goal: Remove confusing behavior from the first external sources shell after manual
  review.
- User value: The author can understand the import summary, clear candidate selection,
  and work with the archive instead of seeing it as a dead-end duplicate of the queue.
- Scope:
  - Fix mojibake in the import summary and manual-check toast.
  - Make page/filter select-all actions switch into clear-selection actions after they
    are active.
  - Add an explicit `Сбросить выделение` action.
  - Clarify queue status filters for items accepted from the queue.
  - Make archive records actionable: add to memory, return to queue, mark `Не evidence`,
    open source, and delete from local archive.
- Tests:
  - UI tests for clearing candidate selection.
  - UI tests for archive actions and returning an archive record to the review queue.
- Docs:
  - Update user guide and wiki external sources page.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
  - `npm run docs:wiki:publish` passed.

### Deferred: Attachment Analysis and Evidence Extraction

- Status: Deferred
- Goal: Return to author-memory attachments and add real extraction/analysis once
  storage and AI/provider boundaries are ready.
- Reason deferred:
  - Slice 1.0.2 stores attachments as supporting material only.
  - Real analysis requires document parsing, OCR/image understanding where relevant,
    provenance, chunking, confidence, and validator/evidence integration.
- Re-open when:
  - File storage boundaries are designed beyond local demo `dataUrl`.
  - AI/provider or deterministic parser boundaries exist for attachment extraction.
  - The validator framework can show evidence from extracted attachment fragments.
- Expected future scope:
  - Extract text from supported document types.
  - Generate attachment-derived `AuthorMemoryEvent` signals.
  - Link assertions to exact attachment fragments with evidence provenance.
  - Let the author approve or reject extracted evidence before it affects position.
- Completed: 2026-06-11

### Slice 1.1: Topics and Fabulas as Editorial Entities

- Status: Done
- Goal: Replace coarse rubric/fabula settings with editable topic and fabula cards.
- User value: The author can shape what the blog is about and which post dramaturgies
  are allowed before content planning starts.
- Scope:
  - Add `Topic`, `Fabula`, `WeightRange`, and `TopicFabulaMatrix`.
  - Show topic cards with rules, purpose, audience value, and author stance.
  - Show fabula cards with dramaturgy, structure, and proof requirements.
  - Add default all-enabled compatibility matrix with manual toggles.
  - Route content-plan suggestions through topic/fabula compatibility.
- Out of scope:
  - Real validators, context chat, AI generation, and hard planning enforcement.
- Implementation notes:
  - The UI lives inside `Редакционная модель` as `Обзор`, `Темы`, `Фабулы`, and
    `Матрица`.
  - Weight ranges are advisory and normalized to `0..100`.
  - Legacy `EditorialModel.rubrics` and `EditorialModel.fabula` remain for
    compatibility.
- Tests:
  - Unit tests for weight ranges and compatibility.
  - UI smoke tests for editing topic/fabula cards.
- Docs:
  - README, architecture overview, user guide, developer guide, demo docs, and roadmap
    updated.
- Demo impact:
  - Demo now includes five AI Product Manager topics, five fabulas, and an all-enabled
    compatibility matrix.
- Acceptance criteria:
  - `Редакционная модель` exposes editable topic and fabula cards.
  - Matrix toggles compatibility and shows warnings for disconnected entities.
  - Old local workspaces load without topic/fabula fields.
  - Existing source-to-learning flow remains working.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Completed: 2026-06-11

### Slice 1.1.1: Editorial Model UX Repair and Frontend UX ADRs

- Status: Done
- Goal: Repair the `Редакционная модель` interface before building validators on top of
  it, and lock frontend UX decisions in ADRs.
- User value: The author gets one coherent cabinet UX: structured rules, explicit
  edit/save flows, compact entity lists, and a validation panel instead of freeform
  text blocks and inconsistent controls.
- Scope:
  - Replace the current accidental hero quote with an explicit project profile header:
    project name, short description, setup status, and entity counters.
  - Add `ProjectProfile` or equivalent workspace fields for project name and project
    description; seed demo as `TG-блог AI Product Manager`.
  - Rename `Обзор` to `Издательство`.
  - Rebuild `Издательство` as a single-column workflow with a right-side validation
    panel.
  - Replace large textareas for author/audience/position/style/goals/forbidden topics
    with structured rule lists.
  - Add rule-level UX: compact display, `+ Правило`, `Редактировать`, `Сохранить`,
    `Отменить`, `Удалить`.
  - Hide `Legacy-рубрики` from the UI; keep legacy fields only as storage/service
    compatibility fallback.
  - Expand `Стиль` into explicit rule groups: voice, language, rhythm, anti-AI
    patterns, and examples of allowed/forbidden phrasing.
  - Rebuild `Темы` as a compact single-column list: one row per topic, expand for
    details, edit/save/cancel for changes.
  - Rebuild `Фабулы` with the same compact list/detail/edit pattern.
  - Keep `Матрица`, but add explicit draft/save/cancel behavior for compatibility
    changes.
  - Add a right-side validation panel on every internal tab with deterministic demo
    checks and visible summary.
  - Make all internal tabs reuse the same `.tabs` visual pattern already used in
    `Память автора`.
  - Create frontend UX ADRs:
    - reuse existing product interaction patterns;
    - editorial settings are structured rules, not textareas;
    - important entity edits use read/edit/save/cancel;
    - editorial setup screens use single-column workflow plus validation panel;
    - no anonymous hero text from domain fields;
    - compact list first, details on demand;
    - validation is a first-class UX surface.
- Out of scope:
  - Real AI validation calls.
  - Full validator framework contracts from Slice 1.2.
  - Context chat.
  - Platform/format weights.
  - Rewriting downstream production flow.
- Implementation notes:
  - Treat this as UX repair, not new product depth.
  - Preserve the topic/fabula runtime contracts from Slice 1.1.
  - Existing local workspaces must normalize missing project/rule fields from demo
    data.
  - Deterministic validation panel can be simple, but it must demonstrate project,
    author, style, topic, fabula, and matrix checks on the seeded demo.
- Tests:
  - Unit/storage tests for new project profile and structured rule normalization.
  - UI tests for tab styling class reuse, rule add/edit/delete, topic expand/edit/save,
    fabula expand/edit/save, matrix draft/save/cancel, and validation panel visibility.
  - Regression test that downstream `Радар -> План -> Фабула поста` still works.
  - `npm test -- --run` and `npm run smoke`.
- Docs:
  - Add ADRs under `docs/adr/`.
  - Update README, user guide, developer guide, architecture overview, demo docs, and
    wiki docs if screenshots are refreshed.
- Demo impact:
  - Demo should show `TG-блог AI Product Manager` as the explicit project profile.
  - Demo validation panel should identify at least one green, one yellow, and one
    actionable recommendation.
- Acceptance criteria:
  - No two-column textarea grid remains in `Редакционная модель`.
  - Internal tabs visually match the existing `Память автора` tab pattern.
  - `Издательство`, `Темы`, `Фабулы`, and `Матрица` all have a right-side validation
    panel.
  - Author/audience/style/goals are represented as editable rules.
  - Topics and fabulas use compact list/detail/edit/save UX.
  - Matrix changes require explicit save/cancel.
  - Frontend UX ADRs are accepted and linked from developer docs.
  - Existing local-first production flow remains working.
- Validation:
  - Domain/application tests for project profile, structured rules, rule CRUD helpers,
    and deterministic validation summary. Done.
  - Storage tests for old workspace normalization and project/rule persistence. Done.
  - UI tests for project header, rule add/save, compact topic/fabula edit flows,
    matrix draft/save behavior, and validation panel visibility. Done.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Completed: 2026-06-11

### Slice 1.1.2: Editorial Model Layout and Manual Validation UX Fixes

- Status: Done
- Goal: Fix the `Редакционная модель` layout problems found after Slice 1.1.1 and
  make validation explicitly author-triggered.
- User value: The author can edit topics, fabulas, and matrix links without broken
  layout or premature validation feedback.
- Scope:
  - Add explicit `Проверить` action to the right validation panel.
  - Store or derive validation run state so saved changes mark the latest validation
    result as stale instead of recalculating live.
  - Show `Еще не проверено`, `Проверено`, and `Требует повторной проверки` states.
  - Fix topic compact rows so long names, weights, rule counts, fabula counts, and
    validation badges wrap within the row.
  - Fix topic preview with normal wrapping and one shared vertical scroll area for
    long detail content.
  - Fix topic edit forms so inputs and textareas stay inside the expanded entity.
  - Apply the same list, preview, and edit containment fixes to fabulas.
  - Rebuild the matrix table formatting with a horizontal scroll container, readable
    wrapped headers, checkbox-only cells, and sticky topic column.
- Out of scope:
  - Real AI validation.
  - Full `ValidatorResult` framework.
  - Context chat.
  - New topic/fabula semantics.
- Implementation notes:
  - Validation should run from saved workspace state, not from incomplete text being
    typed in an edit form.
  - Prefer one shared scroll area per expanded preview, not nested scrollbars per
    field.
  - Matrix cells should use accessible labels for topic/fabula pairs instead of
    visible repeated `да/нет` text.
- Tests:
  - UI test that validation output appears only after clicking `Проверить`.
  - UI test that saved setup changes mark validation as stale.
  - UI tests for topic/fabula row containment and expanded preview structure.
  - UI test that matrix has a horizontal scroll container and sticky topic column
    structure.
  - Regression tests for topic/fabula edit/save/cancel and matrix save/cancel.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Docs:
  - Update user guide and developer guide for manual validation.
  - Update ADR references if implementation changes the interaction contract.
- Demo impact:
  - Demo `Редакционная модель` should be usable at realistic viewport widths with
    long AI Product Manager topics and fabulas.
- Acceptance criteria:
  - Validation panel does not create fresh conclusions while the author types. Done.
  - The author can run validation manually. Done.
  - After saved changes, the panel clearly asks to rerun validation. Done.
  - Topic and fabula list rows, previews, and edit forms do not overflow their cards. Done.
  - Matrix remains readable with horizontal scroll and sticky topic names. Done.
  - Existing production flow remains working. Done.
- Completed: 2026-06-11

### Slice 1.1.3: Add and Delete Topics and Fabulas

- Status: Done
- Goal: Add missing create/delete actions for topic and fabula entities inside
  `Редакционная модель`.
- User value: The author can evolve the editorial system without editing seeded demo
  entities only.
- Scope:
  - Add `+ Тема` and `+ Фабула` actions above compact entity lists.
  - Keep new entities as local drafts until `Сохранить`.
  - Disable save until a title is provided.
  - Add saved entities to the compatibility matrix with default enabled links.
  - Add `Удалить` actions in expanded topic/fabula details with confirmation.
  - Delete related matrix links while leaving already-created production artifacts
    unchanged.
- Out of scope:
  - Validator framework.
  - Context chat suggestions for new entities.
  - Rebuilding existing production artifacts after entity deletion.
- Implementation notes:
  - Use `status: paused` for temporary exclusion and physical delete for unwanted
    entities.
  - Show a stronger confirmation when the entity is referenced by current production
    artifacts.
- Tests:
  - Domain tests for topic/fabula draft creation, add, delete, and matrix link
    normalization. Done.
  - UI tests for adding and deleting topics/fabulas and seeing matrix updates. Done.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Docs:
  - README, user guide, developer guide, architecture overview, demo docs, and roadmap
    updated.
- Demo impact:
  - Demo author can add a custom topic/fabula and confirm that matrix links appear by
    default.
- Acceptance criteria:
  - `+ Тема` creates a draft topic and saves it into the list. Done.
  - `+ Фабула` creates a draft fabula and saves it into the list. Done.
  - New entities appear in the matrix with default enabled links. Done.
  - Delete removes the entity and its matrix links after confirmation. Done.
  - Manual validation snapshot becomes stale after committed add/delete. Done.
- Completed: 2026-06-11

### Slice 1.2: Validator Framework Baseline

- Status: Done
- Goal: Introduce generic validator results across author position, topics, fabulas,
  and editorial setup entities.
- Scope:
  - Add `ValidatorDefinition`, `ValidatorResult`, score/status/evidence model.
  - Add first validators for author position clarity, anti-AI style, audience value,
    and goal consistency.
  - Show compact red/yellow/green indicators with evidence drill-down.
- Implemented:
  - Added `ValidatorStatus`, `ValidatorTargetType`, `ValidatorEvidence`,
    `ValidatorSuggestion`, `ValidatorDefinition`, `ValidatorResult`, and
    `ValidatorRun`.
  - Added deterministic `runEditorialSetupValidators(workspace)` with validators:
    `author-position-clarity`, `anti-ai-style-coverage`, `audience-value-fit`,
    `goal-consistency`, and `topic-fabula-coverage`.
  - Kept validation manual through `Проверить`; live validation remains intentionally
    disabled.
  - Updated the right validation panel to show aggregate score, validator cards,
    evidence, and suggested fixes.
  - Normalized old local workspaces without `ValidatorRun.results`.
- Out of scope:
  - Real AI validation.
  - Draft/release/archive validators.
  - Context chat.
- Validation:
  - Domain tests for validator results, score/status, evidence, suggestions, matrix
    red state, and anti-AI degradation. Done.
  - Storage tests for `ValidatorRun.results` and old snapshot normalization. Done.
  - UI tests for manual validator cards, score, evidence, and stale state. Done.
  - `npm test -- --run` passed.
- Completed: 2026-06-11

### Slice 1.2.1: Author Memory Sources UX Alignment

- Status: Done
- Goal: Align `Память автора -> Источники` with the product-wide operational entity
  catalog UX.
- User value: The author scans sources the same way as topics and fabulas: one
  source per row, key metadata visible, details on demand, and row-level actions.
- Scope:
  - Replace the two-column source card grid with a single-column source list.
  - Show type, title, status, import mode, candidate count, and last checked date in
    each row.
  - Expand a row to show notes and import metadata.
  - Keep existing local/mock actions: open queue, pause/resume, and manual check.
  - Add an ADR requiring single-column list-first layouts for operational entity
    catalogs.
- Out of scope:
  - Real import integrations.
  - Queue/archive behavior changes.
  - New source types or import transitions.
- Validation:
  - UI test for single-column source list, no `.source-grid`, and source detail
    expansion. Done.
  - `npm test -- --run src/App.test.tsx` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-12

### Slice 1.2.2: Source List Visual Repair and UI Guardrails

- Status: Done
- Goal: Repair the broken `Память автора -> Источники` source list layout and add
  browser-level guardrails so similar regressions are caught before manual review.
- User value: Source rows stay readable and operational; autosave feedback no longer
  blocks the workspace as a permanent bottom overlay.
- Scope:
  - Replace the failed multi-column source row with a stable header/meta/actions/detail
    structure.
  - Prevent source titles from collapsing into narrow vertical columns.
  - Make autosave/status toast event-driven and temporary instead of visible on initial
    render.
  - Add `npm run test:visual` as Playwright visual smoke coverage for source rows and
    toast behavior.
  - Add ADR for visual guardrails on operational UI surfaces.
- Out of scope:
  - Full pixel-perfect screenshot baselines for every screen.
  - Redesigning queue/archive behavior.
  - Real external source integrations.
- Validation:
  - UI tests for source row structure and initial toast absence. Done.
  - Playwright visual smoke for row overflow/title collapse/actions/toast lifecycle.
    Done.
- Completed: 2026-06-12

### Slice 1.3: Context Chat Wizard Skeleton

- Status: Done
- Goal: Add a section-aware context chat skeleton as a collapsible overlay, not a
  third right-side column.
- Scope:
  - Added a global `ContextChat` collapsed button and fixed overlay drawer.
  - Synchronized suggestions with active sidebar section and internal tabs for
    `Память автора` / `Редакционная модель`.
  - Added deterministic suggestions that use latest `ValidatorRun.results` and setup
    state.
  - Accepted `add rule/topic/fabula` suggestions open existing draft forms with prefill
    and still require normal `Сохранить`.
  - Added `runValidation` suggestion that invokes the existing manual validation path.
  - Added visual smoke coverage for desktop, laptop, and mobile overlay behavior.
  - Added ADR for collapsible overlay instead of a third column.
- Out of scope:
  - Real AI provider calls.
  - Persistent chat history.
  - Freeform chat input and autonomous edits.
- Validation:
  - Application tests for deterministic suggestions. Done.
  - UI tests for collapsed/expanded state, scope changes, and draft flow opening. Done.
  - Playwright visual smoke for context chat overlay. Done.
  - Full regression commands listed in Slice completion notes.
- Completed: 2026-06-12

### Slice 1.3.1: Context Chat UX Repair and Chat Mode

- Status: Done
- Goal: Repair the first context chat UX so it works as a topbar-triggered,
  tabbed assistant with real chat input and predictable overlay geometry.
- User value:
  - The assistant no longer floats over random screen elements.
  - The drawer opens from the right edge of the app instead of appearing in an
    unexpected centered position on wide screens.
  - The author can ask freeform local questions such as "generate topics" and
    get a safe draft action.
- Scope:
  - Moved the assistant trigger into the topbar and demoted reset demo to an
    icon action.
  - Removed the duplicate `Свернуть` action; `x` is the single close control.
  - Split assistant content into `Чат` and `Подсказки` tabs.
  - Added deterministic chat replies with safe inline actions for topic, fabula,
    rule, and validation requests.
  - Made suggestions dismissible and removed the ambiguous `Принять к сведению`
    action from read-only suggestions.
  - Updated drawer CSS to use right-edge anchoring and visual smoke checks for
    right-edge placement, suggestion button height, and horizontal overflow.
- Out of scope:
  - Real AI provider calls.
  - Persistent chat history.
  - Autonomous workspace edits.
  - A full prompt/agent runtime.
- Validation:
  - Unit tests for deterministic chat replies. Done.
  - UI tests for topbar trigger, chat input, tabbed suggestions, dismiss, and
    safe draft actions. Done.
  - Visual smoke updated to verify drawer right-edge anchoring and normal suggestion
    card/button heights.
- Completed: 2026-06-13

### Slice 1.4: Content Plan as Broadcast Grid

- Status: Done
- Goal: Make the content plan reflect topic, fabula, platform, format, and tempo
  weights.
- Scope:
  - Add a local-first broadcast grid in `План` with multiple slots.
  - Keep `contentPlanItem` as selected-slot compatibility for post brief, release, and
    analytics while adding `contentPlanItems` as the primary grid.
  - Add advisory weight, matrix, paused-entity, and incomplete-slot conflict detection.
  - Let manual grid edits override abstract weights and surface conflicts in the right
    `Сетка вещания` panel.
  - Remove the standalone sidebar item `Фабулы`; editorial fabulas live inside
    `Редакционная модель`, while `Фабула поста` remains an internal production step.
- Validation:
  - Domain tests for deterministic grid generation and conflict detection. Done.
  - Storage tests for old single-item workspace normalization and grid persistence. Done.
  - UI tests for removed sidebar item, broadcast grid edit/save/cancel, slot approval,
    internal post-brief navigation, and downstream regression. Done.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Completed: 2026-06-13

### Slice 1.4.1: Broadcast Planning Concept Correction

- Status: Done
- Goal: Correct the product model around `План` before adding deeper planning UI.
- User value: The author understands that the plan is a broadcast demand layer, while
  signals and post candidates provide the material that fills it.
- Scope:
  - Document the revised flow:
    `Редакционная модель -> Сигналы -> Кандидаты постов -> Сетка вещания -> Фабула поста`.
  - Mark the current Slice 1.4 broadcast grid as a useful local-first prototype, not the
    final planning architecture.
  - Rename the future product focus from `Радар` to `Сигналы`.
  - Define the split between radar settings, found signals, post candidates, and
    calendar slots.
  - Add ADR for separating signals, candidates, and broadcast grid responsibilities.
  - Update README, architecture overview, developer guide, user guide, demo docs, and
    roadmap.
- Out of scope:
  - Runtime UI changes.
  - Calendar implementation.
  - Signal/radar implementation.
  - AI/provider calls.
- Implementation notes:
  - This is a docs/architecture slice that makes Slice 1.5 decision-complete.
  - The existing `contentPlanItems` compatibility layer remains valid.
- Tests:
  - Documentation-only regression: `npm test -- --run` passed.
  - `npm run smoke` passed.
- Docs:
  - Add or update architecture docs and ADRs.
- Demo impact:
  - Demo documentation should explain that the current broadcast grid is temporary
    until signal and candidate layers are implemented.
- Acceptance criteria:
  - Roadmap no longer points directly from Slice 1.4 to archive uniqueness. Done.
  - Architecture describes why `Сигналы` must come before deeper `План`. Done.
  - Next recommended task is `Slice 1.5: Signals and Radar Workspace`. Done.
- Risks:
  - If this correction stays docs-only too long, the UI will continue showing a
    simplified plan that does not yet explain signal deficit or candidate readiness.
- Completed: 2026-06-13

### Slice 1.5: Signals and Radar Workspace

- Status: Done
- Goal: Replace the single `Радар` flow with a first working `Сигналы` workspace.
- User value: The author can see what material the system found, where it came from,
  why it was selected, and approve/correct/reject it before it becomes a post concept.
- Scope:
  - Add top-level sidebar item `Сигналы` and retire `Радар` as a standalone production
    screen.
  - Add internal tabs:
    - `Радары`;
    - `Найденные сигналы`;
    - `Кандидаты постов` placeholder or read-only preview if candidate implementation
      is deferred to Slice 1.6.
  - Add `RadarDefinition` contracts with source, scope, acceptance policy, trigger
    mode, status, last run, and notes.
  - Add `SourceSignal` review fields: radar id, review status, suggested topic,
    suggested fabula, suggested value, duplicate risk, and author correction metadata.
  - Seed demo radars for author memory, archive, external sources, and manual research.
  - Seed demo signals for the AI Product Manager blog.
  - Support HITL actions: approve signal, reject signal, archive signal, correct topic
    or fabula assignment.
  - Persist radar settings and reviewed signals in localStorage.
  - Author corrections create or update author-memory evidence.
- Out of scope:
  - Real Telegram/API/OAuth/crawler integrations.
  - Real AI analysis.
  - Full post candidate generation.
  - Calendar UI.
- Implementation notes:
  - Radars can be deterministic demo sources.
  - Unapproved signals must not create approved post concepts.
  - Signal approval should be explicit unless the radar policy is automatic.
- Tests:
  - Domain tests for radar settings and signal review transitions.
  - Storage tests for old workspace normalization and signal persistence.
  - UI tests for `Сигналы` tabs, radar cards/list, signal filters, approve/reject, and
    correction flow.
  - Regression for existing production flow.
- Docs:
  - Update README, architecture overview, developer guide, user guide, demo docs, wiki
    production flow, and roadmap.
- Demo impact:
  - The AI Product Manager demo should show signals from memory/archive/external mock
    sources before any plan slot is approved.
- Acceptance criteria:
  - User can inspect demo radars. Done.
  - User can review found signals. Done.
  - User can approve, reject, archive, and correct a signal. Done.
  - Signal corrections become visible as author-memory input or evidence. Done.
  - Existing plan/brief/edit/release flow remains working. Done.
- Risks:
  - The boundary between import candidates and source signals must stay clear:
    imported candidates are source material; reviewed signals are editorial triggers.
  - `Кандидаты постов` is intentionally read-only until Slice 1.6.
- Completed: 2026-06-13

### Slice 1.5.1: Radar Rules/Sources and Raw Signal UX Repair

- Status: Done
- Goal: Correct the `Сигналы` model before post candidate assemblies.
- User value: The author can configure radars as search procedures and review raw
  signals without confusing them with post concepts.
- Scope:
  - Model radars as configurable search objects with atomic rules and optional sources.
  - Add local-first add/edit/delete/start/stop flows for radars.
  - Show radar signal counts with the existing red count badge pattern and last run
    date in compact rows.
  - Treat `Найденные сигналы` as raw material: radar, date, finding, evidence,
    search note, duplicate risk, and review status.
  - Remove topic/fabula/value matching from signal review UI; keep compatibility fields
    only for downstream services until Slice 1.6.
  - Fix the right panel summary so counts are separate stat blocks, not concatenated
    text.
  - Add ADRs for radars as configurable search objects and signals as raw material.
- Out of scope:
  - Real radar execution, API, crawler, MCP execution, or AI provider calls.
  - Post candidate assemblies.
  - Calendar planning.
- Validation:
  - Domain tests for radar CRUD and raw signal evidence. Done.
  - Storage normalization for old radars/signals. Done.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
- Completed: 2026-06-13

### Slice 1.5.2: Signals UI Design-System Repair and Visual Guardrails

- Status: Done
- Goal: Repair the `Сигналы` UI so `Радары` and `Найденные сигналы` follow the cabinet design system.
- User value: The author can understand which controls, metadata and evidence belong to each radar or signal.
- Scope:
  - Render radars and found signals as framed rows/cards with visible boundaries, stable metadata and in-card actions.
  - Keep expanded details inside the same entity container.
  - Make signal filters a framed toolbar.
  - Prevent status and duplicate-risk chips from wrapping by letters.
  - Add visual smoke coverage for `Сигналы` across desktop, laptop and mobile.
  - Add ADR for framed cabinet lists and visual coverage.
- Out of scope:
  - Changing radar/signal domain behavior.
  - Post candidate assemblies.
  - Real radar execution, API, crawler, MCP execution or AI provider calls.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-13

### Slice 1.5.3: Signals Layout Polish and Pixel Guardrails

- Status: Done
- Goal: Fix the remaining `Сигналы` layout issues after 1.5.2 and make the visual
  guardrails measure the actual failure modes.
- User value: The author sees a clear `Сигналы` workspace with a section header,
  stable radar/signal rows, readable expanded cards, non-overlapping columns, and
  actions that visibly belong to their entity.
- Scope:
  - Add an explicit `Сигналы` section header above the internal tabs.
  - Stabilize radar rows with identity, body and metadata groups instead of fragile
    pseudo-table columns.
  - Stabilize found-signal rows so title, radar, duplicate risk and status do not
    collide.
  - Add footer spacing and separators for radar/signal actions.
  - Improve radar edit form spacing for rules and sources.
  - Keep the right panel action visually separated from summary counters.
  - Extend visual smoke checks for section header, main/side column gap, action
    spacing, side-panel spacing, edit-form overflow and signal title width.
- Out of scope:
  - New radar execution behavior.
  - Post candidate assemblies.
  - Real API/crawler/MCP/AI provider calls.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.4: Design-System Guardrails and Signals UI Alignment

- Status: Done
- Goal: Align the `Сигналы` header and local layout with the accepted cabinet
  patterns, then make those patterns enforceable through automated design tests.
- User value: The author sees `Сигналы` as part of the same product, not as a locally
  assembled screen; future UI regressions around spacing, tabs, side panels and forms
  are caught before manual review.
- Scope:
  - Reuse the `Редакционная модель` project/profile header pattern for `Сигналы`.
  - Align Signals header metrics to the right edge of the header card, matching the
    operational right-panel rhythm.
  - Render tab counters through the shared red badge/count pattern instead of plain
    text glued to the tab label.
  - Keep the `Радары` toolbar hierarchy readable: title first, descriptor second.
  - Enforce base gaps for `.row-actions` so save/cancel and entity actions cannot
    touch each other.
  - Align radar editor grouped rule/source sections with the base form working width.
  - Add `npm run test:design` for structural design-system checks, including
    main/right column non-overlap and Signals gutter validation.
  - Add ADR for the cabinet layout contract and design-smoke requirements.
- Out of scope:
  - Pixel-perfect screenshot diffing.
  - New signal/radar domain behavior.
  - Post candidate assemblies.
  - Real API/crawler/MCP/AI provider calls.
- Validation:
  - `npm run test:design` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.5: Frontend Design-System Consolidation

- Status: Done
- Goal: Consolidate shared front-end primitives for section headers, entity toolbars,
  ordinary action buttons and radar metadata rows.
- User value: The author sees `Signals`, `Editorial Model` and later cabinet screens as
  one coherent product surface; ordinary work actions no longer look like validation or
  approval gates.
- Scope:
  - Reuse the compact entity toolbar pattern in `Signals -> Radars`: count and
    description on the left, ordinary `+ Radar` action on the right.
  - Keep `+ Radar` as a white secondary work button; reserve red primary buttons for
    validation, approval, save/commit and HITL lifecycle actions.
  - Stabilize radar row metadata slots: status, signal count and last run always occupy
    predictable positions.
  - Render a fallback for missing radar `lastRunAt` instead of leaving a layout hole.
  - Add ADR for canonical cabinet primitives and button taxonomy.
  - Extend `npm run test:design` and UI tests for toolbar action taxonomy and radar
    metadata slot stability.
- Out of scope:
  - Full component extraction into a design-system package.
  - Pixel-perfect screenshot diffs.
  - New product behavior for radars, signals or post candidates.
- Validation:
  - `npm run test:design` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.6: Layout Stability and Form Rhythm Guardrails

- Status: Done
- Goal: Make Signals layout stability and radar editor form rhythm formally
  testable, not only manually reviewable.
- User value: Expanding/collapsing radar cards no longer shifts the workspace, header
  metrics stay aligned to the right edge, and radar editor fields keep visible spacing.
- Scope:
  - Reserve the app scroll gutter so disclosure state does not move centered cabinet
    content horizontally.
  - Keep Signals section metrics pinned to the right edge of the shared section
    header pattern on desktop and wide desktop viewports.
  - Add explicit grid rhythm for radar editor base fields and grouped selects.
  - Extend design-smoke checks with collapse/expand layout stability, wide desktop
    header alignment, and measured field-label spacing.
- Out of scope:
  - New radar/signal product behavior.
  - Pixel-perfect screenshot diffing.
  - Full design-system component extraction.
- Validation:
  - `npm run test:design` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.7: Inline Radar Editing and Multiline Rule Sources

- Status: Done
- Goal: Fix radar editing so existing radars are edited in-place and radar rules/sources
  have enough writing space.
- User value: The author can edit the radar they clicked without scrolling to a duplicate
  form at the top of the list, and can write real search instructions or URL/API/MCP
  source descriptions in multiline fields.
- Scope:
  - Keep new radar creation as a temporary draft form above the list.
  - Render existing radar edit mode inside the selected radar card.
  - Replace one-line radar rule and source-value controls with textareas.
  - Extend UI/design smoke checks so inline radar editing and multiline radar rule/source
    fields are enforced.
- Out of scope:
  - New radar execution behavior.
  - Real external integrations.
  - Post candidate assemblies.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.8: Radar Editorial Filters and Source Discovery Mode

- Status: Done
- Goal: Extend radar setup from trigger rules and sources to a full signal-search
  configuration: trigger rules, search sources, editorial filters, and run settings.
- User value: The author can explain not only what a radar should find and where it
  should look, but also which editorial dimensions should pass, warn, reject, or seek
  useful tension before material becomes a post candidate.
- Scope:
  - Add source discovery modes: specified sources only, specified plus additional
    discovery, and autonomous discovery.
  - Add editorial radar filters for author, audience, positioning, goals, forbidden
    topics, and topics.
  - Keep style out of radar filtering.
  - Remove the radar notes field from the UI while keeping it as storage compatibility.
  - Show deterministic filter evaluations on found signals.
  - Add signal filtering by filter status.
- Out of scope:
  - Real web/API/MCP execution.
  - AI provider calls.
  - Automatic deletion of filtered signals.
  - Post candidate assemblies.
- Validation:
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
  - `npm run docs:screenshots` passed.
- Completed: 2026-06-14

### Slice 1.5.9: React Architecture Baseline and App.tsx Growth Guardrails

- Status: Done
- Goal: Stop further `App.tsx` growth before adding new product surfaces.
- User value: The product can keep evolving without turning every UI change into a
  high-risk edit inside one giant React file.
- Scope:
  - Add ADR `react-ui-uses-feature-modules-not-app-god-file`.
  - Add `React UI Architecture` to the system architecture overview.
  - Add `npm run test:architecture`.
  - Guard the current temporary baseline:
    - `src/App.tsx <= 6900` lines;
    - `src/App.test.tsx <= 850` lines;
    - no new large App-level UI declarations beyond the accepted baseline.
  - Define the feature-module target structure under `src/app`, `src/features/*`,
    `src/shared/ui`, and `src/shared/format`.
- Out of scope:
  - Moving components out of `App.tsx`.
  - Runtime behavior changes.
  - UI visual changes.
  - Workspace, storage, demo data, domain, or application service changes.
- Implementation notes:
  - This is a baseline slice. The limits are intentionally temporary and must only go
    down in later extraction slices.
  - New large screens must be implemented in feature modules, not in `App.tsx`.
- Validation:
  - `npm run test:architecture` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
- Docs:
  - ROADMAP, ADR, SAO, and developer guide are updated.
- Demo impact:
  - No user-visible product behavior changes.
- Acceptance criteria:
  - Architecture smoke blocks unnoticed `App.tsx` growth. Done.
  - ADR and SAO define React feature-module boundaries. Done.
  - ROADMAP points to extraction slices before new planning functionality. Done.
- Risks:
  - The current monolith remains until extraction slices are completed; future work must
    not use this baseline as permission to keep adding code to `App.tsx`.
- Completed: 2026-06-15

### Slice 1.5.10: Extract App Shell and Workspace Controller

- Status: Done
- Goal: Move shell, topbar/sidebar, navigation metadata, and workspace controller logic
  out of `App.tsx` without changing behavior.
- User value: The product gains a smaller app composition root and a safer place to
  wire future features.
- Scope:
  - Create `src/app/`.
  - Extract app shell, sidebar/topbar, section routing metadata, and workspace state
    controller.
  - Keep current local-first persistence and demo behavior unchanged.
  - Lower `App.tsx` and `App.test.tsx` architecture limits after extraction.
- Delivered:
  - Added `src/app/AppShell.tsx`, `Sidebar.tsx`, `Topbar.tsx`, `navigation.ts`,
    `contextChatScope.ts`, `ContextChatOverlay.tsx`, and `useWorkspaceController.ts`.
  - Added `src/shared/ui/Icon.tsx` and `WeightRangeEditor.tsx`.
  - Removed `LocalWorkspaceStore`, autosave/reset, shell state, context-chat state, and
    production orchestration ownership from `src/App.tsx`.
  - Lowered architecture smoke to `App.tsx <= 6300` and large App declarations `<= 30`.
- Out of scope:
  - Extracting individual feature screens.
  - Product behavior changes.
- Validation:
  - `npm run test:architecture`. Passed.
  - `npm test -- --run`. Passed.
  - `npm run smoke`. Passed.
  - `npm run test:design`. Passed.
  - `npm run test:visual`. Passed.
- Completed: 2026-06-15

### Slice 1.5.11: Extract Signals Feature

- Status: Done
- Goal: Move `Сигналы` UI into `src/features/signals` while preserving current radar
  and signal review behavior.
- Notes:
  - This should be the first feature extraction because it is the most recently active
    and visually sensitive workspace.
  - `SignalsView`, `RadarEditor`, `SignalsSidePanel`, and signals label helpers now live
    under `src/features/signals`.
  - `App.tsx` imports the signals feature entry and no longer contains legacy
    `SignalsView` / `RadarView` code.
  - Architecture guardrails were lowered to `App.tsx <= 5400` and large App UI
    declarations `<= 26`.
- Completed: 2026-06-15

### Slice 1.5.12: Extract Editorial Model Feature

- Status: Done
- Goal: Move project profile, editorial rules, topics, fabulas, matrix, and validation
  panel into `src/features/editorial-model`.
- Notes:
  - `EditorialModelView`, project profile UI, publisher rules, topics, fabulas,
    matrix, and setup validation panel now live under `src/features/editorial-model`.
  - `ContextChatIntent` is now an application-level boundary type, while
    `EditorialModelTab` belongs to the editorial-model feature boundary.
  - `App.tsx` imports the editorial-model feature entry and no longer contains
    editorial setup editors, matrix UI, validation panel, or editorial-only helpers.
  - Architecture guardrails were lowered to `App.tsx <= 3600` and large App UI
    declarations `<= 17`.
- Completed: 2026-06-15

### Slice 1.5.13: Extract Author Memory Feature

- Status: Done
- Goal: Move author memory feed, assertions, imports, archive, attachments, and memory
  summary into `src/features/author-memory`.
- Notes:
  - `AuthorMemoryView`, composer, note cards, assertion/evidence correction UI,
    memory tabs, external sources, import queue, archive, bulk dialog, and
    author-memory/import helpers now live under `src/features/author-memory`.
  - `MemoryInternalTab` belongs to the author-memory feature boundary.
  - `App.tsx` imports the author-memory feature entry and no longer contains
    author-memory cards, import queue, archive UI, or author-memory-only helpers.
  - Architecture guardrails were lowered to `App.tsx <= 1700` and large App UI
    declarations `<= 10`.
- Completed: 2026-06-15

### Slice 1.5.14: Extract Production Flow Features

- Status: Done
- Goal: Move plan, briefing, editing, release, analytics, and context chat entry points
  into feature modules without changing the current demo flow.
- Notes:
  - `PlanView`, `BriefView`, `EditView`, `ReleaseView`, and `AnalyticsView` now live
    under `src/features/plan`, `src/features/briefing`, `src/features/editing`,
    `src/features/release`, and `src/features/analytics`.
  - Shared production primitives now live in `src/shared/ui/WorkflowPrimitives.tsx`.
  - Shared production labels, dates, and formatting helpers now live in
    `src/shared/format/production.ts`.
  - `App.tsx` is now a small composition root for shell, controller, and feature
    entrypoints.
  - Architecture guardrails were lowered to `App.tsx <= 350` and large App UI
    declarations `<= 1`.
- Validation:
  - `npm run test:architecture` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
- Completed: 2026-06-15

### Slice 1.5.15: Codebase Size Audit and Modularization Guardrails

- Status: Done
- Goal: Stop large-file growth across domain, application, fixtures, and feature
  modules before new product UI is added.
- User value: The product becomes easier to maintain and safer to extend; new
  contributors can understand module boundaries without reading thousand-line files.
- Scope:
  - Add a codebase size audit for `src/**/*.ts` and `src/**/*.tsx`.
  - Extend `npm run test:architecture` or add a dedicated size guard so large files are
    tracked explicitly.
  - Set temporary baselines for current large files:
    - `src/features/author-memory/AuthorMemoryView.tsx`;
    - `src/domain/editorialWorkspace.ts`;
    - `src/features/editorial-model/EditorialModelView.tsx`;
    - `src/fixtures/demoWorkspace.ts`;
    - `src/features/signals/SignalsView.tsx`;
    - `src/application/editorialServices.ts`.
  - Add rules that these baselines may only decrease in future refactoring slices.
  - Add architecture checks for feature/domain/application boundary ownership.
  - Add ADR for module size, comments, and decomposition guardrails.
  - Update SAO and developer guide with the refactoring chain.
- Out of scope:
  - Moving domain or feature code.
  - Product behavior changes.
  - UI/CSS changes.
- Implementation notes:
  - The first guard should be strict enough to prevent growth, but not block the current
    main branch before decomposition starts.
  - Comments policy should require useful boundary/invariant comments, not noisy
    line-by-line narration.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update ROADMAP, SAO, developer guide, and ADRs.
- Demo impact:
  - None. This is architecture-only.
- Acceptance criteria:
  - Large-file baselines are visible and enforced.
  - The next refactoring slices are explicitly listed before `Slice 1.6`.
  - Architecture docs explain why product slices are paused.
- Risks:
  - Overly strict limits could block necessary refactors; use temporary baselines and
    lower them slice by slice.
- Completed: 2026-06-15

### Slice 1.5.16: Split Domain Workspace Types by Bounded Context

- Status: Done
- Goal: Break `src/domain/editorialWorkspace.ts` type definitions into domain
  bounded-context modules.
- User value: Domain concepts become discoverable by area instead of buried in one
  workspace file.
- Scope:
  - Create domain context modules for:
    - `author-memory`;
    - `editorial-model`;
    - `signals`;
    - `planning`;
    - `briefing`;
    - `editing`;
    - `release`;
    - `analytics`;
    - `workspace`.
  - Move type/interface declarations into those modules.
  - Keep `src/domain/editorialWorkspace.ts` as a temporary compatibility barrel.
  - Add module-level comments that explain each domain context and its invariants.
- Out of scope:
  - Moving transitions/services.
  - Changing storage shape.
  - Changing runtime behavior.
- Implementation notes:
  - Imports should continue to work through the compatibility barrel during this slice.
  - No type should be renamed unless it is required for a clean boundary.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update SAO and developer guide with the new domain structure.
- Demo impact:
  - None.
- Acceptance criteria:
  - `editorialWorkspace.ts` no longer owns all type declarations directly.
  - Existing product flow and tests behave unchanged.
- Risks:
  - Type moves can cause broad import churn; keep a compatibility barrel until later.
- Completed: 2026-06-15

### Slice 1.5.17: Split Domain Transitions and Invariants

- Status: Done
- Goal: Move pure domain transitions and helpers out of the workspace barrel into
  bounded-context modules.
- User value: Business rules become easier to locate, test, and change safely.
- Scope:
  - Move author-memory, editorial-model, signals, planning, release, and analytics
    transitions to their context modules.
  - Add short comments for non-obvious invariants and compatibility behavior.
  - Keep `editorialWorkspace.ts` as a thin public re-export until imports are cleaned.
  - Extend architecture checks so new domain logic cannot be added back to the barrel.
- Out of scope:
  - Application services.
  - UI refactors.
  - Product behavior changes.
- Implementation notes:
  - Preserve function names and deterministic behavior.
  - Prefer small files by role over one file per tiny function.
- Tests:
  - Domain tests for moved transitions.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update developer guide with transition ownership.
- Demo impact:
  - None.
- Acceptance criteria:
  - `editorialWorkspace.ts` is a thin compatibility module.
  - Moved transitions retain existing behavior.
- Risks:
  - Hidden import cycles may appear; fix by adjusting context ownership, not by adding
    cross-layer shortcuts.
- Completed: 2026-06-15

### Slice 1.5.18: Split Application Services

- Status: Done
- Goal: Break `src/application/editorialServices.ts` into cohesive application
  services.
- User value: Deterministic services, future AI boundaries, and workflow orchestration
  become easier to reason about independently.
- Scope:
  - Create application modules for:
    - author memory;
    - signals;
    - planning;
    - briefing;
    - drafting/editing checks;
    - release;
    - analytics.
  - Keep an `application` compatibility barrel for current imports.
  - Add service-level comments that explain deterministic fallback and future AI/provider
    boundaries.
- Out of scope:
  - Real AI provider calls.
  - UI changes.
  - Domain model changes beyond imports.
- Implementation notes:
  - Application services may import domain contexts, but not UI or infrastructure.
  - Keep deterministic behavior byte-for-byte where practical.
- Tests:
  - Existing application/domain tests.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update SAO and developer guide.
- Demo impact:
  - None.
- Acceptance criteria:
  - `editorialServices.ts` is no longer the service god-file.
  - Services have clear ownership boundaries.
- Risks:
  - Over-splitting could create boilerplate; group by workflow role, not by every
    function.
- Completed: 2026-06-15

### Slice 1.5.19: Split Demo Workspace Fixtures

- Status: Done
- Goal: Break `src/fixtures/demoWorkspace.ts` into scenario modules while preserving a
  single demo workspace factory.
- User value: Demo data becomes easier to update with new product slices without
  editing a thousand-line fixture file.
- Scope:
  - Split demo fixtures by context:
    - author memory;
    - editorial model;
    - signals/radars;
    - planning;
    - production artifacts;
    - release and analytics.
  - Keep `createDemoWorkspace` as the public factory.
  - Add comments explaining the permanent AI Product Manager demo story.
- Out of scope:
  - Changing demo behavior or copy.
  - New demo scenarios.
  - UI changes.
- Implementation notes:
  - Avoid fixture barrels that eagerly obscure ownership; keep the public factory
    intentional.
- Tests:
  - Storage reset tests.
  - Demo workspace tests.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update demo docs if fixture ownership changes developer workflow.
- Demo impact:
  - No visible change.
- Acceptance criteria:
  - Demo data is modular and still produces the same workspace after reset.
- Risks:
  - Fixture split can accidentally alter IDs; preserve stable IDs unless intentionally
    changed.
- Completed: 2026-06-15

### Slice 1.5.20: Split Author Memory Feature Internals

- Status: Done
- Goal: Break `src/features/author-memory/AuthorMemoryView.tsx` into cohesive
  subcomponents without changing UX.
- User value: The largest feature surface becomes maintainable and safer to extend.
- Scope:
  - Extract composer, feed, note cards, assertions panel, sources tab, import queue tab,
    archive tab, bulk dialog, and local feature helpers.
  - Keep `AuthorMemoryView` as the feature entrypoint.
  - Add feature-local comments where correction/evidence/import flows have non-obvious
    behavior.
- Out of scope:
  - Product changes.
  - CSS changes.
  - Storage changes.
- Tests:
  - Existing author memory UI tests.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update developer guide with feature internal structure.
- Demo impact:
  - None.
- Acceptance criteria:
  - `AuthorMemoryView.tsx` drops below the new size limit.
  - User-visible behavior is unchanged.
- Risks:
  - Feature-local state can be accidentally split incorrectly; preserve existing
    callback boundaries.
- Completed: 2026-06-15

### Slice 1.5.21: Split Editorial Model Feature Internals

- Status: Done
- Goal: Break `src/features/editorial-model/EditorialModelView.tsx` into tab and panel
  modules without changing UX.
- User value: Editorial model work can continue without reintroducing a feature-level
  god-file.
- Scope:
  - Extract publisher tab, topics tab, fabulas tab, matrix tab, project profile header,
    validation panel, and local helpers.
  - Keep `EditorialModelView` as the feature entrypoint.
- Out of scope:
  - New validators.
  - New editorial-model behavior.
  - CSS changes.
- Tests:
  - Editorial model UI tests.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update developer guide with feature internal structure.
- Demo impact:
  - None.
- Acceptance criteria:
  - `EditorialModelView.tsx` drops below the new size limit.
  - Existing add/edit/delete/validation flows still work.
- Risks:
  - Matrix and topic/fabula editors share state; keep save/cancel behavior identical.
- Completed: 2026-06-15

### Slice 1.5.22: Split Signals Feature Internals

- Status: Done
- Goal: Break `src/features/signals/SignalsView.tsx` into radar, signal, candidate
  preview, and side-panel modules without changing UX.
- User value: Signals can evolve into post candidates without the feature file becoming
  the next monolith.
- Scope:
  - Extract radars tab, radar editor, found signals tab, signal card, candidates preview,
    side panel, and local filter/label helpers.
  - Keep `SignalsView` as the feature entrypoint.
- Out of scope:
  - Post candidate assemblies.
  - Real radar execution.
  - CSS changes.
- Tests:
  - Signals UI tests.
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update developer guide with feature internal structure.
- Demo impact:
  - None.
- Acceptance criteria:
  - `SignalsView.tsx` drops below the new size limit.
  - Radar and signal flows behave unchanged.
- Risks:
  - Signals has recent layout guardrails; visual smoke must remain mandatory.
- Completed: 2026-06-15

### Slice 1.5.23: Bundle and Import Hygiene Baseline

- Status: Done
- Goal: Ensure the new modular structure imports only what it needs and does not
  accidentally pull the whole app into each feature.
- User value: The browser bundle stays understandable and future lazy-loading remains
  possible.
- Scope:
  - Add import hygiene checks for domain/application/shared barrels.
  - Identify heavy imports and broad compatibility barrels that should be phased out.
  - Add a simple bundle/build report or dependency graph check appropriate for Vite.
  - Define public API boundaries for each major context.
- Out of scope:
  - Actual route-level lazy loading unless it is trivial and risk-free.
  - Product behavior changes.
  - UI changes.
- Implementation notes:
  - Compatibility barrels may remain where needed, but new imports should prefer direct
    context modules.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
- Docs:
  - Update SAO and developer guide.
- Demo impact:
  - None.
- Acceptance criteria:
  - Import rules are documented and checked.
  - Product slices can resume without expanding hidden coupling.
- Risks:
  - Premature optimization can distract from maintainability; keep this slice focused
    on visibility and boundaries.
- Completed: 2026-06-15

### Slice 1.5.24: Feature Internals Cleanup and OOP Boundaries

- Status: Done
- Goal: Bring the refactored React/domain structure closer to maintainable feature
  modules by splitting remaining large feature entrypoints and editorial-model
  transitions by role.
- User value: New contributors can open a feature or domain folder and find the
  relevant component, form, tab, validator, or transition without reading a thousand
  lines of unrelated code.
- Scope:
  - Split large feature entrypoints into feature-local tab, panel, editor, and card
    modules while keeping public feature entrypoints stable.
  - Split `src/domain/editorial-model/transitions.ts` into role-owned modules for
    rules, validation, and topic/fabula catalog transitions.
  - Keep compatibility barrels where existing imports need them, but prevent new
    logic from accumulating there.
  - Add architecture smoke limits for the new files and lower limits for the old
    entrypoints.
  - Add ADR coverage for React composition, OOP boundaries, and role-owned domain
    modules.
- Out of scope:
  - Product behavior changes.
  - Visual redesign.
  - New UI states or new domain concepts.
  - Route-level lazy loading.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, ADRs, and roadmap.
- Demo impact:
  - None.
- Acceptance criteria:
  - Large feature entrypoints shrink and delegate to feature-local modules. Done.
  - Editorial-model transitions are split by role with a thin compatibility export. Done.
  - Architecture smoke tracks the new feature-local/domain-owned modules. Done.
  - Behavior and visual regression tests pass. Done.
- Risks:
  - Mechanical extraction can accidentally move state ownership; preserve existing
    props/callback boundaries and use tests to catch regressions.
- Completed: 2026-06-15

### Slice 1.5.25: Author Memory Entry Point Decomposition

- Status: Done
- Goal: Reduce `src/features/author-memory/AuthorMemoryView.tsx` into a thin
  feature composition root without changing behavior, storage, demo data, or CSS.
- User value: Author memory remains maintainable before product work resumes, so
  adding future memory/import behavior does not recreate a feature-level god file.
- Scope:
  - Move memory feed composer/edit/delete/correction state into
    `useMemoryFeedController`.
  - Move import queue/archive/bulk-review state into `useImportReviewController`.
  - Move feed rendering, side panel, and dialogs into feature-local components.
  - Lower architecture smoke limits for `AuthorMemoryView` and the new modules.
- Out of scope:
  - Product behavior changes.
  - Visual redesign or CSS changes.
  - Domain/storage changes.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, and roadmap.
- Demo impact:
  - None.
- Acceptance criteria:
  - `AuthorMemoryView` is below the new architecture limit and contains no feed/import
    orchestration internals. Done.
  - Existing author memory and import/archive flows remain behaviorally unchanged. Done.
  - Full regression commands pass. Done.
- Risks:
  - Hook extraction can accidentally change stale closure behavior; preserve existing
    callback boundaries and rely on regression tests.
- Completed: 2026-06-15

### Slice 1.5.26: Signals Feature Internal Decomposition

- Status: Done
- Goal: Reduce `src/features/signals/SignalsView.tsx` into a thin feature composition
  root without changing behavior, storage, demo data, or CSS.
- User value: Signals can evolve into post candidate assemblies without recreating a
  feature-level god file.
- Scope:
  - Move signals tabs, filters, radar draft, signal draft, and summary state into
    `useSignalsController`.
  - Move header, tabs, radars list, radar card, found signals list, signal card, and
    post-candidates preview into role-owned feature modules.
  - Lower architecture smoke limits for `SignalsView` and the new signals modules.
- Out of scope:
  - Product behavior changes.
  - Visual redesign or CSS changes.
  - Domain/storage changes.
  - Post candidate assemblies.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, and roadmap.
- Demo impact:
  - None.
- Acceptance criteria:
  - `SignalsView` is below the new architecture limit and contains no radar/signal
    orchestration internals. Done.
  - Existing radar and found-signal flows remain behaviorally unchanged. Done.
  - Full regression commands pass. Done.
- Risks:
  - Mechanical extraction can accidentally change expanded/edit state; preserve existing
    callbacks and rely on regression tests.
- Completed: 2026-06-15

### Slice 1.5.27: Author Memory Import Queue Decomposition

- Status: Done
- Goal: Reduce `src/features/author-memory/ImportQueueView.tsx` into a thin
  queue-tab composition root without changing behavior, storage, demo data, or CSS.
- User value: The author-memory import queue can evolve without recreating a large
  feature-level file.
- Scope:
  - Move import queue filters and list/group mode controls into `ImportQueueToolbar`.
  - Move selection summary and bulk archive/reject actions into `ImportQueueBulkBar`.
  - Move group, list, and empty-state rendering into dedicated queue modules.
  - Lower architecture smoke limits for `ImportQueueView` and the new queue modules.
- Out of scope:
  - Product behavior changes.
  - Visual redesign or CSS changes.
  - Domain/storage changes.
  - Post candidate assemblies.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, and roadmap.
- Demo impact:
  - None.
- Acceptance criteria:
  - `ImportQueueView` is below the new architecture limit and contains no filter,
    bulk-action, group-list, or candidate-list rendering internals. Done.
  - Existing import queue filters, selection, bulk actions, and candidate actions
    remain behaviorally unchanged. Done.
  - Full regression commands pass. Done.
- Risks:
  - Mechanical extraction can accidentally change selection behavior; preserve existing
    props/callback boundaries and rely on regression tests.
- Completed: 2026-06-15

### Slice 1.5.28: App Workspace Controller Decomposition

- Status: Done
- Goal: Reduce `src/app/useWorkspaceController.ts` into a thin public facade over
  role-owned app hooks without changing behavior, storage, demo data, or CSS.
- User value: App-level orchestration remains maintainable before product work
  resumes; persistence, chat, signals, production actions, and release export no
  longer live in one god-hook.
- Scope:
  - Move load/save/reset/toast and workspace patch helpers into
    `useWorkspacePersistence`.
  - Move context-chat messages, suggestions, intents, and open/tab state into
    `useContextChatController`.
  - Move radar/signal workspace actions into `useSignalsWorkspaceActions`.
  - Move insight/plan/brief/draft/release/analytics callbacks into
    `useProductionFlowActions`.
  - Move clipboard/download helpers into `releaseExport`.
  - Lower architecture smoke limits for the app controller and new app hooks.
- Out of scope:
  - Product behavior changes.
  - Visual redesign or CSS changes.
  - Domain/storage/demo changes.
- Tests:
  - `npm run test:architecture`.
  - `npm test -- --run`.
  - `npm run smoke`.
  - `npm run test:design`.
  - `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, and roadmap.
- Demo impact:
  - None.
- Acceptance criteria:
  - `useWorkspaceController.ts` is below the new architecture limit and contains no
    context-chat, radar/signal, production-flow, or export internals. Done.
  - Existing app navigation, reset, chat, signals, plan, release, and analytics flows
    remain behaviorally unchanged. Done.
  - Full regression commands pass. Done.
- Risks:
  - App-level action extraction can accidentally change stale workspace reads; keep
    existing callback boundaries and rely on regression tests.
- Completed: 2026-06-15

### Slice 1.5.29: Architecture Drift Guardrails and Agent Workflow Rules

- Status: Done
- Goal: Make architecture guardrails a mandatory part of future development instead of
  a one-time agreement.
- User value: Future product slices can resume with lower risk of bloating
  app/feature/domain files or bypassing the design-system and module ownership rules.
- Scope:
  - Add ADR
    `docs/adr/2026-06-16-architecture-drift-is-prevented-by-agent-and-smoke-guardrails.md`.
  - Strengthen `scripts/architecture-smoke.mjs` with near-limit warnings, successful
    near-limit summary output, warning-level export-count guardrails, and explicit
    feature dependency/barrel hygiene.
  - Update `.agents/skills` so slice implementation, planning, architecture design,
    regression strategy, frontend design-system work, and project onboarding all
    account for architecture guardrails.
  - Update SAO and developer docs with architecture preflight and drift-prevention
    policy.
- Out of scope:
  - Product behavior changes.
  - UI, CSS, storage, demo data, domain contracts, or feature implementation changes.
- Implementation notes:
  - Near-limit and export-count checks are warning-level at this step.
  - Existing hard architecture limits stay unchanged.
  - New architecture rules must have ADR + SAO coverage plus automated check or
    mandatory workflow checklist coverage.
- Architecture impact:
  - Adds process and smoke guardrails before `Slice 1.6`.
  - Makes `Architecture impact` mandatory for new product slices.
  - Keeps `src/features/*` dependency direction explicit: no feature-to-feature imports
    and no root features barrel bypass.
- Tests:
  - `npm run test:architecture` passed and printed a near-limit summary.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - Workflow text check for `.agents/skills/*/SKILL.md` required mentions passed.
  - `npm run test:design` and `npm run test:visual` are not required for this slice
    because UI/CSS do not change.
- Docs:
  - Update ADR, SAO, developer guide, roadmap, and `.agents/skills`.
- Demo impact:
  - None.
- Acceptance criteria:
  - Architecture smoke passes and prints a near-limit summary. Done.
  - Skill files mention required architecture, roadmap, ADR/SAO/checklist, and
    frontend visual validation rules. Done.
  - Slice 1.6 remains the next `Ready` product slice. Done.
- Risks:
  - Warning-level export counts can be noisy; keep them informational until a separate
    cleanup slice lowers public surfaces deliberately.
- Completed: 2026-06-16

### Slice 1.6: First Real Post Candidate Assemblies

- Status: Done
- Goal: Replace the `Кандидаты постов` placeholder with the first working
  compare-and-approve layer.
- User value: The author can compare deterministic post concepts assembled from
  approved signals and choose one as the current concept before building the insight.
- Dependency:
  - Completed after `Slice 1.5.29` architecture guardrails.
- Scope:
  - Add `PostCandidate` as a domain contract with signal, topic, fabula, audience,
    value, goal, platform, title, thesis, evidence summary, confidence, risks, and
    approval status. Candidate `format` was removed in Slice 1.7.1 because it
    duplicated fabula.
  - Store `postCandidates` and selected `postCandidate` in `WorkspaceState`; normalize
    old local workspaces to an empty candidate list and `null` selection.
  - Generate 2-3 deterministic candidates from approved `SourceSignal` records and
    active topic/fabula pairs in the editorial matrix.
  - Show real candidate cards in `Сигналы -> Кандидаты постов` with compare fields,
    confidence, risks, and `Утвердить кандидата`.
  - On approve, select the candidate, set its signal as the current signal, and clear
    stale downstream insight/plan selection/brief/draft/release/analytics artifacts.
  - Make `createInsightCard` use the selected candidate concept when one is approved.
- Out of scope:
  - Candidate edit, reject, request-more, bulk actions, and calendar slot binding.
  - Full calendar view, real AI candidate generation, real search, and automated
    publishing.
- Implementation notes:
  - `PostCandidatesPreviewTab` is now the real candidates tab composition root.
  - Candidate assembly lives in `src/application/postCandidateService.ts`.
  - Candidate approval orchestration lives in
    `src/app/usePostCandidateWorkspaceActions.ts`.
- Architecture impact:
  - Ran architecture preflight before implementation and kept hard limits active.
  - Candidate UI stays in `src/features/signals` with `PostCandidateCard` and
    `usePostCandidatesController`; `useSignalsController` was not expanded.
  - Domain/application logic stays outside React and feature code has no feature-to-
    feature imports.
- Tests:
  - `npm run test:architecture` passed before implementation.
  - Domain/application tests cover deterministic generation, approved-signal filtering,
    candidate-backed insight creation, and downstream reset on approve.
  - UI tests cover candidate cards, approve action, App smoke integration, and empty
    state without approved signals.
  - `npm run test:architecture` passed after implementation.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
- Docs:
  - Update architecture, developer guide, user guide, demo docs, wiki, and roadmap.
- Demo impact:
  - Demo shows 2-3 candidate concepts for the AI Product Manager signal and lets the
    author approve one before `Собрать инсайт -> В план`.
- Acceptance criteria:
  - User can review multiple deterministic candidates. Done.
  - Approved candidate becomes the current concept for the existing insight-to-plan
    flow. Done.
  - Placeholder text is gone and empty state routes the user back to approved signals.
    Done.
- Risks:
  - Candidate generation is deterministic and intentionally simple; edit/reject/request-
    more candidates should be handled in the next product slice.
- Completed: 2026-06-16

### Slice 1.7: Candidate List UX Parity and Review Actions

- Status: Done
- Goal: Bring `Кандидаты постов` to the same large-list UX pattern as
  `Память автора -> Очередь разбора`.
- User value: The author can filter, search, group, edit, reject, and approve post
  candidates without the layout drifting from the rest of the cabinet.
- Scope:
  - Remove the top `Кандидаты постов / Сравните сборки... / counters` hero-summary
    block from the candidates tab.
  - Make the first main-content block a filter card with `Сигнал`, `Статус`, `Тема`,
    `Risk`, full-width search, and `Список / Группы` toggle.
  - Add grouping by signal, topic, status, and risk.
  - Convert candidate cards to the cabinet row pattern with bottom-left inline actions:
    primary red `Утвердить`, secondary `Редактировать` and `Отклонить`.
  - Add inline edit for title, thesis, audience, value, goal, platform, evidence
    summary, and risks. Candidate fabula edit and format cleanup were finalized in
    Slice 1.7.1.
  - Make `Доказательство` full-width inside the facts grid and keep `Risks`
    full-width below facts.
  - Add frontend rule: all large entity lists use the pattern
    `filter card -> search -> list/group toggle -> framed rows -> bottom-left actions`.
- Out of scope:
  - Request-more variants.
  - Bulk actions for candidates.
  - Real AI generation.
  - Calendar slot assignment.
- Implementation notes:
  - Candidate filters/grouping/edit UI is split into role-owned modules under
    `src/features/signals`.
  - `PostCandidatesPreviewTab` remains a composition root; candidate list logic lives
    in `usePostCandidatesController` and `postCandidateFilters`.
  - `SignalsView` and `useSignalsController` were not expanded with candidate behavior.
- Architecture impact:
  - Architecture preflight and final smoke passed.
  - Added architecture baselines for candidate toolbar, grouped list, edit form, and
    filter/group helpers.
  - Domain transitions for edit/reject live in `src/domain/post-candidates`.
  - Workspace mutation remains in `src/app/usePostCandidateWorkspaceActions.ts`.
- Tests:
  - Domain/application tests cover edit, reject, rejected-candidate approval guard, and
    approved edited candidate insight creation.
  - UI tests cover no hero-summary block, filter card, filtering/search/grouping,
    bottom-left actions, primary/secondary button classes, edit save, reject action,
    evidence full-width, empty states, and cards staying in `.memory-main`.
  - `npm run test:architecture` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
- Docs:
  - Update architecture, developer guide, user guide, demo docs, wiki, design workflow,
    and roadmap.
- Demo impact:
  - Demo candidates now use the same filter/search/group UX as the import queue and
    expose edit/reject/approve review actions without changing calendar behavior.
- Acceptance criteria:
  - Candidate cards render in `.memory-main`, never in `.memory-side`. Done.
  - Top hero-summary block is gone. Done.
  - Candidate list follows the shared large-list pattern. Done.
  - Reject/edit do not create downstream artifacts. Done.
  - Only approved candidates can feed `Собрать инсайт`. Done.
- Risks:
  - `PostCandidateCard` and `usePostCandidateWorkspaceActions` are near their smoke
    limits; future candidate behavior should split card subparts and orchestration
    helpers before adding more state.
- Completed: 2026-06-16

### Slice 1.7.1: Candidate Format Cleanup and Edit Context

- Status: Done
- Goal: Remove the confusing candidate `format` field and make candidate editing show
  enough immutable context to edit safely.
- User value: The author understands which signal/topic/fabula combination is being
  edited and no longer sees a duplicate "format" field that repeats the fabula.
- Scope:
  - Remove `format` from `PostCandidate` domain contract, deterministic generation,
    candidate cards, edit form, and tests. Done.
  - Treat old persisted candidate `format` values as legacy storage noise during
    workspace normalize. Done.
  - Show readonly edit context for source signal and suggested topic. Done.
  - Make candidate `fabulaId` editable through a select of active fabulas. Done.
  - Warn when the chosen fabula is not enabled for the candidate topic, but do not
    block saving. Done.
  - Keep candidate topic readonly in this slice. Done.
- Out of scope:
  - Editing topic from the candidate card.
  - Recomputing title/thesis/value automatically after a fabula change.
  - Request-more variants and calendar slot binding.
- Architecture impact:
  - Must avoid further growth in near-limit `PostCandidateCard`; edit context belongs
    in a role-owned candidate edit context module. Done.
  - Domain/application changes stay outside React. Done.
  - Storage compatibility handles legacy `format` without keeping it in the current
    domain type. Done.
- Tests:
  - Domain/application tests for no candidate `format`, editable `fabulaId`, and
    approved edited candidate feeding insight. Done.
  - Storage test for old saved candidates with `format`. Done.
  - UI tests for readonly signal/topic in edit mode, editable fabula select, no
    `Format` field in read mode, and matrix warning for incompatible fabula. Done.
  - `npm run test:architecture` passed.
  - `npm test -- --run` passed.
  - `npm run smoke` passed.
  - `npm run test:design` passed.
  - `npm run test:visual` passed.
- Docs:
  - Update SAO, developer guide, user guide, demo docs, wiki, and roadmap.
- Demo impact:
  - Candidate editing shows the source signal and suggested topic while letting the
    author change only the fabula among structural fields. Done.
- Risks:
  - `PostCandidateEditForm` is exactly at its architecture smoke limit; future
    candidate edit behavior should split field groups before adding more controls.
- Completed: 2026-06-16

### Slice 1.8: Broadcast Grid Settings

- Status: Done
- Goal: Add high-level broadcast settings before calendar implementation.
- User value: The author can configure publishing tempo and candidate expectations
  once, instead of editing every post slot manually.
- Scope:
  - Add `План -> Настройка сетки`.
  - Support:
    - tempo of articles/posts;
    - planning period: week, month, quarter;
    - publishing days and times;
    - min/max candidates per slot;
    - default platform until dedicated platform entities exist;
    - signal selection policy: HITL-only, automatic, or automatic with review.
  - Save settings explicitly.
  - Generate a hybrid publish-window frame for the chosen horizon: slots get
    configured dates/times while deterministic planning can still fill topic/fabula
    ideas.
  - Show deficit/proficit summary with separate available candidate and approved
    concept counters.
- Out of scope:
  - Calendar zoom UI.
  - Real radar execution.
  - AI planning.
- Implementation notes:
  - Settings are general requirements for the grid, not detailed settings for every
    post.
  - Saved settings clear generated slots and downstream production artifacts so the
    grid is explicitly rebuilt.
  - `format` is not a candidate/grid setting in this slice; slot format is derived
    from the fabula title until a dedicated platform/format model exists.
- Architecture impact:
  - Adds planning settings normalization and publish-window generation in domain code.
  - Keeps demand summary in application logic and UI state in role-owned
    `src/features/plan` modules.
  - Storage migration is additive and normalizes legacy settings/items.
- Tests:
  - Domain tests for slot generation from tempo/days/period.
  - UI tests for settings save/cancel and regenerated slot counts.
  - Storage tests for settings persistence.
- Docs:
  - Update docs and wiki screenshots.
- Demo impact:
  - Demo should show a monthly or two-week Telegram planning setup for the AI Product
    Manager blog.
- Acceptance criteria:
  - User can configure the broadcast grid at a high level.
  - System creates slots from settings.
  - Candidate deficit/proficit is visible.
- Risks:
  - Calendar settings can become platform-specific; keep platform entities deferred.
- Completed: 2026-06-17

### Slice 1.8.1: Broadcast Grid UX Parity, Filters, and Calendar Settings

- Status: Done
- Goal: Fix the Slice 1.8 planning UX so `План` follows the same cabinet list,
  tabs, actions, row, warning, and calendar-setting rules as the rest of the product.
- User value: The author can configure the grid visually, filter many slots, inspect
  candidate context, and edit plan-specific fields without losing orientation.
- Scope:
  - Move `Сетка / Настройка сетки` to canonical `.tabs .tab` under the plan header.
  - Remove centered/floating toolbar actions; primary actions align with canonical
    header or row action areas.
  - Add a filter card above broadcast slots with status, platform, topic, fabula,
    risk, search, and list/group toggle.
  - Stabilize broadcast rows so long titles/topics/fabulas wrap inside the main
    content area without horizontal drift.
  - Expand slot details to show candidate/source context: signal, topic, fabula,
    audience, value, goal, thesis/evidence, risks, and plan date/time/platform.
  - Keep edit mode oriented with readonly signal/topic/fabula/candidate context and
    editable plan fields only.
  - Replace weekday toggles in settings with a mini calendar for week/month/quarter
    where clicking a day selects/unselects a publish slot.
  - Show selected/target/remaining/extra slot counts while editing calendar settings.
  - Fix warning contrast in the right panel and enforce action gaps.
- Out of scope:
  - Drag-and-drop calendar.
  - Real AI planning.
  - Bulk plan actions.
  - Full per-slot candidate binding beyond showing the current linked/derived concept.
- Implementation notes:
  - Reuse the cabinet list pattern from `ImportQueueToolbar` and post candidates.
  - Store explicit `publishSlots` in `ContentPlanSettings`; keep weekday/time fields as
    legacy/default fallback for old workspaces.
  - Shared candidate detail display can be derived from the approved `postCandidate`,
    generated candidates, insight, source signal, topic, and fabula.
- Architecture impact:
  - Planning UI remains under `src/features/plan` with separate toolbar, row detail,
    row edit, calendar settings, and filters modules.
  - Domain schedule helpers own publish-slot normalization and calendar generation.
  - Design smoke gains plan-specific checks for tabs, action gaps, row overflow,
    floating toolbar actions, and warning contrast.
- Tests:
  - Domain/application tests for explicit publish slots and fallback days/times.
  - UI tests for tabs placement, filters, grouping, row layout, slot detail context,
    edit context, mini calendar selection, and action classes.
  - Design/visual smoke must cover `План`.
- Docs:
  - Update SAO, developer guide, user guide, wiki/demo notes with plan UX rules and
    mini-calendar settings behavior.
- Demo impact:
  - Demo shows monthly Telegram plan settings with selected publish dates and visible
    deficit/proficit counters.
- Acceptance criteria:
  - `План` uses canonical tabs below the header.
  - Broadcast list has filter card and stable rows. Done.
  - Expanded/edit slot surfaces do not hide source/candidate context. Done.
  - Settings use a clickable mini calendar with target/remaining feedback. Done.
  - Design smoke would fail on the reported tab/action/overflow/contrast regressions. Done.
- Risks:
  - `PlanSettingsPanel` and `BroadcastGridRow` are close enough to smoke limits that
    field groups must be split before adding behavior.
- Completed: 2026-06-17

### Slice 1.8.2: Broadcast Grid Candidate Calendar View

- Status: Done
- Goal: Add a calendar view to the existing broadcast grid candidate list without
  replacing the operational list view.
- User value: The author can keep filtering the grid as a list, then switch to a
  calendar that shows which publish dates already have candidates and inspect the
  rows for a selected date.
- Scope:
  - Add a third view mode in the broadcast grid filter toolbar: `Список`, `Группы`,
    `Календарь`.
  - Reuse the same week/month/quarter mini-calendar logic as `Настройка сетки`.
  - Mark publish dates in calendar cells and show the number of current filtered
    candidates for each date.
  - Clicking a date renders the same broadcast row cards below the calendar for that
    date.
  - Keep filters/search above the calendar so the count and selected-date rows reflect
    the current filter state.
- Out of scope:
  - Full readiness calendar statuses.
  - Drag-and-drop slot movement.
  - Slot/candidate reassignment from the calendar cell.
  - New candidate generation or request-more variants.
- Architecture impact:
  - Calendar view state stays in `useBroadcastGridController`.
  - Calendar grouping and slot merging live in role-owned plan helpers under
    `src/features/plan`.
  - `PlanView` and `BroadcastGridRow` remain near-limit files and receive only wiring,
    not new calendar behavior.
- Tests:
  - UI test covers calendar tab, main-column rendering, date counts, date click, and
    date-specific rows.
  - Design/visual smoke now check that the broadcast calendar view exists, shows
    counts, and renders selected-date rows.
- Docs:
  - Update SAO, developer guide, user guide, demo docs, wiki notes, and roadmap.
- Demo impact:
  - Demo plan can be reviewed either as a filtered list/grouped list or as a compact
    calendar with per-date candidate counts.
- Acceptance criteria:
  - Calendar view appears from the broadcast grid filter toolbar. Done.
  - Calendar period matches the saved week/month/quarter planning setting. Done.
  - Candidate counts reflect the current filtered grid. Done.
  - Clicking a date shows the same row cards as the normal list. Done.
- Completed: 2026-06-17

### Slice 1.9: Editorial Work Queue Foundation

- Status: Done
- Goal: Replace the singleton "current post" production mental model with an
  editorial work queue while preserving the existing one-post editing behavior.
- User value: The author can approve several plan slots and see them as a production
  queue in `Редактура`, then choose which post to work on without overwriting another
  post's brief, draft, final text, or release state.
- Scope:
  - Add an `EditorialWorkItem` domain concept for an approved post in production.
  - Add `editorialWorkItems: EditorialWorkItem[]` and
    `selectedEditorialWorkItemId: string | null` to `WorkspaceState`.
  - Normalize old workspaces by creating an empty queue and preserving current
    singleton production fields as compatibility state.
  - Before Slice 1.10, approving a plan slot or clicking `Подготовить фабулу поста`
    created or updated a work item linked to the plan slot and candidate/source
    context.
  - Add a queue surface to `Редактура` using the shared large-list pattern:
    `filter card -> search -> list/group toggle -> framed rows -> bottom-left actions`.
  - Selecting a row should open the then-current one-post compatibility workbench
    for that work item, initially reusing compatibility fields if needed.
- Out of scope:
  - Full migration of every production action to work-item ids.
  - Release queue.
  - Calendar readiness statuses.
  - Bulk production actions.
- Implementation notes:
  - Treat current `postBrief`, `postDraft`, `finalText`, and `releasePackage` as
    compatibility fields during this slice.
  - Do not rebuild `BriefView`, `EditView`, or `ReleaseView`; wrap/reuse their current
    behavior around selected work-item context.
  - Historical Slice 1.9 note: the first queue seeded item status from then-current
    compatibility artifacts. After Slice 1.10.5, `FinalText` remains internal
    compatibility state and the user-facing stage after draft approval is `visual`.
- Architecture impact:
  - Add role-owned domain/application helpers for editorial work items.
  - Keep `Редактура` UI under `src/features/editing`; avoid growing `App.tsx` or
    `useWorkspaceController`.
  - `useProductionFlowActions` is near-limit; new queue orchestration should move into
    a role-owned action hook or helper rather than expanding it substantially.
- Tests:
  - Storage normalize adds queue fields to old workspaces.
  - Creating a work item from an approved slot preserves slot/candidate context.
  - Selecting one queued post does not erase another queued post.
  - `Редактура` renders a queue and selected-post workbench in main content.
  - Regression: `npm run test:architecture`, `npm test -- --run`, `npm run smoke`,
    `npm run test:design`, `npm run test:visual`.
- Docs:
  - Update SAO, developer guide, user guide, demo docs, and wiki production flow.
- Demo impact:
  - Demo shows at least two approved slots in the editorial queue, with one selected
    for the compatibility selected-post flow.
- Acceptance criteria:
  - Approved slots appear in `Редактура` as production work items.
  - The author can select a post before editing it.
  - Existing one-post production flow still works for the selected item.
  - Work item context shows date, platform, signal, topic, fabula, title, and stage.
- Risks:
  - Partial compatibility can be confusing if singleton fields and work items diverge;
    make selected item ownership explicit in UI and tests.

- Implementation result:
  - Added `EditorialWorkItem`, workspace queue fields, storage normalization, stable
    upsert from approved plan slots, and selected-item compatibility hydration.
  - `Редактура` now starts with the shared list pattern and renders the selected
    compatibility workbench below the queue.
  - Historical note: before Slice 1.10, `Подготовить фабулу поста` opened
    `Редактура`; after Slice 1.10, slot approval prepares the brief automatically.
    `BriefView` remains a compatibility surface.
- Completed: 2026-06-17

### Slice 1.10: Редактура как очередь постов и рабочий стол

- Status: Done
- Goal: Remove the redundant post-fabula preparation step after plan slot approval and
  make `Редактура` the working place for approved production posts.
- User value: After the author approves a candidate in `Сигналы` and approves its slot
  in `План`, the post is already in `Редактура` with an initial fabula/brief prepared.
  The author can review the queue, choose a post, edit it, or return it to candidates
  without hunting through another section.
- Scope:
  - On `План -> Утвердить`, create or update the stable `EditorialWorkItem` from the
    `contentPlanItemId`.
  - Prepare the initial `PostBrief` automatically for that work item.
  - Remove the mandatory visible `Подготовить фабулу поста` step from the plan slot
    happy path.
  - Split `Редактура` into `Посты` and `Рабочий стол`.
  - `Посты` uses the shared large-list pattern: filter card, full-width search,
    list/group toggle, framed collapsible rows, and bottom-left actions.
  - Row actions are `К рабочему столу` and `Вернуть в кандидаты`.
  - `Вернуть в кандидаты` reverses the approved plan slot, removes the work item from
    the queue, clears its production artifacts, and returns the linked candidate to
    draft review state when available.
  - `Рабочий стол` has a searchable post picker and keeps the selected-post stages
    inside the selected post workbench.
  - Add right panels for queue summary and selected-post workbench context.
- Out of scope:
  - Release queue.
  - Real AI drafting.
  - Collaborative editing.
  - Full removal of singleton compatibility fields.
- Architecture impact:
  - `План` owns slot approval only; `Редактура` owns production work after approval.
  - Slot approval orchestration lives in role-owned app/domain helpers, not in React
    JSX.
  - `postBrief`, `postDraft`, `finalText`, `releasePackage`, and
    `editorialLearningNote` remain compatibility fields synchronized with the selected
    work item.
  - `EditView` composes feature-owned posts/workbench modules and must not become a
    god component.
- Tests:
  - Approving a plan slot creates one stable work item and initial brief. Done.
  - Re-approving a slot does not create a duplicate. Done.
  - Returning a post to candidates clears the work item and reverses the slot. Done.
  - `Редактура` renders `Посты / Рабочий стол`, queue actions, picker, and selected
    workbench. Done.
  - Regression: `npm run test:architecture`, `npm test -- --run`, `npm run smoke`,
    `npm run test:design`, `npm run test:visual`.
- Docs:
  - Update SAO, ADRs, developer guide, user guide, demo docs, wiki notes, README, and
    roadmap.
- Demo impact:
  - Demo path becomes `Кандидаты -> Инсайт -> План -> Утвердить слот -> Редактура /
    Посты -> Рабочий стол`.
- Acceptance criteria:
  - Approved slots automatically appear in `Редактура`.
  - No extra mandatory `Подготовить фабулу поста` action is needed after slot approval.
  - The author can open a queued post on the workbench or return it to candidates.
  - Existing fabula/draft/final UX remains recognizable.
- Risks:
  - Compatibility fields can still diverge from work-item state until future slices
    move all production actions to explicit work-item ids.
- Completed: 2026-06-17

### Slice 1.10.1: Editorial Workspace UX Guardrail Repair

- Status: Done
- Goal: Fix the first `Редактура` UX regressions after Slice 1.10 and extend
  design-system smoke coverage to the new editing surface.
- User value: The editorial queue now follows the same cabinet spacing and metric
  patterns as the rest of the product.
- Scope:
  - Reuse the canonical project-profile header padding for `Редактура`.
  - Replace custom vertical right-panel stats with shared compact summary metric
    cards.
  - Remove the redundant `Рабочий пост` header card from the selected-post workbench.
  - Add design-smoke coverage for `Редактура` header padding, metric alignment,
    right-panel summary cards, and absence of redundant workbench headers.
- Architecture impact:
  - No domain or storage changes.
  - UX rules are enforced in `scripts/design-system-smoke.mjs`, not only in docs.
- Tests:
  - `npm run test:design` covers the new editing design contract.
- Docs:
  - Update developer/design-system guidance and roadmap.
- Completed: 2026-06-17

### Slice 1.10.2: Automatic Draft After Fabula Approval

- Status: Done
- Goal: Remove the redundant `Написать драфт` action from the editorial workbench.
- User value: After the author approves the fabula, Glavred immediately moves the
  selected post into draft generation and shows the prepared draft stage instead of
  asking for another button click.
- Scope:
  - `Утвердить фабулу` now approves the `PostBrief` and creates the deterministic
    `PostDraft`, checks, and editor notes in one application transition.
  - Remove the `Написать драфт` action and prop chain from `Редактура`.
  - Historical note: this slice still had a `Финал` workbench stage; Slice 1.10.5
    removes that tab and approves text directly from `Драфт`.
  - Treat a work item with a draft artifact as stage `draft`, not as approved text.
- Architecture impact:
  - Draft creation stays in role-owned application helpers, not in React JSX.
  - Compatibility fields are still synchronized with the selected `EditorialWorkItem`.
- Tests:
  - Application action test verifies brief approval creates draft/checks/notes and
    syncs the selected work item. Done.
  - UI regression verifies `Написать драфт` is absent and the draft editor appears
    after `Утвердить фабулу`. Done.
- Docs:
  - Update user guide, demo docs, wiki notes, and roadmap.
- Completed: 2026-06-17

### Slice 1.10.3: Editorial Workbench Selection and Picker Repair

- Status: Done
- Goal: Fix broken selected-post navigation in `Редактура -> Рабочий стол`.
- User value: `К рабочему столу` opens the exact queued post the author selected, and
  the top post chooser behaves as one dropdown control instead of an input plus a
  duplicate selected row.
- Scope:
  - Make `PostBrief` ids and titles slot-specific instead of reusing the old demo
    hardcoded brief id/title for every editorial work item.
  - Repair legacy selected work item artifacts with the old hardcoded brief id/title
    when a user selects a post from existing local state.
  - Use one consistent row action label: `К рабочему столу`.
  - Replace the workbench picker input/results pair with a single select combobox
    that supports native first-letter typeahead.
  - Extend design-system smoke coverage so the old input plus `.picker-results`
    pattern cannot return.
- Architecture impact:
  - Selection hydration stays in `editorialWorkQueueActions`, outside React.
  - UI keeps a role-owned `EditorialWorkbenchPicker` component.
- Tests:
  - Application action tests verify different plan slots hydrate different brief
    titles.
  - Stateful `EditView` test verifies queue row and picker selection switch the
    active workbench post.
  - Design smoke verifies the picker is a single select combobox.
- Completed: 2026-06-17

### Slice 1.10.4: Editable Fabula Brief With Candidate Context

- Status: Done
- Goal: Make `Редактура -> Рабочий стол -> Фабула` a complete working screen for the
  selected post.
- User value: The author sees the original approved candidate and slot context while
  editing the production fabula, instead of guessing which signal/topic/fabula is being
  changed.
- Scope:
  - Show read-only context for signal, topic, fabula, audience, value, goal, platform,
    publication date/time, confidence, candidate evidence, and candidate risks.
  - Add inline edit mode for the `PostBrief` artifact: title, thesis, conflict, author
    position, audience, evidence, examples, structure, CTA, risks, and sources.
  - Keep candidate/slot identity read-only in the workbench; identity changes remain in
    `Сигналы` and `План`.
  - Saving an edited fabula sets the brief back to `draft`, syncs the selected
    `EditorialWorkItem`, and clears stale draft/checks/notes/final/release/learning
    artifacts.
  - Re-approving the edited fabula keeps the Slice 1.10.2 behavior: a new deterministic
    draft, checks, and notes are created immediately.
- Architecture impact:
  - `PostBrief` is not expanded with candidate or slot fields.
  - `src/features/editing/editorialWorkItemContext.ts` assembles read-only context from
    `WorkspaceState`, selected `EditorialWorkItem`, `ContentPlanItem`, `PostCandidate`,
    `SourceSignal`, `Topic`, and `Fabula`.
  - Brief editing lives in production transitions and app-level workspace patch
    helpers, not in React JSX.
- Tests:
  - Domain test covers `editPostBrief` and multiline normalization. Done.
  - Application action test covers selected work item sync and stale downstream reset.
    Done.
  - UI tests cover full context, edit/save/cancel, and returning to the `Фабула` stage
    after editing. Done.
- Docs:
  - Update SAO, user guide, demo docs, wiki, and roadmap.
- Completed: 2026-06-17

### Slice 1.10.5: Draft Approval Without Final Tab

- Status: Done
- Goal: Remove `Финал` as a separate workbench tab and approve post text directly in
  `Драфт`.
- User value: The author edits and approves the post where the text is visible, instead
  of switching to another tab only to press `Утвердить текст`.
- Scope:
  - Move `Утвердить текст` into the `Драфт` stage.
  - Add clear draft actions at the bottom-left: `Сохранить правки`, `Утвердить текст`,
    and `Вернуться к фабуле`.
  - Remove or hide the `Финал` tab from `Редактура -> Рабочий стол`.
  - Keep `FinalText` as a compatibility approved-text artifact for storage, release,
    and analytics bridges, but stop exposing `Финал` as a user workflow step.
  - Editing an already approved draft returns the selected work item to `draft` and
    clears stale visual/release/learning state.
- Out of scope:
  - Visual generation or visual approval.
  - Real platform publication.
  - Renaming `FinalText` in the domain model.
- Architecture impact:
  - Text approval remains owned by `src/features/editing` and production application
    actions.
  - `Выпуск` must not regain text-editing or text-approval behavior.
- Tests:
  - Domain/application test: approving a draft creates or updates the compatibility
    approved-text artifact and moves the work item toward visual readiness. Done.
  - UI test: `Финал` tab is absent and `Утвердить текст` is visible in `Драфт`. Done.
  - UI test: draft edits have explicit save/approve behavior and do not require
    switching tabs. Done.
- Docs:
  - Update user guide, demo docs, wiki, and SAO to describe `Драфт` as the text
    approval stage.
- Acceptance criteria:
  - A selected post workbench shows `Фабула / Драфт`, not `Фабула / Драфт / Финал`.
  - Text approval is completed from `Драфт`.
  - The next visible production step is `Визуал`.
- Implementation result:
  - `Редактура -> Рабочий стол` now shows only `Фабула / Драфт`.
  - Draft text uses an explicit edit buffer with `Сохранить правки` and
    `Утвердить текст`; typing no longer persists silently.
  - Approving text still creates compatibility `FinalText`, but the selected work item
    moves to `visual/todo` instead of `readyForRelease`.
  - Legacy stored work items with stage `final` normalize to `visual`.
- Completed: 2026-06-18

### Slice 1.10.6: Visual Stage Foundation

- Status: Done
- Goal: Add `Визуал` as the stage after text approval.
- User value: The author finishes a post as a complete publication unit, not only as
  text.
- Scope:
  - Add a `Визуал` stage inside the selected post workbench after approved text.
  - Store a minimal visual artifact: mode, one user-facing visual brief, approval
    status, and compatibility fields for future adapters.
  - Support three visual creation modes:
    - `Сгенерировать`: prepare one visual brief for a future generation adapter.
    - `Найти мем`: prepare one visual brief for future meme search.
    - `Мем + генерация`: prepare one visual brief for a future two-step meme selection
      and customization flow.
  - Support `без визуала` as an explicit mode.
  - Show the approved text context while preparing the visual.
  - Keep the visual stage local and deterministic/demo-ready.
- Out of scope:
  - Real image generation.
  - Real internet search or meme crawling.
  - Real hybrid image transformation.
  - Asset upload pipeline.
  - Platform-specific crop presets beyond simple labels.
- Architecture impact:
  - `Редактура` owns visual preparation and approval.
  - Visual state belongs to the selected `EditorialWorkItem`; it is not owned by
    `Выпуск`.
  - Visual mode is a domain enum, not free-form UI text, so future generation/search
    adapters can attach to it without changing the workbench contract.
- Tests:
  - Domain/application tests for visual artifact creation, editing, approval, and
    `без визуала` mode. Done.
  - Domain/application tests for the three visual modes: generate, meme search, and
    hybrid meme-based generation. Done.
  - UI tests for the `Визуал` stage, mode selector, bottom-left actions, and visible
    text context. Done.
- Acceptance criteria:
  - Approved text leads to a visible `Визуал` stage.
  - The author can choose `Сгенерировать`, `Найти мем`, `Мем + генерация`, or
    `без визуала`.
  - Visual modes use one Russian `Бриф` field, except `Без визуала`, which has no
    extra field, and can be saved/approved without real external calls.
- Implementation result:
  - Added `PostVisual` as selected-post compatibility state and selected
    `EditorialWorkItem.visual`.
  - `Редактура -> Рабочий стол` now has `Фабула / Драфт / Визуал`.
  - `Визуал` supports `Сгенерировать`, `Найти мем`, `Мем + генерация`, and
    `Без визуала` as local deterministic placeholders.
  - Visual save/approve uses explicit bottom-left actions and a local edit buffer.
  - Visual approval does not mark the item `readyForRelease`; Slice 1.10.7 owns that
    handoff rule.
- Completed: 2026-06-18

### Slice 1.10.6.1: Visual Variants Review Flow

- Status: Done
- Goal: Turn `Визуал` from a direct approval button into a review flow:
  `Бриф -> Подготовить варианты -> Выбрать вариант -> Утвердить визуал`.
- User value: The author can compare visual directions before approving the post's
  visual decision, matching the future generate/search/remix adapters.
- Scope:
  - Add `PostVisualVariant` and store variants, selected variant, and batch number
    inside `PostVisual`.
  - Generate deterministic placeholder variants for `Сгенерировать`, `Найти мем`,
    and `Мем + генерация`.
  - Keep `Без визуала` as a shortcut decision without a brief or variant list.
  - Add transitions for preparing variants, selecting a variant, approving only a
    selected variant, and confirming no visual.
  - Reset variants, selection, and approval when mode or brief is edited.
  - Update the visual workbench and right panel readiness summary.
- Out of scope:
  - Real image generation.
  - Real internet meme search.
  - Real image remix or asset upload.
  - Marking the post `readyForRelease`.
- Architecture impact:
  - Variant generation is deterministic application logic, not React state.
  - `PostVisual` remains selected-post compatibility state until the full work-item
    production model replaces singleton artifacts.
  - Future image/search/remix adapters will attach after the same review contract.
- Tests:
  - Domain/application tests for preparing, selecting, approving, no-visual shortcut,
    invalid selection, and reset after brief edits. Done.
  - UI tests for no direct visual approval before variants, variant cards, selection,
    approval after selection, more variants, edit brief, and no-visual shortcut. Done.
- Acceptance criteria:
  - `Утвердить визуал` is unavailable until a visual variant is selected.
  - `Подготовить варианты` creates three deterministic placeholder cards for visual
    modes.
  - `Без визуала` can be confirmed without variants.
  - `К выпуску: нет` remains true until Slice 1.10.7.
- Completed: 2026-06-18

### Slice 1.10.6.2: Two-Step Meme Remix Visual Flow

- Status: Done
- Goal: Make `Мем + генерация` a two-step visual flow: first choose the meme
  reference, then generate/select the custom remix variant and approve it.
- User value: The author can control the cultural reference before Glavred proposes
  custom generated adaptations, instead of treating remix as one generic variant list.
- Scope:
  - Split `memeRemix` UI into two local stages inside `Визуал`:
    - `Выбрать мем`: prepare and select one deterministic meme reference.
    - `Сгенерировать кастом`: prepare deterministic remix variants based on the
      selected meme reference and the same visual brief.
  - Keep `Сгенерировать` and `Найти мем` on the existing one-step variant review flow.
  - Store the selected meme reference in `PostVisual` using existing compatibility
    reference fields where possible; add a small explicit field only if needed.
  - Approval for `memeRemix` is allowed only after a remix variant is selected, not
    after selecting the meme reference.
  - Add clear bottom-left actions: `Выбрать мем`, `Сгенерировать кастом`,
    `Выбрать вариант`, `Утвердить визуал`, `Править бриф`, `Вернуться к драфту`.
  - Store `memeReferences`, `selectedMemeReferenceId`, and `memeReferenceBatch` in
    `PostVisual` alongside final remix variants and selection.
- Out of scope:
  - Real meme search.
  - Real image generation or transformation.
  - Uploading user images.
  - Changing readiness rules or `readyForRelease`.
- Architecture impact:
  - Keep the two-step state in visual domain/application transitions, not in React-only
    state.
  - Avoid expanding `EditorialVisualStage` into a god component; extract meme-remix
    step UI if the branch grows.
  - Existing visual variants service can be extended with a separate deterministic
    reference batch and remix batch.
- Tests:
  - Domain/application tests for selecting a meme reference before remix generation.
    Done.
  - Domain/application tests that `memeRemix` cannot approve after reference selection
    alone. Done.
  - UI tests for reference cards, selected reference, remix variant cards, and approval
    only after remix selection. Done.
  - Regression: `npm run test:architecture`, `npm test -- --run`, `npm run smoke`,
    `npm run test:design`, `npm run test:visual`.
- Docs:
  - Update roadmap, SAO, user guide, demo docs, and wiki production flow to state that
    `Мем + генерация` is two-step.
- Acceptance criteria:
  - `Мем + генерация` first shows meme/reference options.
  - After choosing a reference, the user can generate custom remix variants.
  - Visual approval requires a selected custom remix variant.
  - Other visual modes keep their existing behavior.
- Completed: 2026-06-18

### Slice 1.10.6.3: App Flow Test Ownership Guardrails

- Status: Done
- Goal: Stop `src/App.test.tsx` from becoming a second god file and move app-flow
  regression coverage beside feature owners.
- User value: Future slices can add tests without turning one large regression file
  into an unreviewable bottleneck.
- Scope:
  - Keep `src/App.test.tsx` shell/navigation-only.
  - Move feature app-flow scenarios into feature-owned `*AppFlow.test.tsx` files for
    signals, author memory, editorial model, context chat, plan, editing, release, and
    analytics.
  - Add small `src/test-support` flow drivers for repeated navigation/setup only.
  - Add ADR and SAO rules for test ownership.
  - Update `.agents/skills` so future slices choose the correct test owner.
  - Lower the architecture smoke limit for `App.test.tsx` and add test-file baselines.
- Out of scope:
  - Rewriting test assertions or changing product behavior.
  - Splitting existing large domain/storage/component tests beyond adding guardrails.
- Architecture impact:
  - Test ownership now mirrors production ownership.
  - `src/test-support` is a helper layer, not a page-object or hidden business-logic
    layer.
  - `npm run test:architecture` enforces test file limits and prevents feature-flow
    helpers in `App.test.tsx`.
- Tests:
  - Feature app-flow tests preserve the existing 38 App-level scenarios. Done.
  - Architecture smoke verifies the new test ownership baselines. Done.
- Docs:
  - Added ADR `2026-06-18-app-flow-tests-follow-feature-ownership.md`.
  - Updated SAO, developer guide, and agent skills.
- Acceptance criteria:
  - `src/App.test.tsx` is under the new shell-only limit.
  - Feature user-flow tests live beside their owning feature.
  - Future additions to near-limit test files are blocked by workflow and smoke
    guardrails.
- Completed: 2026-06-18

### Slice 1.10.7: Ready Post Handoff

- Status: Done
- Goal: Define when an editorial work item becomes `readyForRelease`.
- User value: The author sees a clear finish line in `Редактура`: text is approved and
  visual decision is complete.
- Scope:
  - Mark a post `readyForRelease` when text is approved and either visual is approved
    or `без визуала` is selected.
  - Introduce the future `ReadyPost` projection for release-log consumption.
  - Show ready state in `Редактура -> Посты` and `Рабочий стол`.
  - Keep `Выпуск` passive: it reads ready posts later, but does not edit them.
- Out of scope:
  - Publication attempts.
  - Platform integrations.
  - Analytics ingestion.
- Architecture impact:
  - `ReadyPost` is a handoff projection from editing to release delivery.
  - `ReleasePackage` remains compatibility/manual-export state until Slice 1.11
    replaces it with release log entries.
- Tests:
  - Domain/application tests for ready-state rules.
  - UI tests for ready badges and no-visual readiness.
- Acceptance criteria:
  - Ready status requires text approval and visual completion.
  - Ready posts can be listed as candidates for future release logging.
- Completed: unknown

### Slice 1.11: Release Log Foundation

- Status: Backlog
- Goal: Turn `Выпуск` into a publication log for ready and published posts, not an
  editorial workbench.
- User value: After content is approved in `Редактура`, `Выпуск` shows delivery state:
  what is ready, what was attempted, what was published, and what failed.
- Scope:
  - Add a release log list for `ReadyPost` / publication attempts.
  - Track publication status, platform, scheduled/published time, external link, adapter
    status, error message, and retry notes.
  - Add filters/search/grouping by platform, publication status, date, and topic.
  - Keep any existing `ReleasePackage` UI as compatibility/manual-export surface only
    until it is replaced by log entries.
  - Prepare the boundary for future `PublicationAdapter` integrations.
- Out of scope:
  - Editing text or visual.
  - Release checklist as content-preparation workflow.
  - Real platform APIs, autoposting, or external calendar integrations.
- Implementation notes:
  - `Выпуск` consumes ready posts and publication attempts.
  - Publication attempts create `PublicationLogEntry` records; they do not mutate
    production text or visual artifacts.
- Architecture impact:
  - `Редактура` owns preparation: fabula, draft, visual, and ready state.
  - `Выпуск` owns delivery: attempts, statuses, external links, and platform errors.
  - `ReleasePackage` is compatibility/manual-export state and should not become the
    future source of truth.
- Tests:
  - Ready posts appear in release log without exposing editing actions.
  - Publication log entries track status/link/error independently of editorial content.
  - UI shows a log/list first and no text/visual editing workbench.
- Docs:
  - Update user guide, demo docs, wiki, SAO, and ADR references.
- Acceptance criteria:
  - `Выпуск` is described and implemented as a release log foundation.
  - Text and visual changes are only done in `Редактура`.
  - Manual export is clearly compatibility behavior until platform adapters exist.

### Slice 1.12: Calendar View for Broadcast Plan

- Status: Backlog
- Goal: Add a broader calendar view that shows readiness across planning, editing,
  release, and analytics after production work items exist.
- User value: The author can see upcoming risk, ready posts, published posts, and
  where attention is needed across the whole production system.
- Scope:
  - Add calendar readiness statuses derived from plan slots and editorial work items:
    empty, waiting for signal approval, has candidates, concept approved, in editing,
    final approved, release ready, exported, and at risk.
  - Support week/month/quarter/year zoom levels if the UI remains readable.
  - Click a day/slot to open a detail panel below the calendar.
  - Detail panel links to signals, candidates, editing work item, release package, or
    analytics depending on status.
  - Preserve current list/grid views as operational views.
- Out of scope:
  - Real platform publication links beyond manual/demo URLs.
  - External calendar integrations.
  - Real-time collaboration.
- Implementation notes:
  - This slice should happen after editorial/release queues so readiness reflects real
    work-item state instead of singleton artifacts.
- Tests:
  - UI tests for zoom levels, status rendering, slot detail panel, and navigation.
  - Visual smoke tests for month and week layouts at desktop/laptop/mobile widths.
  - Regression for downstream production flow.
- Docs:
  - Update user guide, wiki screenshots, demo docs, and architecture overview.
- Demo impact:
  - Demo should show a near-future slot needing attention, one post in editing, and
    one release-ready or exported post.
- Acceptance criteria:
  - Calendar clearly shows what is ready and what needs intervention.
  - Clicking a slot explains the next action.
  - Existing production flow remains reachable.
- Risks:
  - Calendar UI can easily become too dense; start with compact badges and a detail
    panel.

### Slice 1.13: Archive and Uniqueness Baseline

- Status: Backlog
- Goal: Treat released and imported posts as author memory, signal material, and
  uniqueness context.
- Scope:
  - Add stronger archive records for released and imported posts.
  - Link archive posts to author-position evidence when explicitly accepted.
  - Let archive records become signal sources.
  - Add deterministic uniqueness checks against archive titles/body snippets.

### Slice 2.0: Backend AI Execution Architecture Baseline

- Status: Done
- Goal: Start the backend track as a disciplined AI execution layer with OpenRouter as
  the default provider target.
- User value: The project can move from deterministic placeholders toward real LLM
  behavior without exposing provider keys in the browser or creating a backend
  monolith.
- Scope:
  - Add `.env.example` and local `.env` variables for frontend/backend bridge,
    backend server settings, persistence, OpenRouter, and
    `langgraph-document-ai-platform`.
  - Add ADR for backend responsibility, OpenRouter default, and provider/library
    boundaries.
  - Update SAO, developer guide, and agent skills with backend OOP/SRP rules.
  - Extend architecture smoke so backend env/ADR/SAO guardrails are checked before
    backend code appears.
- Out of scope:
  - Creating runtime backend code.
  - Calling OpenRouter.
  - Installing backend dependencies.
  - Persisting workspace state on the server.
- Architecture impact:
  - Backend starts as an AI execution layer, not a full workspace replacement.
  - Domain objects remain provider-free.
  - API handlers must stay thin; application services own use cases; infrastructure
    adapters own OpenRouter, persistence, queue, and document-AI calls.
  - New backend files must stay small and role-owned; no 2-3k line modules, no god
    services, and no boilerplate-only packages.
- Tests:
  - `npm run test:architecture` checks the env/ADR/SAO backend guardrails.
- Acceptance criteria:
  - OpenRouter env variables are documented.
  - `.env` exists locally for developer tokens but is ignored by Git.
  - Backend architecture rules are present in ADR/SAO/agent workflow docs.
- Completed: 2026-06-18

### Slice 2.1: Backend Foundation and OpenRouter Environment

- Status: Done
- Goal: Add the first thin backend service with environment validation and a health
  surface.
- User value: The team can run a real backend process and verify OpenRouter
  configuration before wiring product flows to AI.
- Scope:
  - Add a minimal Python/FastAPI backend under `backend/`.
  - Add typed settings loaded from environment variables documented in `.env.example`.
  - Add `/health` and `/api/health` endpoints with provider configuration status that
    does not reveal secrets.
  - Add a small OpenRouter configuration validator; do not call the provider yet.
  - Add backend test command and architecture smoke baselines for backend files.
  - Update developer setup docs with backend run/test commands.
- Out of scope:
  - Real LLM calls.
  - Database migrations beyond optional local configuration validation.
  - Workspace sync, auth, queues, or publication adapters.
- Architecture impact:
  - Backend code follows `backend/app/api`, `backend/app/domain`,
    `backend/app/application`, and `backend/app/infrastructure`.
  - API modules contain routing only.
  - Application services own use cases.
  - Infrastructure adapters own env/provider edges.
  - Architecture smoke must add backend file-size and forbidden-import checks in this
    slice.
- Tests:
  - Backend unit tests for settings normalization and health response. Done.
  - Architecture smoke for backend ownership and env contract. Done.
  - Existing frontend regression remains green. Done.
- Acceptance criteria:
  - Backend starts locally. Done.
  - Missing OpenRouter token is reported as unconfigured, not as a crash. Done.
  - No provider call happens in Slice 2.1. Done.
- Completed: 2026-06-18

### Slice 2.2: AI Run Contract and Audit Trail

- Status: Done
- Goal: Add a backend-side AI run model before the first provider call.
- Scope:
  - Define provider-agnostic `AiRun` with capability, status, provider/model,
    sanitized request payload, result payload, error, fallback flag, and timestamps.
    Done.
  - Add local durable SQLite audit store using stdlib `sqlite3`, defaulting to
    `var/glavred-ai-runs.sqlite3`. Done.
  - Add application service and repository boundary for create/read/list audit
    records. Done.
  - Add `/api/ai-runs` create/read/list endpoints without provider execution. Done.
  - Extend `/api/health` with secret-safe AI run audit readiness. Done.
  - Keep prompt templates and provider adapters outside API handlers. Done.
- Out of scope:
  - Calling OpenRouter.
  - Running prompts or generating drafts/visuals.
  - Frontend integration, workspace sync, auth, queue, or migrations.
- Architecture impact:
  - `backend/app/domain/ai_run.py` owns provider-free AI run types.
  - `backend/app/application/ai_run_service.py` owns audit use cases and secret
    redaction.
  - `backend/app/infrastructure/sqlite_ai_run_repository.py` owns SQLite schema and
    persistence.
  - `backend/app/api/ai_runs.py` stays a thin HTTP mapping layer.
- Tests:
  - Backend API/repository tests for schema creation, create/read/list, filtering,
    404, redaction, and health response. Done.
  - Architecture smoke backend baselines and forbidden-import checks. Done.
  - Existing frontend regression remains green. Done.
- Acceptance criteria:
  - Audit records are durable in SQLite. Done.
  - API responses do not expose OpenRouter token or absolute DB path. Done.
  - Slice 2.2 does not call any provider. Done.
- Completed: 2026-06-18

### Slice 2.3: First OpenRouter Draft Run

- Status: Done
- Goal: Replace one deterministic draft-generation path with an OpenRouter-backed run
  behind the backend application boundary.
- Scope:
  - Build draft request from approved `PostBrief`, author/editorial context, and HITL
    constraints. Done.
  - Call OpenRouter through an infrastructure adapter. Done.
  - Normalize result into the existing `PostDraft` shape. Done.
  - Fall back to deterministic drafting on missing config, provider error, or invalid
    result. Done.
  - Connect `Утвердить фабулу` to the backend draft endpoint with a local emergency
    fallback when the backend is unreachable. Done.
  - Record every backend draft generation as an `AiRun`. Done.
- Out of scope:
  - Streaming, retries, queues, auth, workspace backend persistence, prompt management
    UI, and frontend AI-run history.
- Architecture impact:
  - `backend/app/api/drafts.py` stays a thin HTTP mapping layer.
  - `backend/app/application/draft_generation_service.py` owns provider/fallback
    orchestration and audit creation.
  - `backend/app/infrastructure/openrouter_draft_adapter.py` owns OpenRouter HTTP.
  - `src/infrastructure/backendDraftClient.ts` is the only frontend HTTP mapper for
    draft generation.
- Tests:
  - Backend route tests cover OpenRouter success, missing config fallback, provider
    error fallback, audit visibility, and secret safety. Done.
  - Frontend client/action tests cover backend request mapping and workspace sync for
    generated drafts. Done.
  - Architecture smoke covers new backend/frontend bridge modules. Done.
- Acceptance criteria:
  - `POST /api/drafts/generate` returns a `PostDraft` and `AiRun`. Done.
  - `Утвердить фабулу` can use backend/OpenRouter without exposing provider keys in the
    browser. Done.
  - Local deterministic drafting remains the emergency fallback when backend is
    unreachable. Done.
- Completed: 2026-06-18

### Slice 2.3.1: Dockerized Local Full-Stack Runner

- Status: Done
- Goal: Make the current frontend + backend stack build and run with one Docker
  Compose command.
- Scope:
  - Add backend and frontend Dockerfiles. Done.
  - Add `compose.yaml` that starts FastAPI and Vite together. Done.
  - Keep `.env` as runtime-only local configuration and exclude secrets from Docker
    build context. Done.
  - Mount `./var` for local SQLite AI run audit state. Done.
  - Add backend CORS settings so the Dockerized frontend can call the backend. Done.
- Out of scope:
  - Postgres, Redis, workers, queues, auth, production deployment, and reverse proxy.
- Architecture impact:
  - Docker is an execution wrapper, not a new ownership layer.
  - Backend API/application/domain/infrastructure boundaries remain unchanged.
  - Future DB/queue services should be added to Compose as separate infrastructure
    services behind explicit backend adapters.
- Tests:
  - Backend CORS contract test. Done.
  - Architecture smoke requires Docker local-stack files. Done.
- Acceptance criteria:
  - `docker compose up --build` is the documented full-stack startup command. Done.
  - Dockerized frontend runs at `http://localhost:5176`; backend remains at
    `http://localhost:8000`. Done.
- Completed: 2026-06-18

### Slice 2.3.2: AI Run Observability and Draft Generation Status

- Status: Done
- Goal: Make draft generation diagnosable in backend audit records and understandable
  in the editorial UI while keeping workspace state local-first.
- Scope:
  - Store full local sanitized draft-generation trace in `AiRun.requestPayload`:
    capability input, prompt messages, provider request summary, model,
    temperature, and response format. Done.
  - Store full generated draft body and provider/fallback metadata in
    `AiRun.resultPayload`. Done.
  - Keep secrets, authorization headers, API keys, and absolute local paths out of
    audit responses. Done.
  - Add lightweight `PostDraft.generation` metadata in frontend workspace state:
    source, `AiRun` id, provider, model, fallback flag, timestamp, and optional
    error. Done.
  - Show draft-generation pending state immediately after `Утвердить фабулу` and
    block duplicate clicks while the backend run is pending. Done.
  - Show trace summary in `Драфт` and the `Рабочий стол` side panel, including
    OpenRouter success, backend fallback, or local emergency fallback. Done.
- Out of scope:
  - Streaming, queueing, retries, prompt management UI, AI-run history UI, workspace
    backend persistence, and LangGraph integration.
- Architecture impact:
  - Prompt construction and audit payload assembly live in application modules, not
    API handlers or infrastructure adapters.
  - OpenRouter adapter returns provider metadata and receives already-built prompt
    messages for auditability.
  - Frontend stores only trace summary and `AiRun` id; the full prompt/body trace
    stays in local SQLite audit storage.
- Tests:
  - Backend tests cover OpenRouter success trace, fallback trace, full draft body,
    provider metadata, and secret redaction. Done.
  - Frontend tests cover generation pending UI, duplicate-click blocking, backend
    trace metadata, backend fallback metadata, and local emergency fallback. Done.
- Acceptance criteria:
  - `GET /api/ai-runs/{id}` returns enough trace to answer what prompt/messages were
    sent, what provider returned, and whether fallback was used. Done.
  - After `Утвердить фабулу`, the user sees generation progress instead of an empty
    draft screen. Done.
- Completed: 2026-06-18

### Slice 2.3.3: AI Run Trace Debug Page

- Status: Done
- Goal: Add a separate frontend debug page for inspecting one backend `AiRun` trace by
  run id without adding another surface to the main editorial cabinet.
- Scope:
  - Add `/ai-runs` as an out-of-cabinet debug route. Done.
  - Add a run-id input and `GET /api/ai-runs/{id}` client. Done.
  - Render run summary, request payload, result payload, fallback flag, provider/model,
    and safe error context using the existing visual language. Done.
  - Support `?runId=<id>` as a direct link format for debugging. Done.
- Out of scope:
  - AI run history list UI, search by capability, deletion, retention controls,
    workspace sync, or provider replay.
- Architecture impact:
  - Debug UI stays in `src/features/ai-runs`.
  - Backend trace fetch lives in a dedicated infrastructure client instead of expanding
    the near-limit draft-generation client.
  - The page is intentionally not part of the main cabinet navigation.
- Tests:
  - Frontend client test covers successful fetch and missing run error. Done.
  - Feature test covers run-id lookup, rendered request/result JSON, error state, and
    `/ai-runs` route isolation from the cabinet. Done.
- Acceptance criteria:
  - A developer can open `/ai-runs`, paste an `AiRun ID`, and see the detailed local
    trace. Done.
- Completed: 2026-06-18

### Slice 2.3.4: Agentic Draft Runner Architecture Plan

- Status: Done
- Goal: Replace the "one request, one draft" drafting direction with a queued,
  traceable multi-step agent runner architecture before implementation starts.
- Scope:
  - Define `DraftRun` as the long-running orchestration record above individual
    provider `AiRun` calls. Done.
  - Document the target pipeline: context build, rule-pack compilation, material
    plan, draft strategy, candidate drafts, validators, revision loop, and result
    selection. Done.
  - Confirm that topic, fabula, signal, post candidate, publisher rules, and approved
    brief context cannot be flattened into one prompt. Done.
  - Move the next backend priority from document import to queued draft execution.
    Done.
- Out of scope:
  - Runtime queue implementation.
  - Real multi-step LLM orchestration.
  - Frontend status UI changes beyond roadmap/docs.
- Architecture impact:
  - `DraftRun` owns orchestration state; `AiRun` remains a provider-call audit record.
  - Celery/Redis become the preferred local queue/worker direction for long drafting
    runs.
  - Validators and rule packs are first-class application/domain concepts, not prompt
    text hidden inside one request.
- Tests:
  - `npm run test:architecture` for docs/architecture guardrails.
- Acceptance criteria:
  - Roadmap, SAO, developer docs, and ADR agree that the next implementation slice is
    queued `DraftRun`, not a bigger synchronous prompt. Done.
- Completed: 2026-06-19

### Slice 2.4: Draft Run Contract and Queue Foundation

- Status: Done
- Goal: Introduce the first durable queued drafting runner without real complex LLM
  reasoning yet.
- User value: After approving a fabula, the author sees a real long-running drafting
  job with status, steps, and trace instead of a synchronous black-box request.
- Scope:
  - Add Redis and Celery to the local Docker stack. Done.
  - Add provider-free `DraftRun`, `DraftRunStep`, and `DraftRunStatus` domain
    contracts. Done.
  - Add SQLite persistence for draft runs and steps in
    `var/glavred-draft-runs.sqlite3`. Done.
  - Add `POST /api/draft-runs`, `GET /api/draft-runs/{id}`, and
    `GET /api/draft-runs/{id}/events` polling read-model. Done.
  - Add a Celery task that executes a deterministic placeholder pipeline:
    build context -> compile rule pack -> create material plan -> create draft
    strategy -> generate deterministic draft -> validate -> complete. Done.
  - Keep existing `POST /api/drafts/generate` as compatibility fallback during the
    transition. Done.
  - Update frontend `Утвердить фабулу` to start a draft run and show queued/running
    status before draft completion. Done.
- Out of scope:
  - Real OpenRouter multi-step reasoning.
  - Real search/retrieval.
  - LangGraph integration.
  - Multi-candidate draft review.
  - Full workspace backend persistence.
- Implementation notes:
  - API handlers remain thin.
  - Application services own run creation, task dispatch, and state transitions.
  - Infrastructure owns Celery, Redis, persistence adapters, and provider calls.
  - Domain stays provider-free, queue-free, and persistence-free.
- Architecture impact:
  - This slice creates the backend execution model for all future long AI workflows.
  - `DraftRun` is the parent orchestration trace; individual LLM/provider calls inside
    it will create child `AiRun` records in later slices.
  - Architecture smoke adds backend baselines and forbidden-import checks for queue
    modules. Done.
- Tests:
  - Backend tests for creating a queued run, worker task step transitions, completed
    deterministic draft, and dispatch failure. Done.
  - Frontend tests for pending/running/completed states after approving a fabula. Done.
  - `npm run test:backend`, `npm run test:architecture`, `npm test -- --run`,
    `npm run smoke`, and `docker compose config --quiet`. Done.
- Docs:
  - Update SAO, developer guide, README, and demo docs with draft-run startup and
    debugging instructions. Done.
- Demo impact:
  - Demo shows a queued draft run progressing through named steps. Done.
- Acceptance criteria:
  - A draft run can be started, tracked, completed, and inspected locally. Done.
  - The UI no longer treats drafting as a single synchronous provider request. Done.
  - Existing emergency fallback remains available if backend/worker is unavailable. Done.
- Risks:
  - Introducing queue infrastructure can create boilerplate; keep modules role-owned
    and small.
  - Worker state and frontend polling can drift; keep status contracts explicit.
- Completed: 2026-06-19

### Slice 2.5: Draft Run Context Builder

- Status: Done
- Goal: Build the full draft-run context from the selected editorial work item.
- Scope:
  - Include approved brief, plan slot, post candidate, source signal, topic, fabula,
    publisher rules, and available author-position evidence.
  - Expose context summary in draft-run trace.
  - Do not mutate workspace state from context building.
- Architecture impact:
  - Context builder is an application service with provider-free DTOs.
  - `PostBrief` must not absorb candidate/slot/source fields.
- Done:
  - Frontend builds a read-only `draftContext` snapshot from the selected work item
    and sends it to `POST /api/draft-runs`.
  - Backend persists `draftContext` in the durable `DraftRun.requestPayload`.
  - Worker `context` step writes a normalized summary with work item, plan slot,
    candidate, source signal, topic, fabula, publisher rules, author-position
    evidence, and `missingContext`.
  - Old brief/editorial-model-only requests remain compatible.
- Completed: 2026-06-19

### Slice 2.6: Draft Rule Pack Compiler

- Status: Done
- Goal: Compile publisher, topic, fabula, signal, and brief constraints into explicit
  rule packs before generation.
- Scope:
  - Produce hard constraints, soft constraints, evidence requirements, dramaturgy
    requirements, topic-fit requirements, and quality rubric.
  - Record rule-pack artifacts in draft-run trace.
  - Keep validators separate from prompt builders.
- Architecture impact:
  - RulePack domain DTOs stay provider-free and persistence-free.
  - Rule-pack compilation is isolated in role-owned application modules, not added
    to near-limit context, pipeline, run-domain, or SQLite repository files.
- Done:
  - Added provider-free `RulePack`, `RulePackRule`, and `RulePackRequirement`.
  - Added deterministic compilation from normalized context summary to
    hard/soft constraints, evidence requirements, dramaturgy requirements,
    topic-fit requirements, quality rubric, and forbidden moves.
  - Worker `rulePack` step now writes the compiled artifact to draft-run trace.
  - Brief-only compatibility runs still receive a minimal rule pack.
- Completed: 2026-06-19

### Slice 2.7: Material Plan and Draft Strategy Steps

- Status: Done
- Goal: Add the first LLM-assisted planning steps before draft generation.
- Scope:
  - Generate a material plan from context and rule pack.
  - Generate a draft strategy from material plan and fabula/topic rules.
  - Store both as draft-run artifacts with child `AiRun` records.
  - Fall back to deterministic planning if OpenRouter is unavailable.
- Architecture impact:
  - Material planning and strategy are application services with provider calls
    behind infrastructure adapters and child `AiRun` audit records.
  - `draft_run_pipeline.py` remains a coordinator; provider calls and prompt
    builders stay in role-owned modules.
- Done:
  - Worker `materialPlan` and `strategy` steps now call OpenRouter when configured
    and deterministic fallback otherwise.
  - Step artifacts include `source`, `aiRunId`, `fallbackUsed`, `error?`, and the
    full material-plan or draft-strategy payload.
  - `DraftRun.ai_run_ids` records child planning `AiRun` ids for trace inspection.
  - Final prose generation remained deterministic until Slice 2.8.
- Completed: 2026-06-19

### Slice 2.8: Agentic Multi-Candidate Draft Generation

- Status: Done
- Goal: Generate and compare several draft candidates instead of one draft.
- Scope:
  - Generate 2-3 draft candidates from strategy, rule pack, material plan, and
    context.
  - Store candidate title/body/rationale/evidence/risk plus child `AiRun` ids in
    `steps[4].artifactPayload`.
  - Select the best candidate with deterministic v1 scorecard while preserving
    alternatives for debug and future UI review.
  - Keep `DraftRun.finalDraft` frontend-compatible by returning the selected
    candidate only.
  - Completed 2026-06-19.
- Completed: 2026-06-19

### Slice 2.8.1: AI Run Trace Workbench

- Status: Done
- Goal: Turn `/ai-runs` from a raw JSON page into a usable trace analysis workbench.
- Scope:
  - Keep `/ai-runs` outside the main cabinet navigation, but render it with the same
    design-system rhythm and cabinet spacing.
  - Add a compact run lookup header, summary metrics, and provider/fallback/status
    cards.
  - Parse known trace payloads into semantic sections: draft step, provider request,
    prompt messages, candidate/material/strategy result, provider metadata, fallback
    context, and raw JSON.
  - Show prompt messages as a searchable/filterable message list with role badges and
    a readable selected-message panel.
  - Wrap JSON in readable, copyable, line-wrapped panels; raw JSON remains available
    but is not the primary analysis surface.
  - Do not add backend endpoints; use `GET /api/ai-runs/{id}` as the source of truth.
  - Completed 2026-06-19.
- Completed: 2026-06-19

### Slice 2.8.1.1: Draft Run Trace Timeline and Trace UI Repair

- Status: Done
- Goal: Make `/ai-runs` analyze a full queued `DraftRun`, not only one child
  OpenRouter call.
- Scope:
  - Accept either a parent `DraftRun ID` or a single `AiRun ID`.
  - Try `GET /api/draft-runs/{id}` first; only after `404`, fall back to
    `GET /api/ai-runs/{id}`.
  - For parent runs, load all child `AiRun` records and render the logical runner
    timeline: `context -> rulePack -> materialPlan -> strategy -> draft ->
    validation -> complete`.
  - Show child LLM calls inside their logical step with provider, model, status,
    fallback flag, and `AiRun ID`.
  - Move semantic artifacts into a canonical `Смысловой результат` tab.
  - Replace custom trace tabs with canonical `.tabs .tab`, repair spacing, and add
    design/visual smoke coverage for `/ai-runs`.
  - Completed 2026-06-19.
- Completed: 2026-06-19

### Slice 2.9: Source Ledger Foundation

- Status: Done
- Goal: Add the source-ledger layer before validators and revision.
- User value: Glavred starts tracking which claims are grounded, allowed, risky, or
  forbidden before it writes or judges a post.
- Scope:
  - Add provider-free `SourceLedger`, `SourceLedgerClaim`, and
    `ForbiddenInference` DTOs.
  - Build a DraftRun-local ledger from approved brief, post candidate, source signal,
    author correction, candidate evidence, risks, and author-position evidence.
  - Store the ledger inside `steps[0].artifactPayload.sourceLedger` without adding a
    new `DraftRunStepKey` or SQLite migration. Done.
  - Include provenance ids, confidence, allowed-use notes, risky claims, and missing
    source warnings.
  - Keep old brief-only runs compatible with a minimal ledger and explicit warnings.
- Out of scope:
  - Real web search or archive retrieval.
  - Claim-level UI in the main workbench.
  - Validator scoring or revision.
- Implementation notes:
  - Do not expand near-limit context builder or pipeline files; add role-owned ledger
    domain/application modules. Done.
  - `SourceLedger` is not a replacement for `SourceSignal`; it is a drafting artifact
    that says what can safely be used.
- Architecture impact:
  - Enforces ADR `2026-06-20-drafting-quality-requires-source-ledger-and-post-contract`.
  - Future validators must consume ledger claims instead of inferring provenance from
    final draft text.
- Tests:
  - Ledger builder extracts claims and risks from full context.
  - Missing source/candidate data creates warnings instead of failing the run.
  - Brief-only compatibility run creates a minimal ledger.
  - `npm run test:backend`, `npm run test:architecture`, `npm test -- --run`,
    `npm run smoke`, `docker compose config --quiet`.
- Docs:
  - Update SAO, developer guide, user/demo/wiki notes, and roadmap.
- Demo impact:
  - Demo DraftRun trace shows claim/provenance inventory before draft writing.
- Acceptance criteria:
  - A developer can inspect a DraftRun and see source claims, allowed use, risks, and
    forbidden inferences. Done.
  - No validator/revision behavior is added yet. Done.
  - Completed 2026-06-20.
- Risks:
  - Claim extraction can become over-complicated; keep v1 deterministic and traceable.
- Completed: 2026-06-20

### Slice 2.10: Feasibility Gate and Post Contract

- Status: Done
- Goal: Decide whether the approved post can be written safely and lock the editorial
  contract before prose generation.
- User value: Weak or under-sourced posts stop with a clear reason instead of producing
  a confident but unsafe draft.
- Scope:
  - Add `FeasibilityReport` with statuses `feasible`, `feasible_with_constraints`,
    `needs_research`, `needs_human_decision`, and `infeasible`.
  - Add `PostContract` with locked thesis, audience value, CTA, allowed claims,
    forbidden moves, platform constraints, and fabula obligations.
  - Store both artifacts in DraftRun trace.
  - If the run is not feasible, return a readable blocked state instead of silently
    generating a weak draft.
- Architecture impact:
  - `PostContract` becomes the invariant consumed by strategies, candidates,
    validators, and revisions.
  - `PostBrief` remains editable fabula content and must not absorb contract/ledger
    fields.
- Tests:
  - Feasible full context proceeds.
  - Missing evidence produces constrained or needs-human status.
  - Infeasible context does not generate a final draft.
- Done:
  - Added `feasibility` and `postContract` DraftRun logical steps before `rulePack`.
  - Added deterministic feasibility gate over `SourceLedger` claims, warnings, risks,
    and forbidden inferences.
  - Added `PostContract` artifact for safe runs and `postContract: notCreated` for
    blocked runs.
  - Quality-blocked runs finish as `DraftRun.status=succeeded` with `finalDraft=null`
    and `complete.status=blocked`, so frontend shows a blocked state instead of using
    compatibility/local fallback.
  - `/ai-runs` semantic trace now reads feasibility and contract artifacts.
  - Completed 2026-06-20.
- Completed: 2026-06-20

### Slice 2.10.1: DraftRun Candidate Link Recovery and Feasibility Calibration

- Status: Done
- Goal: Fix a false quality block when an approved plan slot has source/topic/fabula
  evidence but the editorial work item lost `postCandidateId`.
- User value: The author does not get a confusing "stopped before generation" result
  when Glavred can safely recover or proceed from the approved source context.
- Scope:
  - Recover linked post candidates during plan-slot approval and DraftRun context
    building.
  - Avoid guessing when several approved candidates match the same signal.
  - Calibrate feasibility so `missing-candidate` is constrained, not blocking, when
    source signal evidence, brief evidence, topic, and fabula are present.
  - Keep hard blocking for missing/ambiguous candidate links when evidence is not
    strong enough.
- Architecture impact:
  - Candidate linking lives in a role-owned frontend application helper shared by
    plan approval and DraftRun context.
  - Feasibility evidence checks live in a backend policy helper instead of expanding
    the near-limit feasibility gate.
- Tests:
  - Candidate recovery by `postCandidateId`, by source/topic/fabula, and ambiguous
    source-only matches.
  - Plan-slot approval persists recovered `postCandidateId`.
  - Feasibility proceeds with constraints when candidate is missing but source/brief
    evidence is available.
  - Pipeline continues to draft for the recovered/constrained case and still blocks
    genuinely weak context.
- Done:
  - Diagnosed `DraftRun d5d17b60-a711-485f-923e-91a93f263f12`: it stopped because
    `candidate=null` while source signal, topic, fabula, and evidence were present.
  - Added shared candidate-link recovery and adjusted feasibility policy.
  - Completed 2026-06-22.
- Completed: 2026-06-22

### Slice 2.11: Rule Registry v2 and Validator Bindings

- Status: Done
- Goal: Evolve the current rule pack into a machine-readable rule registry snapshot.
- Scope:
  - Add rule ids, scope, conditions, priority, severity, observable criteria,
    validator type, examples, and repair policy.
  - Compile a selected `RuleRegistrySnapshot` for each DraftRun.
  - Derive the existing `RulePack` from registry snapshot, source ledger, and post
    contract.
- Architecture impact:
  - Validators and directed revisions must reference rule ids instead of anonymous
    prose constraints.
- Done:
  - Added provider-free `RuleRegistrySnapshot`, `RuleRegistryRule`, and `RuleBinding`
    DTOs.
  - Added role-owned registry compiler modules and kept `RulePack` as a compatibility
    payload derived from the registry.
  - Stored `ruleRegistrySnapshot` inside the existing `rulePack` DraftRun step without
    changing step order or SQLite schema.
  - Updated `/ai-runs` semantic trace to show a readable Rule registry summary.
  - Completed 2026-06-22.
- Completed: 2026-06-22

### Slice 2.11.1: Publication Size Contract Foundation

- Status: Done
- Goal: Add an explicit publication-size contract without hard-linking fabulas to
  platforms.
- User value: Planning can express whether a post is a Telegram note, LinkedIn post,
  or article-sized artifact while keeping `Signal X Topic X Fabula` reusable.
- Scope:
  - Add editable publication size profiles to `ContentPlanSettings`.
  - Add optional `publicationSizeProfileId` to plan slots.
  - Add `Fabula.sizeIntent = compact | standard | deep` as dramaturgical scale, not
    platform binding.
  - Send publication-size context to queued `DraftRun`.
  - Resolve `PublicationSizeContract` inside `PostContract`.
  - Add deterministic size rules to `RuleRegistrySnapshot`.
- Architecture impact:
  - Size constraints live in `PostContract` / `RuleRegistry`, not in `PostCandidate`
    and not in platform-specific fabula forks.
  - Slot profile wins over plan default; plan default wins over platform demo default;
    fabula scale adjusts target range without crossing hard limits.
- Done:
  - Added frontend/domain publication size profiles and fabula scale intent.
  - Added plan settings UI for publication size profiles and fabula scale selector.
  - Added backend `PublicationSizeContract` resolver and registry size rules.
  - Added trace rendering for the size contract.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12: Contract-Based Rhetorical Plans

- Status: Done
- Goal: Generate several rhetorical plans from source ledger, post contract, rule pack,
  material plan, and fabula.
- Scope:
  - Replace the single strategy mental model with 2-3 plans such as research,
    contrast/polemic, and practical/checklist.
  - Store plans with planned moves, claims to use, claims to avoid, CTA route, and
    risks.
  - Draft candidates must consume one plan each.
- Done:
  - Added provider-free rhetorical plan DTOs and deterministic fallback plans.
  - Added OpenRouter-backed rhetorical planning step with child `AiRun` audit and
    fallback behavior.
  - Inserted `rhetoricalPlans` between `strategy` and `draft` without changing SQLite
    schema.
  - Linked every draft candidate to a `rhetoricalPlanId`.
  - Updated `/ai-runs` semantic trace to show rhetorical plans and candidate plan
    linkage.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12.1: DraftRun Stale Runner Recovery and Fallback Discipline

- Status: Done
- Goal: Stop live queued `DraftRun` records from being masked by the old
  compatibility draft endpoint when provider-backed steps take longer than the
  frontend polling timeout.
- Scope:
  - Mark long-running worker steps `running` before OpenRouter/application calls.
  - Persist child `AiRun` ids incrementally as each LLM/application step completes.
  - Add computed `isStale`, `staleReason`, and `lastProgressAt` fields to
    `GET /api/draft-runs/{id}` without changing SQLite schema.
  - Treat a live queued/running `DraftRun` as the primary source of truth in the
    frontend; do not call `/api/drafts/generate` merely because polling has taken a
    long time.
  - Show long-running/stale state, current step, DraftRun ID, and trace link in
    `Редактура -> Рабочий стол -> Драфт`.
  - Show `stale-running` state in `/ai-runs` timeline.
- Done:
  - Added step progress helper and stale inspector.
  - Added Celery task time limits and safe timeout failure handling.
  - Updated frontend polling discipline so live runs keep polling instead of falling
    back after timeout.
  - Added stale/last-progress UX in the draft generation screen and right panel.
  - Updated trace view-model to render stale-running state.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12.2: Draft Candidate Scoring and Selection Trace

- Status: Done
- Goal: Make the `draft` trace step readable as candidate generation, scoring, and
  final selection instead of one large JSON artifact.
- User value: A developer or operator can inspect a DraftRun and immediately see
  which draft candidates were generated, how each candidate scored, and why the
  selected draft won.
- Scope:
  - Add derived trace nodes inside the existing `draft` step for candidate artifacts,
    deterministic scorecard, and final selection.
  - Keep backend steps, API responses, and SQLite schema unchanged.
  - Show candidate details, rhetorical plan linkage, source/fallback, score, risks,
    weaknesses, and child `AiRun ID` in `/ai-runs`.
  - Show scorecard and selected-draft rationale as separate readable detail panels.
  - Keep raw JSON available as fallback, but make it secondary to the readable trace.
- Out of scope:
  - Manual candidate selection in the editor UI.
  - New backend `DraftRunStepKey` values.
  - Validator/revision loop behavior.
- Architecture impact:
  - `/ai-runs` may render derived read-model nodes for large step artifacts, but those
    nodes do not change durable backend step order.
  - Runtime orchestration remains `rhetoricalPlans -> draft -> validation`.
- Done:
  - Added feature-owned draft candidate trace read-model module.
  - Added derived `Кандидат`, `Скоринг кандидатов`, and `Выбор итогового драфта`
    nodes under the `draft` timeline step.
  - Added semantic sections for draft candidates, scorecard, and selected candidate.
  - Repaired nested trace row wrapping so provider/model/id values do not break layout.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12.2.1: Scorecard Trace Table Repair

- Status: Done
- Goal: Make the draft candidate scorecard readable as a comparison table instead of
  duplicated text rows in the generic detail renderer.
- User value: A developer or operator can inspect why one draft candidate won without
  parsing a long blob of `total/hard/evidence/topic/fabula/value/risk` text.
- Scope:
  - Keep backend API, DraftRun steps, and SQLite schema unchanged.
  - Render scorecard rows as a dedicated table in `/ai-runs`.
  - Show candidate title, compact candidate id, total score, criterion breakdown,
    risk penalty, and selected/winner state.
  - Remove duplicated score rows from the readable detail summary.
  - Preserve JSON/Raw tabs for audit fallback.
- Out of scope:
  - Changing candidate selection logic.
  - Adding manual candidate selection.
  - Adding a new durable scoring step.
- Architecture impact:
  - Scorecard tables are a frontend trace view-model projection of existing
    `draft.artifactPayload.selection.scorecard` data.
  - Runtime orchestration and persisted backend artifacts stay unchanged.
- Done:
  - Added typed scorecard semantic sections.
  - Added a dedicated scorecard comparison table renderer.
  - Updated trace tests so scorecard details are not rendered as `Rows` text blobs.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12.3: Source Intent and Research Plan

- Status: Done
- Goal: Normalize approved fabula `sources` into a typed source intent and build the
  first research plan before prose generation.
- User value: The author can tell Glavred which external sources or public proof
  should support the post, and the runner treats that as research work rather than as
  another prompt paragraph.
- Scope:
  - Add provider-free DTOs for `SourceIntent`, `SourceIntentItem`, and `ResearchPlan`.
  - Parse approved `PostBrief.sources` into URL seeds, search-query hints, required
    proof, optional proof, and framing-only sources.
  - Add a DraftRun artifact after context/source ledger that states what should be
    read, searched, verified, or avoided.
  - Show source intent and research plan in `/ai-runs` semantic trace.
  - Keep actual web retrieval/search out of this slice.
  - Add `Редактура -> Рабочий стол -> Фабула` source-intent preview while preserving
    `PostBrief.sources: string[]`.
- Out of scope:
  - Real internet search.
  - URL fetching.
  - Evidence extraction.
  - Validator/revision behavior.
- Architecture impact:
  - Approved fabula sources become typed drafting inputs, not raw prompt text.
  - `PostBrief` keeps its current shape; the new artifacts live in DraftRun
    application/domain modules and trace payloads.
  - API routes remain thin; no provider or web calls in React/domain/API handlers.
- Tests:
  - Source strings become deterministic source intent items. Done.
  - URL/search/framing/required proof cases are classified. Done.
  - Research plan survives missing or empty sources. Done.
  - DraftRun trace shows source intent and research plan. Done.
- Docs:
  - Update SAO/developer docs with `SourceIntent -> ResearchPlan`. Done.
- Demo impact:
  - Demo fabula sources can include one external proof hint, but no live web calls yet.
- Acceptance criteria:
  - `/ai-runs?runId=...` shows what the runner intends to research before writing.
    Done.
  - Draft generation still completes through existing fallback/provider paths. Done.
  - Completed 2026-06-23.
- Risks:
  - Source classification can be too heuristic; keep it conservative and visible in
    trace.
- Completed: 2026-06-23

### Slice 2.12.3.1: Fabula Research Strategy Defaults

- Status: Done
- Goal: Move source/research defaults from per-post editing into
  `Редакционная модель -> Фабулы`, while keeping `Редактура -> Фабула` as the final
  per-post override.
- User value: The author does not have to retype the same source strategy for every
  post, but can still override the exact research instructions before generation.
- Scope:
  - Add `Fabula.researchStrategy` with `auto` and `manual` modes.
  - Normalize legacy fabulas with auto research strategy defaults.
  - Add a research strategy editor to `Редакционная модель -> Фабулы`.
  - Seed new `PostBrief.sources` from fabula manual instructions or deterministic
    auto instructions based on topic, fabula, candidate, signal, and proof needs.
  - Keep `PostBrief.sources: string[]` as the approved runtime input for DraftRun.
  - Add trace diagnostics for source origin: `fabulaManual`, `fabulaAuto`,
    `userOverride`, or `empty`.
- Out of scope:
  - Real web search.
  - URL fetching.
  - Retrieval/extraction.
  - New DraftRun steps or SQLite schema changes.
- Architecture impact:
  - `Fabula.researchStrategy` is default policy.
  - `PostBrief.sources` is the concrete approved override for one post.
  - `SourceIntent` continues to consume only approved brief sources.
- Tests:
  - Legacy fabula normalization. Done.
  - Manual and auto research source seeding. Done.
  - Fabula editor mode/instructions behavior. Done.
  - DraftRun context and trace origin diagnostics. Done.
- Docs:
  - README, SAO, developer guide, user guide, demo docs, and research ADR updated.
    Done.
- Acceptance criteria:
  - Research defaults can be configured on a fabula. Done.
  - New work briefs receive manual or auto sources. Done.
  - The editor can override sources before DraftRun. Done.
  - Completed 2026-06-23.
- Completed: 2026-06-23

### Slice 2.12.4: Public Evidence Retrieval Foundation

- Status: Done
- Goal: Add the first retrieval/extraction foundation for approved source intent.
- User value: Glavred starts grounding drafts in public material instead of only the
  internal signal/fabula bundle.
- Scope:
  - Add provider-free `PublicEvidenceItem`.
  - Add infrastructure boundary for URL read/search adapters.
  - In v1, support real one-URL reads for explicit URL seeds and trace search tasks
    as `notConfigured` until a search provider is selected.
  - Store extraction results and failures in DraftRun trace.
  - Keep secrets and browser/provider details out of domain/API handlers.
- Out of scope:
  - Full crawler.
  - Full web search product UI.
  - Paid search provider selection UX.
  - Validators and directed revision.
- Architecture impact:
  - Public retrieval is infrastructure-owned; application services reconcile output.
  - External claims must carry provenance, confidence, allowed use, and extraction
    notes.
- Tests:
  - URL/search seeds create evidence items or safe extraction warnings.
  - Adapter failures are traceable and safe.
  - No generated draft treats failed retrieval as proof.
- Docs:
  - Update debug docs with public evidence trace reading.
- Demo impact:
  - Demo can show placeholder external evidence records in `/ai-runs`.
- Acceptance criteria:
  - Public evidence appears as structured trace data, not as hidden prompt context. Done.
- Validation:
  - Targeted backend and trace tests passed during implementation.
- Completed:
  - Completed 2026-06-24.
- Risks:
  - Placeholder retrieval must not pretend to be real proof; label source clearly.

### Slice 2.12.4.1: OpenRouter Web Search Adapter

- Status: Done
- Goal: Execute general public search tasks through OpenRouter server-tool web search
  before merging public evidence into the source ledger.
- User value: Source-intent requests such as "find opinion leaders" no longer stop at
  a `notConfigured` trace when backend web tools are explicitly enabled.
- Scope:
  - Add opt-in env settings for OpenRouter web tools:
    `OPENROUTER_WEB_TOOLS_ENABLED`, `OPENROUTER_WEB_SEARCH_MODEL`, and
    `OPENROUTER_WEB_SEARCH_MAX_RESULTS`.
  - Add infrastructure adapter for OpenRouter `openrouter:web_search` server tool.
  - Add application service that executes `findPublicSources` and `verifyClaim`
    tasks, records child `AiRun` audit, and converts returned citations into
    `PublicEvidenceItem` candidates.
  - Keep exact URL reading on the existing URL reader.
  - Keep disabled/missing-provider search as explicit `notConfigured` attempts.
- Out of scope:
  - SourceLedger merge.
  - Search provider UI.
  - Web crawling, browser automation, cache, retries, or cost controls beyond the
    explicit opt-in flag and max results.
- Architecture impact:
  - Provider HTTP/citation parsing lives in `backend/app/infrastructure`.
  - Search task orchestration and child `AiRun` creation live in
    `backend/app/application`.
  - Domain DTOs remain provider-free.
- Tests:
  - Disabled web tools produce `notConfigured` search attempts. Done.
  - Configured OpenRouter search creates evidence items and child `AiRun`. Done.
  - Provider errors create failed attempts and safe warnings. Done.
  - `/ai-runs` semantic trace shows search provider/model/child AiRun ids. Done.
- Docs:
  - README, SAO, developer guide, user guide, wiki, ADR, and `.env.example` updated.
    Done.
- Acceptance criteria:
  - With `OPENROUTER_WEB_TOOLS_ENABLED=true`, public search tasks create traceable
    child `AiRun` records and evidence candidates. Done.
- Completed:
  - Completed 2026-06-24.
- Risks:
  - OpenRouter server tools are beta; keep raw trace and safe disabled fallback.
  - Search citations are still evidence candidates, not merged ledger claims until
    Slice 2.12.5.

### Slice 2.12.4.2: Public Evidence Query and Relevance Repair

- Status: Done
- Goal: Repair public search query construction and reject irrelevant citations before
  external evidence can enter the source-ledger merge slice.
- User value: A source request such as "find opinion leaders" is searched as the real
  research instruction, not as an internal `target-1` id, and trace explains rejected
  search drift.
- Scope:
  - Add provider-free public evidence query builder.
  - Use `verificationTask.instruction` as the primary search query and preserve
    `target` as a technical link to source-target metadata.
  - Add deterministic relevance guard for OpenRouter citations.
  - Store `builtQuery`, original task, source target, exclusions, and rejected
    citations in `publicEvidence` attempts and child `AiRun` trace.
  - Update `/ai-runs` readable trace for accepted evidence and rejected citations.
- Out of scope:
  - SourceLedger merge, evidence synthesis, validators, and draft-scoring changes.
  - New search provider selection, caching, retries, or SQLite schema changes.
- Architecture impact:
  - Query construction and relevance filtering are role-owned application modules.
  - OpenRouter-specific provider calls remain in infrastructure/application adapter
    wiring; domain stays provider-free.
- Tests:
  - Search with `target: target-1` and a real instruction uses the instruction query.
  - Relevant citation creates a `PublicEvidenceItem`.
  - Irrelevant citation is rejected with `search-result-drift` and warning
    `search-no-relevant-evidence`.
  - Trace view model shows built query and rejected citations.
- Docs:
  - Update drafting docs to state planned search tasks are not proof until accepted by
    relevance filtering and later merged into `SourceLedger`.
- Demo impact:
  - `/ai-runs` can now demonstrate why a search result was accepted or rejected.
- Acceptance criteria:
  - OpenRouter web search no longer receives bare technical target ids as the query.
  - Public evidence trace distinguishes accepted evidence from rejected citations.
- Validation:
  - Targeted backend and trace tests passed during implementation.
- Completed:
  - Completed 2026-06-24.
- Risks:
  - Deterministic relevance v1 is conservative; good citations with little lexical
    overlap can be rejected and should be improved with synthesis in later slices.

### Slice 2.12.4.3: Draft Candidate Fallback Selection Guard

- Status: Done
- Goal: Prevent emergency deterministic fallback candidates from becoming the final
  draft when at least one provider-generated candidate is available.
- User value: A temporary provider failure in one branch no longer promotes a
  technical placeholder into the editor as if it were a publication-quality post.
- Scope:
  - Add selection guard metadata for candidate publishability.
  - Penalize or exclude `deterministicFallback` candidates when viable OpenRouter
    candidates exist.
  - Detect non-publishable candidate bodies containing raw artifact dumps, JSON/Python
    object fragments, mojibake, or explicit "needs provider rewrite" weaknesses.
  - Keep fallback candidates visible in `/ai-runs` as diagnostic artifacts, but mark
    them as skipped or heavily penalized for final selection.
  - Update scorecard trace to explain why a candidate was excluded or penalized.
- Out of scope:
  - SourceLedger external evidence merge.
  - Relevance synthesis, validators, directed revision, or provider retry policy.
  - New DraftRun steps or SQLite schema changes.
- Implementation notes:
  - This slice fixes the diagnosed run `096e4d74-7671-40ff-aedf-5d751678ffb2`,
    where an OpenRouter branch failed, deterministic fallback emitted raw internal
    evidence objects, and the selector still chose that fallback as the final draft.
  - The selector should prefer a lower-scoring provider candidate over a fallback
    placeholder unless all provider candidates are unavailable or invalid.
  - If all candidates are non-publishable, the run should complete with a clear
    blocked/failed drafting artifact rather than silently publishing a placeholder.
- Implementation result:
  - Added a provider-free publishability policy for draft candidates.
  - Extended the draft scorecard with `publishable`, `selectionStatus`,
    `selectionPenalty`, and `selectionReasons`.
  - `deterministicFallback` candidates are excluded when a publishable provider
    candidate exists; raw artifact dumps, mojibake, empty fields, and "needs provider
    rewrite" weaknesses are excluded.
  - If no candidate is publishable, the `DraftRun` completes as quality-blocked:
    `status=succeeded`, `finalDraft=null`, `complete.blockedBy=draftCandidateSelection`.
  - `/ai-runs` scorecard table and the diagnostics helper now show status, penalty,
    and exclusion reasons.
- Architecture impact:
  - Candidate quality gating belongs in role-owned candidate selection/application
    modules, not in API, infrastructure, or DraftRun persistence.
  - Domain DTOs remain provider-free; provider/fallback source is selection metadata.
- Tests:
  - Fallback candidate is not selected when a viable OpenRouter candidate exists. Done.
  - Candidate with raw artifact/object dump is marked non-publishable. Done.
  - Scorecard includes exclusion/penalty reasons. Done.
  - All-fallback/all-invalid case returns a clear non-publishable outcome. Done.
  - Existing successful all-provider candidate selection remains compatible. Done.
- Docs:
  - Update SAO/developer docs if selection guard becomes an explicit pipeline rule.
- Demo impact:
  - `/ai-runs` should make the diagnosed failure mode understandable: fallback is
    retained for debugging, not promoted to final content.
- Acceptance criteria:
  - A single failed candidate branch cannot make deterministic placeholder text the
    selected final draft when other provider candidates exist.
- Risks:
  - Over-penalizing fallback could hide useful local drafts when provider output is
    also poor; keep trace explicit and conservative.
- Completed: unknown

### Slice 2.12.5: SourceLedger External Evidence Merge

- Status: Done
- Goal: Merge public evidence into the source ledger and synthesize what it changes
  before feasibility, post contract, rule registry, and drafting.
- User value: The runner can explain which external material supports, qualifies, or
  weakens the post before it writes candidates.
- Scope:
  - Add `EvidenceSynthesis`. Done.
  - Merge accepted `PublicEvidenceItem` records into the existing SourceLedger. Done.
  - Mark external claims as `canState`, `needsQualification`,
    `canUseAsFraming`, or `doNotState`. Done.
  - Feed enriched ledger/synthesis into feasibility, post contract, rule registry,
    planning, and candidates. Done.
  - Show enriched ledger and synthesis in `/ai-runs`. Done.
- Out of scope:
  - Validator scoring.
  - Directed revision.
  - Long-term source cache.
- Architecture impact:
  - Feasibility and PostContract must consume enriched ledger when public evidence
    exists.
  - Validators remain deferred until the source ledger includes both internal and
    public claims.
- Tests:
  - External evidence creates ledger claims with stable ids. Done.
  - Failed/skipped public evidence attempts create warnings, not claims. Done.
  - Feasibility/post contract/rule registry use the enriched ledger when public
    evidence exists. Done.
- Docs:
  - Update SAO/developer/user/demo docs. Done.
- Demo impact:
  - Demo trace should show at least one external claim merged into ledger.
- Acceptance criteria:
  - DraftRun trace shows internal claims, public claims, and synthesis before
    contract/rule planning.
- Risks:
  - Over-trusting external snippets; keep allowed-use conservative.
- Completed: 2026-06-24

### Slice 2.12.5.1: MaterialPlan Evidence Accountability and Retry

- Status: Done
- Goal: Prevent `materialPlan` from silently ignoring enriched SourceLedger evidence.
- User value: DraftRun trace now explains whether the runner used public/internal
  evidence, rejected it with reasons, retried the planner, or fell back only as an
  emergency.
- Scope:
  - Add `OPENROUTER_BACKUP_MODEL` as an optional retry model. Done.
  - Project usable internal/external claims into a short `usableEvidenceCandidates`
    list for `materialPlan`. Done.
  - Require MaterialPlan to select evidence or explain rejected evidence. Done.
  - Retry primary model with stricter repair prompt, then optional backup model. Done.
  - Use deterministic fallback only after all LLM attempts fail accountability. Done.
  - Show attempts, accepted/rejected evidence, attribution, and fallback state in
    `/ai-runs`. Done.
- Out of scope:
  - New DraftRun steps, SQLite migration, prose-quality validators, and directed
    revision.
- Architecture impact:
  - Evidence projection, accountability, retry policy, and retry orchestration are
    separate application modules.
  - `DraftMaterialPlanService` remains a thin step service; provider calls stay behind
    OpenRouter infrastructure.
- Tests:
  - Empty evidence without rejection reasons triggers retry. Done.
  - Valid rejection/selection accountability is stored in the artifact. Done.
  - Backup model retry is used when configured. Done.
  - Emergency fallback is explicit and traceable. Done.
- Acceptance criteria:
  - A non-empty enriched ledger cannot be ignored by `materialPlan` without visible
    accountability in trace.
- Risks:
  - Retry increases latency and model cost when the planner ignores evidence; this is
    intentional until validators and directed revision exist.
- Completed: 2026-06-24

### Slice 2.13: Deterministic Linter and Validator Orchestrator

- Status: Done
- Completed: 2026-06-24
- Goal: Add the first report-only validation layer after draft candidates are
  generated.
- Scope:
  - Added provider-free `DraftValidationReport`, `DraftCandidateValidationReport`,
    `DraftValidatorFinding`, and `DraftValidatorStatus`.
  - Added deterministic validators for size/shape, CTA and contract signals,
    source attribution, rejected evidence misuse, forbidden moves, raw artifact
    leakage, and publishability consistency.
  - Replaced the placeholder `validation` step artifact with a real report for all
    candidates, marking the selected candidate separately.
  - Kept the slice report-only: findings are visible in trace but do not change
    `finalDraft` selection.
  - Updated `/ai-runs?runId=...` semantic trace to show validation summary,
    per-candidate quality, source attribution findings, size findings, and
    publishability findings.
- Explicitly out of scope:
  - OpenRouter/LLM-assisted validators.
  - Changing ranking, selection, fallback policy, or directed revision from
    validation findings.

#### Deferred Follow-Up: LLM-Assisted Validator Reports

- Status: Backlog
- Goal: Add optional provider-backed validators for source grounding,
  publisher/voice, topic/fabula fit, coherence/compression, and audience value.
- Rule:
  - Provider-backed validators must consume `SourceLedger`, `PostContract`,
    `RuleRegistry`, `MaterialPlan`, and draft candidates. They must not reconstruct
    provenance from prose alone.

### Slice 2.13.1: Attribution Validator Calibration

- Status: Done
- Goal: Calibrate deterministic attribution validation so it flags real missing
  source attribution without creating false positives for valid author/source mentions.
- User value:
  - `/ai-runs?runId=...` validation warnings become actionable instead of noisy.
  - Slice 2.14 can consume attribution findings without repairing already-correct
    drafts.
- Scope:
  - Expand attribution markers from `PublicEvidenceItem` and external ledger
    provenance: source title, domain, URL, author/person names when visible, source
    organization, and source label.
  - Treat mentions such as `Tian Pan`, `Vamsee Jasti`, `SQ Collective`, `Alan Knox`,
    source title, or source domain as valid attribution when they match the referenced
    claim.
  - Add trace/debug fields for expected attribution markers and matched markers.
  - Keep warnings when source-backed claims appear with no visible attribution or
    qualification.
- Out of scope:
  - LLM attribution judgment.
  - Changing candidate ranking or final draft selection.
- Tests:
  - Candidate with valid author/source mention does not get false attribution warning.
  - Candidate with numeric/public claim and no source marker still gets warning.
  - Trace semantic validation panel shows matched/expected attribution markers.
- Result:
  - Attribution validation now matches markers per external claim instead of accepting
    any source mention globally.
  - Findings expose expected/matched/missing attribution markers in validation
    metadata and `/ai-runs` semantic trace.
- Completed: 2026-06-24

### Slice 2.13.2: JSON Step Retry Discipline

- Status: Done
- Goal: Stop going directly to deterministic fallback when an OpenRouter JSON step
  returns malformed JSON or the wrong shape.
- User value:
  - Agentic steps become more reliable and fallback becomes a last resort rather than
    the first response to provider formatting errors.
- Scope:
  - Introduce reusable retry policy for JSON-producing LLM steps:
    primary attempt -> stricter repair retry -> optional `OPENROUTER_BACKUP_MODEL`
    retry -> deterministic emergency fallback.
  - Apply first to `rhetoricalPlans`, because the control run
    `d2286a22-bf90-43c1-93a0-26d4aab937e1` fell back after
    `OpenRouter response JSON is not an object`.
  - Persist attempts in the step artifact: model, aiRunId, status, error, validation
    result, backup/fallback markers.
  - Keep provider tokens and raw secrets out of trace.
- Out of scope:
  - Changing generated prose quality directly.
  - Adding retries for every provider step in one large refactor.
- Tests:
  - malformed primary response triggers repair retry;
  - malformed repair response triggers backup retry when configured;
  - all failed attempts trigger explicit deterministic fallback;
  - valid retry response prevents fallback;
  - trace shows attempts and final source.
- Result:
  - `rhetoricalPlans` now uses primary, repair, optional backup, then deterministic
    fallback.
  - The step artifact stores `attempts[]`, and DraftRun `aiRunIds` includes all child
    provider attempts.
- Completed: 2026-06-25

### Slice 2.13.3: LLM-Assisted Validator Reports

- Status: Done
- Completed: 2026-06-25
- Goal: Add provider-backed, report-only editorial validators after deterministic
  validation and before ranking/revision.
- User value:
  - Validation starts judging actual editorial quality, not only formal lint issues.
- Scope:
  - Added provider-free `LlmDraftValidationReport`,
    `LlmCandidateValidationReport`, and `LlmValidatorAttempt` DTOs.
  - Added one report-only OpenRouter JSON validation call per candidate for source
    grounding, publisher/author fit, topic/fabula fit, coherence/compression, and
    audience value.
  - LLM validation consumes `SourceLedger`, `PostContract`, `RuleRegistry`,
    `MaterialPlan`, draft candidate text, and deterministic validation findings.
  - Added primary, repair, optional backup-model retry discipline for validation
    JSON; unconfigured provider returns `not-run` without fake findings.
  - Saved child `AiRun` ids for validation attempts and exposed them in the DraftRun
    validation trace.
  - Findings remain report-only; ranking/revision consumes them in 2.14.
- Out of scope:
  - Automatic rewrite.
  - Changing final draft selection.
  - Freeform prose critique without rule/claim references.
- Tests:
  - Provider success stores LLM validator findings in `validation` artifact.
  - Provider malformed/error response falls back safely or marks validator
    unavailable without blocking run.
  - Trace shows deterministic and LLM validation findings separately.
- Result:
  - Existing `validation` artifacts now keep deterministic findings and optional
    `llmValidationReport` side by side.
  - `/ai-runs?runId=...` shows LLM validation status, attempts, and findings next to
    deterministic validation.

### Slice 2.13.3.1: LLM Validation Report Normalization and Evidence Trace Repair

- Status: Done
- Completed: 2026-06-25
- Goal: Normalize LLM validation reports and repair readable evidence trace before
  ranking/revision consumes those artifacts.
- User value:
  - `/ai-runs?runId=...` no longer treats positive LLM pass notes as warnings, and
    evidence handoff from public evidence to material planning is easier to inspect.
- Scope:
  - Split actionable LLM validation `findings` from positive/pass `observations`.
  - Treat `pass`, `ok`, `positive`, `observation`, and `No repair needed` items as
    observations unless they are critical actionable issues.
  - Keep old `findings[]`-only provider responses compatible.
  - Show LLM actionable findings and observations separately in trace.
  - Show enriched public-evidence ledger counts, evidence synthesis counts, and nested
    `materialPlan` selected/rejected evidence in readable trace.
  - Update the DraftRun diagnostics helper to read `publicEvidence.enrichedSourceLedger`
    and nested material-plan artifacts.
- Out of scope:
  - Changing final draft selection.
  - Ranking, revision, or blocking based on validation.
  - New DraftRun steps or SQLite schema changes.
- Tests:
  - Positive/no-repair LLM notes become observations and do not raise warning status.
  - Actionable LLM warnings remain findings.
  - Trace shows LLM findings/observations and nested evidence artifacts.
- Result:
  - `llmValidationReport.summary` now includes `observationCount`.
  - Candidate reports keep `findings[]` for actionable issues and `observations[]` for
    positive/pass notes.
  - The trace workbench distinguishes selected/rejected evidence from public evidence
    retrieval and synthesis.

### Slice 2.14: Pairwise Ranking and Directed Revision

- Status: Done
- Goal: Choose the best candidate and perform one targeted repair without losing the
  post contract.
- Scope:
  - Pairwise rank candidates with a traceable scorecard.
  - Build one directed revision instruction from concrete lint/validator findings.
  - Preserve locked claims and forbidden moves during revision.
  - Keep the best previous candidate if revision regression is worse.
- Result:
  - Added provider-free ranking/revision DTOs and role-owned backend services for
    pairwise ranking, directed revision, revision instruction building, and regression
    guarding.
  - `validation.rankingRevision` now stores pairwise comparison, repair instruction,
    revised candidate, regression guard result, and final decision.
  - `DraftRun.finalDraft` is resolved after validation/ranking/revision instead of
    directly from the old draft scorecard.
  - `/ai-runs?runId=...` shows ranking/revision semantic sections.
  - Built-in publication size defaults were expanded for Telegram post, LinkedIn post,
    and LinkedIn article, while user-edited profiles are preserved.
- Completed: 2026-06-25

### Slice 2.14.1: DraftRun Long-Running Step Progress Budget

- Status: Done
- Goal: Prevent long provider-heavy steps from looking stuck while preserving the
  queued DraftRun as the source of truth.
- Trigger:
  - Control DraftRun `fe837b55-15d9-4e8a-b5b8-d10b30889947` succeeded and validated
    Slice 2.14 ranking/revision, but took about 13 minutes.
  - Control DraftRun `fe837b55-15d9-4e8a-b5b8-d10b30889947` spent long periods inside
    `draft` / `validation` without intermediate progress.
  - Control DraftRun `fe837b55-15d9-4e8a-b5b8-d10b30889947` reached
    `validation.rankingRevision` successfully, but UI/trace would show little
    information while multiple child provider calls are in flight.
  - Control DraftRun `fe837b55-15d9-4e8a-b5b8-d10b30889947` also showed public search
    warnings; prior control `b8963623-f92d-4d35-b57d-678ecb458af1` with broader public
    evidence fan-out became stale during `publicEvidence`.
- Scope:
  - Add per-attempt progress updates for provider-heavy steps where possible:
    `publicEvidence`, `draft`, `validation`, `pairwiseRanking`, and
    `directedRevision`.
  - Add explicit runtime budgets for web search task count and LLM validation calls in
    local smoke/evaluation mode.
  - Ensure Celery timeout/failure is reflected in DraftRun state, not only worker logs.
  - Keep compatibility fallback discipline unchanged: a live DraftRun must not be
    replaced by `/api/drafts/generate`.
- Result:
  - Added artifact-level `progress` payloads for long-running DraftRun steps without
    adding SQL tables or new `DraftRunStepKey` values.
  - `publicEvidence` now records URL/search/skip/synthesis operations; `draft` records
    candidate-generation operations; `validation` records deterministic lint, per
    candidate LLM validation, pairwise ranking, directed revision, and regression
    guard operations.
  - Operation updates reuse existing step artifact writes, so `draft_runs.updated_at`
    moves during live work and stale detection does not fire while real progress is
    being persisted.
  - The main workbench shows the current operation label in the generating state, and
    `/ai-runs?runId=...` renders nested operations under logical steps.
  - Added `backend/app/application/draft_run_step_progress.py` and
    `src/infrastructure/draftRunProgress.ts` as role-owned progress helpers.
- Completed: 2026-06-25

### Slice 2.15: Iterative Revision Loop and Improvement Gate

- Status: Done
- Completed: 2026-06-25
- Goal: Replace one-shot directed revision with a bounded improvement loop where each
  revised draft must prove measurable improvement over the previous best draft.
- User value:
  - The author receives a draft that has been repeatedly repaired against concrete
    findings instead of a single "not worse" revision.
  - The trace explains what was improved, what stayed unresolved, and why the runner
    stopped.
- Trigger:
  - Control DraftRun `26b3f82e-5ed2-452c-9d2b-113310c83f9c` proved that Slice 2.14
    runs pairwise ranking and one directed revision, but the revision was accepted
    because it did not worsen deterministic validation, while several original repair
    goals remained unresolved.
- Scope:
  - Add backend setting `DRAFT_REVISION_MAX_ITERATIONS` with a documented default.
  - Build a revision loop around the current selected candidate:
    - validate current best draft;
    - derive concrete repair goals from deterministic and LLM findings;
    - call OpenRouter for a revised candidate;
    - re-run deterministic validation on the revised candidate;
    - compare previous best vs revised candidate through pairwise ranking;
    - accept the revised candidate only when it improves measurable repair goals.
  - Track each cycle in `validation.rankingRevision.revisionLoop`:
    - cycle number;
    - base candidate id;
    - repair goals;
    - revised candidate id;
    - validation before/after;
    - pairwise old-vs-new comparison;
    - accepted/rejected decision;
    - resolved and unresolved repair goals;
    - added constraints for the next cycle.
  - If a revised candidate is worse or fails to close targeted goals:
    - keep the previous best draft;
    - add explicit anti-regression constraints so the next attempt does not repeat the
      same failed move;
    - continue until the configured iteration limit or stop condition.
  - Stop the loop when:
    - all critical findings are closed and warnings are below the v1 threshold;
    - no candidate improves over the current best;
    - `DRAFT_REVISION_MAX_ITERATIONS` is reached;
    - provider calls fail after the existing JSON retry discipline.
  - Set `finalDraft` from the best accepted candidate after the loop, not immediately
    after the first directed revision.
- Out of scope:
  - Human editor decision learning.
  - Multi-model tournament beyond existing primary/repair/backup retry policy.
  - New SQLite tables or new DraftRun steps.
  - Full UI editor for manually choosing between revision cycles.
- Implementation notes:
  - Keep the loop in role-owned application modules; do not grow near-limit
    `draft_run_pipeline.py`, `draft_ranking_revision_service.py`, or validation
    services directly.
  - Store loop artifacts inside the existing `validation` step under
    `rankingRevision.revisionLoop`; no schema migration.
  - Revision acceptance must be stronger than "not worse": it must show resolved
    repair goals or a pairwise win with no new critical findings.
  - Remaining unresolved goals must be visible in trace and passed into later cycles as
    constraints.
- Architecture impact:
  - `PostContract`, `RuleRegistry`, `SourceLedger`, `MaterialPlan`, validators, and
    pairwise ranking become the control loop for prose improvement.
  - `finalDraft` becomes the output of a bounded revision loop rather than a direct
    candidate-selection result.
- Tests:
  - Backend tests for max-iteration setting, accepted improvement, rejected regression,
    unresolved-goal carryover, provider failure, and stop reasons.
  - Trace tests for cycle list, resolved/unresolved goals, old-vs-new comparison, and
    final best candidate.
  - Regression: `npm run test:backend`, `npm run test:architecture`,
    `npm test -- --run`, `npm run smoke`, `npm run test:design`,
    `npm run test:visual`, `docker compose config --quiet`, `git diff --check`.
- Docs:
  - Update SAO/developer/user/demo docs: revision loop is the main quality-improvement
    mechanism; human learning follows after the machine loop is traceable.
- Demo impact:
  - Demo trace should show at least one revision cycle with clear resolved and
    unresolved goals.
- Acceptance criteria:
  - A revised draft is accepted only when it improves the previous best by explicit
    repair-goal closure or pairwise win without regression.
  - If a revision does not improve, the previous best remains final and the failed move
    is recorded as a constraint.
  - The number of improvement cycles is controlled by `DRAFT_REVISION_MAX_ITERATIONS`.
  - `/ai-runs?runId=...` shows why the loop stopped and which draft became final.
- Result:
  - Added `DRAFT_REVISION_MAX_ITERATIONS` with default `3` and runtime-safe minimum
    `1`.
  - Added provider-free revision loop DTOs and role-owned application modules for loop
    config, repair-goal evaluation, and bounded cycle orchestration.
  - `validation.rankingRevision.revisionLoop` now records each revision cycle:
    repair goals, constraints, revised candidate, deterministic validation before/after,
    old-vs-new pairwise comparison, resolved/unresolved goals, acceptance decision, and
    child `AiRun` ids.
  - `DraftRun.finalDraft` is now selected from the final best candidate after the
    bounded loop. Rejected revisions remain trace artifacts and feed anti-regression
    constraints into the next cycle.
  - `/ai-runs?runId=...` shows revision loop cycles, final source, and stop reason.

### Strategic Correction: Deep Drafting Intelligence

- Status: Accepted
- Goal: Move the drafting track from defensive validation/reporting to an editorial
  lab that can create stronger post ideas.
- Trigger:
  - Slice 2.15 proved that bounded revision works mechanically, but the result can
    still be dry, generic, or formally improved without becoming editorially strong.
  - The next quality problem is not "produce a better failure report"; it is "create
    better intellectual conditions before and during writing."
- Architecture rule:
  - Preserve the existing quality spine:
    `SourceLedger -> FeasibilityGate -> PostContract -> RuleRegistry -> MaterialPlan ->
    RhetoricalPlans -> DraftCandidates -> Validators -> Ranking -> RevisionLoop`.
  - Add a new editorial-lab layer around it:
    `ArticleDossier + ContextPacks + Editorial Roles + Model Portfolio`.
  - Future model calls must consume task-specific context packs, not raw DraftRun
    blobs and not only the latest artifact.
  - Evidence must become interpreted editorial implications before prose-generation
    prompts can use it as support.
  - Critique must be an explicit role in the pipeline, not only validation metadata.
- ADR:
  - `docs/adr/2026-06-26-drafting-needs-editorial-lab-context-memory-and-model-roles.md`.
- Next slices:
  - 2.15.1 role-specific model configuration.
  - 2.15.2 ArticleDossier and context packs.
  - 2.15.3 evidence interpretation.
  - 2.15.4 prosecutor/editor critic role.
  - 2.15.5 alternative-angle tournament.
  - 2.15.6 deep revision loop v2.
  - 2.15.6.2 research-depth profiles and DraftRun budget modes.
  - 2.15.6.3 model stabilization and universal JSON retry repair.
  - 2.15.6.4 final draft quality snapshot.
  - 2.15.6.4.1 final quality contract and independent gate review.

### Slice 2.15.1: Multi-Model Drafting Roles

- Status: Done
- Goal: Replace `DEFAULT/BACKUP` thinking with role-specific model selection.
- User value:
  - The runner can deliberately ask different model families for research, strategy,
    writing, critique, review, and alternative angles instead of repeating one model's
    habits.
- Scope:
  - Add env/settings for role models:
    `DRAFT_RESEARCH_MODEL`, `DRAFT_STRATEGY_MODEL`, `DRAFT_WRITER_MODEL`,
    `DRAFT_CRITIC_MODEL`, `DRAFT_REVIEW_MODEL`, `DRAFT_ANOTHER_ANGLE_MODEL`,
    while keeping `OPENROUTER_BACKUP_MODEL` as technical fallback.
  - Add provider-free role enum/value objects and application-level resolver.
  - Wire existing planning/writing/review calls through the resolver where practical,
    without changing prompt semantics yet.
  - Trace every role/model choice in DraftRun artifacts and child `AiRun` payloads.
- Out of scope:
  - New critique loop.
  - ArticleDossier.
  - UI model settings.
  - Provider tournament logic.
- Architecture impact:
  - Model identity becomes role policy, not scattered per service.
  - Backup remains fallback; another-angle/review/critic are creative/editorial roles.
- Tests:
  - Settings load role model env values and default sanely.
  - Resolver chooses role model, then default, then backup only for retry/fallback.
  - Child `AiRun` traces show role and chosen model without secrets.
  - Existing provider calls remain compatible when role env values are empty.
- Docs:
  - Update `.env.example`, SAO, developer guide, and roadmap.
- Acceptance criteria:
  - A DraftRun trace can answer: which model played researcher, writer, critic, review,
    and another-angle roles.
- Result:
  - Added provider-free `DraftModelRole` / `DraftModelSelection` DTOs and
    `draft_model_role_resolver`.
  - Added env/settings for research, strategy, writer, review, critic, and
    another-angle models. `.env.example` now carries the balanced recommended preset:
    default `deepseek/deepseek-v4-pro`, backup `qwen/qwen3.7-plus`, search
    `perplexity/sonar-pro`, research `google/gemini-3.1-pro-preview`, strategy
    `z-ai/glm-5.2`, writer `anthropic/claude-sonnet-4.6`, review
    `openai/gpt-5.4-mini`, critic `openai/gpt-5.2`, another-angle `qwen/qwen3.7-max`.
  - Wired research, strategy, writer, review, ranking, and revision services through
    the resolver without changing prompt semantics.
  - Child `AiRun` request payloads, step artifacts, retry attempts, candidates, and
    `/ai-runs` readable trace now expose `modelRole`, `selectedModel`, and
    `modelSelectionSource`.
  - Backup retry still uses `OPENROUTER_BACKUP_MODEL`; public search still uses
    `OPENROUTER_WEB_SEARCH_MODEL`.
- Completed: 2026-06-26

### Slice 2.15.2: Article Dossier and Context Packs

- Status: Done
- Goal: Add DraftRun-local article memory and task-specific context selection.
- User value:
  - Later steps stop losing useful research/critique context and stop drowning models
    in raw artifacts.
- Scope:
  - Add provider-free `ArticleDossier` with evidence cards, claim cards, tension cards,
    angle cards, critique cards, decision cards, rejected moves, voice notes, and open
    questions.
  - Add `ContextPackBuilder` role-owned application modules for researcher,
    strategist, writer, critic, reviewer, and another-angle prompts.
  - Store dossier/context-pack snapshots in existing step artifacts; no SQLite schema
    migration in v1.
  - Trace what each role received and why.
- Out of scope:
  - Long-term vector store.
  - Cross-DraftRun memory persistence.
  - Changing final draft selection.
- Architecture impact:
  - Context engineering becomes explicit application logic.
  - Raw DraftRun JSON must not be used as the normal prompt context for writing roles.
- Tests:
  - Dossier is built from SourceLedger, public evidence, material plan, validators,
    ranking, and revision loop artifacts.
  - Context packs include relevant cards and exclude unrelated bulk.
  - Legacy runs without dossier remain readable.
- Acceptance criteria:
  - `/ai-runs?runId=...` can show the article memory and each role's context pack.
- Result:
  - Added provider-free `ArticleDossier`, `DossierCard`, `ContextPack`, and
    `ContextPackItem` DTOs.
  - Added deterministic article-memory builders that create DraftRun-local cards from
    ledger, public evidence, contract/rules, material planning, candidates,
    validation, ranking, and revision artifacts.
  - Existing `publicEvidence`, `rulePack`, `materialPlan`, `strategy`,
    `rhetoricalPlans`, `draft`, and `validation` artifacts can now carry
    `articleDossier` and `contextPacks` snapshots without new steps or SQLite schema.
  - Strategy/writer/review child `AiRun` request traces include the role-specific
    `contextPack` they received.
  - `/ai-runs?runId=...` renders Article Dossier and Context Packs as semantic trace
    sections, while old runs without these fields remain readable.
- Completed: 2026-06-26

### Slice 2.15.3: Evidence Interpretation, Not Citation Injection

- Status: Done
- Goal: Convert public evidence into editorial implications before writing.
- Current pipeline reference:
  - `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` is the maintained AS IS map of the
    generation pipeline and must be updated together with its PDF when this slice
    changes DraftRun behavior.
- Target design:
  - `docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.md` and
    `docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.pdf` define the proposed
    evidence-interpretation handoff for this slice.
- User value:
  - Sources stop appearing as forced reference name-drops and start shaping the post's
    thought, conflict, and author position.
- Scope:
  - Add `EvidenceInterpretation` artifacts: source-backed implications, tensions,
    angle opportunities, limits, forbidden overclaims, and usable examples.
  - Use OpenRouter JSON call with deterministic fallback.
  - Feed interpreted implications into ArticleDossier and writer/critic context packs.
  - Preserve raw `PublicEvidenceItem` and merged ledger claims separately.
- Out of scope:
  - New web search provider.
  - Final prose rewrite.
  - Source citation UI.
- Architecture impact:
  - Public evidence cannot be injected directly into prose prompts as a flat list of
    references; it must pass through interpretation first.
- Tests:
  - Accepted public evidence produces implications tied to claim/source ids.
  - Weak/irrelevant evidence creates limits or rejected implications, not proof.
  - Writer context pack receives implications, not raw citation dumps.
- Acceptance criteria:
  - Trace explains what each source changes in the editorial argument.
- Result:
  - Added provider-free `EvidenceInterpretation` DTOs for implications, tensions,
    usable examples, limits, forbidden overclaims, reader-value hooks, and rejected
    evidence uses.
  - Added provider-backed `EvidenceInterpretationService` with strategy-role model
    selection, primary/repair/optional-backup JSON attempts, child `AiRun` audit, and
    deterministic fallback.
  - Integrated interpretation inside the existing `rulePack` artifact without new
    DraftRun steps or SQLite schema changes.
  - ArticleDossier and role ContextPacks now receive interpretation cards, so later
    strategy/writer/review calls can use source meaning instead of raw citation dumps.
  - MaterialPlan and draft-candidate prompts now prefer interpretation artifacts over
    raw snippets.
  - `/ai-runs?runId=...` renders `EvidenceInterpretation` as a readable semantic
    section and maps child `evidenceInterpretation` AiRuns under the `rulePack` step.
- Completed: 2026-06-26

### Slice 2.15.4: Prosecutor / Editor Critic Loop

- Status: Done
- Goal: Add a dedicated editorial critic role that challenges draft candidates before
  revision.
- User value:
  - The system can identify boring, generic, over-sourced, under-argued, or
    authorless drafts even when formal validators pass.
- Scope:
  - Add `EditorialCritiqueReport` with findings for blandness, weak tension, missing
    author stance, forced references, generic AI prose, unsupported leap, and unclear
    reader value.
  - Use `DRAFT_CRITIC_MODEL` and role-specific context pack.
  - Store critique in validation/ranking artifacts and ArticleDossier.
  - Keep report-only for this slice; ranking/revision consumption is later.
- Out of scope:
  - Changing final draft selection.
  - Human editor UI for critique acceptance.
- Architecture impact:
  - Critique is not the same as validation. Validators check contract; critic attacks
    editorial quality and idea strength.
- Tests:
  - Critic report is stored and trace-visible.
  - Positive observations are separated from actionable critique.
  - Missing provider marks critic `not-run`, not fake findings.
- Acceptance criteria:
  - Trace can answer: why the critic thinks this post is weak or strong.
- Result:
  - Added provider-free `EditorialCritiqueReport`, candidate critique, observation,
    and attempt DTOs.
  - Added `DraftEditorialCritiqueService` using `DRAFT_CRITIC_MODEL`, critic
    `ContextPack`, OpenRouter JSON retry discipline, sanitized child `AiRun` records,
    and `not-run` behavior when provider config is missing.
  - Stored `validation.editorialCritiqueReport` inside the existing `validation`
    artifact without new DraftRun steps or SQLite schema changes.
  - Kept the report explicitly non-actionable for final selection in this slice:
    pairwise ranking, revision loop, and `finalDraft` behavior remain unchanged.
  - Added critic cards to ArticleDossier so future alternative-angle and deep revision
    slices can consume weak moves, risks, and voice/tension observations.
  - `/ai-runs?runId=...` now renders `Editorial critique` separately from
    deterministic validation and LLM validation.
- Completed: 2026-06-26

### Slice 2.15.5: Alternative Angle Tournament

- Status: Done
- Goal: Generate and compare a genuinely different framing route using a dedicated
  another-angle role/model.
- User value:
  - The system can escape a mediocre local optimum instead of endlessly polishing one
    angle.
- Scope:
  - Use `DRAFT_ANOTHER_ANGLE_MODEL` to propose alternative rhetorical plans from
    ArticleDossier and critique.
  - Generate at least one candidate from the alternative angle.
  - Compare original route vs alternative route by idea strength, source fit, author
    stance, and reader value.
  - Store tournament result in trace.
- Out of scope:
  - Full multi-agent autonomous planning.
  - Manual UI for choosing angle.
- Architecture impact:
  - Alternative angle is not fallback and not retry. It is intentional creative
    divergence.
- Tests:
  - Alternative angle receives a different prompt/context pack from ordinary writer.
  - Trace distinguishes original route, alternative route, and chosen route.
  - If another-angle provider fails, existing route remains usable.
- Acceptance criteria:
  - A DraftRun can show at least one non-identical route and why it was accepted or
    rejected.
- Result:
  - Added provider-free `AlternativeAngleRoute` and `AlternativeAngleTournament`
    artifacts.
  - Added a critic-driven tournament inside the existing `validation` step: initial
    validation/critic runs first, then `DRAFT_ANOTHER_ANGLE_MODEL` proposes one
    challenger route, `DRAFT_WRITER_MODEL` writes one challenger candidate, and final
    validation/ranking/revision runs on the merged candidate pool.
  - Kept `anotherAngle` explicitly separate from fallback/retry: provider unavailable
    or malformed route responses produce `not-run`/`failed` tournament trace and the
    original candidate pool continues unchanged.
  - Added child `AiRun` traces for `alternativeAngleRoute` and
    `alternativeAngleCandidate`, including model-role metadata.
  - `/ai-runs?runId=...` now renders `Alternative angle tournament` as a semantic
    trace section.
- Completed: 2026-06-27

### Slice 2.15.6: Deep Revision Loop v2

- Status: Done
- Goal: Make the revision loop optimize for editorial improvement, not only validator
  cleanup.
- User value:
  - The final draft improves its idea, structure, source use, and author stance across
    cycles.
- Scope:
  - Revision loop consumes ArticleDossier, EvidenceInterpretation, EditorialCritique,
    rejected moves, and alternative-angle tournament results.
  - Acceptance requires improvement across explicit editorial dimensions:
    idea strength, tension, reader value, author stance, source integration, and
    validator health.
  - Rejected revisions become structured `rejectedMoves` in ArticleDossier.
  - Stop reasons distinguish validator-clean, editorially-improved, no-fresh-angle,
    provider-failed, and max-iterations.
- Out of scope:
  - Human learning capture; remains Slice 2.16.
  - Infinite autonomous loops.
- Architecture impact:
  - Revision loop becomes editorial optimization over dossier state, not a local patch
    over the latest draft.
- Tests:
  - A revision that lowers warnings but weakens idea strength is rejected.
  - A revision that improves critique goals without validator regression can be
    accepted.
  - Rejected moves are carried into the next cycle context pack.
- Acceptance criteria:
  - Trace can explain not only that the draft improved, but what editorial dimension
    improved and what moves were banned.
- Result:
  - Added provider-free revision-loop trace fields for editorial goals, dimension
    scores, resolved/unresolved editorial goals, rejected moves, acceptance decision,
    and per-cycle stop reason.
  - Added role-owned backend modules for editorial goal projection, editorial
    improvement evaluation, rejected-move constraints, and revision-cycle execution.
  - Directed revision now receives validator goals, editorial goals, rejected moves,
    anti-regression constraints, dossier/context pack, evidence interpretation, and
    alternative-angle lessons.
  - Pairwise ranking now asks for editorial dimension scores and stores them in
    attempts for revision-loop policy and `/ai-runs` trace.
  - Acceptance policy rejects revisions that improve validator health but regress key
    editorial dimensions such as idea strength, reader value, source integration, or
    author stance.
  - `/ai-runs?runId=...` shows editorial goals, dimension scores, rejected moves, and
    revision-loop stop reason.
- Follow-up from live control run:
  - DraftRun `692ab2f7-320a-4191-b5bf-eca7efddfa8c` confirmed that the updated
    backend/worker reaches `validation`, executes alternative-angle tournament, accepts
    revision cycle 1, and then can become stale inside `directed-revision-cycle-2`.
    This is an orchestration reliability issue for a follow-up repair slice; it is not
    part of the 2.15.6 editorial-loop policy itself.
- Completed: 2026-06-27

### Slice 2.15.6.1: Revision Operation Timeout and Validation Progress Commit Repair

- Status: Done
- Goal: Prevent provider-heavy validation/revision operations from leaving a DraftRun
  permanently `running/stale`.
- User value:
  - A long drafting run either finishes with the best available draft or fails/blocks
    with a readable reason; it does not silently hang inside a revision cycle.
- Scope:
  - Add operation-level safe wrappers for validation sub-operations that call providers:
    editorial critique, alternative-angle candidate generation, pairwise ranking, and
    directed revision.
  - If a provider or post-processing operation cannot produce a usable result, mark the
    nested operation `failed`, persist the safe error, and let the pipeline continue or
    stop with an explicit `provider-failed` / `operation-failed` reason.
  - Ensure revision loop keeps the previous best candidate when a later revision cycle
    fails.
  - Persist validation child `AiRun` ids to the parent DraftRun incrementally or at the
    end of the validation step so `/ai-runs?runId=...` can load the full trace.
  - Store enough partial validation/ranking/revision state in the `validation` artifact
    that stale/failure diagnostics can show completed sub-operations.
- Out of scope:
  - Changing prose prompts or editorial quality policy.
  - Adding new DraftRun steps, SQL columns, or main-cabinet UI.
  - Reworking the model portfolio.
- Architecture impact:
  - Validation becomes more fault-tolerant at sub-operation level while keeping the
    existing `validation` step and `rankingRevision.revisionLoop` trace contract.
- Tests:
  - Directed revision cycle 2 provider/post-processing failure marks the operation
    failed and finalizes with the previous best candidate.
  - Alternative-angle candidate failure does not leave the run running forever.
  - Parent `DraftRun.aiRunIds` includes validation child runs.
  - Old DraftRuns without these partial artifacts remain readable.
- Docs:
  - Update the AS IS pipeline map and developer docs to explain operation-level
    failure handling inside `validation`.
- Acceptance criteria:
  - Re-running the diagnosed scenario does not produce stale `directed-revision-cycle-2`;
    the run finishes or records a safe explicit failure/blocked reason.
- Result:
  - Added artifact merge helpers so validation operation progress preserves partial
    deterministic/LLM/critic/tournament/ranking/revision artifacts instead of replacing
    them with progress-only payloads.
  - Validation operation progress now appends child `AiRun` ids to the parent DraftRun
    as operations complete.
  - Added safe operation wrappers for provider-heavy validation paths and wired them
    into alternative-angle route/candidate generation and revision-loop revision/
    pairwise operations.
  - If a later revision cycle fails after a usable best draft exists, the loop keeps the
    previous best candidate, marks the nested operation failed, records a safe stop
    reason, and finalizes instead of staying stale.
  - Added regression coverage for cycle-2 directed-revision failure and progress merge
    behavior.
- Completed: 2026-06-27

### Slice 2.15.6.2: Research Depth Profiles and DraftRun Budget Modes

- Status: Done
- Goal: Make public-evidence depth and execution cost explicit instead of hardcoding
  one source/search volume for every fabula.
- User value:
  - A compact Telegram opinion post, a standard LinkedIn post, and a deep LinkedIn
    market-research article can use different research depth without changing the
    whole pipeline by hand.
  - Developers can run a fast but complete smoke DraftRun without pretending that the
    production pipeline is shorter than it really is.
- Scope:
  - Add `Fabula.researchDepth` values such as `light`, `standard`, `deep`, and
    `marketResearch`.
  - Add backend/frontend normalization so old fabulas default to `standard`.
  - Add config-driven budget profiles per research depth: search task cap, accepted
    public-evidence cap, external ledger claim cap, URL/read cap, and revision/search
    cycle caps where relevant.
  - Add `DRAFT_RUN_EXECUTION_MODE=smoke|standard|full` and mode-specific budget
    overrides. Smoke mode must still execute the real step sequence; it only lowers
    counts/time budgets.
  - Add a `DraftRunBudget` / budget resolver artifact to trace: requested depth,
    execution mode, effective caps, and which caps were hit.
  - Apply budgets to `sourceIntent`, `publicEvidence`, evidence merge, material-plan
    projection, candidate count where safe, and revision loop limit without changing
    DraftRun step order or SQLite schema.
- Out of scope:
  - New search provider behavior.
  - Changing prose prompts for quality.
  - UI comparison for source depth effectiveness.
- Architecture impact:
  - Research volume becomes a controlled contract derived from fabula policy and
    execution mode, not a global magic number.
  - Smoke mode becomes an official DraftRun execution profile, not an ad hoc local
    shortcut.
- Tests:
  - Old fabulas normalize to `researchDepth=standard`.
  - Budget resolver combines fabula depth and execution mode deterministically.
  - Smoke mode runs the full step sequence with lower caps.
  - Deep/market-research fabulas allow larger evidence/source budgets than light
    fabulas.
  - Trace shows effective budgets and cap hits.
- Docs:
  - Update SAO, developer guide, user guide, demo docs, `.env.example`, and AS IS
    pipeline map/PDF if runtime trace semantics change.
- Acceptance criteria:
  - A DraftRun trace can explain why it searched/read N sources and whether that was
    caused by fabula research depth, smoke mode, or provider limits.
- Risks:
  - If depth budgets are too low, deep articles will still look thin; if too high, test
    runs stay expensive. Start conservative and make caps visible in trace.
- Delivered:
  - Added `Fabula.researchDepth` with frontend editing, compact chips, demo depths,
    DraftRun context propagation, and legacy workspace normalization.
  - Added `DraftRunBudget` and resolver with `light`, `standard`, `deep`,
    `marketResearch`, and `smoke` caps.
  - Added `DRAFT_RUN_EXECUTION_MODE`, budget override env keys, capped source
    research tasks, public retrieval, search result count, external claims, usable
    material evidence, draft candidates, and smoke revision iterations.
  - `/ai-runs?runId=...` now shows DraftRun budget, caps, used counts, skipped tasks,
    and trimmed evidence/claims in semantic trace.
  - Updated docs and regenerated the AS IS pipeline PDF.
- Control run note:
  - Smoke DraftRun `37678736-364d-4310-b76f-aca76dbf0fd5` confirmed research/public
    evidence budget caps and trace visibility, but also showed that provider-heavy
    validation/critic/alternative-angle calls can still make smoke runs long. This is
    not fixed by 2.15.6.2 because the slice only caps research/evidence/candidates and
    revision iterations; a later execution-budget slice should add per-role provider
    call caps or a dedicated cheap smoke validation profile.
- Completed: 2026-06-27

### Slice 2.15.6.3: Model Stabilization and Universal JSON Retry Repair

- Status: Done
- Goal: Stabilize provider-heavy DraftRun execution before judging prose quality again.
- User value:
  - The writer/critic roles use less exotic recommended models while another-angle
    remains a distinct model family.
  - A single malformed provider response no longer silently disables critic,
    alternative-angle, planning, validation, candidate generation, or revision work.
  - Trace clearly shows whether the pipeline tried primary, repair prompt, and backup
    model before giving up.
- Scope:
  - Recommended defaults:
    - `DRAFT_WRITER_MODEL=anthropic/claude-haiku-4.5`
    - `DRAFT_CRITIC_MODEL=openai/gpt-4.1`
    - `DRAFT_ANOTHER_ANGLE_MODEL=qwen/qwen3.7-max` remains separate from writer.
  - Fix propagation of `fabula.researchDepth` into backend context summary so
    `DraftRunBudget` resolves `light/deep/marketResearch` instead of silently falling
    back to `standard`.
  - Promote JSON retry discipline from partial service-level usage into a project-wide
    architecture rule backed by ADR
    `docs/adr/2026-06-27-llm-json-steps-use-universal-retry-policy.md`.
  - Inventory every JSON-producing LLM step: source research plan, evidence synthesis,
    evidence interpretation, material plan, strategy, rhetorical plans, draft
    candidates, LLM validation, editorial critic, alternative-angle route/candidate,
    pairwise ranking, directed revision, and future JSON provider calls.
  - Route all JSON-producing provider calls through a shared application-level policy:
    `primary -> primary-repair -> optional OPENROUTER_BACKUP_MODEL -> explicit
    fallback/not-run/failed outcome`.
  - Ensure repair prompts include the previous validation/parse error and required JSON
    shape.
  - Ensure every attempt creates or updates child `AiRun` audit with label, model,
    model role, backup flag, status, parse/validation error, and safe provider
    metadata.
  - Keep deterministic fallback only for steps where a domain-safe deterministic result
    exists; otherwise return explicit `not-run` or `failed` without fake findings.
  - Add a public-prose guard to writer/revision prompts: internal artifacts such as
    `SourceLedger`, `publicEvidence`, `validators`, `RuleRegistry`, and `PostContract`
    must not leak as unexplained dev-jargon.
  - Strengthen revision-loop trace so accepted cycles record a concrete reason:
    resolved validator/editorial goals, a clear pairwise win, and no deterministic
    regression.
- Out of scope:
  - Changing search/source budgets; owned by 2.15.6.2.
  - Changing final draft quality scoring; owned by 2.15.6.4 and later.
  - Redesigning ranking, source retrieval, or final scoring.
- Architecture impact:
  - Any future LLM JSON step must use the universal retry policy; direct
    single-call-then-fallback JSON parsing is no longer allowed in application code.
  - The architecture smoke suite should detect new JSON LLM services that bypass the
    shared policy where practical; otherwise the developer checklist must require it.
- Tests:
  - `fabula.researchDepth=marketResearch` produces `DraftRunBudget` depth
    `marketResearch`.
  - Malformed primary response triggers repair prompt for each migrated service group.
  - Malformed repair response triggers backup model when configured and distinct from
    primary.
  - All failed attempts produce explicit fallback/not-run/failed trace with safe errors.
  - Critic and alternative-angle candidate JSON errors no longer skip immediately to
    failure without retry.
  - Writer prompts include the public-prose/internal-jargon constraint.
  - Accepted revision cycles without resolved goals must include an explicit pairwise
    acceptance reason.
  - Existing material/rhetorical validation behavior remains compatible.
- Docs:
  - Update SAO, developer guide, ADR index/links, diagnostics checklist, and AS IS
    pipeline map/PDF after implementation.
- Acceptance criteria:
  - Given any child `AiRun` for a JSON-producing step, `/ai-runs?runId=...` can show
    all JSON attempts and why the final JSON result was accepted, repaired, backed up,
    or abandoned.
- Risks:
  - A universal policy can become too generic for role-specific prompts. Keep the
    retry engine shared, but let each service own its required schema and repair prompt
    details.
- Delivered:
  - Updated recommended writer/critic defaults in `.env.example` and documentation.
  - Added backend context propagation for `fabula.researchDepth`.
  - Added universal JSON retry to draft candidate generation and alternative-angle
    challenger prose generation; directed revision, editorial critique, validation,
    pairwise, rhetorical, material, and evidence interpretation already use the shared
    retry policy.
  - Writer/revision prompts now forbid leaking internal pipeline artifacts as
    unexplained public prose.
  - Revision-loop accepted cycles now store concrete acceptance reasons rather than
    empty success.
- Control run notes:
  - DraftRun `fcac701c-19e2-4aa0-bf30-95b8f8c6fe08` showed that
    `anthropic/claude-haiku-4.5` is unsuitable as current JSON writer: every writer
    JSON attempt failed and the run was saved by backup model attempts.
  - DraftRun `861500e3-f4b6-4a44-9767-edf86653af13` showed that
    `openai/gpt-4.1-mini` is reliable for writer JSON primary attempts, but the final
    prose is too report-like for a primary writer role. It should be treated as a
    technical backup or cheap baseline, not as the final recommended writer.
- Completed: 2026-06-27

### Slice 2.15.6.3.1: Writer Model Strength, Backup Separation, and Generation Params

- Status: Done
- Goal: Make the writer role strong enough for public prose while keeping a stable
  technical JSON backup path.
- User value:
  - Generated drafts should stop looking like cautious research summaries produced by
    a cheap backup model.
  - The team can evaluate writer quality without confusing primary writer behavior
    with emergency backup behavior.
- Scope:
  - Replace recommended writer default with a stronger primary model:
    `DRAFT_WRITER_MODEL=openai/gpt-4.1`.
  - Keep `OPENROUTER_BACKUP_MODEL=openai/gpt-4.1-mini` as a technical JSON backup in
    recommended local config and docs.
  - Keep `DRAFT_CRITIC_MODEL=openai/gpt-4.1` as a separate strict-review role, not
    another writer alias.
  - Keep `DRAFT_ANOTHER_ANGLE_MODEL=qwen/qwen3.7-max` as creative divergence.
  - Add role/step generation parameter settings:
    - `DRAFT_WRITER_TEMPERATURE`
    - `DRAFT_WRITER_TOP_P`
    - `DRAFT_REVISION_TEMPERATURE`
    - `DRAFT_REVISION_TOP_P`
    - `DRAFT_JSON_REPAIR_TEMPERATURE`
    - `DRAFT_ANOTHER_ANGLE_TEMPERATURE`
  - Defaults:
    - writer candidates: temperature `0.65`, top-p `0.9`;
    - directed revision: temperature `0.35`, top-p `0.85`;
    - JSON repair: temperature `0.15`;
    - another-angle route: temperature `0.8`.
  - Thread the effective params into OpenRouter request payloads and child `AiRun`
    trace metadata.
  - Ensure backup retries use backup params appropriate for JSON discipline, not the
    creative writer temperature.
  - Capture a sanitized raw response excerpt in child `AiRun` metadata when JSON parse
    fails, so diagnostics can distinguish empty output, markdown fences, prose instead
    of JSON, and malformed JSON.
  - Add a diagnostics checklist item: primary writer JSON success rate must be visible
    before judging prose quality.
- Out of scope:
  - Changing ranking, retrieval, evidence interpretation, or revision-loop acceptance
    policy.
  - A full A/B experiment harness; this slice only makes controlled A/B runs possible.
  - Full model A/B harness; Sonnet is recorded as an experimental prose candidate, not
    the current stable JSON writer default.
- Implementation notes:
  - Keep `openai/gpt-4.1-mini` as observed-good backup from DraftRun
    `861500e3-f4b6-4a44-9767-edf86653af13`.
  - Control DraftRun `c1a93b24-e3f0-407d-9186-db92aa2914e9` showed that
    `anthropic/claude-sonnet-4.5` still failed primary/repair writer JSON attempts
    and left the draft step long-running; therefore the stable writer default for this
    slice is `openai/gpt-4.1`.
  - Do not keep writer and backup equal in recommended configuration.
  - Parameter settings belong to backend config and provider request construction, not
    hard-coded prompt text.
- Architecture impact:
  - `DraftModelSelection` remains the source of model identity; generation params are
    a sibling selection artifact, not a new model role.
  - Trace must show both model role and generation params for provider calls whose
    output quality depends on them.
- Tests:
  - Settings load and normalize new writer/revision/repair/another-angle params.
  - Writer calls pass writer params.
  - Directed revision calls pass revision params.
  - JSON repair attempts pass low repair temperature.
  - Backup retries use backup model and repair-safe params.
  - JSON parse failures store a sanitized raw excerpt without secrets.
  - Old AiRun traces without params remain readable.
- Docs:
  - Update `.env.example`, README, SAO, developer guide, user guide, demo docs,
    diagnostics checklist, and AS IS pipeline map/PDF.
- Demo impact:
  - Demo DraftRun can be re-run with the stronger writer baseline and compared against
    the previous `gpt-4.1-mini` run.
- Acceptance criteria:
  - A fresh DraftRun can show `DRAFT_WRITER_MODEL=openai/gpt-4.1` as primary writer,
    `OPENROUTER_BACKUP_MODEL=openai/gpt-4.1-mini` as backup, effective params in trace,
    and no hidden writer/backup conflation.
- Risks:
  - Stronger writer may still produce report-like prose if prompts/context packs push
    it toward citation-heavy summaries. That is addressed by 2.15.6.4.
- Delivered:
  - Added role/attempt generation params for writer, directed revision, JSON repair,
    and another-angle calls.
  - OpenRouter JSON calls now support optional `top_p`.
  - Child `AiRun` request payloads record `generationParams`; JSON parse failures can
    carry sanitized raw response excerpts for diagnostics.
  - Recommended stable local portfolio is now writer `openai/gpt-4.1`, technical JSON
    backup `openai/gpt-4.1-mini`, critic `openai/gpt-4.1`, another-angle
    `qwen/qwen3.7-max`.
  - Sonnet `anthropic/claude-sonnet-4.5` was tested in DraftRun
    `c1a93b24-e3f0-407d-9186-db92aa2914e9`; it failed writer primary/repair JSON
    reliability and is not the current stable default.
- Control run:
  - DraftRun `d3197fda-2b71-4d43-b30f-2149555782be` completed successfully with
    `finalDraft`.
  - Writer primary `openai/gpt-4.1` succeeded for 3 draft candidates, 1 alternative
    candidate, and 3 directed revisions.
  - Effective params were visible in trace: writer `temperature=0.65/topP=0.9`,
    revision `temperature=0.35/topP=0.85`.
  - Remaining quality issues are not this slice: validation still reports warnings and
    public-source density/prose quality remains owned by 2.15.6.4.
- Completed: 2026-06-28

### Slice 2.15.6.4: Final Draft Quality Gate and Public Prose Repair

- Status: Done
- Goal: run a final machine acceptance check on the delivered `finalDraft` after
  `rankingRevision.revisionLoop`, then optionally make one targeted public-prose
  repair before returning the post to the editor.
- User value:
  - The author receives a final post, not an internal evidence report disguised as a
    post.
  - The trace explains whether final prose was accepted as-is, repaired, or kept
    unchanged because the repair regressed.
- Scope delivered:
  - Added `validation.rankingRevision.finalQualityGate`.
  - Gate computes `finalDraftStatus`, `publicProseStatus`,
    `sourceIntegrationStatus`, `internalJargonLeaks`, `sourceDumpRisk`,
    `authorVoiceStrength`, `readerValueClarity`, `finalRepairGoals`,
    `acceptedRepair`, and a gate-level `finalDecision`.
  - Gate detects unexplained internal terms such as `SourceLedger`,
    `publicEvidence`, `validators`, `PostContract`, and `RuleRegistry`.
  - Gate detects source-dump risk relative to `Fabula.researchDepth` instead of a
    global source-count rule.
  - If status is `warning` or `critical`, gate builds one final repair instruction and
    calls the existing writer directed-revision service.
  - Final repair is accepted only after deterministic regression guard and public
    prose improvement checks pass; otherwise the previous best draft remains the
    delivered `finalDraft`.
  - `/ai-runs?runId=...` shows a separate `Final quality gate` semantic section with
    status, repair goals, repair decision, and final source.
- Out of scope:
  - A second candidate tournament.
  - Full LLM validation rerun after final repair.
  - Human editor decision learning; remains Slice 2.16.
- Architecture impact:
  - `backend/app/application/draft_final_quality_gate.py` owns the final public-prose
    acceptance and one-shot repair handoff.
  - `draft_ranking_revision_service.py` remains the thin integration point that
    chooses the final candidate after the gate.
- Tests:
  - Clean final draft passes without repair.
  - Internal jargon leak creates final repair goals.
  - Accepted final repair becomes the delivered final draft.
  - Rejected final repair remains visible in trace but does not replace final draft.
  - Trace renders `Final quality gate` separately from validation, revision loop, and
    final draft decision.
- Completed: 2026-06-28

### Slice 2.15.6.4.1: Final Quality Contract and Independent Gate Review

- Status: Done
- Goal: make final draft acceptance contract-based and model-independent instead of
  relying only on deterministic heuristics plus writer self-repair.
- User value:
  - The returned draft is judged against the selected editorial model, fabula,
    research depth, publication kind, and post contract, not against hardcoded taste.
  - Research-heavy posts can remain source-heavy when the fabula asks for research,
    while ordinary author posts are protected from becoming source inventories.
  - The trace explains who accepted the final prose, by which criteria, and whether
    post-repair quality actually improved.
- Scope:
  - Add `FinalQualityContract` under existing
    `validation.rankingRevision.finalQualityGate`.
  - Build the contract from `PostContract`, `RuleRegistrySnapshot`,
    `Fabula.researchDepth`, `Fabula.sizeIntent`, publication kind, source/evidence
    obligations, and available editorial model/fabula settings.
  - Add config:
    - `DRAFT_FINAL_GATE_MODEL=`
    - `DRAFT_FINAL_REPAIR_MAX_ITERATIONS=2`
  - Replace the current writer recommendation
    `DRAFT_WRITER_MODEL=openai/gpt-4.1` with a stronger primary writer model.
    Recommended candidate for the slice: `DRAFT_WRITER_MODEL=openai/gpt-5.1`.
    Rationale: `gpt-4.1` was stable for JSON, but it is no longer strong enough to
    be the main prose/revision engine for this pipeline. `openai/gpt-5.1` is available
    on OpenRouter, has a larger context window, and is positioned for stronger
    instruction following and more natural long-form output. Keep
    `OPENROUTER_BACKUP_MODEL=openai/gpt-4.1-mini` as technical JSON backup, not as
    creative writer.
  - Add a final-gate model resolver:
    - use `DRAFT_FINAL_GATE_MODEL` when configured;
    - otherwise use `DRAFT_CRITIC_MODEL` if it differs from `DRAFT_WRITER_MODEL`;
    - otherwise use `DRAFT_REVIEW_MODEL`;
    - record `modelIndependence=weak` when final gate and writer use the same model.
  - Replace the current critic recommendation
    `DRAFT_CRITIC_MODEL=openai/gpt-4.1` with a non-writer, non-Anthropic default.
    Recommended candidate for the slice: `DRAFT_CRITIC_MODEL=google/gemini-2.5-pro`
    if available through OpenRouter; otherwise use the strongest stable non-writer
    model already configured locally. Do not switch critic to Anthropic until JSON
    reliability is proven.
  - Final gate performs an independent JSON review of the delivered final draft
    using the final quality contract and the universal JSON retry policy.
  - Final repair becomes a bounded loop:
    gate review -> repair goals -> writer repair -> gate recheck, up to
    `DRAFT_FINAL_REPAIR_MAX_ITERATIONS`.
  - Acceptance compares pre/post gate reports and accepts repair only when contract
    findings improve without deterministic regression.
  - Add specific contract-aware checks:
    - source density is evaluated relative to `researchDepth` and publication kind;
    - source mentions must feed author interpretation rather than become inventory;
    - author voice is judged against explicit editorial/fabula settings when present;
    - invented examples must be source-backed or clearly marked as hypothetical;
    - internal pipeline jargon remains forbidden in public prose.
  - Fix source task normalization found in DraftRun
    `8b30bc91-1f78-4c24-9ed0-7c5b517eb4b6`: `namedSource` values without an HTTP
    URL must not become `readUrl`; they should become search/named-source lookup
    tasks or explicit skipped diagnostics.
- Out of scope:
  - Adding new DraftRun steps or SQL schema.
  - Human editor decision learning; remains Slice 2.16.
  - A new candidate tournament.
  - Hardcoding one global definition of "good prose" independent of editorial model
    and fabula.
- Implementation notes:
  - Keep `draft_final_quality_gate.py` as the orchestration owner, but move final
    contract construction and final-gate LLM parsing into role-owned modules.
  - The independent gate is review/critic work, not writer work; writer only performs
    repair instructions after the gate produces actionable findings.
  - Use ADR `2026-06-27-llm-json-steps-use-universal-retry-policy`; final-gate JSON
    must run primary -> repair -> optional backup -> explicit failed/not-run.
- Architecture impact:
  - Final draft acceptance becomes a contract layer over the delivered prose.
  - Model independence becomes trace-visible for final acceptance.
  - Final repair loop remains inside `validation.rankingRevision.finalQualityGate`;
    no new `DraftRunStepKey`.
- Tests:
  - Contract builder reflects research depth, publication kind, fabula scale, and
    source integration expectations.
  - Gate review uses configured `DRAFT_FINAL_GATE_MODEL` and falls back through the
    documented resolver.
  - Writer calls use the new recommended `DRAFT_WRITER_MODEL=openai/gpt-5.1` and
    still follow universal JSON retry; if `gpt-5.1` cannot reliably return writer
    JSON in the control run, the slice must record the failure and choose the next
    strongest stable writer candidate before being marked Done.
  - Writer and final gate using the same model records `modelIndependence=weak`.
  - `DRAFT_FINAL_REPAIR_MAX_ITERATIONS=2` allows at most two final repair cycles.
  - Research-heavy contract tolerates more source references than light/standard
    author posts, but still requires interpretation.
  - Unmarked invented example creates a gate finding; marked hypothetical example can
    pass when the contract allows it.
  - `namedSource` without URL no longer triggers URL fetch failure.
  - Old runs without `FinalQualityContract` remain readable.
- Docs:
  - Update `.env.example`, README, SAO, developer guide, user guide, demo docs,
    diagnostics skill, AS IS pipeline map, and regenerated PDF.
- Demo impact:
  - Demo should show final gate contract/review/repair cycles in `/ai-runs` trace.
- Acceptance criteria:
  - A fresh DraftRun shows final gate model role, selected model, independence status,
    final quality contract, pre/post repair reports, and clear final decision.
  - The same run shows writer primary attempts using a stronger non-`gpt-4.1` model
    with valid JSON and no immediate fallback to the technical backup.
  - If final text remains warning after repair limit, trace explains why the previous
    best draft was returned and what unresolved findings remain.
- Risks:
  - `google/gemini-2.5-pro` OpenRouter slug/availability may differ locally; keep the
    env value overrideable and verify during the slice.
  - `openai/gpt-5.1` may require prompt/parameter tuning for strict writer JSON even
    if prose quality improves; the slice must judge both JSON reliability and prose
    direction before changing the stable default.
  - A stronger gate can over-constrain creative prose if contract construction ignores
    fabula/editorial settings; tests must cover research-heavy and author-opinion
    variants.
- Completed: 2026-06-28
- Delivered:
  - Added `FinalQualityContract` and independent `finalGate` model review under
    `validation.rankingRevision.finalQualityGate`.
  - Added `DRAFT_FINAL_GATE_MODEL` and `DRAFT_FINAL_REPAIR_MAX_ITERATIONS=2`.
  - Updated recommended model defaults: writer `openai/gpt-5.1`,
    critic/final gate `google/gemini-2.5-pro`, backup `openai/gpt-4.1-mini`.
  - Final quality repair now supports bounded cycles and accepts repairs only when
    gate findings improve without deterministic regression.
  - Named sources without HTTP URLs are sanitized away from `readUrl` into searchable
    source tasks.
  - `/ai-runs` trace shows final quality contract, independent review attempts,
    repair cycles, and final decision.

### Slice 2.15.6.4.2: Final Gate Attribution Handoff Repair

- Status: Done
- Goal: repair false final-gate attribution warnings caused by free-text
  `claimsRequiringAttribution` values that cannot be resolved to source-backed claim
  provenance.
- User value:
  - The final gate no longer starts needless final repair when the public prose
    visibly names sources and the independent final-gate review passes source
    integration.
  - `/ai-runs?runId=...` distinguishes real missing attribution from diagnostic
    material-plan handoff noise.
- Scope delivered:
  - Added deterministic attribution requirement normalization for material-plan
    attribution requirements.
  - Free-text requirements such as `95% ... attribute to B2BNotes` now map to
    external ledger claims by source title, URL/domain, source label, and provenance
    markers.
  - Unresolvable attribution requirements are recorded as diagnostic metadata and
    `evidence.attribution.diagnostic`, not as actionable warning findings.
  - Final quality gate now separates `actionableAttributionFindings` from
    `diagnosticAttributionNoise` and records `attributionReview`.
  - `FinalQualityContract` records resolved attribution claim ids plus unresolved
    attribution requirements and requirement matches.
  - `/ai-runs` final gate trace shows attribution review, actionable findings, and
    diagnostic attribution noise.
  - `GET /api/draft-runs/{id}` now returns top-level `completedAt` computed from the
    completed `complete` step when the parent table has no separate completion column.
- Out of scope:
  - New DraftRun steps, SQLite migration, source retrieval changes, ranking changes,
    and prose-generation changes.
- Tests:
  - Free-text attribution maps to external claim ids by source marker.
  - Unresolved free-text attribution is diagnostic and does not create warning status.
  - Final gate does not run repair solely for non-actionable attribution noise when
    independent source integration passes.
  - Completed DraftRun API response exposes `completedAt`.
- Autofix note:
  - Control DraftRun `2fd74512-78b8-4146-989a-d446d255f273` exposed that the
    alternative-angle challenger path re-ran expensive LLM validation and editorial
    critique for already validated original candidates. This produced stale-looking
    validation progress and unnecessary provider churn. The repair keeps the pipeline
    shape but validates only the challenger after merge, then combines challenger
    reports with the initial validation reports.
  - Follow-up control DraftRun `73efa020-c39e-4328-b604-5c78b1161121` exposed that
    evidence interpretation inside `rulePack` could make the run look stale on the
    previous `postContract` step while JSON retries were still happening. The repair
    marks `rulePack` as running before evidence interpretation and records nested
    `evidenceInterpretation` operations for primary/repair/backup attempts.
- Docs:
  - Updated AS IS pipeline map, developer guide, diagnostics skill, and regenerated
    PDF.
- Completed: 2026-06-28

### Slice 2.16: Versioned Human Revision Loop and Editor Decision Snapshot

- Status: Done
- Goal: Add an unlimited human-in-the-loop revision cycle after the machine
  `finalDraft`, while capturing the editor's final decision against the actual
  machine trace.
- User value:
  - The editor can comment on the delivered draft, ask the system to improve it,
    receive `v2`, `v3`, `v4`, and continue as many times as needed.
  - The editor can select any version as final, including `v1`; the latest version
    is not automatically the approved version.
  - The final decision is understandable: selected version, remaining risks,
    validation status, final-gate status, and the human comments that shaped it are
    visible together.
- Scope:
  - Convert the delivered machine `finalDraft` into draft version `v1` in the
    editing workspace.
  - Add local `draftVersions[]` with `versionId`, `versionNumber`, `source`,
    `baseVersionId`, `title`, `body`, `comment`, `revisionSummary`, `aiRunId?`,
    `createdAt`, and `selectedAsFinal`.
  - Add an editor comment flow in `Редактура -> Рабочий стол -> Драфт`:
    comment field, `Улучшить по комментарию`, version list, version preview, and
    `Сделать финальной`.
  - Add a backend endpoint for one human-comment revision call:
    current version + editor comment + compact DraftRun context -> revised title/body
    + `revisionSummary` + child `AiRun ID`.
  - Store `EditorDecisionSnapshot` when a version is selected as final. It must link
    the human decision to:
    - selected version id and source;
    - base DraftRun id;
    - `finalQualityGate` summary;
    - `revisionLoop` stop reason and accepted/rejected cycles summary;
    - `alternativeAngleTournament` status/outcome;
    - deterministic and LLM validation summary for the delivered machine candidate;
    - unresolved risks and warnings still relevant to the selected version;
    - editor comments and manual edits made before selection.
  - Manual text edits create a version with `source=manualEdit` rather than mutating
    an existing version in place.
  - Failed human-comment revision does not create a new version; UI shows a clear
    error and keeps the current version list intact.
- Out of scope:
  - Cross-post learning, rule-improvement queue, or automatic updates to Topic,
    Fabula, publisher rules, prompts, model choices, or validators.
  - LLM comparison of all human versions.
  - Multi-user approval workflow.
  - Backend long-term persistence for editor learning beyond the existing local
    workspace and child `AiRun` trace.
- Implementation notes:
  - One human comment produces one backend revision attempt. The loop is unlimited
    because the editor can submit another comment, not because the backend runs an
    autonomous loop.
  - Human revision prompt must preserve `PostContract`, allowed claim ids, forbidden
    moves, source attribution constraints, and final quality contract.
  - Use the writer role and existing JSON retry discipline for the human-comment
    revision endpoint.
  - The `EditorDecisionSnapshot` is a per-post decision record, not a learning engine.
- Architecture impact:
  - No new DraftRun step is required.
  - Add frontend/local workspace version state and a small backend application service
    for human-comment revision.
  - If new trace or child `AiRun` semantics are added, update
    `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` and regenerate
    `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf`.
- Tests:
  - Machine `finalDraft` becomes version `v1`.
  - A human comment creates `v2`; a second comment creates `v3`.
  - The editor can select `v1` as final after `v3` exists.
  - Manual edit creates a `manualEdit` version.
  - Failed revision call does not create a new version.
  - `EditorDecisionSnapshot` includes selected version, DraftRun id,
    final-gate/revision/alternative-angle/validation summaries, unresolved risks, and
    human comments.
  - Existing DraftRun polling and trace views remain compatible.
- Docs:
  - Update README, developer guide, user guide, demo docs, AS IS pipeline map, and PDF.
- Demo impact:
  - Demo should show at least one machine final draft, one human comment revision,
    and choosing a non-latest version as final.
- Acceptance criteria:
  - The editor can run an unlimited comment -> revision -> version cycle.
  - Versions are immutable and numbered.
  - Any version can be selected as final.
  - Final selection produces an `EditorDecisionSnapshot` grounded in the actual
    machine trace, not a generic acceptance flag.
- Risks:
  - Version state can become confusing if UI does not clearly distinguish selected,
    previewed, latest, and final versions.
  - Human-comment revision may accidentally violate source/contract constraints if the
    prompt does not carry the compact final-quality context.
- Dependency:
  - Requires 2.15.6.2-2.15.6.4.2 so the decision snapshot observes controlled
    research depth, universal JSON retry behavior, contract-based final draft
    acceptance, and calibrated final-gate attribution handoff.
- Completed: 2026-06-28

### Slice 2.16.0.1: HITL Revision Quality Check and Comment Compliance Trace

- Status: Done
- Goal: Add a diagnostic quality layer for every human-comment revision created
  after the machine `finalDraft`.
- User value:
  - The editor can see whether a new `v2/v3/...` actually followed the comment.
  - The editor can see risks such as lost source markers, internal pipeline jargon,
    public-prose regression, or missed comment intent before choosing a version as
    final.
  - A warning does not block the HITL loop; it makes the trade-off visible.
- Scope:
  - Extend `POST /api/drafts/revise-with-comment` so a successful writer revision is
    followed by a lightweight review-role quality check.
  - Use existing JSON retry discipline for the check: primary, repair, optional backup,
    then `notRun` if no usable result is available.
  - Add `HumanCommentRevisionQualityCheck` with status, comment compliance, source
    integrity, public prose status, internal jargon leaks, regression warnings,
    matched/missed comment intents, summary, and attempts.
  - Store `qualityCheck` on `DraftVersion` for `source=humanCommentRevision`.
  - Show compact version quality status in the draft version list and readable
    quality summary for the active version.
  - Keep quality check diagnostic only: failed/unavailable review does not cancel a
    successfully created version, and warning/critical versions can still be selected
    as final.
- Out of scope:
  - Learning-signal aggregation and rule-improvement queue; remains 2.16.1.
  - Blocking human revisions or automatically choosing the best human version.
  - New DraftRun steps, SQLite migration, or turning human revisions into DraftRuns.
- Tests:
  - Backend endpoint returns `qualityCheck` on successful human revision.
  - Malformed/unavailable review returns a created revision with `qualityCheck.notRun`.
  - Regression overlay detects missed source markers and internal jargon leaks.
  - Frontend stores quality metadata on versions and renders warning/pass/unavailable
    status without blocking final selection.
- Docs:
  - Updated README, developer guide, user guide, demo docs, AS IS pipeline map, and PDF.
- Completed: 2026-06-29

### Slice 2.16.1: Editorial Learning Notes in Author Memory

- Status: Done
- Goal: Capture post-run human editing lessons as reviewable auto-notes inside
  `Память автора`, not as a separate hidden rule queue.
- User value:
  - The author can see what the system thinks it learned from final version choice,
    human comments, manual edits, rejected versions, and HITL quality checks.
  - Nothing silently changes rules, prompts, topics, fabulas, or validators.
  - A learning note becomes active memory only after the editor accepts it.
- Scope:
  - Add `AuthorNote.type = editorialLearning` with UI label
    `Редакторское наблюдение`.
  - Create or update one deterministic auto-note when the editor marks a draft
    version as final.
  - Store structured `editorialLearning` metadata: linked `finalTextId`, `draftId`,
    optional `draftRunId`, selected version, machine `v1`, human comments, manual edit
    count, rejected version ids, quality-check summaries, unresolved risks, suggested
    takeaway, and status `pendingReview | accepted | rejected`.
  - Add tags `editorial-learning`, `hitl`, `draft-version`, plus detected signals such
    as `author-stance`, `tone`, `source-integration`, `structure`, and
    `comment-compliance`.
  - Show the notes in `Память автора` with an `Авто` badge and status
    `На проверке / Принято / Отклонено`.
  - Add filter `Редакторские наблюдения`.
  - Let pending notes be accepted, rejected, or edited from the author-memory feed.
  - Exclude pending/rejected learning notes from author-position inference; accepted
    notes participate through normal author-memory events.
- Out of scope:
  - Automatic mutation of publisher rules, Topic, Fabula, validators, prompts, model
    choices, or drafting settings.
  - A separate rule-improvement queue.
  - New backend persistence or cloud/cross-user learning.
  - New LLM calls; learning note text and metadata are deterministic.
- Implementation notes:
  - Note id is deterministic from `FinalText.id`, so repeated final-save of the same
    decision updates the note rather than creating duplicates.
  - Selecting an older version after human or machine revisions records rejected
    version ids and rejected-machine-move context.
  - Quality-check warnings explain why a rejected version may have been rejected, but
    they are not promoted into a rule.
- Tests:
  - Legacy author notes normalize unchanged.
  - Legacy `editorialLearning` notes normalize to pending review metadata.
  - Final version selection creates one pending learning note.
  - Repeating the same final decision does not create duplicates.
  - Pending/rejected notes do not affect `inferAuthorPositionAssertions`.
  - Accepted learning notes create author-memory events and can influence inference.
  - UI shows the learning-note filter, status badges, and accept/reject actions.
  - Choosing `v1` after `v2/v3` records rejected version ids.
- Docs:
  - Updated README, SAO, developer guide, user guide, demo docs, AS IS pipeline map,
    and PDF.
- Acceptance criteria:
  - Final selection creates a readable pending editorial-learning note in Author
    Memory.
  - The editor controls whether the learning becomes active memory.
  - No rule/prompt/model mutation happens in this slice.
- Completed: 2026-06-29

### Slice 2.16.1.1: Seeded HITL Learning Demo Scenarios

- Status: Done
- Goal: Make the 2.16/2.16.0.1/2.16.1 HITL learning mechanism visible immediately
  in the demo workspace after reset/seed.
- User value:
  - The editor can open the app and see a ready versioned draft with human comments,
    quality-check metadata, a non-latest final version, and the linked
    `Редакторское наблюдение` in Author Memory.
  - The seeded scenario demonstrates the product loop without requiring a live
    DraftRun, OpenRouter calls, or manual setup.
- Scope delivered:
  - Added a seeded post draft with immutable versions:
    - `v1`: machine final;
    - `v2`: human-comment revision for `усиль авторскую позицию`, selected as final;
    - `v3`: human-comment revision for `добавь 3 критерия`, kept as rejected risk;
    - `v4`: manual/editorial version for `убери сухой отчетный тон`, also rejected.
  - Added realistic `qualityCheck` metadata for human-comment versions:
    matched/missed intents, source/public-prose/internal-jargon status, and warning/pass
    summaries.
  - Added a linked `FinalText.editorDecisionSnapshot` where `v2` is final even though
    later versions exist.
  - Seeded one pending `AuthorNote.type=editorialLearning` with selected/rejected
    versions, comments, quality-check summaries, unresolved risks, and suggested
    takeaway.
  - Kept `editorialLearning` unavailable in the manual composer; it remains an
    auto-note type.
- Out of scope:
  - New backend DraftRun behavior, new LLM calls, or substituting real HITL runs.
  - Changing author-memory inference rules beyond demonstrating pending vs accepted
    note behavior.
- Tests:
  - Demo workspace contains the versioned HITL draft, quality checks, final snapshot,
    and pending editorial-learning note.
  - Pending seeded note does not affect author-position inference until accepted.
  - `Редактура -> Рабочий стол -> Драфт` renders seeded versions and final marker.
  - `Память автора -> Редакторские наблюдения` renders the seeded auto-note and lets
    the editor accept it into memory.
- Docs:
  - Updated README, user guide, and demo docs so the seeded scenario can be found in
    the UI.
- Completed: 2026-06-29

### Slice 2.17.0: SaaS Blog Portfolio Architecture

- Status: Done
- Goal: Define the SaaS-ready product boundary around users, independent blog
  projects, publication channels, and benchmark portfolios before changing runtime
  state.
- User value:
  - The product direction becomes clear: one author can operate several independent
    media systems without memory, learning, channels, or drafting traces leaking
    between them.
  - The three real blog ideas become first-class benchmark targets instead of loose
    examples.
- Scope:
  - Document `UserAccount`, `BlogProject`, `ProjectMembership`,
    `PublicationChannel`, `PublicationGroup`, and `PlatformVariant` boundaries.
  - Define which data is user-scoped, project-scoped, and channel-scoped.
  - Define the target hierarchy:
    `UserAccount -> BlogProject -> Author Memory / Editorial Model / Publication Channels -> Content Production -> Platform Variants -> Learning`.
  - Capture the decision in ADR
    `docs/adr/2026-06-29-blog-project-portfolio-saas-boundary.md`.
  - Add detailed architecture contract
    `docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md`.
  - Update SAO, README, user/developer/demo docs, and roadmap.
- Out of scope:
  - Runtime auth UI.
  - Backend auth/session implementation.
  - New storage migration.
  - Multi-platform DraftRun execution.
- Implementation notes:
  - `BlogProject` represents one independent blog/media system, not a platform.
  - Existing `WorkspaceState` should become project-scoped in later slices.
  - Do not couple fabulas directly to Telegram, LinkedIn, Dzen, or any other platform;
    platform constraints resolve in channel/contract layers.
- Architecture impact:
  - Establishes the next product boundary above the current local workspace.
  - Keeps DraftRun pipeline intact while preparing project/channel context.
- Tests:
  - Documentation-only slice: `git diff --check` passed.
- Docs:
  - ROADMAP, SAO, README, developer guide, user guide, demo docs, ADR, and SaaS blog
    portfolio architecture document.
- Demo impact:
  - Defines the upcoming two-user / three-blog demo benchmark portfolio.
- Acceptance criteria:
  - Docs explain why SaaS starts with `BlogProject`, not autoposting. Done.
  - Next implementation slice is clearly `2.17.1`. Done.
  - Three target blogs and benchmark use are recorded. Done.
- Risks:
  - If this layer is skipped, later auth and platform work may hard-code singleton
    workspace assumptions.
- Completed: 2026-06-29

### Slice 2.17.1: Local Multi-Account and Blog Project Switcher

- Status: Done
- Goal: Add a local-first SaaS shell with demo users and project switching while
  keeping the current editorial workspace intact inside one selected project.
- User value:
  - The app starts to feel like SaaS: the user selects an account and then a blog
    project.
  - One user can have two independent blogs, and another user can have one blog.
- Scope:
  - Add local `UserAccount`, `BlogProject`, and `ProjectMembership` domain contracts.
  - Add `activeUserId`, `activeProjectId`, and `workspacesByProjectId` storage shape.
  - Migrate the current singleton workspace into the first selected project.
  - Add project switcher UI to the app shell.
  - Keep all existing sections project-scoped by selected project.
- Out of scope:
  - Real authentication/security.
  - Backend persistence.
  - Team roles beyond demo owner/member metadata.
  - Multi-platform variants.
- Implementation notes:
  - This is a local SaaS simulation, not an auth guarantee.
  - Keep old workspace normalization compatible.
  - Keep portfolio/project logic in role-owned modules; do not expand near-limit
    workspace, demo fixture, or DraftRun context files.
- Architecture impact:
  - Added a local portfolio store around project-scoped `WorkspaceState` without
    changing backend persistence or DraftRun contracts.
  - Existing singleton workspace storage is migrated into a default project when
    present.
- Tests:
  - Storage migration tests. Done.
  - UI app-flow tests for switching users/projects. Done.
  - Regression: `npm test -- --run`, `npm run smoke`, `npm run test:architecture`,
    `npm run test:design`, `npm run test:visual`, `docker compose config --quiet`,
    and `git diff --check`.
- Docs:
  - README, user guide, developer guide, demo docs, roadmap.
- Demo impact:
  - Demo opens with user/project choices instead of one implicit workspace.
  - Slice 2.17.1 seeds the local shell with two users and three project containers;
    Slice 2.17.2 adds realistic per-blog memory/editorial/benchmark content. Done.
- Acceptance criteria:
  - Switching projects does not leak notes, drafts, learning notes, or plan state.
    Done.
  - Existing single-workspace reset remains backward compatible. Done.
- Risks:
  - Project shell can become heavy; keep it a thin wrapper around existing workspace.
- Completed: 2026-06-29

### Slice 2.17.1.1: Sidebar Portfolio Switcher Placement Repair

- Status: Done
- Goal: Move local user/blog switching from the extra top strip into the sidebar
  identity block.
- User value:
  - The workbench regains vertical space.
  - Account and blog context live where users expect global identity controls.
- Scope:
  - Replace the top portfolio strip with a compact sidebar footer switcher.
  - Keep the local portfolio store, domain contracts, and project isolation unchanged.
  - Show current blog and user in the collapsed footer state.
  - Reveal user/blog selectors in an inline sidebar panel.
- Out of scope:
  - Backend auth.
  - Project settings screen.
  - Real per-blog demo content.
- Architecture impact:
  - Keeps `src/app` as shell composition: App passes a sidebar footer node, while
    portfolio UI stays feature-owned.
  - Removes the temporary top-level portfolio UI from the main content column.
- Tests:
  - UI app-flow test verifies the switcher is inside `aside.side`, not `main.main`.
  - Project/user switching and project isolation tests remain green.
- Docs:
  - Updated roadmap, SaaS portfolio architecture, user guide, and demo docs.
- Demo impact:
  - Demo portfolio control now appears in the lower-left sidebar identity area.
- Completed: 2026-06-30

### Slice 2.17.2: Three-Blog Benchmark Demo Portfolio

- Status: Done
- Goal: Seed two users and three realistic blog projects as demo and benchmark data.
- User value:
  - The app demonstrates real variation: different author memory, editorial models,
    platforms, languages, research depth, and quality criteria.
  - The same pipeline can be judged against more than one content style.
- Scope:
  - Add demo user A with two independent blogs:
    - `AI Design Patterns`;
    - `Каша из топора`.
  - Add demo user B with one blog:
    - `Блог Главреда`.
  - Seed each blog with project profile, author memory, editorial rules, topics,
    fabulas, publication channels, source/radar examples, plan slots, and at least one
    benchmark scenario. Done.
  - Define per-blog benchmark expectations:
    - `AI Design Patterns`: initial research-heavy pattern catalog seed; superseded by 2.17.4.1 as Russian Telegram-first industrial AI.
    - `Каша из топора`: Telegram-native author voice, RevOps/Product Marketing,
      irony, strong stance, not consulting memo.
    - `Блог Главреда`: product philosophy, practical cases, build-in-public,
      multi-platform Telegram/Dzen adaptation.
- Out of scope:
  - Live ingestion from real channels.
  - Private user materials committed to Git.
  - Automated benchmark runner.
- Implementation notes:
  - Public repository fixtures must stay sanitized.
  - Real private inputs can later live in a gitignored benchmark pack.
  - Implemented fixture ownership in `src/fixtures/demoBenchmarkPortfolio.ts` to avoid
    expanding near-limit `demoWorkspace.ts`.
- Architecture impact:
  - Turns demo data into benchmarkable portfolio fixtures.
  - Keeps the existing local portfolio contracts unchanged.
- Tests:
  - Demo fixture tests for project isolation and seeded data completeness.
  - UI smoke for project switcher and per-blog landing context.
- Docs:
  - Demo README, user guide, roadmap.
- Demo impact:
  - The old AI Product Manager demo becomes one benchmark-like project or is migrated
    into the new portfolio.
- Acceptance criteria:
  - After reset, all three blogs are visible and distinct.
  - Each blog has enough memory/editorial data to run the existing production flow.
- Risks:
  - Demo data can become too large; keep each blog representative, not exhaustive.
- Completed: 2026-06-30

### Slice 2.17.3: Backend Auth and Project Persistence Boundary

- Status: Done
- Goal: Introduce the first real backend boundary for users, sessions, projects, and
  project-scoped workspace persistence.
- User value:
  - The SaaS shell stops being only local demo state and can evolve toward real
    accounts.
- Scope:
  - Add backend contracts for users, sessions, projects, memberships, and workspace
    snapshots.
  - Add thin FastAPI routes and application services.
  - Add dev-safe auth mode suitable for local testing.
  - Frontend starts backend-first: authenticated session loads backend projects and
    workspace snapshots; `401` shows login; network failure falls back to local demo.
- Out of scope:
  - Full production auth provider selection.
  - Billing, organizations, invites, SSO.
  - DraftRun schema changes unless required to link runs to projects.
- Implementation notes:
  - Backend routes remain thin; project persistence is an application service.
  - Do not persist secrets or `.env` values.
- Architecture impact:
  - Starts moving project state behind backend without rewriting DraftRun.
- Tests:
  - Backend API tests, frontend integration tests, architecture smoke.
- Docs:
  - Developer setup, env docs, SAO, and ADR
    `2026-06-30-dev-password-session-auth-boundary`.
- Demo impact:
  - Demo can run in local-only or backend-backed project mode.
- Acceptance criteria:
  - A project can be loaded/saved through backend in dev mode.
  - Project isolation survives backend round-trip.
- Risks:
  - Auth can sprawl; keep v1 deliberately narrow.
- Completed: 2026-06-30

### Slice 2.17.3.1: Project Dashboard and Project Lifecycle UX

- Status: Done
- Goal: Make the project dashboard the default post-login destination and add the
  first project lifecycle actions.
- User value:
  - A user sees the portfolio first, opens the intended blog deliberately, and can
    create, rename, or archive projects without entering the wrong cabinet.
- Scope:
  - Add app-level `projectDashboard | projectCabinet` navigation mode.
  - Show active projects as dashboard cards with description, language, status,
    benchmark role, update date, and compact workspace summary.
  - Add `Новый проект`, `Переименовать`, and soft `В архив` actions.
  - Keep the lower-left project switcher inside the cabinet and add `Все проекты`.
  - Add backend `POST /api/projects`, `PATCH /api/projects/{projectId}`, and
    `GET /api/projects?includeArchived=true`.
  - Add matching local fallback lifecycle operations.
- Out of scope:
  - Publication channels.
  - Project deletion.
  - Organization/team administration.
  - DraftRun pipeline changes.
- Implementation notes:
  - Archive is a soft project status; snapshots are preserved.
  - Backend mode and local fallback use the same dashboard UX.
  - New project creation starts from a minimal normalized workspace, not an onboarding
    wizard.
- Architecture impact:
  - Portfolio lifecycle logic stays in backend services and role-owned frontend
    modules instead of screen-level shortcuts.
- Tests:
  - Backend lifecycle API tests and frontend dashboard/switcher/backend-store tests.
- Docs:
  - README, user guide, developer guide, demo docs, and SaaS portfolio architecture.
- Demo impact:
  - Demo now starts from a portfolio dashboard rather than immediately entering the
    default project.
- Acceptance criteria:
  - Login leads to dashboard.
  - Opening a card enters the selected project cabinet.
  - `Все проекты` returns from cabinet to dashboard.
  - Archive hides projects from active list and shows them in archive filter.
- Risks:
  - Project lifecycle can become a full admin console; keep this slice to owner-local
    create/rename/archive.
- Completed: 2026-06-30

### Slice 2.17.3.2: Project Dashboard Layout Polish

- Status: Done
- Goal: Make the post-login project dashboard feel like a compact SaaS workspace
  instead of a sparse stretched page.
- User value:
  - A user can recognize account-level navigation and see project cards as stable
    tiles, including the single-project case.
- Scope:
  - Add a dashboard-level left sidebar with account identity, session status, and
    account navigation placeholders: `Проекты`, `Аккаунт`, `Статистика`, `Биллинг`,
    and `Настройки`.
  - Keep only `Проекты` functional in this slice; do not fake account, billing, or
    analytics sections.
  - Constrain project cards to a bounded tile grid with at most two cards per row on
    desktop and one column on narrower screens.
  - Keep project lifecycle behavior from 2.17.3.1 unchanged.
- Out of scope:
  - Real account settings, billing, statistics, team management, or routing.
  - Backend API changes.
  - Publication channel modeling.
- Architecture impact:
  - Dashboard polish stays inside the portfolio feature UI and shared styles; no
    DraftRun, storage, or backend contracts change.
- Tests:
  - Project dashboard component coverage for account navigation and dashboard shell.
  - Design, visual, architecture, smoke, and regression checks.
- Docs:
  - README, user guide, developer guide, demo docs, SaaS portfolio architecture, and
    roadmap.
- Acceptance criteria:
  - A single project card no longer stretches across the full dashboard width.
  - Two projects render as a two-card row on desktop.
  - Dashboard has visible account navigation while project cabinets keep their
    lower-left project switcher.
  - Placeholder account sections are visible but disabled until later slices.
- Completed: 2026-06-30

### Slice 2.17.3.3: Project Dashboard App Shell Alignment

- Status: Done
- Goal: Align the project dashboard with the editorial cabinet shell instead of
  rendering it as a separate sparse page.
- User value:
  - The portfolio entry point feels like the same product as the project cabinet:
    full-height left navigation, topbar, centered working canvas, and stable project
    tiles.
- Scope:
  - Rebuild `ProjectDashboardView` as a dashboard-local app shell using the same
    structural patterns as the cabinet: `.app`, `.side`, `.main`, `.topbar`, and
    `.scroll`.
  - Keep `AppShell` itself out of the dashboard because it is tied to
    `WorkspaceSection` and project-cabinet navigation.
  - Move the owner profile block to the sidebar footer and keep `Проекты`,
    `Аккаунт`, `Статистика`, `Биллинг`, and `Настройки` in the left navigation.
  - Center dashboard content in a working canvas close to the combined width of the
    cabinet's central and right columns.
  - Keep `Новый проект` under the page header, above summary/filter/grid controls.
  - Keep the project grid at two cards per desktop row, one column on narrow screens,
    and a bounded centered layout for single-project users.
- Out of scope:
  - Backend API changes.
  - Account, billing, statistics, or settings implementation.
  - Publication channel modeling.
- Architecture impact:
  - Dashboard shell alignment remains a portfolio UI concern; project lifecycle,
    storage, auth, and DraftRun behavior stay unchanged.
- Tests:
  - Project dashboard component tests assert shell structure, sidebar footer owner,
    disabled account placeholders, action placement, and single-card grid mode.
  - Design, visual, architecture, smoke, and regression checks.
- Docs:
  - README, user guide, developer guide, demo docs, SaaS portfolio architecture, and
    roadmap.
- Acceptance criteria:
  - Dashboard root uses the product app shell structure.
  - Owner profile is shown in the sidebar footer, not the top of a floating card.
  - `Новый проект` appears below the page header.
  - A single project card remains bounded and centered.
- Completed: 2026-07-01

### Slice 2.17.3.4: Roadmap Tracker Source of Truth

- Status: Done
- Goal: Move roadmap editing behind a SQLite-backed CLI, reviewable JSONL export, and generated Markdown report.
- User value: Agents can query and update roadmap state without hand-editing a 6000+ line Markdown file, while humans still get a readable report.
- Scope:
  - SQLite local tracker database
  - JSONL review export
  - generated ROADMAP.md
  - CLI commands for list next show add-slice update-status import export render check
  - ADR and workflow docs
- Out of scope:
  - Product runtime behavior changes.
- Architecture impact:
  - Moves roadmap editing behind a tracker/export/render workflow.
- Tests:
  - Roadmap CLI import/export/render/check coverage.
- Docs:
  - README, ADR, contributor guide, developer guide, AGENTS, and roadmap docs.
- Acceptance criteria:
  - Agents can use CLI commands instead of manually editing ROADMAP.md.
  - ROADMAP.md renders from docs/roadmap/slices.export.jsonl.
  - Roadmap changes remain reviewable in git diff.
- Completed: 2026-07-01

### Slice 2.17.4: Publication Channels and Platform Profiles

- Status: Done
- Goal: Model actual publishing destinations as project-owned channels before
  generating or publishing multi-platform variants.
- User value:
  - A blog can explicitly say where it publishes and why: Telegram, LinkedIn, Dzen,
    or another platform.
- Scope:
  - Add `PublicationChannel` domain contract with platform, title, URL/handle,
    language, audience, role, publishing mode, and default size profile.
  - Move content plan platform choices toward channel ids.
  - Add channel settings UI in the project/editorial model area.
  - Keep manual/export behavior; no platform API integration yet.
- Out of scope:
  - Autoposting.
  - OAuth/API credentials.
  - Multi-target DraftRun.
- Implementation notes:
  - Channel is not the same as platform: one project can have multiple channels on one
    platform.
- Architecture impact:
  - Separates channel setup from plan slots and DraftRun contracts.
- Tests:
  - Domain normalization, UI channel CRUD, planning compatibility.
- Docs:
  - User/developer/demo docs.
- Demo impact:
  - Seed AI Design Patterns with LinkedIn-oriented channel candidates; seed
    `Каша из топора` with Telegram; seed `Блог Главреда` with Telegram + Dzen.
- Acceptance criteria:
  - Plan slots can reference project channels without breaking legacy platform fields.
- Risks:
  - Channel settings can duplicate publication-size settings; keep size contract
    resolver as the downstream owner.
- Completed: 2026-07-01

### Slice 2.17.4.1: AI Design Patterns Project Rework

- Status: Done
- Goal: Rework the `AI Design Patterns` benchmark project from user-provided inputs before continuing multi-platform planning.
- User value:
  - The demo project now represents a real client-attraction blog concept: Russian Telegram-first industrial AI design patterns for ТОиР/EAM, Decision Intelligence, hybrid AI, and a future OSS pattern book.
  - The benchmark can test whether generation stays inside industrial AI and produces reusable patterns instead of generic AI news.
- Scope:
  - Capture sanitized inputs from the industrial AI / ТОиР material and author blog context.
  - Update project profile, editorial model, author memory, rules, topics, fabulas, radars, source signals, publication channels, and benchmark expectations.
  - Add a project blueprint document in product entities so future fixture/database loading has a clear source.
- Out of scope:
  - Product runtime behavior changes.
  - Live source ingestion from Telegram or private PDFs.
  - Multi-platform DraftRun execution or publication adapters.
- Implementation notes:
  - Private user materials are paraphrased into sanitized fixtures; source documents are not committed.
  - Project-specific fixture data lives in `src/fixtures/demoAiDesignPatternsProject.ts`; the portfolio assembler only wires it into the two-user/three-blog demo.
- Architecture impact:
  - Keeps `WorkspaceState` and portfolio contracts unchanged.
  - Establishes a document-first pattern for project rework slices.
- Tests:
  - Updated demo benchmark fixture tests for Russian Telegram-first industrial AI data, source signals, channels, and isolation.
- Docs:
  - Added `docs/architecture/AI_DESIGN_PATTERNS_PROJECT_BLUEPRINT.md`.
  - Updated README, demo README, user guide, developer guide, and architecture docs.
- Demo impact:
  - After reset/demo seed, `AI Design Patterns` shows industrial AI memory, topics, fabulas, radars, Telegram primary channel, paused GitHub pattern-book experiment, and a ready Decision Intelligence Workbench scenario.
- Acceptance criteria:
  - AI project no longer defaults to English/LinkedIn-first. Done.
  - Ready scenario is `Decision Intelligence Workbench` as a Telegram pattern card. Done.
  - Project-specific fixture lives outside near-limit demo workspace files. Done.
- Risks:
  - Future LinkedIn/site adaptation still needs a separate variant slice after the Russian Telegram baseline stabilizes.
- Completed: 2026-07-02

### Slice 2.17.4.1.1: Цех прикладной магии Project Rework

- Status: Done
- Goal: Rework the former `AI Design Patterns` benchmark into the user-approved `Опытный цех «Сборочная»` concept with clean Publisher ownership, reusable industrial AI topics/fabulas, and backend-visible demo data.
- User value:
  - The industrial AI benchmark stops sounding like a dry generic pattern catalog and becomes a distinctive client-attraction project with a workshop/test-stand metaphor, stronger author stance, and usable generation inputs.
  - The project now has a clearer public identity: cases, papers, OSS, and author materials go through a workshop and produce tested industrial AI patterns, protocols, anti-patterns, or RFC questions.
- Scope:
  - Update `docs/architecture/AI_DESIGN_PATTERNS_PROJECT_BLUEPRINT.md` as the concept source.
  - Update `src/fixtures/demoAiDesignPatternsProject.ts` and portfolio/backend seed labels while preserving technical id `project-ai-design-patterns`.
  - Move reusable-output and evidence/limits rules out of `author`/`positioning` into style-owned editorial rules.
  - Add six reusable industrial AI topics, six reusable fabulas, and a curated non-one-to-one topic/fabula matrix.
  - Refresh backend-visible dev project metadata and minimal workspace snapshot through portfolio API.
- Out of scope:
  - DraftRun pipeline changes.
  - Publication adapters or multi-platform generation.
  - Live ingestion from the user's private source documents or Telegram archive.
- Architecture impact:
  - Keeps the project rework in role-owned fixture/docs modules.
  - Reinforces that UI-visible Publisher blocks and DraftRun context are backed by `editorialRules`, not only summary text fields.
  - Keeps `PublicationChannel` as destination mechanics only; audience remains project/editorial-contract owned.
- Tests:
  - Updated demo fixture, portfolio flow, editorial model flow, backend seed, and blueprint validation tests.
  - Full frontend regression and backend regression passed.
- Docs:
  - Updated README, demo README, user guide, developer guide, SaaS architecture, system architecture overview, and the project blueprint.
- Demo impact:
  - After reset/demo seed, the founder portfolio shows `Опытный цех «Сборочная»` instead of `AI Design Patterns`.
  - The active project contains workshop-style author memory, Publisher rules, topics, fabulas, matrix, Telegram channel, paused GitHub pattern-book experiment, and the Decision Intelligence Workbench ready scenario.
- Acceptance criteria:
  - Public project name is `Опытный цех «Сборочная»`. Done.
  - Active Publisher groups `author`, `audience`, and `goal` are non-empty and semantically correct. Done.
  - `ai-pattern-rule-pattern-output` is no longer an `author` rule and `ai-pattern-rule-proof-limits` is no longer a `positioning` rule. Done.
  - Topic/fabula matrix is curated and not one-to-one. Done.
  - Backend mode no longer shows stale `AI Design Patterns` project metadata after local refresh. Done.
- Risks:
  - Existing browser localStorage or old backend snapshots can still preserve stale project names until reset/logout/reload or a backend workspace refresh.
  - Future LinkedIn/site adaptation remains a later slice after the Russian Telegram baseline stabilizes.
- Completed: 2026-07-02

### Slice 2.17.4.2: Северная стена Project Rework

- Status: Done
- Goal: Rework the former `Каша из топора` benchmark project into `Северная стена`, a Telegram-first consulting-attraction blog about engineering complex B2B sales systems.
- User value:
  - The RevOps/Product Marketing benchmark project becomes a realistic author project with a sharper audience, stronger genre, clearer client-attraction purpose, and usable benchmark scenarios.
- Scope:
  - Rename the user-facing project to `Северная стена` while preserving technical id `project-kasha-iz-topora` for compatibility.
  - Add a project blueprint in Glavred entities: project profile, editorial model, author memory, rules, topics, fabulas, radars, source signals, channels, and benchmark expectations.
  - Update sanitized project fixture data from the user's inputs and private source materials without committing the source PDF text.
  - Keep one alpine metaphor: route, rope team, gear, belay, fog, summit, base camp.
  - Seed a ready Telegram scenario: `Сделка не зависла. Она потеряла маршрут`.
  - Prefer a project-specific fixture module instead of expanding near-limit portfolio/demo files.
- Out of scope:
  - Product runtime behavior changes.
  - Live import from private materials or old channels.
  - Multi-platform DraftRun execution.
  - Publication adapters.
- Architecture impact:
  - Follows the document-first project rework pattern established by 2.17.4.1.
  - Keeps `PublicationChannel` project-owned and keeps old `platform` fields as compatibility labels.
- Tests:
  - Demo fixture tests for project isolation and seeded Северная стена data completeness.
  - Portfolio switcher flow checks the new public project name and memory isolation.
  - Backend seed tests verify dev auth seed exposes the current project title.
- Docs:
  - Project blueprint, demo docs, user/developer docs, architecture docs, roadmap tracker.
- Acceptance criteria:
  - `Северная стена` has distinct author memory, Telegram voice, topics, fabulas, source signals, and ready benchmark scenario grounded in user inputs.
  - No AI Design Patterns or Glavred memory leaks into this project.
  - Existing backend/local portfolio users see the new public project name without changing project ids.
- Risks:
  - Existing local backend snapshots can preserve old workspace payloads; local dev DB may need a one-time project row/snapshot refresh after implementation.
- Completed: 2026-07-02

### Slice 2.17.4.2.1: Северная стена Editorial Contract Calibration

- Status: Done
- Goal: Calibrate the `Северная стена` project contract after editorial review so the demo project has a usable author persona, business goals, audience boundary, style rules, and fabula dramaturgy.
- User value:
  - The RevOps benchmark becomes a real client-attraction project brief instead of a generic content seed.
  - Future fixture loading has a clear approved document in Glavred product entities.
- Scope:
  - Fill the `Author` section with a field-practitioner persona based on sanitized project materials.
  - Add explicit project goals: client attraction, RevOps market education, commercial-system engineering, pragmatic team positioning, and AI as acceleration rather than the main topic.
  - Rewrite `Audience` as reader segment and buying context only.
  - Move the rule about starting from recognizable deal pain into `Voice` and the relevant fabula.
  - Update the `Северная стена` fixture and tests so the UI shows the calibrated author/goals/audience/style contract.
- Out of scope:
  - App-wide publication-channel audience boundary changes.
  - DraftRun quality, model, retrieval, or generation changes.
  - Multi-platform generation and publication adapters.
- Implementation notes:
  - Private user materials remain paraphrased and sanitized; no source PDF text is committed.
  - Keep the alpine metaphor pure: route, rope team, gear, belay, fog, wall, base camp.
- Architecture impact:
  - Keeps the project-specific blueprint pattern from 2.17.4.1/2.17.4.2.
  - Does not change `WorkspaceState` contracts.
- Tests:
  - Demo fixture tests for non-empty author, explicit goals, audience without style-rule leakage, and pain-first rule in style/fabula data.
  - Portfolio/demo tests confirming `Северная стена` remains isolated from other projects.
- Docs:
  - `Северная стена` blueprint, demo docs, user/developer docs, and tracker-rendered roadmap.
- Demo impact:
  - Demo reset should show the corrected project contract in the `Северная стена` project.
- Acceptance criteria:
  - `Author` is non-empty and describes a field practitioner, not a generic brand voice.
  - `Goals` are present and map to consulting client attraction.
  - `Audience` does not contain dramaturgy/style rules.
  - Pain-first opening guidance lives in `Voice` and/or a specific fabula.
- Risks:
  - Overwriting useful roughness with consulting polish; preserve the sharper alpine voice.
- Completed: 2026-07-02

### Slice 2.17.4.2.2: Publication Channel Audience and Editorial Contract Boundary Repair

- Status: Done
- Goal: Repair two product-wide ownership boundaries: project audience must live in the editorial contract / post brief, not publication channels; and `editorialRules` must be the canonical editable editorial contract for Author, Audience, Goals, Positioning, Style and Forbidden blocks, not a duplicate shadow of `editorialModel` summary fields.
- User value:
  - Channel settings become simpler and less misleading.
  - Editors see one working place for author/audience/goals rules.
  - DraftRun context uses the same visible blocks the editor configured, not stale duplicated summaries.
- Scope:
  - Deprecate legacy `PublicationChannel.audience` in domain normalization and new fixtures.
  - Remove the audience block from `PublicationChannelsTab` cards/forms.
  - Preserve old snapshots that still contain channel audience data without using it for generation.
  - Define `editorialRules` groups `author`, `audience`, `goal`, `positioning`, `style*`, and `forbiddenTopic` as the canonical editable editorial contract used by UI and DraftRun.
  - Treat `editorialModel.author`, `editorialModel.audience`, and `editorialModel.goals` as derived/legacy summary fields during compatibility normalization; they must not become an independent second source of truth.
  - Normalize legacy workspaces by synthesizing missing `editorialRules` from old `editorialModel` summary fields when needed, so old projects do not show empty Publisher blocks.
  - Ensure `buildDraftRunContext` and backend context summaries use `PostBrief.audience || editorialRules(audience) || legacy EditorialModel.audience`, never channel audience.
  - Ensure DraftRun author/goals/style context prefers visible `editorialRules` over stale `editorialModel` duplicates when rules exist.
  - Update channel fixture builders so channels contain destination, language, role, mode, status, and default size/profile only.
- Out of scope:
  - Platform variants.
  - Per-channel audience segmentation.
  - Publication adapters, OAuth, or autoposting.
  - Full removal of legacy `editorialModel` fields from storage in this slice.
- Implementation notes:
  - If future channel-specific nuance is needed, model it as adaptation notes or platform-variant guidance, not as a second audience owner.
  - If compact model summaries are still useful, compute them from rules or keep them explicitly marked as compatibility summaries.
- Architecture impact:
  - Enforces ADR `publication-channel-audience-boundary` and adds/updates an editorial contract ownership note.
  - Clarifies the distinction between destination setup, editable editorial contract, and legacy summaries.
- Tests:
  - Domain normalization keeps legacy channel audience readable but ignored.
  - Legacy workspaces with only `editorialModel.author/audience/goals` synthesize visible `editorialRules`.
  - UI tests verify channel forms/cards do not show audience.
  - Publisher UI tests verify Author, Audience and Goals blocks are populated from rules.
  - DraftRun context tests verify audience comes from brief/rules/model fallback and never channel audience.
  - DraftRun context tests verify author/goals prefer `editorialRules` over stale model summaries.
  - Demo fixture tests verify channels no longer duplicate project audience and seeded project blocks are not empty.
- Docs:
  - ADR, architecture overview, SaaS portfolio architecture, developer guide, user/demo docs, and roadmap.
- Demo impact:
  - Demo channel cards stop showing a duplicate audience block.
  - Demo Publisher blocks remain populated after backend snapshot normalization.
- Acceptance criteria:
  - No new editable channel audience UI remains.
  - Generation context has one auditable audience source.
  - Author/Audience/Goals blocks are visible rules, not duplicated hidden summaries.
  - Old workspaces still load and do not show empty Publisher blocks when legacy summary data exists.
- Risks:
  - Some projects may later need channel-specific audience nuance; defer that to platform variants/adaptation notes.
  - Legacy `editorialModel` fields may remain useful as API/export summaries, so the slice must clarify ownership before deleting anything.
- Completed: 2026-07-02

### Slice 2.17.4.2.2.1: Project Blueprint Creation Skill

- Status: Done
- Goal: Create a reusable local agent skill that turns an approved blog-project blueprint into consistent Glavred project data, sanitized fixtures, backend-visible demo snapshots, docs, and validation checks.
- User value:
  - New and reworked projects stop being hand-wired through ad hoc fixture edits, direct SQLite patches, or stale backend snapshots.
  - Project setup becomes repeatable: author memory, Publisher contract, editorial rules, topics, reusable fabulas, topic/fabula matrix, channels, plan scenarios, and benchmark expectations come from one agreed blueprint.
  - The failures we just hit become hard checks: empty Author/Audience/Goals blocks, mojibake/question-mark Cyrillic, channel-level audience duplication, one-to-one topic/fabula coupling, and backend mode showing old seeded data.
- Scope:
  - Add a local `.agents/skills/project-blueprint-creation/SKILL.md` for creating or reworking blog projects from approved blueprint documents.
  - Add skill-owned references/templates for the required blueprint shape: project profile, author image, goals, audience, positioning, style, forbidden moves, author memory, editorial rules, topics, reusable fabulas, topic/fabula matrix, publication channels, source signals, ready scenarios, and benchmark criteria.
  - The skill must start by reading the roadmap tracker, `ui-design-systems/START-HERE.md`, SaaS portfolio architecture, existing project blueprints, demo fixture builders, and current backend seed/snapshot behavior.
  - Define the canonical mapping rules:
    - Publisher/editorial contract blocks are owned by canonical editorial rules/groups used by UI and pipeline.
    - `PublicationChannel` owns destination mechanics only: platform, title/handle, language, role, publishing mode, status, default size profile.
    - Channel audience is not canonical and must not duplicate Publisher audience.
    - Topic defines editorial territory; Fabula defines reusable story mechanics and must be applicable across multiple topics where intended.
  - Define the correct write path: update UTF-8 source docs and fixture builders first, run validation, then refresh backend snapshots through safe scripts or application seed/reset flow; never patch Cyrillic demo content into SQLite through brittle inline shell commands.
  - Add or update fixture validation helpers/tests that fail on empty Publisher blocks, missing `editorialRules`, mojibake/question-mark runs, channel audience duplication, degenerate topic/fabula one-to-one matrix, and missing ready benchmark scenarios.
  - Document how to make a changed project visible in backend mode: when to reset local portfolio DB, when to migrate/update snapshots, and how to verify that UI reads the refreshed project.
- Out of scope:
  - Implementing a product UI wizard for project creation.
  - Persisting project blueprints as a new runtime domain object.
  - Running DraftRun quality benchmarks for the new project.
  - Reworking Severnaya Stena topic/fabula content itself; that remains `2.17.4.2.3`.
- Implementation notes:
  - This is an agent workflow skill plus validation guardrails, not a runtime product feature.
  - The approved blueprint document is the planning source; generated fixture/backend state is the implementation output.
  - The skill must explicitly avoid manual duplication between summary text fields and canonical `editorialRules`; if compatibility summaries remain, they are mirrors, not the source of truth.
  - The skill should include a compact checklist for human approval before implementation starts, so project concepts are reviewed before they enter fixtures.
  - UTF-8 safety is part of the workflow: write files as UTF-8, validate rendered Cyrillic, and never trust mojibake PowerShell output without a UTF-8-aware read.
- Architecture impact:
  - Establishes a repeatable project-creation/rework boundary parallel to DraftRun TO BE planning.
  - Reduces accidental coupling between project blueprints, demo fixtures, backend snapshots, UI-visible Publisher blocks, and publication channels.
  - Makes future benchmark projects easier to extend without turning `demoWorkspace` or portfolio seed modules into god files.
- Tests:
  - Add fixture/project validation tests for required Publisher groups, channel boundary, mojibake detection, reusable fabula matrix, and ready scenario completeness.
  - Add demo portfolio tests proving backend-visible projects can be refreshed from source fixtures without corrupting Cyrillic.
  - Add a skill smoke/manual validation note if there is no automated skill test harness.
  - Run targeted tests plus roadmap checks: `npm test -- --run --pool=threads --maxWorkers=4`, `npm run test:architecture`, `npm run smoke`, `python -m backend.app.roadmap check`, `git diff --check`.
- Docs:
  - Update `AGENTS.md`/skills guidance, `docs/developer/DEVELOPER_GUIDE.md`, `docs/user/USER_GUIDE.md` if the visible workflow changes, `demo/README.md`, and `docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md`.
  - Link the new skill from project blueprint docs and explain when a blueprint must be prepared before fixture changes.
- Demo impact:
  - Future demo projects are created through a blueprint-backed checklist and validation path instead of one-off fixture edits.
  - Existing AI Design Patterns / Severnaya Stena / Glavred projects become reusable examples for the workflow.
- Acceptance criteria:
  - The repository contains a usable `project-blueprint-creation` agent skill with clear inputs, steps, outputs, and validation checklist.
  - A new or reworked project can be implemented from an approved blueprint through documented skill steps.
  - Fixture validation catches empty Author/Audience/Goals blocks, channel audience duplication, mojibake, and one-to-one topic/fabula coupling.
  - The workflow explains how to refresh local backend snapshots safely and verify the result in UI/backend mode.
  - `2.17.4.2.3` remains the next content-calibration slice after this workflow guardrail is in place.
- Risks:
  - A skill can enforce process only when agents actually use it; keep real fixture/domain validation tests as the hard safety net.
  - Snapshot refresh can still be confusing if local dev DB state diverges; document the exact safe reset/migration path.
  - Over-validating the topic/fabula matrix could block legitimate narrow projects; make the degeneracy check configurable or project-intent-aware.
- Completed: 2026-07-02

### Slice 2.17.4.2.3: Северная стена Topic/Fabula Matrix Calibration

- Status: Done
- Goal: Calibrate the `Северная стена` editorial model so goals, positioning, topics, fabulas, and the topic/fabula matrix have distinct responsibilities and produce reusable drafting combinations.
- User value:
  - The project becomes a better real benchmark for RevOps / complex B2B sales content.
  - Editors can combine subjects and dramaturgies instead of picking from four nearly hard-coded topic+fabula pairs.
  - DraftRun receives cleaner inputs: goals are business/editorial aims, positioning is author stance, topics are domains, and fabulas are reusable narrative forms.
- Scope:
  - Move `AI как легкое снаряжение` from `goal` to `positioning` and phrase it as author stance, not blog objective.
  - Clean `goal` rules so they contain only business/editorial goals: client attraction through expertise, RevOps market education, engineering approach to complex B2B sales, trust in a small fast practical team.
  - Rewrite topics as subject domains: client relief, RevOps belay, deal gear, lost route, sales-marketing-product rope team, procurement/DMU/internal politics.
  - Rewrite fabulas as reusable dramaturgical forms: fog removal, failure analysis, gear check, field route, control point/checklist, summit brief.
  - Rebuild `topicFabulaMatrix` so each key fabula is compatible with at least two or three meaningful topics.
  - Update ready scenario to use one topic and one reusable fabula without semantic overlap.
  - Update `docs/architecture/SEVERNAYA_STENA_PROJECT_BLUEPRINT.md` and benchmark metadata.
- Out of scope:
  - Global Topic/Fabula domain redesign for all projects.
  - UI matrix redesign.
  - DraftRun pipeline changes.
  - Live generation quality evaluation.
- Implementation notes:
  - Keep the alpine metaphor consistent; do not mix pilot/war jargon back in.
  - Treat `Фабула` as a reusable genre/dynamic, not as a renamed topic.
  - Keep the blog sharper than a student RevOps handbook: audience, pain, stakes, field examples and practical route logic must remain visible.
- Architecture impact:
  - Exercises the project blueprint creation skill on a real project rework.
  - Clarifies project-level content modeling rules for future benchmark blogs.
- Tests:
  - Fixture tests verify no `goal` rule contains AI-as-gear.
  - Fixture tests verify AI-as-gear exists under positioning.
  - Fixture tests verify key fabulas map to multiple topics.
  - Fixture tests verify topics and fabulas do not duplicate each other by id/title/description intent.
  - Existing demo portfolio and architecture tests remain green.
- Docs:
  - Update `SEVERNAYA_STENA_PROJECT_BLUEPRINT.md`, demo README if needed, and roadmap artifacts.
- Demo impact:
  - `Северная стена` becomes a stronger benchmark project with a real matrix instead of paired topic/fabula rows.
- Acceptance criteria:
  - Goals, positioning, topics and fabulas are visibly separated in UI and fixtures.
  - `AI как легкое снаряжение` appears in Positioning, not Goals.
  - The topic/fabula matrix supports cross-combination rather than one-to-one pairs.
  - The ready scenario remains runnable and project-specific.
- Risks:
  - Over-generalizing fabulas may make the project less vivid; keep scenario examples concrete even when fabulas are reusable.
- Completed: 2026-07-02

### Slice 2.17.4.3: Блог Главреда Project Rework

- Status: Done
- Goal: Rework the `Блог Главреда` benchmark project before continuing multi-platform planning.
- User value:
  - The product/philosophy blog becomes a stronger benchmark for explaining Glavred's editorial philosophy, practical methods, and Telegram/Dzen adaptation readiness.
- Scope:
  - Capture product-context assumptions and any user inputs for `Блог Главреда`.
  - Update sanitized project profile, author memory, editorial rules, topics, fabulas, channels, source signals, and benchmark expectations.
  - Prefer a project-specific fixture module and blueprint document.
- Out of scope:
  - Product runtime behavior changes.
  - Multi-platform DraftRun execution.
  - Publication adapters.
- Architecture impact:
  - Should follow the document-first project rework pattern established by 2.17.4.1.
  - Should start after the audience/channel boundary repair so new channel fixtures do not repeat deprecated audience data.
- Tests:
  - Demo fixture tests for project isolation and Glavred-specific seeded data completeness.
- Docs:
  - Project blueprint, demo docs, user/developer docs, roadmap tracker.
- Acceptance criteria:
  - `Блог Главреда` has stronger product-philosophy positioning and ready Telegram/Dzen-oriented benchmark context.
- Risks:
  - Should not become generic product marketing; must stay tied to Glavred's actual editorial pipeline philosophy.
- Completed: 2026-07-03

### Slice 2.17.4.4: Upstream Search and Signal Architecture

- Status: Done
- Goal: Design the upstream half of Glavred: how internal/external material becomes reviewed source signals and then post candidates before planning and DraftRun.
- User value:
  - The product stops depending on manually seeded post ideas and starts explaining how it finds, filters, and frames material for future posts.
- Scope:
  - Define the upstream data flow: `SourceRegistry -> RadarRun -> FoundMaterial -> SourceSignal -> SignalScore -> PostCandidate -> Plan`.
  - Separate raw material, reviewed signal, and editorial candidate responsibilities.
  - Define provider-free DTOs and ownership boundaries for source registry, radar execution, found material, signal extraction, scoring, and candidate assembly.
  - Decide how project settings, author memory, publisher rules, topics, fabulas, channels, and research depth influence upstream selection.
  - Add/refresh ADR and SAO sections for upstream ownership.
- Out of scope:
  - Real web search execution.
  - New DraftRun steps.
  - Multi-platform planning/generation.
  - Autoposting or publication adapters.
- Implementation notes:
  - Preserve existing ADR rule: `SourceSignal` is raw reviewed material; topic/fabula assignment belongs to `PostCandidate`.
  - Treat DraftRun as downstream: it should receive a justified candidate, not do first-pass editorial discovery.
  - Plan for local-first demo compatibility and backend-ready execution contracts.
- Architecture impact:
  - Introduces the upstream product spine before channel variants: source discovery, material normalization, signal scoring, and candidate assembly.
- Tests:
  - Architecture smoke/checklist for upstream module ownership.
  - Tracker/ADR consistency checks.
- Docs:
  - SAO, ADR, developer guide, user guide, demo README, roadmap.
- Demo impact:
  - Three benchmark blogs should describe which upstream scenario each will exercise.
- Acceptance criteria:
  - The next implementation slices have clear domain/application/infrastructure/UI boundaries.
  - The roadmap pauses multi-target downstream work until upstream discovery has a working v1.
- Risks:
  - Over-designing a search platform before a small working runner; keep v1 source adapters narrow.
- Completed: 2026-07-03

### Slice 2.17.4.5: Source Registry and Radar Run Contract

- Status: Done
- Goal: Make radars executable objects with project-owned source registry and traceable run records, even before external search is fully automated.
- User value:
  - The user can see what sources a radar is allowed to inspect, when it ran, what it attempted, what it skipped, and why.
- Scope:
  - Add provider-free contracts for `SourceRegistry`, `SourceHandle`, `RadarRun`, `RadarRunOperation`, and `FoundMaterial`.
  - Support internal sources: author memory, archive/import queue, previous posts, manual notes.
  - Support configured external handles: URL, open-web query, social/profile handle as metadata, document/source placeholder.
  - Store run status, operation trace, budget/caps, found material ids, errors, skipped sources, and used search rules.
  - Add local-first fixtures and UI trace/read model inside `Сигналы -> Радары`.
- Out of scope:
  - Autonomous web crawling.
  - LLM extraction/scoring.
  - Candidate assembly changes.
  - Backend persistence tables beyond current workspace snapshot unless unavoidable.
- Implementation notes:
  - This slice may keep execution deterministic/manual, but the contract must match later provider-backed runs.
  - Radar configuration remains project-scoped and must not leak across portfolio projects.
- Architecture impact:
  - Moves radars from static settings toward auditable upstream orchestration.
- Tests:
  - Domain normalization tests for legacy radars and source handles.
  - UI tests for run status/trace and project isolation.
  - Demo fixture tests for three-blog source registry coverage.
- Docs:
  - User guide, developer guide, demo README, SAO.
- Demo impact:
  - Each benchmark blog gets at least one ready radar with explicit allowed sources and expected material type.
- Acceptance criteria:
  - A radar can have a visible run record and found material trace without creating post candidates yet.
- Risks:
  - UI can become noisy; keep run trace compact and expandable.
- Completed: 2026-07-03

### Slice 2.17.4.5.1: Radar Settings and Run Trace Tabs

- Status: Done
- Goal: Separate radar configuration from deterministic run diagnostics by adding internal tabs inside expanded radar rows.
- User value: Radar settings stay readable while run trace and found material diagnostics move into a dedicated place.
- Scope:
  - Add internal Settings and Run Trace tabs inside expanded radar cards
  - move source handles, latest RadarRun operations, found materials, skipped reasons and run summary into the Run Trace tab
  - keep compact row metadata short
  - preserve existing deterministic Run radar behavior.
- Out of scope:
  - Product runtime behavior changes.
- Architecture impact:
  - Moves roadmap editing behind a tracker/export/render workflow.
- Tests:
  - Roadmap CLI import/export/render/check coverage.
- Docs:
  - README, ADR, contributor guide, developer guide, AGENTS, and roadmap docs.
- Acceptance criteria:
  - Agents can use CLI commands instead of manually editing ROADMAP.md.
  - ROADMAP.md renders from docs/roadmap/slices.export.jsonl.
  - Roadmap changes remain reviewable in git diff.
- Completed: 2026-07-03

### Slice 2.17.4.6: External Search Radar Runner v1

- Status: Done
- Goal: Run a narrow, budgeted external search for selected radars and store normalized found materials instead of hand-seeded signals only.
- User value:
  - The system can bring fresh external material into the editorial workflow for review.
- Scope:
  - Add backend/application runner for open-web query and URL read operations from `RadarRun`.
  - Reuse existing OpenRouter web search/URL reader infrastructure where practical.
  - Apply project/fabula research depth and execution budget caps to upstream search.
  - Normalize results into `FoundMaterial` with source title, URL, snippet/summary, capturedAt, operation provenance, and retrieval warnings.
  - Show found materials under `Сигналы -> Радары` before they become source signals.
- Out of scope:
  - Full crawler/RSS/social API integrations.
  - Candidate generation.
  - DraftRun changes.
  - Multi-platform variants.
- Implementation notes:
  - External search failures must produce explicit failed operations, not silent empty state.
  - Use smoke mode to keep local evaluation cheap.
- Architecture impact:
  - Adds provider-backed upstream retrieval while keeping raw found material separate from editorial signals.
- Tests:
  - Backend runner tests with fake search/read adapters.
  - Budget cap tests.
  - UI tests for found materials and failed operations.
- Docs:
  - Developer guide, user guide, demo README, diagnostics notes.
- Demo impact:
  - Seeded benchmark radars can demonstrate what a real run would collect, even when provider is unavailable.
- Acceptance criteria:
  - A radar run can produce traceable found materials or a clear failed/empty result.
- Risks:
  - Provider instability and cost; v1 must be bounded and trace-visible.
- Completed: 2026-07-03

### Slice 2.17.4.6.0: Backend Architecture Recovery Charter and Package Contract

- Status: Done
- Goal: Stop backend architecture drift before adding more DraftRun or upstream runtime behavior by documenting the current state, target bounded-context layout, and enforceable guardrails.
- User value:
  - Contributors can understand where backend code belongs before touching the drafting pipeline.
  - New backend slices stop adding more flat `draft_*` modules and unowned helper functions.
- Scope:
  - Add `BACKEND_ARCHITECTURE_AS_IS.md` with a factual inventory of backend packages, draft-related files, high-risk modules, and current guardrail gaps.
  - Add `BACKEND_ARCHITECTURE_TARGET.md` with target bounded contexts: drafting, upstream, portfolio, ai-runs, roadmap, shared.
  - Add ADR `backend-bounded-contexts-and-operation-contracts`.
  - Add backend architecture smoke v1 for no-new-flat `backend/app/application/draft_*.py` and `backend/app/domain/draft_*.py` files outside an explicit legacy allowlist.
  - Add checks for module ownership docstrings, architecture anchors, top-level public function ceilings, and backend dependency direction.
  - Update developer docs and agent workflow rules so backend changes read the new architecture docs first.
- Out of scope:
  - Moving existing runtime modules.
  - Changing DraftRun behavior, step order, prompts, providers, or database schema.
  - Solving every existing legacy violation immediately.
- Implementation notes:
  - This is the architecture stop-line slice: it prevents further deterioration before package migration starts.
  - Legacy files should be captured in a baseline/allowlist with explicit debt labels rather than silently accepted as target architecture.
- Architecture impact:
  - Turns backend architecture from informal guidance into an enforced contract.
  - Introduces bounded-context ownership as a required backend dimension, not only file-size limits.
- Tests:
  - `npm run test:architecture` includes backend architecture smoke v1.
  - Targeted tests for the backend architecture checker fixtures if practical.
  - `python -m backend.app.roadmap check`.
- Docs:
  - Add backend AS IS and TARGET architecture docs.
  - Update SAO, developer guide, AGENTS/skills guidance, and roadmap artifacts.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - A new flat `backend/app/application/draft_new_thing.py` fails architecture smoke unless added to the explicit legacy allowlist.
  - New backend modules without ownership/architecture docstrings fail architecture smoke.
  - The next Ready task remains in the backend recovery track.
- Risks:
  - Overly strict checks can block useful work; start with legacy allowlists and tighten them slice by slice.
- Completed: 2026-07-03

### Slice 2.17.4.6.0.1: Drafting Backend Package Skeleton and Compatibility Shims

- Status: Done
- Goal: Create the target `backend/app/drafting` package boundary without changing runtime behavior.
- User value:
  - Developers get an obvious home for DraftRun code instead of adding another flat `draft_*` file.
- Scope:
  - Create `backend/app/drafting/` with subpackages for `api`, `domain`, `application/workflow`, `application/steps`, `application/operations`, `application/artifacts`, and `infrastructure` as needed.
  - Add `backend/app/drafting/README.md` and `DRAFTING_BACKEND_COMPONENT_MAP.md` with component ownership and doc anchors.
  - Add compatibility shims/re-export modules only where needed to keep imports stable during migration.
  - Wire architecture smoke to require new DraftRun code to land under `backend/app/drafting`.
- Out of scope:
  - Moving complex logic into the new package.
  - Changing provider calls, prompts, storage, or pipeline results.
- Implementation notes:
  - The skeleton must be useful, not boilerplate: each package needs an explicit owner and allowed dependency direction.
- Architecture impact:
  - Introduces the future bounded context while keeping legacy import compatibility.
- Tests:
  - Architecture smoke for package presence, doc anchors, and import boundaries.
  - Existing backend DraftRun tests remain green.
- Docs:
  - Update backend target architecture and developer guide with the new package map.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - `backend/app/drafting` exists with documented responsibilities and no runtime behavior changes.
  - Legacy DraftRun tests pass through compatibility shims.
- Risks:
  - Skeleton packages can become empty boilerplate; keep them minimal and tied to the migration plan.
- Completed: 2026-07-03

### Slice 2.17.4.6.0.2: Unified DraftStep and JsonOperation Contracts

- Status: Done
- Goal: Introduce a shared DraftRun step contract and JSON LLM operation contract so new services stop inventing one-off payload/result shapes.
- User value:
  - Pipeline behavior becomes easier to reason about because every step returns the same kind of outcome and trace metadata.
- Scope:
  - Add provider-free `DraftStep`, `DraftStepContext`, `DraftStepOutcome`, and `DraftStepTrace` contracts under the drafting package.
  - Add `JsonLlmOperation` / `JsonOperationAttempt` contract using the existing universal JSON retry policy.
  - Adapt one or two low-risk existing steps through adapters without changing artifacts.
  - Document when top-level helper functions are allowed and when a class/service is required.
- Out of scope:
  - Migrating every DraftRun step.
  - Changing JSON prompts or model portfolio.
- Implementation notes:
  - Use adapter wrappers first; avoid large rewrites until the contract is proven on small steps.
- Architecture impact:
  - Creates the common seam for the later workflow orchestrator refactor.
- Tests:
  - Contract tests for `DraftStepOutcome` serialization and error handling.
  - JSON operation tests for primary, repair, backup, and failed/not-run outcomes.
- Docs:
  - Update component map and ADR with the step/operation contract.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - New DraftRun step code can implement one standard protocol instead of bespoke result dataclasses.
  - Architecture smoke can detect new public `dict[str, Any]` step contracts in the drafting package.
- Risks:
  - Overgeneralizing too early; keep the contract small and based on existing artifacts.
- Completed: 2026-07-03

### Slice 2.17.4.6.0.3: DraftRun Workflow Orchestrator Refactor

- Status: Done
- Goal: Turn `draft_run_pipeline.py` from a long procedural scenario into a thin facade over `DraftWorkflow` and a step registry.
- User value:
  - A developer can locate each pipeline step without reading one monolithic orchestration method.
- Scope:
  - Add `DraftWorkflow`, `DraftStepRegistry`, and workflow state/context objects under `backend/app/drafting/application/workflow`.
  - Move orchestration sequencing behind registered step objects while preserving existing step order and artifacts.
  - Keep `backend/app/application/draft_run_pipeline.py` as a compatibility facade during migration.
  - Preserve progress persistence, child AiRun id collection, finalDraft selection, and failure behavior.
- Out of scope:
  - Moving all individual step implementations.
  - Changing DraftRun schema or public API.
- Implementation notes:
  - This is behavior-preserving: same inputs, same step artifacts, same trace contract.
- Architecture impact:
  - Separates workflow control from step implementation and prepares step-by-step package migration.
- Tests:
  - Existing DraftRun pipeline tests must remain green.
  - Add workflow registry tests for step order and failure propagation.
- Docs:
  - Update DraftRun AS IS and backend component map if the runtime entrypoint changes.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - `draft_run_pipeline.py` becomes a thin compatibility entrypoint.
  - Pipeline trace and finalDraft results are unchanged on existing tests.
- Risks:
  - Subtle progress/partial-artifact regressions; keep tests focused on stale/failure paths, not only happy path.
- Completed: 2026-07-03

### Slice 2.17.4.6.0.3.1: Таймаут и сокращение payload для RulePack Evidence Interpretation

- Status: Done
- Goal: Защитить `rulePack.evidenceInterpretation`: provider-heavy операция получает timeout envelope, compact payload, safe failed operation trace и deterministic fallback.
- User value: DraftRun не остается навсегда `running` на `rulePack`; диагностика показывает, сколько правил/evidence ушло в provider, где произошел timeout/error и какой fallback был использован.
- Scope:
  - Добавить `DRAFT_EVIDENCE_INTERPRETATION_TIMEOUT_SECONDS` с default `75`.
  - Обернуть provider-backed `EvidenceInterpretation` попытку в operation-level timeout.
  - Создавать failed child `AiRun`, вызывать `progress.fail_operation` и продолжать repair/backup/fallback после timeout.
  - Сократить provider payload до post contract, accepted evidence, evidence synthesis, external claims and relevant rule subset.
  - Записывать input stats и operation timings в trace.
- Out of scope:
  - Новые DraftRun step keys, SQLite schema changes, prompt-quality redesign, global JSON-operation timeout generalization.
  - Изменение порядка `rulePack -> materialPlan` или выбор модели `DRAFT_STRATEGY_MODEL`.
- Architecture impact:
  - Первый runtime repair помещает `backend/app/drafting/application/operations` как bounded-context место для timeout and compact provider-input helpers.
  - Legacy `EvidenceInterpretationService` остается на месте до package migration, но теперь использует reusable operation helper слой.
- Tests:
  - Backend tests for timeout continuation, failed child `AiRun`, compact payload, provider success, malformed/empty JSON retry/fallback, and settings default.
  - DraftRun pipeline regression, architecture smoke, roadmap render/export/check, and smoke.
- Docs:
  - Update DraftRun AS IS Markdown/PDF, backend target architecture, drafting component map, developer guide, `.env.example`, tracker export and generated roadmap.
- Demo impact:
  - No demo fixture change; live verification should use a fresh DraftRun after implementation.
- Acceptance criteria:
  - A hung evidence interpretation attempt times out, records safe failure trace, and does not leave `rulePack` running.
  - Provider request payload is compact and records original/compact counts.
  - Successful evidence interpretation behavior remains unchanged.
  - Deterministic fallback remains explicit if all provider attempts fail or time out.
- Risks:
  - Python cannot kill a blocked provider thread; the timeout envelope contains the DraftRun workflow but a broader worker watchdog remains future infrastructure work.
- Completed: 2026-07-04

### Slice 2.17.4.6.0.3.2: Universal LLM Operation Envelope, Payload Budgets, and Incident Taxonomy

- Status: Ready
- Goal: Ввести сквозную governance-систему для всех provider-heavy LLM operations: единый operation envelope, retry/fallback policy, payload stats, incident taxonomy, blast-radius diagnostics и project-specific architecture guardrails.
- User value: DraftRun перестает чиниться точечно: если одна LLM operation зависла, вернула malformed JSON, ушла в fallback или получила слишком большой payload, система показывает это как диагностируемый инцидент и не допускает повторения того же паттерна в других шагах.
- Scope:
  - Провести inventory всех текущих DraftRun/HITL/Radar provider-heavy LLM operations: source intent, public evidence search/reader wrappers where applicable, evidence interpretation, material plan, strategy, rhetorical plans, draft candidate, LLM validation, editorial critique, alternative angle, directed revision, pairwise ranking, final quality gate, HITL revision and HITL quality check.
  - Ввести единый `LlmOperationEnvelope`/`JsonOperationEnvelope` в bounded-context/shared layer с явными профилями: `interactive`, `background`, `longBackground`, `batch`.
  - Разделить timeout semantics: provider HTTP timeout, whole-attempt timeout, step budget, run budget, stale watchdog; запретить трактовать один короткий timeout как универсальный SLA для ночной генерации.
  - Сделать fallback инцидентом: каждый fallback/backup/not-run/deterministic result получает `incidentType`, `incidentSeverity`, `probableCause`, `needsFollowUp`, `model`, `provider`, `attemptLabel`, `payloadStats` and safe error.
  - Добавить incident taxonomy: provider timeout, network error, provider 4xx/5xx, malformed JSON, schema/shape failure, payload too large, context over-budget, deterministic fallback, backup accepted, stale operation, cancellation/worker failure.
  - Ввести обязательные `inputStats` для LLM calls: prompt char estimate, approximate token estimate where available, rule count, evidence count, claim count, source count, candidate count, model, timeout profile, retry policy, generation params.
  - Обновить diagnostics skill: при повторяемом классе проблемы skill обязан делать blast-radius scan по всем LLM operations, отличать slow background execution от stuck operation, и эскалировать на architecture slice when the same failure pattern is systemic.
  - Усилить architecture smoke/AST checks: новые provider-heavy calls не могут появляться вне operation envelope; новые JSON LLM operations не могут возвращать raw dict without `JsonOperationResult`; новые fallback paths должны иметь incident metadata.
  - Обновить ADR/SAO/backend target docs: project-specific rule is that LLM runtime governance is a first-class architecture boundary, not an optional helper.
- Out of scope:
  - Prompt-quality rewrite, model portfolio experiments, DraftRun step order changes, SQLite schema changes, UI trace redesign, and full payload budget policy tuning.
  - Changing every operation's business semantics; this slice standardizes execution envelope and incident reporting first.
- Implementation notes:
  - Start from a provider-neutral contract and migrate existing operations behind adapters where direct rewrite is too risky.
  - Keep long-running background generation valid: the goal is bounded, explainable execution, not forcing all operations under 75 seconds.
  - Preserve deterministic fallbacks only where domain-safe; unsafe fallback paths must return `not_run` or `failed` with incident metadata.
- Architecture impact:
  - Establishes a cross-cutting LLM operation boundary used by DraftRun, HITL, and future Radar extraction/scoring.
  - Adds project-specific guardrails to architecture smoke, not just generic folder/package checks.
  - Makes agent diagnostics responsible for systemic escalation, not only local root-cause notes.
- Tests:
  - Contract tests for all envelope statuses: accepted, repaired, backupAccepted, fallback, notRun, failed, timeout, cancelled/stale.
  - AST/architecture smoke negative fixtures for raw provider calls, raw dict JSON results, fallback without incident metadata, and missing inputStats.
  - Regression tests for representative migrated operations: evidence interpretation, draft candidate, editorial critique, directed revision, HITL quality check.
  - Roadmap render/export/check and smoke.
- Docs:
  - ADR: universal LLM operation governance and incident taxonomy.
  - Update SAO, backend target architecture, DraftRun AS IS, developer guide, diagnostics skill, slice implementation guidance, and relevant agent skills.
- Demo impact:
  - No demo content change; trace examples in docs should use recent run `d31addee-cdd5-473c-a930-2028e013293e` as evidence that slow background runs are not the same as stuck runs.
- Acceptance criteria:
  - Every current LLM JSON/provider-heavy operation is either behind the envelope or explicitly listed in a temporary debt allowlist with owner, reason and removal slice.
  - Any fallback creates an incident record; fallback is never silently treated as normal success.
  - Diagnostics can answer: what was sent, how large it was, which attempt failed, why fallback happened, and whether this is a systemic pattern.
  - New raw LLM calls outside the envelope fail architecture smoke.
  - The next `python -m backend.app.roadmap next` points here until this governance layer is implemented.
- Risks:
  - Broad cross-cutting migration can create churn; mitigate with adapters, allowlist debt, and targeted representative tests.
  - Too strict timeouts can break legitimate background generation; timeout profiles must be explicit and workload-specific.

### Slice 2.17.4.6.0.3.3: DraftRun Payload Budget Policies

- Status: Backlog
- Goal: Формализовать payload budgets для DraftRun operations, чтобы каждая LLM operation получала ровно тот контекст, который ей нужен, а не весь accumulated artifact dump.
- User value: Генерация становится дешевле, быстрее и стабильнее; качество диагностики растет, потому что видно не только что модель не ответила, но и почему payload был неоправданно тяжелым.
- Scope:
  - Описать per-operation input contracts: какие поля нужны source intent, evidence interpretation, material plan, strategy, rhetorical plans, writer, critic, revision, final gate, HITL revision and quality check.
  - Ввести payload budget profiles by operation type and execution mode: max prompt chars/tokens, max rules, max claims, max evidence items, max candidates, max source snippets, max prior drafts.
  - Разделить semantic inputs: `mustHave`, `shouldHave`, `diagnosticOnly`, `neverSendToProvider`.
  - Сделать deterministic compactors/selectors per operation, not one generic truncation helper.
  - Запретить отправку полного `ruleRegistrySnapshot`, full source ledger, full validation artifact, full candidate pool or full revision trace без явного budget policy.
  - Сохранять trim/suppression metadata: what was sent, what was trimmed, why, and whether trimming changes quality risk.
  - Подключить payload budget violations к incident taxonomy from `2.17.4.6.0.3.2`.
- Out of scope:
  - Changing model choices, prompt wording beyond input contracts, DraftRun step order, UI redesign, external search algorithms.
- Implementation notes:
  - EvidenceInterpretation compact builder from `2.17.4.6.0.3.1` becomes one instance of the general policy, not a special one-off.
  - Budget defaults must respect background generation: slower is acceptable, unbounded or semantically noisy input is not.
- Architecture impact:
  - Creates a provider-input boundary between artifacts and prompts: artifacts may stay rich, provider payloads must be curated.
  - Moves context shaping from ad hoc prompt builders into named application policies.
- Tests:
  - Unit tests for each operation compactor: preserves required fields, trims diagnostic noise, records stats.
  - Regression tests proving large rule/evidence/candidate sets no longer inflate provider payloads beyond configured budgets.
  - Architecture smoke for forbidden full-artifact provider payload patterns where statically detectable.
- Docs:
  - Update DraftRun AS IS, backend target architecture, developer guide and diagnostics checklist with per-operation payload budgets.
- Demo impact:
  - No fixture change; benchmark DraftRuns should report payload stats in trace.
- Acceptance criteria:
  - Every LLM operation has an explicit payload budget policy or debt allowlist entry.
  - Trace includes sent/trimmed counts and prompt size estimates.
  - Full artifact dumps are not sent to provider unless explicitly justified and budgeted.
- Risks:
  - Over-trimming can degrade quality; policies must preserve `mustHave` fields and expose quality risks when context is removed.

### Slice 2.17.4.6.0.3.4: Validation and Revision Loop Runtime Guard

- Status: Backlog
- Goal: Добавить runtime guard для `validation` / ranking-revision loop: long-running validation is allowed, but must be budgeted, trace-visible, and unable to spin indefinitely.
- User value: Background DraftRun может работать 20-40 минут, но редактор и разработчик видят, какие validation/revision operations идут, сколько бюджета осталось, почему loop продолжается, and when it will stop.
- Scope:
  - Ввести validation-loop budget profile: max wall-clock, max LLM calls, max revision cycles, max pairwise rounds, max final-gate repair cycles, max consecutive non-improving attempts.
  - Разделить slow-but-healthy progress from stuck operation using heartbeat/current operation markers and operation-level envelope from `2.17.4.6.0.3.2`.
  - Сделать revision loop stop reasons explicit: budgetExhausted, maxIterations, noImprovement, providerIncident, acceptedQuality, humanReviewRequired.
  - Ensure every validation sub-operation records operation id, model role, attempt label, payload stats, incident metadata if fallback/backup/not-run happens.
  - Add stale/long-operation diagnostics that do not mark healthy background run as failed solely because it exceeds a short interactive timeout.
  - Update run diagnostics to show validation runtime breakdown: LLM validation, editorial critique, alternative angle, pairwise ranking, directed revision, final quality gate.
- Out of scope:
  - Quality scoring redesign, new critic model selection, new DraftRun steps, final prose quality changes.
- Implementation notes:
  - Use the universal operation envelope instead of another local timeout helper.
  - Use background timeout profile by default; interactive UI polling should report progress, not kill the run prematurely.
- Architecture impact:
  - Converts validation/revision from a collection of nested calls into a budgeted loop with explicit runtime contract.
  - Builds on incident taxonomy and payload budgets instead of duplicating error handling.
- Tests:
  - Fake provider tests for slow but progressing validation loop.
  - Tests for max wall-clock/call/cycle budget stop reasons.
  - Tests for stuck sub-operation creating incident and controlled loop termination.
  - Regression tests for accepted final draft path and blocked human-review-required path.
- Docs:
  - Update DraftRun AS IS, diagnostics skill, developer guide and trace docs with validation-loop runtime budget semantics.
- Demo impact:
  - No demo fixture change; live DraftRun diagnostics can use `d31addee-cdd5-473c-a930-2028e013293e` as an example of long validation that eventually completed.
- Acceptance criteria:
  - Validation cannot run indefinitely without heartbeat/progress and budget accounting.
  - Long background validation is not misreported as stuck if operations continue to complete.
  - Stop reason is always present when validation exits without a normal accepted final draft.
- Risks:
  - Too aggressive guardrails can reduce quality by stopping useful revision cycles; defaults must distinguish smoke/interactive/background/full modes.

### Slice 2.17.4.6.0.4: Drafting Context, Evidence, and Planning Package Migration

- Status: Backlog
- Goal: Move the early DraftRun clusters into the drafting bounded context with documented owners and stable compatibility imports after LLM operation governance is in place.
- User value:
  - The research and planning half of DraftRun becomes navigable by pipeline stage rather than by a flat filename prefix.
- Scope:
  - Migrate context, source intent, source ledger, public evidence, feasibility, post contract, rule pack, evidence interpretation, material plan, strategy, and rhetorical plan modules into drafting step/artifact packages in small sub-batches.
  - Keep legacy imports working through shims until all call sites are updated.
  - Update tests to target the new package paths where practical.
  - Tighten allowlists so migrated legacy flat files cannot be reintroduced.
- Out of scope:
  - Candidate generation, validation, revision, final quality gate migration.
  - Prompt redesign or evidence quality changes.
- Implementation notes:
  - Move by cohesive cluster and run targeted tests after each cluster in the implementation slice.
- Architecture impact:
  - Shrinks the flat `application/draft_*` surface and makes early pipeline responsibilities explicit.
- Tests:
  - Source ledger, source intent, public evidence, rule pack, material plan, strategy, and rhetorical plan tests.
  - `npm run test:architecture` with tightened legacy allowlist.
- Docs:
  - Update component map and DraftRun AS IS module references.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - Early DraftRun clusters live under `backend/app/drafting` or have documented temporary shims.
  - No behavior change in DraftRun planning tests.
- Risks:
  - Large import churn; use compatibility shims and avoid mixing behavior changes with moves.

### Slice 2.17.4.6.0.5: Drafting Candidate, Validation, and Revision Package Migration

- Status: Backlog
- Goal: Move the late DraftRun clusters into the drafting bounded context and standardize candidate/validation/revision contracts.
- User value:
  - The quality-critical backend code becomes easier to audit, debug, and extend without breaking hidden contracts.
- Scope:
  - Migrate candidate generation/selection, LLM validation, editorial critique, alternative angle, ranking, revision loop, final quality gate, and human-comment revision quality modules into drafting packages.
  - Normalize late-step result contracts onto `DraftStepOutcome` where feasible.
  - Keep AiRun audit payload compatibility and old trace readability.
  - Tighten architecture smoke against top-level public helper function sprawl in migrated packages.
- Out of scope:
  - Changing quality policy, prompts, ranking algorithm, or final draft selection semantics.
  - New HITL learning behavior.
- Implementation notes:
  - This slice should be split internally into sub-batches if the diff becomes too large.
- Architecture impact:
  - Completes most DraftRun code movement into the drafting bounded context.
- Tests:
  - Candidate, validation, critic, alternative angle, ranking/revision, final quality gate, human revision tests.
  - Backward-compat trace tests for old runs where available.
- Docs:
  - Update component map, DraftRun AS IS, developer guide, and migration notes.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - Late DraftRun clusters live under `backend/app/drafting` or have explicit temporary shims.
  - Architecture smoke rejects new flat late-stage `draft_*` files.
- Risks:
  - This is the highest-risk migration because it touches provider-heavy and trace-heavy code.

### Slice 2.17.4.6.0.6: Backend Documentation and Agent Guardrail Hardening

- Status: Backlog
- Goal: Make the new backend architecture durable for future agents and contributors.
- User value:
  - A new contributor can understand backend structure from docs and cannot accidentally add code in the old broken style without a failing check.
- Scope:
  - Finalize backend README, drafting README, component map, and migration notes.
  - Update AGENTS.md and local skills so backend work must read the backend architecture docs and obey bounded-context placement.
  - Add strict-mode architecture smoke for new modules and reduce legacy allowlists after migrations.
  - Document a backend module template with `Architecture`, `Owner`, `Used by`, and `Does not own` anchors.
  - Add checklist for reviewing provider-heavy services, JSON contracts, and trace payloads.
- Out of scope:
  - Further product features or search quality improvements.
- Implementation notes:
  - This is where the recovery track becomes the normal development contract.
- Architecture impact:
  - Turns the refactor into enforceable team practice instead of one-time cleanup.
- Tests:
  - Architecture smoke strict-mode checks.
  - Docs presence checks for backend component anchors.
  - Roadmap tracker check/render/export.
- Docs:
  - Update SAO, developer guide, contributor guide, AGENTS.md, and skills guidance.
- Demo impact:
  - No user-facing demo change.
- Acceptance criteria:
  - New backend modules without owner docs or correct package placement fail checks.
  - Agents have explicit backend workflow instructions before future runtime work resumes.
- Risks:
  - Too much process can slow delivery; keep checks mechanical and actionable.

### Slice 2.17.4.6.1: Search Intent Planner and Campaign Trace

- Status: Backlog
- Goal: Turn a radar configuration into a typed search campaign with query intents, source strategy, and traceable rationale before provider search runs.
- User value:
  - The user can see not only search results, but what the radar decided to look for, which evidence types it tried to cover, and why.
- Scope:
  - Add provider-free `SearchPlan`, `SearchIntent`, `SearchQuery`, and `SearchCampaignTrace` contracts.
  - Derive query intents from radar definition, source handles, project language, topics, fabulas, publisher rules, research depth, and benchmark project profile.
  - Generate multiple query families: broad discovery, case/example, benchmark/paper, OSS/tooling, limitation/critique, and freshness queries where relevant.
  - Store generated queries, intent rationale, source strategy, and skipped intent reasons in `RadarRun`.
- Out of scope:
  - LLM query expansion.
  - Signal extraction or scoring.
  - Candidate assembly.
  - Scheduled radar runs.
- Implementation notes:
  - Deterministic planner is the baseline for every later search layer.
  - The planner must not assign final topic/fabula ownership to raw material.
- Architecture impact:
  - Introduces explicit search-planning contracts between `RadarRun` and provider retrieval.
- Tests:
  - Planner tests for the three benchmark projects.
  - Tests for language-aware query generation and evidence-type coverage.
  - Trace tests proving generated queries and rationale are persisted.
- Docs:
  - Update upstream architecture, developer guide, user guide, and demo README.
- Demo impact:
  - Benchmark radars show readable search plans before any provider call.
- Acceptance criteria:
  - A radar can produce a traceable search campaign without calling a provider.
  - Each campaign has at least several typed intents or explicit skipped reasons.
- Risks:
  - Deterministic queries can become formulaic; later LLM expansion must improve breadth without replacing traceability.

### Slice 2.17.4.6.1.1: Golden Radar Benchmark Scenario

- Status: Backlog
- Goal: Add one canonical radar benchmark scenario for `Опытный цех «Сборочная»` so upstream search changes can be evaluated against a stable diagnostic case.
- User value:
  - The team can test radar search quality on a concrete industrial AI scenario instead of judging by one-off screenshots or ad hoc live runs.
- Scope:
  - Add provider-free `RadarBenchmarkScenario` metadata for `benchmark-industrial-ai-maintenance-cases`.
  - Bind it to project `project-ai-design-patterns` and the industrial AI cases radar.
  - Define expected query intents, evidence types, minimum raw results, selected reads, found materials, source diversity, and unacceptable noise.
  - Add recorded fixture adapters/results so the scenario runs without network or OpenRouter spend.
  - Produce a deterministic benchmark report covering intent coverage, source diversity, read success, noise, and trace completeness.
  - Ensure the benchmark proves no `SourceSignal`, `PostCandidate`, plan slot, or DraftRun is created.
- Out of scope:
  - Three-project benchmark corpus.
  - Live provider quality approval.
  - Signal extraction, scoring, candidate assembly, or DraftRun changes.
  - New UI trace page.
- Implementation notes:
  - The scenario should exercise the mature search algorithm: search plan, query fan-out, raw results, dedupe, selective URL read, and normalized `FoundMaterial`.
  - Use recorded fixture mode as the regression gate; live smoke mode can remain documented/manual until the broader harness slice.
- Architecture impact:
  - Introduces benchmark-scenario ownership as application/test support around upstream search, not inside React feature components.
- Tests:
  - Recorded benchmark test for `Опытный цех «Сборочная»` industrial AI cases.
  - Assertions for expected intents, evidence-type coverage, read decisions, source diversity, and no downstream artifact creation.
  - Regression with existing radar runner tests.
- Docs:
  - Update upstream architecture, developer guide, demo README, and roadmap artifacts.
- Demo impact:
  - The three-blog portfolio gets one explicit golden upstream-search diagnostic scenario before the full benchmark corpus.
- Acceptance criteria:
  - A single command/test can run the golden scenario without network access and produce a readable pass/warning/fail report.
  - The report explains what the radar searched, what it found, what it rejected, and which expectations were not met.
- Risks:
  - Fixture quality can become too curated; keep recorded data realistic and include at least one noisy/duplicate result.

### Slice 2.17.4.6.1.2: RadarRun Trace Page

- Status: Backlog
- Goal: Add a dedicated `RadarRun` trace page similar to DraftRun/AiRun trace inspection so search diagnostics are readable outside the compact radar card.
- User value:
  - The editor and developer can inspect exactly how a radar searched, selected, skipped, failed, and normalized material without digging through JSON or cramped inline panels.
- Scope:
  - Add route/page `/radar-runs?runId=<id>` or equivalent app route for one `RadarRun`.
  - Show project, radar, run status, budget, mode, start/completion timestamps, and provider/config summary.
  - Render search plan, source handles, operation timeline, raw results, selected-for-read, rejected-before-read, found materials, warnings, and errors.
  - Add benchmark verdict section when a `RadarBenchmarkScenario` report is available.
  - Link from `Сигналы -> Радары -> Трасса запуска` to the dedicated trace page.
  - Keep old/minimal radar runs readable when they do not have `searchPlan`, `rawResults`, or benchmark metadata.
- Out of scope:
  - Editing radar configuration from the trace page.
  - Signal approval, candidate assembly, or DraftRun trace changes.
  - New backend persistence tables.
- Implementation notes:
  - Treat the page as a read model over existing workspace/backend snapshot data.
  - Reuse the semantic trace approach from `/ai-runs?runId=...`, but keep upstream search concepts separate from DraftRun concepts.
- Architecture impact:
  - Separates diagnostic trace inspection from the operational radar card UI and prevents `RadarCard` from becoming a diagnostics god component.
- Tests:
  - UI tests for trace page rendering with full external run metadata.
  - Compatibility tests for old deterministic/minimal runs.
  - Link/navigation test from radar run tab to trace page.
- Docs:
  - Update user guide, developer guide, demo README, and upstream architecture.
- Demo impact:
  - Demo users can open a readable trace for the golden industrial AI benchmark run.
- Acceptance criteria:
  - A user can open one run id and understand search plan, operations, raw results, triage, found materials, and benchmark verdict.
  - The compact radar card remains usable and does not duplicate the full diagnostic page.
- Risks:
  - Trace page can become too dense; use progressive disclosure and semantic sections rather than raw JSON dumps.

### Slice 2.17.4.6.2: Search Result Triage, Deduplication, and Selective Reading

- Status: Backlog
- Goal: Stop treating provider result order as quality by adding explainable pre-read triage, URL canonicalization, deduplication, diversity selection, and selective URL reading.
- User value:
  - The radar reads fewer but better materials and explains which links were selected, rejected, duplicated, or unreadable.
- Scope:
  - Add raw search result normalization before `FoundMaterial` creation.
  - Canonicalize URLs, domains, titles, and duplicate groups.
  - Score snippet-level relevance, evidence type, source credibility, novelty, project fit, and risk.
  - Select diverse results across query intents and domains before URL reading.
  - Store `selectedForRead`, `rejectedBeforeRead`, duplicate groups, and read failures in trace.
- Out of scope:
  - LLM extraction/scoring.
  - Full source credibility database.
  - Candidate generation.
- Implementation notes:
  - Search-result triage is diagnostic, not final editorial judgment.
  - Failed URL reads must remain visible as warnings, not disappear.
- Architecture impact:
  - Adds the retrieval-quality layer between provider search and durable found material.
- Tests:
  - Dedupe tests for URL variants and repeated provider results.
  - Triage tests for strong case materials, weak generic articles, duplicates, and unreadable URLs.
  - UI/trace tests for selected/rejected/read-failed materials.
- Docs:
  - Update upstream architecture, diagnostics notes, developer guide, and user guide.
- Demo impact:
  - Demo radars show why some links were read and others were not.
- Acceptance criteria:
  - Provider results are not blindly promoted in search order.
  - Read selection is diverse and trace-visible.
- Risks:
  - Triage can over-filter surprising materials; keep rejected-before-read inspectable.

### Slice 2.17.4.6.3: Source Strategy Adapters and Domain-Aware Search

- Status: Backlog
- Goal: Make search behavior depend on source type and editorial intent instead of using one generic open-web query path for everything.
- User value:
  - Radars can deliberately search known domains, URLs, project documents, open web, OSS repositories, papers, and future feeds without mixing their responsibilities.
- Scope:
  - Add source strategy policy for `openWebQuery`, `knownUrl`, `domain`, `document`, `internal`, and future OSS/paper/feed adapters.
  - Support site/domain-restricted search where applicable.
  - Add direct URL read strategy for known URLs.
  - Keep unsupported adapters explicit with `skipped/not-implemented` operations.
  - Extend trace with source strategy, adapter used, and per-source skipped reasons.
- Out of scope:
  - Full RSS/social/crawler integrations.
  - Provider credentials for external platform APIs.
  - Signal extraction.
- Implementation notes:
  - `SourceHandle` remains project-owned; adapters are infrastructure/application concerns.
  - Internal sources continue to run without provider calls.
- Architecture impact:
  - Separates source registry semantics from provider execution mechanics.
- Tests:
  - Strategy selection tests per source handle type.
  - Domain-restricted query tests.
  - Project isolation tests for source handles and runs.
- Docs:
  - Update upstream architecture, source registry docs, developer guide, and demo README.
- Demo impact:
  - Each benchmark project can show different source strategy mix.
- Acceptance criteria:
  - A radar run can explain how each source handle was executed or skipped.
  - Open-web, known URL, and internal sources have distinct behavior.
- Risks:
  - Adapter matrix can grow too quickly; keep v1 policy small and explicit.

### Slice 2.17.4.6.4: LLM-Assisted Query Expansion and Search Critic

- Status: Backlog
- Goal: Add a controlled LLM layer that improves search campaigns without hiding deterministic planner decisions or becoming the only search brain.
- User value:
  - Radars can find less obvious materials and alternative angles while keeping every generated query, assumption, and failure visible.
- Scope:
  - Add optional LLM-assisted query expansion after deterministic search plan creation.
  - Use research/review role model with universal JSON retry policy.
  - Ask the model for missing query intents, counter-queries, domain-specific vocabulary, source-type hints, and blind spots.
  - Add a search critic pass that flags weak campaigns before execution when budget allows.
  - Persist LLM attempts, selected model, generation params, accepted/rejected query suggestions, and fallback behavior.
- Out of scope:
  - Letting LLM directly approve signals or candidates.
  - Hidden autonomous browsing loops.
  - Unbounded query generation.
- Implementation notes:
  - Deterministic planner is always available as fallback.
  - LLM expansion may improve breadth, but cannot erase deterministic trace.
- Architecture impact:
  - Adds an AI-assisted planning layer while preserving provider-free domain contracts.
- Tests:
  - JSON retry tests for malformed query expansion.
  - Fallback tests when LLM is unavailable.
  - Tests that deterministic queries remain present.
- Docs:
  - Update ADR/architecture notes about LLM search planning boundaries.
  - Update developer/user diagnostics docs.
- Demo impact:
  - Benchmark radars can show deterministic vs AI-expanded query plans.
- Acceptance criteria:
  - LLM-expanded campaigns are trace-visible and bounded.
  - Provider failure does not block deterministic search.
- Risks:
  - LLM may add noisy or over-broad queries; require accepted/rejected query suggestions in trace.

### Slice 2.17.4.6.5: Radar Search Evaluation Harness and Benchmark Corpus

- Status: Backlog
- Goal: Make search quality measurable with benchmark radar scenarios before promoting the upstream search runner as reliable.
- User value:
  - The team can compare search algorithm changes on the three benchmark blogs instead of judging by screenshots or single lucky runs.
- Scope:
  - Add benchmark radar fixtures for `Опытный цех`, `Северная стена`, and `Блог Главреда`.
  - Define expected evidence types, unacceptable noise, freshness expectations, diversity targets, and must-not-miss source categories.
  - Add evaluation reports for recall proxies, precision proxies, duplicate rate, read success rate, source diversity, evidence-type coverage, and trace completeness.
  - Add smoke-mode benchmark runs that do not require high spend.
- Out of scope:
  - Automatic quality approval.
  - Full web-scale recall measurement.
  - DraftRun text quality evaluation.
- Implementation notes:
  - Metrics are directional: enough to catch regressions and compare algorithms, not a scientific IR benchmark.
- Architecture impact:
  - Converts demo portfolio into an upstream-search evaluation harness.
- Tests:
  - Benchmark fixture tests.
  - Evaluation report unit tests.
  - Smoke benchmark command or documented manual workflow.
- Docs:
  - Update demo README, developer guide, and diagnostics docs.
- Demo impact:
  - Three benchmark blogs become repeatable upstream search scenarios.
- Acceptance criteria:
  - A benchmark run can say what improved, regressed, or remained unknown.
  - Empty/low-quality search results produce actionable diagnostics.
- Risks:
  - Metrics can incentivize quantity over usefulness; keep editorial evidence-type expectations visible.

### Slice 2.17.4.6.6: Search Memory, Refresh Policy, and Production Controls

- Status: Backlog
- Goal: Move radar search from useful prototype to production-ready operation with history, refresh rules, caching, rate limits, retries, and cost controls.
- User value:
  - Radars can be rerun safely without repeatedly surfacing the same stale links, burning budget unpredictably, or hiding provider instability.
- Scope:
  - Add project-scoped search memory for seen URLs, material fingerprints, duplicate groups, and previously rejected materials.
  - Add freshness and recheck policy for changed/stale materials.
  - Add cache boundaries for search results and URL reads.
  - Add provider retry/backoff, timeout handling, rate and cost accounting, and production diagnostics.
  - Distinguish empty, partial, failed, stale-only, and provider-limited runs.
- Out of scope:
  - Scheduled background jobs unless already available.
  - Cross-user shared index.
  - External publication or social APIs.
- Implementation notes:
  - This is the production-readiness gate before treating upstream search as a dependable product subsystem.
- Architecture impact:
  - Adds operational reliability around provider-backed upstream search while keeping project isolation.
- Tests:
  - Cache and refresh policy tests.
  - Retry/backoff/failure tests with fake adapters.
  - Budget/cost accounting tests.
  - Regression tests proving reruns do not spam duplicate materials.
- Docs:
  - Update operations diagnostics, developer guide, user guide, and upstream architecture.
- Demo impact:
  - Demo runs can show seen/new/stale material distinctions.
- Acceptance criteria:
  - Repeated radar runs are bounded, explainable, and do not repeatedly surface the same material as new.
  - Provider instability is visible and recoverable.
- Risks:
  - Search memory can hide useful rediscoveries; keep manual reset/reconsider path.

### Slice 2.17.4.7: Signal Extraction and Editorial Scoring

- Status: Backlog
- Goal: Convert found materials into reviewed `SourceSignal` candidates with explicit editorial scoring before they can feed post candidates.
- User value:
  - The user sees not just raw links, but why a material is promising, weak, duplicate, off-position, or worth turning into a post idea.
- Scope:
  - Add `SignalExtractionReport` and `SignalScore` contracts.
  - Extract possible source signals from found materials using deterministic rules plus optional review-role JSON call where useful.
  - Score novelty, source credibility, author fit, audience value, positioning fit, topic fit, evidence strength, and risk.
  - Keep `SourceSignal` raw/reviewed: no final topic/fabula ownership yet.
  - Add status: `candidate`, `approved`, `rejected`, `archived`, with explainable scoring metadata.
- Out of scope:
  - Draft text generation.
  - Multi-platform planning.
  - Long-term learning/promotion rules.
- Implementation notes:
  - Universal JSON retry policy applies to any LLM extraction/scoring call.
  - Deterministic fallback can produce diagnostic scoring only where safe; no fake high-quality signal.
- Architecture impact:
  - Introduces the editorial judgment layer between retrieval and candidate assembly.
- Tests:
  - Extraction/scoring unit tests for good, duplicate, off-position, and weak-source materials.
  - JSON retry/failure trace tests if LLM scoring is used.
  - UI tests for score breakdown and review actions.
- Docs:
  - SAO, developer guide, user guide.
- Demo impact:
  - Benchmark blogs get scored signals that reflect their distinct editorial policies.
- Acceptance criteria:
  - A found material can become a scored signal with clear reasons and risks.
- Risks:
  - Scoring can become opaque; require visible dimension-level explanations.

### Slice 2.17.4.8: Signal x Topic x Fabula Candidate Assembly v2

- Status: Backlog
- Goal: Replace mechanical approved-signal ? topic/fabula pairing with explainable candidate assembly and ranking.
- User value:
  - The user receives fewer but stronger post candidates, each explaining why this signal fits this topic, fabula, audience value, and channel context.
- Scope:
  - Add `CandidateAssemblyReport`, `CandidateMatch`, and `CandidateRanking` contracts.
  - Use signal scores, topic/fabula matrix, publisher rules, author memory, channel/default platform, and benchmark expectations.
  - Generate multiple candidate angles only when justified; avoid blind Cartesian products.
  - Explain accepted/rejected topic/fabula matches and candidate risks.
  - Preserve manual edit/approve/reject flow for candidates.
- Out of scope:
  - DraftRun generation changes.
  - Multi-target variants.
  - Automatic plan scheduling.
- Implementation notes:
  - Candidate assembly may start deterministic with optional review-role ranking later.
  - Candidate ids must remain stable enough for plan/workbench links.
- Architecture impact:
  - Moves editorial composition logic into `PostCandidateAssembly` rather than `Signals` UI or `Plan`.
- Tests:
  - Candidate assembly tests for one signal with multiple topics/fabulas.
  - Tests preventing one-to-one topic/fabula coupling regressions.
  - UI tests for candidate rationale and rejection reasons.
- Docs:
  - Developer guide, user guide, SAO.
- Demo impact:
  - Three benchmark blogs should show distinct candidate logic from the same upstream pattern.
- Acceptance criteria:
  - Candidate list is ranked and explainable; no hard `.slice(0, 3)` from blind pairing remains as the main logic.
- Risks:
  - Ranking can hide useful alternatives; keep rejected/alternative matches inspectable.

### Slice 2.17.4.9: Signal Review and Candidate Workbench UX

- Status: Backlog
- Goal: Make the upstream workspace usable: materials, signals, and post candidates become separate readable work surfaces with clear actions and diagnostics.
- User value:
  - The editor can inspect found material, approve/reject signals, compare post candidates, and send the chosen concept to the plan without guessing what happened.
- Scope:
  - Refine `Сигналы` into explicit layers: `Материалы`, `Сигналы`, `Кандидаты`, `Диагностика`.
  - Add compact/expanded states for found material, scored signal, and post candidate cards using the approved design-system card patterns.
  - Show score/rationale, source provenance, topic/fabula match, risks, and next action.
  - Add manual override/correction path that is trace-visible.
  - Keep plan handoff compatible with current downstream flow.
- Out of scope:
  - New DraftRun behavior.
  - Multi-platform variant workbench.
  - Autoposting.
- Implementation notes:
  - Must use `ui-design-systems/START-HERE.md` and existing cabinet/card patterns.
  - Do not put editing forms under action buttons; edit mode transforms fields in place.
- Architecture impact:
  - UI read models follow upstream domain boundaries instead of mixing raw signals and post concepts.
- Tests:
  - App-flow tests from radar run to material to signal to candidate to plan.
  - Visual/design smoke for compact/expanded/edit states.
  - Project isolation tests.
- Docs:
  - User guide, demo README, wiki/screenshots if applicable.
- Demo impact:
  - Demo portfolio can demonstrate upstream work before DraftRun quality is evaluated.
- Acceptance criteria:
  - A user can understand and operate the upstream flow end-to-end without opening DraftRun.
- Risks:
  - The section can become visually dense; prioritize progressive disclosure and two-column cabinet layout.

### Slice 2.17.5: Multi-Target Planning and Variant Workbench

- Status: Backlog
- Goal: Let one editorial idea target multiple publication channels while keeping a
  shared fabula/brief and separate platform variants.
- User value:
  - The author can plan one post for Telegram + Dzen, or LinkedIn article + Telegram
    companion, without duplicating the whole work item manually.
- Scope:
  - Add `targetChannelIds` or equivalent target group on plan/work items.
  - Add `PublicationGroup` for one shared editorial idea.
  - Add per-channel `PlatformVariant` state under the selected work item.
  - Update workbench UX with tabs/segmented controls:
    `Общий замысел`, then one tab per channel variant.
- Out of scope:
  - Running multi-platform DraftRun.
  - Real publication adapters.
  - Cross-platform analytics.
- Implementation notes:
  - Shared brief remains the source of intent; platform variants own their draft,
    version history, final approval, and readiness.
- Architecture impact:
  - Adds platform-variant state without changing author memory or topic/fabula reuse.
- Tests:
  - Domain tests for target groups and variant isolation.
  - UI tests for channel tabs and final selection per variant.
- Docs:
  - User guide, SAO, roadmap.
- Demo impact:
  - `Блог Главреда` can show a Telegram + Dzen work item.
- Acceptance criteria:
  - One work item can hold at least two channel variants without overwriting drafts.
- Risks:
  - UI complexity; keep v1 focused on one selected work item.

### Slice 2.17.6: Multi-Platform DraftRun Contract v1

- Status: Backlog
- Goal: Generate platform-specific variants from one shared editorial idea using
  explicit contracts rather than one generic text.
- User value:
  - A Telegram post and a Dzen article can share evidence/thesis but differ in length,
    structure, voice density, CTA, and examples.
- Scope:
  - Build shared context/evidence once where practical.
  - Resolve separate `PostContract` and publication-size contract per target channel.
  - Run one DraftRun per platform variant in v1, linked by `PublicationGroupId`.
  - Show trace links per variant.
- Out of scope:
  - A monolithic group-run orchestrator.
  - Autoposting.
  - Platform API credentials.
- Implementation notes:
  - Prefer transparent separate runs first; optimize shared orchestration later.
  - Keep planned source/evidence work reusable across variant contracts.
- Architecture impact:
  - Extends DraftRun context with project/channel/variant identity while preserving
    current step order.
- Tests:
  - Backend/frontend contract tests for variant-specific context.
  - Smoke run for two variants from one shared work item.
- Docs:
  - DraftRun AS IS map and PDF must be updated when implemented.
- Demo impact:
  - `Блог Главреда` becomes the first multi-platform benchmark.
- Acceptance criteria:
  - Two channel variants can be generated, traced, approved, and learned from
    independently.
- Risks:
  - Cost and runtime increase; use budget modes and smoke mode for diagnostics.

### Slice 2.17.7: Blog Portfolio Benchmark Runner

- Status: Backlog
- Goal: Turn the three-blog demo portfolio into a repeatable benchmark for pipeline
  quality and regression diagnosis.
- User value:
  - Changes to models, prompts, retrieval, validation, revision, and platform
    adaptation can be judged against multiple real editorial systems.
- Scope:
  - Add benchmark scenario definitions per blog.
  - Add a runner that can execute selected scenarios in smoke/standard/full mode.
  - Produce a report covering project isolation, channel adaptation, author voice,
    source use, final quality gate status, HITL readiness, and learning-note output.
  - Keep private benchmark inputs gitignored.
- Out of scope:
  - Automatic approval of quality.
  - Full analytics ingestion.
  - Publishing to platforms.
- Implementation notes:
  - The benchmark should say "good enough to continue" vs "repair slice needed" using
    roadmap-aware diagnostics.
- Architecture impact:
  - Converts demo portfolio into a product-quality test harness.
- Tests:
  - Runner unit tests, smoke benchmark tests, docs for private fixtures.
- Docs:
  - Developer guide, demo README, diagnostics skill notes.
- Demo impact:
  - Demo portfolio becomes both visible product sample and repeatable quality suite.
- Acceptance criteria:
  - At least one scenario per blog can be run and summarized.
  - Reports distinguish expected future gaps from unexpected regressions.
- Risks:
  - Benchmark can become expensive; v1 must support smoke mode.

### Future Slice: Rule Promotion from Accepted Editorial Learning Notes

- Status: Backlog
- Goal: Turn accepted `editorialLearning` notes into explicit, reviewable proposals
  for publisher rules, Topic/Fabula guidance, source strategy, validators, prompts, or
  model policy.
- Scope:
  - Read only accepted editorial-learning notes.
  - Group repeated lessons across posts.
  - Create explainable improvement proposals linked back to versions, comments,
    quality checks, and final decisions.
  - Require explicit human approval before mutating any editorial setting.
- Out of scope:
  - Silent prompt/rule mutation.
  - Automatic fine-tuning.
  - Cross-user learning.

### Deferred: Document AI Platform Import Adapter

- Status: Deferred
- Goal: Integrate `langgraph-document-ai-platform` behind a backend adapter for
  document/archive analysis.
- Reason deferred:
  - The current product risk is drafting orchestration, not archive import. The next
    backend foundation should establish durable queue/run semantics first.
- Re-open when:
  - Queued `DraftRun` semantics and trace contracts are stable enough to reuse for
    document workflows.

## Completed Slices

- Slice 0.1: Bootstrap Project Structure. Completed 2026-06-03.
- Slice 0.2: Brief-Backed Bootstrap Update. Completed 2026-06-03.
- Slice 0.3: Architecture Baseline for the First Product Perimeter. Completed 2026-06-03.
- Slice 0.4: First Working Flow to Approved Post Brief. Completed 2026-06-03.
- Slice 0.5: Draft and Editorial Checks. Completed 2026-06-03.
- Slice 0.6: Manual Export and Release Prep. Completed 2026-06-04.
- Slice 0.7: Analytics Prep and Editorial Learning Notes. Completed 2026-06-04.
- Slice 0.8: AI Provider Architecture Baseline. Completed 2026-06-04.
- Slice 0.9: Author Position Product Reframe. Completed 2026-06-10.
- Slice 1.0: Author Memory Feed and Position Evidence Baseline. Completed 2026-06-10.
- Slice 1.0.1: Author Memory UX Hardening. Completed 2026-06-10.
- Slice 1.0.2: Author Memory File Attachments. Completed 2026-06-10.
- Slice 1.0.3: GitHub Wiki Screenshot Documentation Baseline. Completed 2026-06-11.
- Slice 1.0.4: Author Memory External Sources and Import Design. Completed 2026-06-11.
- Slice 1.0.5: External Sources Local UI Shell. Completed 2026-06-11.
- Slice 1.0.5.1: External Sources UX Fixes. Completed 2026-06-11.
- Slice 1.1: Topics and Fabulas as Editorial Entities. Completed 2026-06-11.
- Slice 1.1.1: Editorial Model UX Repair and Frontend UX ADRs. Completed 2026-06-11.
- Slice 1.1.2: Editorial Model Layout and Manual Validation UX Fixes. Completed 2026-06-11.
- Slice 1.1.3: Add and Delete Topics and Fabulas. Completed 2026-06-11.
- Slice 1.2: Validator Framework Baseline. Completed 2026-06-11.
- Slice 1.2.1: Author Memory Sources UX Alignment. Completed 2026-06-12.
- Slice 1.2.2: Source List Visual Repair and UI Guardrails. Completed 2026-06-12.
- Slice 1.3: Context Chat Wizard Skeleton. Completed 2026-06-12.
- Slice 1.3.1: Context Chat UX Repair and Chat Mode. Completed 2026-06-13.
- Slice 1.4: Content Plan as Broadcast Grid. Completed 2026-06-13.
- Slice 1.4.1: Broadcast Planning Concept Correction. Completed 2026-06-13.
- Slice 1.5: Signals and Radar Workspace. Completed 2026-06-13.
- Slice 1.5.1: Radar Rules/Sources and Raw Signal UX Repair. Completed 2026-06-13.
- Slice 1.5.2: Signals UI Design-System Repair and Visual Guardrails. Completed 2026-06-13.
- Slice 1.5.3: Signals Layout Polish and Pixel Guardrails. Completed 2026-06-14.
- Slice 1.5.4: Design-System Guardrails and Signals UI Alignment. Completed 2026-06-14.
- Slice 1.5.5: Frontend Design-System Consolidation. Completed 2026-06-14.
- Slice 1.5.6: Layout Stability and Form Rhythm Guardrails. Completed 2026-06-14.
- Slice 1.5.7: Inline Radar Editing and Multiline Rule Sources. Completed 2026-06-14.
- Slice 1.5.8: Radar Editorial Filters and Source Discovery Mode. Completed 2026-06-14.
- Slice 1.5.9: React Architecture Baseline and App.tsx Growth Guardrails. Completed 2026-06-15.
- Slice 1.5.10: Extract App Shell and Workspace Controller. Completed 2026-06-15.
- Slice 1.5.11: Extract Signals Feature. Completed 2026-06-15.
- Slice 1.5.12: Extract Editorial Model Feature. Completed 2026-06-15.
- Slice 1.5.13: Extract Author Memory Feature. Completed 2026-06-15.
- Slice 1.5.14: Extract Production Flow Features. Completed 2026-06-15.
- Slice 1.5.15: Codebase Size Audit and Modularization Guardrails. Completed 2026-06-15.
- Slice 1.5.16: Split Domain Workspace Types by Bounded Context. Completed 2026-06-15.
- Slice 1.5.17: Split Domain Transitions and Invariants. Completed 2026-06-15.
- Slice 1.5.18: Split Application Services. Completed 2026-06-15.
- Slice 1.5.19: Split Demo Workspace Fixtures. Completed 2026-06-15.
- Slice 1.5.20: Split Author Memory Feature Internals. Completed 2026-06-15.
- Slice 1.5.21: Split Editorial Model Feature Internals. Completed 2026-06-15.
- Slice 1.5.22: Split Signals Feature Internals. Completed 2026-06-15.
- Slice 1.5.23: Bundle and Import Hygiene Baseline. Completed 2026-06-15.
- Slice 1.5.24: Feature Internals Cleanup and OOP Boundaries. Completed 2026-06-15.
- Slice 1.5.25: Author Memory Entry Point Decomposition. Completed 2026-06-15.
- Slice 1.5.26: Signals Feature Internal Decomposition. Completed 2026-06-15.
- Slice 1.5.27: Author Memory Import Queue Decomposition. Completed 2026-06-15.
- Slice 1.5.28: App Workspace Controller Decomposition. Completed 2026-06-15.
- Slice 1.5.29: Architecture Drift Guardrails and Agent Workflow Rules. Completed 2026-06-16.
- Slice 1.6: First Real Post Candidate Assemblies. Completed 2026-06-16.
- Slice 1.7: Candidate List UX Parity and Review Actions. Completed 2026-06-16.
- Slice 1.7.1: Candidate Format Cleanup and Edit Context. Completed 2026-06-16.
- Slice 1.8: Broadcast Grid Settings. Completed 2026-06-17.
- Slice 1.8.1: Broadcast Grid UX Parity, Filters, and Calendar Settings. Completed 2026-06-17.
- Slice 1.8.2: Broadcast Grid Candidate Calendar View. Completed 2026-06-17.
- Slice 1.9: Editorial Work Queue Foundation. Completed 2026-06-17.
- Slice 1.10: Редактура как очередь постов и рабочий стол. Completed 2026-06-17.
- Slice 1.10.1: Editorial Workspace UX Guardrail Repair. Completed 2026-06-17.
- Slice 1.10.2: Automatic Draft After Fabula Approval. Completed 2026-06-17.
- Slice 1.10.3: Editorial Workbench Selection and Picker Repair. Completed 2026-06-17.
- Slice 1.10.4: Editable Fabula Brief With Candidate Context. Completed 2026-06-17.
- Slice 1.10.5: Draft Approval Without Final Tab. Completed 2026-06-18.
- Slice 1.10.6: Visual Stage Foundation. Completed 2026-06-18.
- Slice 1.10.6.1: Visual Variants Review Flow. Completed 2026-06-18.
- Slice 1.10.6.2: Two-Step Meme Remix Visual Flow. Completed 2026-06-18.
- Slice 1.10.6.3: App Flow Test Ownership Guardrails. Completed 2026-06-18.
- Slice 1.10.7: Ready Post Handoff. Completed unknown.
- Slice 2.0: Backend AI Execution Architecture Baseline. Completed 2026-06-18.
- Slice 2.1: Backend Foundation and OpenRouter Environment. Completed 2026-06-18.
- Slice 2.2: AI Run Contract and Audit Trail. Completed 2026-06-18.
- Slice 2.3: First OpenRouter Draft Run. Completed 2026-06-18.
- Slice 2.3.1: Dockerized Local Full-Stack Runner. Completed 2026-06-18.
- Slice 2.3.2: AI Run Observability and Draft Generation Status. Completed 2026-06-18.
- Slice 2.3.3: AI Run Trace Debug Page. Completed 2026-06-18.
- Slice 2.3.4: Agentic Draft Runner Architecture Plan. Completed 2026-06-19.
- Slice 2.4: Draft Run Contract and Queue Foundation. Completed 2026-06-19.
- Slice 2.5: Draft Run Context Builder. Completed 2026-06-19.
- Slice 2.6: Draft Rule Pack Compiler. Completed 2026-06-19.
- Slice 2.7: Material Plan and Draft Strategy Steps. Completed 2026-06-19.
- Slice 2.8: Agentic Multi-Candidate Draft Generation. Completed 2026-06-19.
- Slice 2.8.1: AI Run Trace Workbench. Completed 2026-06-19.
- Slice 2.8.1.1: Draft Run Trace Timeline and Trace UI Repair. Completed 2026-06-19.
- Slice 2.9: Source Ledger Foundation. Completed 2026-06-20.
- Slice 2.10: Feasibility Gate and Post Contract. Completed 2026-06-20.
- Slice 2.10.1: DraftRun Candidate Link Recovery and Feasibility Calibration. Completed 2026-06-22.
- Slice 2.11: Rule Registry v2 and Validator Bindings. Completed 2026-06-22.
- Slice 2.11.1: Publication Size Contract Foundation. Completed 2026-06-23.
- Slice 2.12: Contract-Based Rhetorical Plans. Completed 2026-06-23.
- Slice 2.12.1: DraftRun Stale Runner Recovery and Fallback Discipline. Completed 2026-06-23.
- Slice 2.12.2: Draft Candidate Scoring and Selection Trace. Completed 2026-06-23.
- Slice 2.12.2.1: Scorecard Trace Table Repair. Completed 2026-06-23.
- Slice 2.12.3: Source Intent and Research Plan. Completed 2026-06-23.
- Slice 2.12.3.1: Fabula Research Strategy Defaults. Completed 2026-06-23.
- Slice 2.12.4: Public Evidence Retrieval Foundation. Completed - Completed 2026-06-24..
- Slice 2.12.4.1: OpenRouter Web Search Adapter. Completed - Completed 2026-06-24..
- Slice 2.12.4.2: Public Evidence Query and Relevance Repair. Completed - Completed 2026-06-24..
- Slice 2.12.4.3: Draft Candidate Fallback Selection Guard. Completed unknown.
- Slice 2.12.5: SourceLedger External Evidence Merge. Completed 2026-06-24.
- Slice 2.12.5.1: MaterialPlan Evidence Accountability and Retry. Completed 2026-06-24.
- Slice 2.13: Deterministic Linter and Validator Orchestrator. Completed 2026-06-24.
- Slice 2.13.1: Attribution Validator Calibration. Completed 2026-06-24.
- Slice 2.13.2: JSON Step Retry Discipline. Completed 2026-06-25.
- Slice 2.13.3: LLM-Assisted Validator Reports. Completed 2026-06-25.
- Slice 2.13.3.1: LLM Validation Report Normalization and Evidence Trace Repair. Completed 2026-06-25.
- Slice 2.14: Pairwise Ranking and Directed Revision. Completed 2026-06-25.
- Slice 2.14.1: DraftRun Long-Running Step Progress Budget. Completed 2026-06-25.
- Slice 2.15: Iterative Revision Loop and Improvement Gate. Completed 2026-06-25.
- Slice 2.15.1: Multi-Model Drafting Roles. Completed 2026-06-26.
- Slice 2.15.2: Article Dossier and Context Packs. Completed 2026-06-26.
- Slice 2.15.3: Evidence Interpretation, Not Citation Injection. Completed 2026-06-26.
- Slice 2.15.4: Prosecutor / Editor Critic Loop. Completed 2026-06-26.
- Slice 2.15.5: Alternative Angle Tournament. Completed 2026-06-27.
- Slice 2.15.6: Deep Revision Loop v2. Completed 2026-06-27.
- Slice 2.15.6.1: Revision Operation Timeout and Validation Progress Commit Repair. Completed 2026-06-27.
- Slice 2.15.6.2: Research Depth Profiles and DraftRun Budget Modes. Completed 2026-06-27.
- Slice 2.15.6.3: Model Stabilization and Universal JSON Retry Repair. Completed 2026-06-27.
- Slice 2.15.6.3.1: Writer Model Strength, Backup Separation, and Generation Params. Completed 2026-06-28.
- Slice 2.15.6.4: Final Draft Quality Gate and Public Prose Repair. Completed 2026-06-28.
- Slice 2.15.6.4.1: Final Quality Contract and Independent Gate Review. Completed 2026-06-28.
- Slice 2.15.6.4.2: Final Gate Attribution Handoff Repair. Completed 2026-06-28.
- Slice 2.16: Versioned Human Revision Loop and Editor Decision Snapshot. Completed 2026-06-28.
- Slice 2.16.0.1: HITL Revision Quality Check and Comment Compliance Trace. Completed 2026-06-29.
- Slice 2.16.1: Editorial Learning Notes in Author Memory. Completed 2026-06-29.
- Slice 2.16.1.1: Seeded HITL Learning Demo Scenarios. Completed 2026-06-29.
- Slice 2.17.0: SaaS Blog Portfolio Architecture. Completed 2026-06-29.
- Slice 2.17.1: Local Multi-Account and Blog Project Switcher. Completed 2026-06-29.
- Slice 2.17.1.1: Sidebar Portfolio Switcher Placement Repair. Completed 2026-06-30.
- Slice 2.17.2: Three-Blog Benchmark Demo Portfolio. Completed 2026-06-30.
- Slice 2.17.3: Backend Auth and Project Persistence Boundary. Completed 2026-06-30.
- Slice 2.17.3.1: Project Dashboard and Project Lifecycle UX. Completed 2026-06-30.
- Slice 2.17.3.2: Project Dashboard Layout Polish. Completed 2026-06-30.
- Slice 2.17.3.3: Project Dashboard App Shell Alignment. Completed 2026-07-01.
- Slice 2.17.3.4: Roadmap Tracker Source of Truth. Completed 2026-07-01.
- Slice 2.17.4: Publication Channels and Platform Profiles. Completed 2026-07-01.
- Slice 2.17.4.1: AI Design Patterns Project Rework. Completed 2026-07-02.
- Slice 2.17.4.1.1: Цех прикладной магии Project Rework. Completed 2026-07-02.
- Slice 2.17.4.2: Северная стена Project Rework. Completed 2026-07-02.
- Slice 2.17.4.2.1: Северная стена Editorial Contract Calibration. Completed 2026-07-02.
- Slice 2.17.4.2.2: Publication Channel Audience and Editorial Contract Boundary Repair. Completed 2026-07-02.
- Slice 2.17.4.2.2.1: Project Blueprint Creation Skill. Completed 2026-07-02.
- Slice 2.17.4.2.3: Северная стена Topic/Fabula Matrix Calibration. Completed 2026-07-02.
- Slice 2.17.4.3: Блог Главреда Project Rework. Completed 2026-07-03.
- Slice 2.17.4.4: Upstream Search and Signal Architecture. Completed 2026-07-03.
- Slice 2.17.4.5: Source Registry and Radar Run Contract. Completed 2026-07-03.
- Slice 2.17.4.5.1: Radar Settings and Run Trace Tabs. Completed 2026-07-03.
- Slice 2.17.4.6: External Search Radar Runner v1. Completed 2026-07-03.
- Slice 2.17.4.6.0: Backend Architecture Recovery Charter and Package Contract. Completed 2026-07-03.
- Slice 2.17.4.6.0.1: Drafting Backend Package Skeleton and Compatibility Shims. Completed 2026-07-03.
- Slice 2.17.4.6.0.2: Unified DraftStep and JsonOperation Contracts. Completed 2026-07-03.
- Slice 2.17.4.6.0.3: DraftRun Workflow Orchestrator Refactor. Completed 2026-07-03.
- Slice 2.17.4.6.0.3.1: Таймаут и сокращение payload для RulePack Evidence Interpretation. Completed 2026-07-04.


## Blocked Items

- None.


## Open Questions

- Which author memory event types beyond raw thoughts, link reactions, and corrections
  should be first-class?
- Should platform weights remain advisory, or become hard validation constraints after
  topic/fabula validator coverage exists?
- How much of the context chat should ship before real AI provider calls?
- How should import candidates, reviewed source signals, and post candidates share
  provenance without becoming the same entity?
- What is the minimum useful archive import for uniqueness, source signals, and
  author-position evidence?
- Which hosted deployment target should be used after local-first development?
- Should the first production auth implementation use a built-in dev/password mode,
  a managed provider, or a staged adapter boundary with local SaaS shell first?
- When should `Опытный цех «Сборочная»` add LinkedIn/site variants after the Russian
  Telegram-first industrial AI baseline is stable?
- For `Блог Главреда`, should Telegram + Dzen be the first multi-platform benchmark,
  or should LinkedIn be added earlier for B2B/product-market reach?

## Next Recommended Task

Implement `Slice 2.17.4.6.0.3.2: Universal LLM Operation Envelope, Payload Budgets, and Incident Taxonomy`.
