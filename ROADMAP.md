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

### Slice 2.12.5: SourceLedger External Evidence Merge

- Status: Done (2026-06-24)
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

### Slice 2.12.5.1: MaterialPlan Evidence Accountability and Retry

- Status: Done (2026-06-24)
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

### Slice 2.15.5: Alternative Angle Tournament

- Status: Ready
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

### Slice 2.15.6: Deep Revision Loop v2

- Status: Backlog
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

### Slice 2.16: Regression Report and Editor Decision Learning

- Status: Backlog
- Goal: Capture the human editor's final decision after the machine revision loop is
  complete.
- Scope:
  - Store `RegressionReport` after the bounded revision loop.
  - Show compact editor-facing report: why selected, used claims, unresolved risks,
    resolved repair goals, and validation status.
  - Save human edits, overrides, rejected machine moves, and rule-improvement signals
    for future learning.
- Dependency:
  - Requires the 2.15.x deep drafting intelligence slices so editor learning observes a
    meaningful editorial-lab process, not only a formally bounded revision loop.

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
- Slice 1.0.2: Author Memory File Attachments. Completed 2026-06-10.
- Slice 1.0.3: GitHub Wiki Screenshot Documentation Baseline. Completed 2026-06-11.
- Slice 1.0.4: Author Memory External Sources and Import Design. Completed 2026-06-11.
- Slice 1.0.5: External Sources Local UI Shell. Completed 2026-06-11.
- Slice 1.0.5.1: External Sources UX Fixes. Completed 2026-06-11.
- Slice 1.1: Topics and Fabulas as Editorial Entities. Completed 2026-06-11.
- Slice 1.1.1: Editorial Model UX Repair and Frontend UX ADRs. Completed 2026-06-11.
- Slice 1.1.2: Editorial Model Layout and Manual Validation UX Fixes. Completed
  2026-06-11.
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
- Slice 1.5.4: Design-System Guardrails and Signals UI Alignment. Completed
  2026-06-14.
- Slice 1.5.5: Frontend Design-System Consolidation. Completed 2026-06-14.
- Slice 1.5.6: Layout Stability and Form Rhythm Guardrails. Completed 2026-06-14.
- Slice 1.5.7: Inline Radar Editing and Multiline Rule Sources. Completed
  2026-06-14.
- Slice 1.5.8: Radar Editorial Filters and Source Discovery Mode. Completed
  2026-06-14.
- Slice 1.5.9: React Architecture Baseline and App.tsx Growth Guardrails. Completed
  2026-06-15.
- Slice 1.5.10: Extract App Shell and Workspace Controller. Completed 2026-06-15.
- Slice 1.5.11: Extract Signals Feature. Completed 2026-06-15.
- Slice 1.5.12: Extract Editorial Model Feature. Completed 2026-06-15.
- Slice 1.5.13: Extract Author Memory Feature. Completed 2026-06-15.
- Slice 1.5.14: Extract Production Flow Features. Completed 2026-06-15.
- Slice 1.5.15: Codebase Size Audit and Modularization Guardrails. Completed
  2026-06-15.
- Slice 1.5.16: Split Domain Workspace Types by Bounded Context. Completed
  2026-06-15.
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
- Slice 1.5.29: Architecture Drift Guardrails and Agent Workflow Rules. Completed
  2026-06-16.
- Slice 1.6: First Real Post Candidate Assemblies. Completed 2026-06-16.
- Slice 1.7: Candidate List UX Parity and Review Actions. Completed 2026-06-16.
- Slice 1.7.1: Candidate Format Cleanup and Edit Context. Completed 2026-06-16.
- Slice 1.8: Broadcast Grid Settings. Completed 2026-06-17.
- Slice 1.8.1: Broadcast Grid UX Parity, Filters, and Calendar Settings. Completed
  2026-06-17.
- Slice 1.8.2: Broadcast Grid Candidate Calendar View. Completed 2026-06-17.
- Slice 1.9: Editorial Work Queue Foundation. Completed 2026-06-17.
- Slice 1.10: Редактура как очередь постов и рабочий стол. Completed 2026-06-17.
- Slice 1.10.1: Editorial Workspace UX Guardrail Repair. Completed 2026-06-17.
- Slice 1.10.2: Automatic Draft After Fabula Approval. Completed 2026-06-17.
- Slice 1.10.3: Editorial Workbench Selection and Picker Repair. Completed
  2026-06-17.
- Slice 1.10.4: Editable Fabula Brief With Candidate Context. Completed 2026-06-17.
- Slice 1.10.5: Draft Approval Without Final Tab. Completed 2026-06-18.
- Slice 1.10.6: Visual Stage Foundation. Completed 2026-06-18.
- Slice 1.10.6.1: Visual Variants Review Flow. Completed 2026-06-18.
- Slice 1.10.6.2: Two-Step Meme Remix Visual Flow. Completed 2026-06-18.
- Slice 1.10.6.3: App Flow Test Ownership Guardrails. Completed 2026-06-18.
- Slice 2.0: Backend AI Execution Architecture Baseline. Completed 2026-06-18.
- Slice 2.1: Backend Foundation and OpenRouter Environment. Completed 2026-06-18.
- Slice 2.2: AI Run Contract and Audit Trail. Completed 2026-06-18.
- Slice 2.3: First OpenRouter Draft Run. Completed 2026-06-18.
- Slice 2.3.1: Dockerized Local Full-Stack Runner. Completed 2026-06-18.
- Slice 2.3.2: AI Run Observability and Draft Generation Status. Completed
  2026-06-18.
- Slice 2.3.3: AI Run Trace Debug Page. Completed 2026-06-18.
- Slice 2.3.4: Agentic Draft Runner Architecture Plan. Completed 2026-06-19.
- Slice 2.4: Draft Run Contract and Queue Foundation. Completed 2026-06-19.
- Slice 2.5: Draft Run Context Builder. Completed 2026-06-19.
- Slice 2.6: Draft Rule Pack Compiler. Completed 2026-06-19.
- Slice 2.7: Material Plan and Draft Strategy Steps. Completed 2026-06-19.
- Slice 2.8: Agentic Multi-Candidate Draft Generation. Completed 2026-06-19.
- Slice 2.8.1: AI Run Trace Workbench. Completed 2026-06-19.
- Slice 2.8.1.1: Draft Run Trace Timeline and Trace UI Repair. Completed
  2026-06-19.
- Slice 2.9: Source Ledger Foundation. Completed 2026-06-20.
- Slice 2.10: Feasibility Gate and Post Contract. Completed 2026-06-20.
- Slice 2.10.1: DraftRun Candidate Link Recovery and Feasibility Calibration.
  Completed 2026-06-22.
- Slice 2.11: Rule Registry v2 and Validator Bindings. Completed 2026-06-22.
- Slice 2.11.1: Publication Size Contract Foundation. Completed 2026-06-23.
- Slice 2.12: Contract-Based Rhetorical Plans. Completed 2026-06-23.
- Slice 2.12.1: DraftRun Stale Runner Recovery and Fallback Discipline. Completed
  2026-06-23.
- Slice 2.12.2: Draft Candidate Scoring and Selection Trace. Completed 2026-06-23.
- Slice 2.12.2.1: Draft Candidate Scorecard Trace UI. Completed 2026-06-23.
- Slice 2.12.3: Source Intent and Research Plan. Completed 2026-06-23.
- Slice 2.12.3.1: Fabula Research Strategy Defaults. Completed 2026-06-23.
- Slice 2.12.4: Public Evidence Retrieval Foundation. Completed 2026-06-24.
- Slice 2.12.4.1: OpenRouter Web Search Adapter. Completed 2026-06-24.
- Slice 2.12.4.2: Public Evidence Query and Relevance Repair. Completed 2026-06-24.
- Slice 2.12.5: SourceLedger External Evidence Merge. Completed 2026-06-24.
- Slice 2.12.5.1: MaterialPlan Evidence Accountability and Retry. Completed
  2026-06-24.
- Slice 2.13: Deterministic Linter and Validator Orchestrator. Completed
  2026-06-24.
- Slice 2.13.1: Attribution Validator Calibration. Completed 2026-06-24.
- Slice 2.13.2: JSON Step Retry Discipline. Completed 2026-06-25.
- Slice 2.13.3: LLM-Assisted Validator Reports. Completed 2026-06-25.
- Slice 2.13.3.1: LLM Validation Report Normalization and Evidence Trace Repair.
  Completed 2026-06-25.
- Slice 2.14: Pairwise Ranking and Directed Revision. Completed 2026-06-25.
- Slice 2.14.1: DraftRun Long-Running Step Progress Budget. Completed 2026-06-25.
- Slice 2.15: Iterative Revision Loop and Improvement Gate. Completed 2026-06-25.

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

## Next Recommended Task

Continue the backend track with `Slice 2.15.5: Alternative Angle Tournament`.
