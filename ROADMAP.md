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

- Status: Ready
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
  - User can inspect demo radars.
  - User can review found signals.
  - User can approve, reject, archive, and correct a signal.
  - Signal corrections become visible as author-memory input or evidence.
  - Existing plan/brief/edit/release flow remains working.
- Risks:
  - The boundary between import candidates and source signals must stay clear:
    imported candidates are source material; reviewed signals are editorial triggers.

### Slice 1.6: Post Candidate Assemblies

- Status: Backlog
- Goal: Add post candidates as explicit combinations of signal, topic, fabula,
  audience, value, goal, platform, and format.
- User value: The author can compare several proposed post concepts for one future
  slot instead of approving the first generated idea.
- Scope:
  - Add `PostCandidate` contracts.
  - Generate deterministic candidates from approved signals and editorial model.
  - Respect min/max candidate count from future or temporary planning settings.
  - Show candidates in `Сигналы -> Кандидаты постов`.
  - Let the author approve one candidate, reject candidates, request more variants, or
    edit the assembly.
  - Approved candidate becomes the input for `Фабула поста`.
- Out of scope:
  - Full calendar view.
  - Real AI candidate generation.
  - Automated publishing.
- Implementation notes:
  - Candidate approval should synchronize the compatibility `contentPlanItem` only
    when a concrete plan slot is selected or created.
  - Candidate edits should be explicit save/cancel operations.
- Tests:
  - Domain tests for candidate generation and approval.
  - UI tests for comparing, approving, rejecting, and editing candidates.
  - Regression for `Фабула поста` creation from an approved candidate.
- Docs:
  - Update architecture, developer guide, user guide, demo docs, wiki, and roadmap.
- Demo impact:
  - Demo should show at least 2-3 candidate concepts for a planned AI Product Manager
    post.
- Acceptance criteria:
  - User can review multiple candidates for the same editorial need.
  - Approved candidate starts the existing post-brief flow.
  - Rejected candidates do not affect plan or production artifacts.
- Risks:
  - Candidate UX can become noisy; keep the first view compact with details on demand.

### Slice 1.7: Broadcast Grid Settings

- Status: Backlog
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
    - default platform and format until dedicated platform entities exist;
    - signal selection policy: HITL-only, automatic, or automatic with review.
  - Save settings explicitly.
  - Generate empty calendar slots for the chosen horizon.
  - Show plan deficit/proficit summary based on available approved signals and
    candidates.
- Out of scope:
  - Calendar zoom UI.
  - Real radar execution.
  - AI planning.
- Implementation notes:
  - Settings are general requirements for the grid, not detailed settings for every
    post.
  - Saved settings should mark generated slots/candidates stale when changed.
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

### Slice 1.8: Calendar View for Broadcast Plan

- Status: Backlog
- Goal: Replace the list-only plan view with a calendar that shows slot readiness and
  lets the author zoom into a day or slot.
- User value: The author can see upcoming risk, ready posts, published posts, and
  where attention is needed.
- Scope:
  - Add `План -> Календарь выпуска`.
  - Support week/month/quarter/year zoom levels.
  - Show slot statuses:
    - empty;
    - waiting for signal approval;
    - has candidates;
    - concept approved;
    - in production;
    - ready;
    - published;
    - at risk.
  - Click a day/slot to open a detail panel below the calendar.
  - Detail panel links to signals, candidates, post brief, editing, release, or
    analytics depending on status.
  - Preserve current list/grid view as a secondary operational view if useful.
- Out of scope:
  - Real platform publication links beyond manual/demo URLs.
  - External calendar integrations.
  - Real-time collaboration.
- Implementation notes:
  - Use status colors consistently and keep text labels available for accessibility.
  - Calendar should summarize counts without forcing the user to inspect every slot.
- Tests:
  - UI tests for zoom levels, status rendering, slot detail panel, and navigation.
  - Visual smoke tests for month and week layouts at desktop/laptop/mobile widths.
  - Regression for downstream production flow.
- Docs:
  - Update user guide, wiki screenshots, demo docs, and architecture overview.
- Demo impact:
  - Demo should show a near-future slot that needs signal/candidate attention and one
    approved slot ready for production.
- Acceptance criteria:
  - Calendar clearly shows what is ready and what needs intervention.
  - Clicking a slot explains the next action.
  - Existing production flow remains reachable.
- Risks:
  - Calendar UI can easily become too dense; start with compact slot badges and a
    detail panel.

### Slice 1.9: Archive and Uniqueness Baseline

- Status: Backlog
- Goal: Treat released and imported posts as author memory, signal material, and
  uniqueness context.
- Scope:
  - Add stronger archive records for released and imported posts.
  - Link archive posts to author-position evidence when explicitly accepted.
  - Let archive records become signal sources.
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

Start `Slice 1.5: Signals and Radar Workspace`.
