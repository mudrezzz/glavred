# External Source Import Concept

## Purpose

External source import is the future layer that brings the author's prior material
into `AuthorMemory` without turning the product into a blind data dump.

The key rule is:

> Imported material can be collected in bulk, but it cannot strengthen the author
> position model until the author reviews it, bulk-accepts it under an explicit policy,
> or routes it into archive-only storage.

Slice 1.0.4 is a design slice. It defines UX, contracts, safety rules, and the next
implementation step. It does not add real API integrations, crawling, OAuth, backend
jobs, or runtime TypeScript contracts.

## User Experience Model

External sources should live inside `Память автора`, because they are another way to
feed the author's memory. The future memory screen should have four work areas:

- `Лента`: current notes, links, files, corrections, and evidence-backed assertions.
- `Источники`: configured places where the author has already left thoughts.
- `Очередь разбора`: imported candidates waiting for review or bulk action.
- `Архив`: accepted historical posts and long-form materials.

This keeps day-to-day capture and historical ingestion close, but separates loose
manual notes from unreviewed imported material.

## Source Settings UX

The `Источники` tab should show source cards.

Source types:

- Telegram channel.
- Social profile.
- Blog or site.
- Document or talk file.
- Article archive.
- Manual upload.

Each source card should show:

- source type and title;
- URL or file reference;
- import mode;
- current status;
- last checked time;
- last imported time;
- candidate count;
- failed/paused reason when relevant;
- short author note about why this source matters.

Primary actions:

- `Добавить источник`;
- `Проверить вручную`;
- `Открыть очередь`;
- `Пауза`;
- `Удалить источник`.

The first implementation should be local-first and mock-backed. It can save source
settings and seeded candidates, but it must not claim that Telegram, social networks,
blogs, or files are actually connected.

## Add Source Flow

The add-source flow is a short wizard:

1. Choose source type.
2. Enter title and URL or file reference.
3. Select import mode.
4. Select default evidence policy.
5. Save source.

Import modes:

- `manualOnly`: source is documented, but no candidates are generated automatically.
- `reviewedQueue`: imported material enters `Очередь разбора`.
- `archiveOnly`: accepted items go to archive by default.
- `bulkArchive`: optimized for large archives; safe default for old posts.

Default evidence policy:

- `canSupportAssertions`: accepted material can support future author-position claims.
- `archiveOnly`: material is searchable/history material but does not strengthen
  assertions by default.
- `ignored`: material is kept for context only.

## Import Review Queue UX

The `Очередь разбора` tab should be built for both small and large imports.

Top controls:

- search;
- source filter;
- type filter;
- date range;
- status filter;
- duplicate-risk filter;
- evidence-policy filter;
- view switch: `Список`, `Группы`, `Дубликаты`, `Требуют проверки`.

Candidate card content:

- title;
- excerpt;
- original date;
- source and original URL/file reference;
- detected tags;
- suggested target: memory or archive;
- duplicate risk;
- evidence policy;
- review status;
- provenance preview.

Individual actions:

- `Принять в память`;
- `Принять в архив`;
- `Отклонить`;
- `Объединить`;
- `Не использовать как evidence`.

## Bulk Review UX

Large archives must not require the author to review every item manually.

Selection controls:

- row/card checkboxes;
- `Выбрать все на странице`;
- `Выбрать все по фильтру`;
- exclude individual candidates after selecting by filter;
- clear selection.

Bulk actions:

- `Добавить все`;
- `Принять выбранные в память`;
- `Принять выбранные в архив`;
- `Отклонить выбранные`;
- `Не использовать выбранные как evidence`.

`Добавить все` must respect the current filter. If the user filters to one source or
one month, only matching items are included.

Before any bulk action, the UI must show a confirmation summary:

- total selected candidates;
- sources included;
- date range;
- duplicate-risk count;
- low-confidence count;
- destination: memory or archive;
- evidence impact;
- whether undo is available.

For large historical archives, the default safe action is `Принять в архив`, not
`Принять в память`. This creates a searchable archive base without immediately
rewriting the live author-position model.

After a bulk action, show `Отменить последнее групповое действие` while the action is
reversible. Future backend implementations may limit undo windows, but the local-first
UI shell can support undo by keeping the previous candidate statuses in workspace
state.

## Grouping UX

The queue should support grouping so the author can review patterns instead of
individual items.

Group types:

- by source;
- by month or year;
- by detected tag or future topic;
- by duplicate cluster;
- by evidence risk;
- by import status.

Each group should show:

- group title;
- candidate count;
- representative excerpts;
- dominant tags;
- risk level;
- suggested bulk action.

Group actions:

- open group;
- accept group to archive;
- accept group to memory;
- ignore group as evidence;
- reject group.

## Evidence and Provenance Rules

Imported material must preserve provenance:

- source type;
- source title;
- original URL or file reference;
- original date if known;
- import date;
- acceptance date;
- acceptance mode: manual or bulk;
- acceptance reason when provided.

Unreviewed candidates cannot affect `AuthorPositionAssertion`.

Bulk-accepted archive items can become part of the archive, but should not
automatically strengthen author-position assertions unless their evidence policy is
explicitly changed to `canSupportAssertions` through a later evidence review.

Manually accepted memory items can become `AuthorNote` inputs for future assertion
inference.

## Conceptual Contracts

These contracts are conceptual for Slice 1.0.4 and should not be added as runtime
TypeScript yet.

- `AuthorExternalSource`: configured source.
- `ExternalSourceType`: `telegramChannel | socialProfile | blogSite | document |
  articleArchive | manualUpload`.
- `ExternalSourceStatus`: `planned | connected | needsReview | imported | paused |
  failed`.
- `ImportMode`: `manualOnly | reviewedQueue | archiveOnly | bulkArchive`.
- `ImportedMemoryCandidate`: unreviewed imported item.
- `ImportReviewStatus`: `new | acceptedToMemory | acceptedToArchive |
  bulkAcceptedToArchive | merged | rejected | ignoredForEvidence`.
- `ImportCandidateGroup`: grouped set of candidates.
- `BulkImportSelection`: selected candidates by ids or active filter.
- `BulkImportAction`: reversible action history entry.
- `ArchiveRecord`: accepted historical material.
- `Provenance`: source and acceptance metadata.
- `EvidencePolicy`: `canSupportAssertions | archiveOnly | ignored`.

## Next Implementation Slice

The next implementation slice should be `Slice 1.0.5: External Sources Local UI
Shell`.

Recommended first runtime scope:

- add a local-first `Источники` tab inside `Память автора`;
- add mock source cards for the AI Product Manager demo;
- add a mock review queue with 15-30 candidates;
- implement filters, grouping, selection, `Добавить все`, and undo locally;
- persist source settings, candidates, groups, and bulk action state in local storage;
- keep imported candidates from changing current assertions until accepted.
