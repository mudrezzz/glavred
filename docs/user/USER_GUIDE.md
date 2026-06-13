# User Guide

Glavred currently provides a local-first editorial cabinet with author memory and a
working production flow.

The app starts with `Память автора`: loose thoughts, link reactions, and manual
corrections that become evidence-backed assertions about the author's position. From
there, the user can still move through the production flow from source signal to
insight card, content plan item, approved post brief, deterministic draft, editorial
checks, approved final text, manual release package, and captured editorial learning
notes.

Work is saved in browser local storage. Save/status messages appear only after an
explicit action and disappear automatically; the app does not keep a permanent bottom
toast over the workspace.

For a visual walkthrough with real interface screenshots, use the GitHub Wiki after it
has been initialized:

- GitHub Wiki: `https://github.com/mudrezzz/glavred/wiki`
- Wiki source in this repository: `docs/wiki/Home.md`

## Run Locally

```bash
npm install
npm run dev
```

Open the local URL printed by Vite.

## Visual Wiki

The wiki explains the current product through real screenshots:

- `Память автора`: quick thoughts, links, files, targeted corrections, evidence, and
  confidence.
- Production flow: `Сигналы -> Инсайт -> План -> Фабула поста`.
- Release and analytics: final text, manual export, and captured learning note.
- Local-first demo: reset, persistence, and screenshot refresh commands.

Planning note: the current `План` screen is a local-first broadcast grid prototype.
`Сигналы` now owns radar settings and signal review. The next product slice adds
`Кандидаты постов` before the plan becomes a true calendar. Until then, the grid
demonstrates slot approval and downstream production, not the final signal-driven
planning model.

## Demo Context

The permanent demo is a Telegram blog by an AI Product Manager who shares research
experience building AI-B2B products.

The seeded notes cover:

- workflow risk instead of model choice;
- evals as a product function;
- demo magic failing after pilot;
- manual correction from support automation to GTM/adoption;
- enterprise trust through evidence and rollback;
- confidence boundaries from customer interviews.

## External Sources Local Shell

External source import is now available as a local-first UI shell inside
`Память автора`. It uses demo sources and mock candidates only. No Telegram API,
OAuth, crawler, backend, scheduled ingestion, or AI analysis is connected.

The UX keeps source review inside `Память автора` and separates it from the current
manual note feed through internal tabs:

- `Источники`: configure places where the author already leaves thoughts, such as a
  Telegram channel, social profile, blog/site, article archive, document, or manual
  upload.
- `Очередь разбора`: review imported candidates before they become memory or archive
  records.
- `Архив`: keep accepted historical posts and long-form materials with source
  provenance.

The `Источники` tab uses the same operational catalog pattern as topics and fabulas:
one source per row, key metadata visible immediately, row actions attached to the
source, and full notes/details after expanding the row.

For large archives, the planned queue supports group work:

- select one item, a page, or all items matching the active filter;
- clear the current selection from the same toolbar when the selected set is no longer
  needed;
- group by source, date, tag, duplicate cluster, or evidence risk;
- use `Добавить все` with a confirmation summary;
- accept many items into archive without reading every post;
- undo the latest bulk action when available.

Unreviewed imported material will not change `Как система поняла автора`. Bulk-added
archive material will also stay distinguishable from manually reviewed evidence.

## Editorial Model

`Редакционная модель` is the setup workspace for the virtual publishing project. It uses the same tab pattern as `Память автора` and has four internal tabs:

- `Издательство`: project profile plus structured rule blocks for author, audience, position, style, goals, and forbidden topics.
- `Темы`: compact one-row-per-topic list. Use `+ Тема` to create a draft row, then `Сохранить` to commit it. Expand a row to see details; use `Редактировать`, `Сохранить`, and `Отменить` to commit changes.
- `Фабулы`: the same compact list/detail/edit pattern for post dramaturgy entities, with `+ Фабула` for new dramaturgy patterns.
- `Матрица`: topic-fabula compatibility table. Checkbox changes stay in draft state until `Сохранить матрицу`; `Отменить` rolls the draft back.

Every tab has a right-side validation panel, but it does not validate live while you are still filling the setup. Click `Проверить` when you want a review. The panel stores the latest validation snapshot and switches to `Требует повторной проверки` after you save changed rules, topics, fabulas, project profile, or matrix links. In the current slice the check is deterministic: it reviews project profile, atomic rule coverage, style/anti-AI rules, topic/fabula compatibility, and goal readiness. Later validator slices will replace this scaffold with richer evidence and scores.

Deleting a topic or fabula removes it and all of its matrix links from the local workspace. Use `Пауза` when the entity should stay in the model but temporarily stop participating in planning. If a topic or fabula is already referenced by current production artifacts, Glavred warns before deletion; existing artifacts are not rewritten automatically in this slice.

Slice 1.2 turns the manual setup check into validator cards. The current validators
cover author-position clarity, anti-AI style coverage, audience value fit, goal
consistency, and topic/fabula coverage. Each card shows score, red/yellow/green
status, evidence, and suggested fixes.

## Signals

`Сигналы` replaces the old single `Радар` screen. It is the first review layer between
raw material and production.

The section has three internal tabs:

- `Радары`: demo radar definitions for author memory, archive, external sources, and
  manual research. Each row shows source type, acceptance policy, trigger mode, status,
  last run, and notes.
- `Найденные сигналы`: reviewable raw signals with filters by radar, status, search
  text, and duplicate risk. Expand a signal to see radar provenance, date, finding,
  evidence, duplicate search note, author correction, and actions.
- `Кандидаты постов`: read-only preview for Slice 1.6. Full candidate assemblies are
  not implemented yet.

Available signal actions:

- `Утвердить сигнал`: marks the signal approved and makes it the current source signal
  for `Собрать инсайт`.
- `Редактировать`: lets you correct title, topic, fabula, value, and author
  correction through save/cancel UX.
- `В архив`: keeps the signal as non-active material.
- `Отклонить`: marks the signal rejected.

Manual corrections create author-memory input, so signal review also teaches the system
about the author's choices. Unapproved signals do not create post concepts.

### Signals correction after Slice 1.5.1

`Радары` are now editable search procedures.

Use this tab to:

- add a radar with `+ Радар`;
- edit its title, acceptance policy, trigger mode, rules, and sources;
- add one rule per search instruction;
- use `NOT` when a condition should exclude material;
- add several sources, or leave sources empty if the rules are enough for a future AI
  search layer;
- start, pause, or delete a radar.

`Найденные сигналы` now shows raw material only. A signal is not a post candidate yet.
It does not ask you to choose a topic or fabula. Review the radar, date, finding,
evidence, duplicate risk, and search note, then approve, archive, reject, or correct
the signal.

Approved signals become available for future `Кандидаты постов`. Slice 1.6 will add
the matching layer: signal + topic + fabula + audience + value.

### Signals UI after Slice 1.5.2

`Радары` and `Найденные сигналы` use framed rows. The row border shows which metadata,
details, evidence, and actions belong to the same entity. Expand one row at a time to
inspect details without losing the surrounding list context.

Status and duplicate-risk chips stay compact; if a row looks visually broken, treat it
as a UI regression rather than expected behavior.

Slice 1.5.3 adds the explicit `Сигналы` section header above the tabs and tightens the
layout: radar rows show source, title, status, signal count, and last run as one entity;
found-signal rows keep radar, title, date, duplicate risk, and review status readable.
Expanded details and edit forms stay inside the same card, and actions sit in a
separated footer.

## Context Chat

Use the `Помощник` button in the topbar to open the context chat. It is closed by
default and has no floating page button, so it does not cover working forms or lists.
When expanded, it opens as an overlay drawer from the right edge of the app; on narrow
screens it behaves like a bottom sheet. Use the `x` button to close it.

The assistant is synchronized with the current sidebar section and with internal tabs in
`Память автора` and `Редакционная модель`. It has two modes:

- `Чат`: ask a question about the current section or request a safe draft, for example
  “сгенерируй темы согласно настройкам издательства”.
- `Подсказки`: review deterministic recommendations for the current section. The tab
  shows a count, suggestions scroll inside the assistant, and read-only suggestions can
  be dismissed with `x`.

In this slice the assistant is deterministic: it reads the current workspace and latest
validator run, then suggests safe next steps. It does not call an AI provider.

Accepted suggestions do not save changes automatically. For example, `Создать черновик
темы`, `Создать черновик фабулы`, and `Добавить правило` only open the existing draft
form with prefilled fields. The author still reviews, edits, and clicks `Сохранить`.

## Current Supported Flow

- Open `Память автора`.
- Review seeded notes and the `Как система поняла автора` panel.
- Add a thought without a title, or reveal `+ Заголовок` if a title helps.
- Add a small local file through `+ Файл` when a thought or link reaction needs
  supporting material. Files are limited to 1 MB in the local demo.
- Remove an attached file before saving, or remove/replace it while editing a note.
- Add a link reaction and check the local preview before saving.
- Use search and type filters above the feed when the memory grows.
- Expand long notes with `Показать полностью` and collapse them back with `Свернуть`.
- Edit or delete notes from the card actions; evidence-backed notes ask for
  confirmation before deletion.
- Use `Корректировать` on an inferred assertion or evidence item to create a targeted
  manual correction.
- If a correction contradicts current evidence, choose `Смержить`, `Заменить вывод`,
  or `Откатить корректировку`.
- Use `Голосом` when the browser supports speech recognition; otherwise the button
  stays disabled and the text area remains the fallback.
- Review evidence behind author-position assertions.
- Open the internal `Источники` tab to inspect the demo source list for the AI Product
  Manager scenario.
- Open `Очередь разбора`, filter candidates by source/status/evidence policy/duplicate
  risk, and switch between `Список` and `Группы`.
- Use `В память` for one reviewed candidate when it should become active author
  memory. Use `В архив`, `Отклонить`, or `Не evidence` for non-active material.
- Use `Выбрать все по фильтру` and `Добавить все` for large archive-safe batches.
  Confirm the summary before applying the bulk action.
- After a page or filter selection, use `Сбросить выделение` or the switched
  `Снять выделение...` action to clear selected candidates.
- Queue statuses `Принятые из очереди` and `Bulk archive из очереди` show candidates
  that were processed from the queue. The separate `Архив` tab also includes seeded
  historical archive records that never existed as queue candidates.
- Open `Архив` to see accepted archive records with provenance. From an archive card
  you can add a record into active memory, return it to the review queue, mark it
  `Не evidence`, open the original source, or delete it from the local archive.
- Use `Отменить последнее групповое действие` when the latest bulk decision should be
  reverted.
- Open `Редакционная модель`, review the project profile in `Издательство`, add or edit one structured rule, and check the right-side validation panel.
- Open `Темы` and `Фабулы`, expand one row, use `Редактировать`, then `Сохранить` or `Отменить`.
- Open `Матрица`, toggle one compatibility checkbox, then use `Сохранить матрицу` or `Отменить`.
- Open `Сигналы`.
- Inspect `Радары`, then open `Найденные сигналы`.
- Approve, archive, reject, or edit one signal. Approved signal becomes the current
  input for the production flow.
- Generate an insight card from the approved signal.
- Add the insight to `План`.
- Review the broadcast grid: each slot has date, platform, format, topic, fabula,
  priority, status, and advisory warnings.
- Expand a slot, edit it if needed, then use `Сохранить` or `Отменить`.
- Approve one slot through the first HITL gate.
- Generate and edit a post brief through `Подготовить фабулу поста`. This is an
  internal production step, not a separate sidebar section.
- Approve the post brief through the second HITL gate.
- Open `Редактура`.
- Click `Написать драфт`.
- Review the four checks: `Стиль`, `Анти-AI`, `Фактчек`, and `Политика`.
- Read editor notes, edit the draft manually, and approve the final text through the
  third HITL gate.
- Open `Выпуск`.
- Click `Подготовить выпуск`.
- Review Telegram target, release checklist, final text, and Markdown preview.
- Mark checklist items, click `Готово к выпуску`, then use `Скопировать текст` or
  `Скачать Markdown`.
- Open `Аналитика`.
- Click `Подготовить аналитику`.
- Enter manual metrics and editorial conclusions.
- Click `Зафиксировать выводы`.
- Reload the page and confirm local workspace state persists.
- Reset the demo scenario from the topbar.

## Not Yet Supported

- Real AI classification of author memory.
- Real analysis of attached documents, images, screenshots, PDFs, or text files.
- Real archive ingestion and uniqueness checks.
- Real external source ingestion, OAuth, crawlers, scheduled imports, and API-backed
  archive parsing.
- Real AI-generated insights, briefs, or drafts.
- Autoposting and real platform publishing integrations.
- Real metrics ingestion or AI analytics.
