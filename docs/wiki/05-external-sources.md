# External sources

External source import is planned, not implemented yet. The purpose is to bring the
author's older material into `Память автора` without turning the author-position model
into an opaque automatic import.

## What sources mean

Future sources are places where the author has already left thoughts:

- Telegram channel;
- social profile;
- blog or site;
- article archive;
- document or talk file;
- manual upload.

Each source should have a card with title, type, URL or file reference, status, import
mode, last checked/imported time, candidate count, and a short author note.

## Review queue

Imported material should first appear in `Очередь разбора`. The queue shows candidates
with excerpt, source, original date, detected tags, duplicate risk, suggested target,
and evidence policy.

Individual actions:

- `Принять в память`;
- `Принять в архив`;
- `Отклонить`;
- `Объединить`;
- `Не использовать как evidence`.

Unreviewed candidates do not change `Как система поняла автора`.

## Bulk import

Large archives must support group work. If the author imports 1,000 old Telegram posts,
they should not have to review every post manually.

Planned bulk controls:

- select item;
- select page;
- select all by active filter;
- group by source, month, tag, duplicate cluster, or evidence risk;
- `Добавить все`;
- accept selected into archive;
- accept selected into memory;
- ignore selected as evidence;
- undo latest bulk action.

Before `Добавить все`, the UI should show a summary: total items, sources, date range,
duplicate-risk count, low-confidence count, destination, and evidence impact.

For large historical archives, the safe default is `Принять в архив`, not `Принять в
память`. Archive material remains useful for search, uniqueness, and future evidence
review, but it should not immediately rewrite author-position assertions.

## Demo direction

For the AI Product Manager demo, the future source set should include a Telegram
archive, customer interview notes, blog essays, talk documents, and manual research
uploads.
