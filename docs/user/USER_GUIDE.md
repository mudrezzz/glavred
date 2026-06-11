# User Guide

Glavred currently provides a local-first editorial cabinet with author memory and a
working production flow.

The app starts with `Память автора`: loose thoughts, link reactions, and manual
corrections that become evidence-backed assertions about the author's position. From
there, the user can still move through the production flow from source signal to
insight card, content plan item, approved post brief, deterministic draft, editorial
checks, approved final text, manual release package, and captured editorial learning
notes.

Work is saved in browser local storage.

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
- Production flow: `Радар -> План -> Фабулы`.
- Release and analytics: final text, manual export, and captured learning note.
- Local-first demo: reset, persistence, and screenshot refresh commands.

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

## Topics And Fabulas

`Редакционная модель` now has four internal tabs:

- `Обзор`: the existing author, audience, positioning, style, boundaries, and goals.
- `Темы`: editable topic cards with purpose, audience value, author stance, rules,
  forbidden angles, and advisory weight range.
- `Фабулы`: editable dramaturgy cards with structure, proof requirements, rules, and
  advisory weight range.
- `Матрица`: topic-fabula compatibility checkboxes.

The matrix starts with every topic/fabula pair enabled. Turning off a pair removes that
combination from deterministic planning. If a topic or fabula has no active compatible
pair, the screen shows a warning before it silently disappears from future plans.

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
- Open the internal `Источники` tab to inspect demo source cards for the AI Product
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
- Open `Редакционная модель`, review `Обзор`, edit topic cards, edit fabula cards, and
  adjust the `Матрица` when a fabula should not be used for a topic.
- Review or edit the demo source signal in `Радар`.
- Generate an insight card.
- Add the insight to `План`.
- Approve the plan item through the first HITL gate.
- Generate and edit a post brief in `Фабулы`.
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
- Context chat.
- Real archive ingestion and uniqueness checks.
- Real external source ingestion, OAuth, crawlers, scheduled imports, and API-backed
  archive parsing.
- Real AI-generated insights, briefs, or drafts.
- Autoposting and real platform publishing integrations.
- Real metrics ingestion or AI analytics.
