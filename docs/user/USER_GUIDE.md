# User Guide

Glavred currently provides the first local-first editorial cabinet.

The current app lets you move from a source signal to an insight card, a content plan
item, an approved post brief, a deterministic draft, editorial checks, and an approved
final text, prepare a manual release package, and capture editorial learning notes.
Work is saved in browser local storage.

The product direction is being expanded. The next version should make the author's
own thoughts, reactions, corrections, topics, fabulas, rules, and validators the center
of the experience. The current flow remains usable, but it will become the production
layer below an author memory and author position workspace.

Planned next user-facing areas:

- an internal author memory feed for loose thoughts, links, reactions, and corrections;
- editable topic cards with rules, weight ranges, and validator indicators;
- editable fabula cards and a topic/fabula compatibility matrix;
- Content Design Records for durable content rules;
- structured audience, persona, goal, platform, and metric settings;
- right-side context chat synchronized with the selected section;
- validator indicators with evidence and suggested fixes.

## Run Locally

```bash
npm install
npm run dev
```

Open the local URL printed by Vite.

## Current Supported Flow

- Edit the `Редакционная модель`.
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
- Review Telegram/LinkedIn targets, release checklist, final text, and Markdown
  preview.
- Mark checklist items, click `Готово к выпуску`, then use `Скопировать текст` or
  `Скачать Markdown`.
- Open `Аналитика`.
- Click `Подготовить аналитику`.
- Enter manual metrics and editorial conclusions.
- Click `Зафиксировать выводы`.
- Reload the page and keep the local workspace state.
- Reset the demo scenario from the topbar.

## Not Yet Supported

- Real source ingestion.
- Real AI-generated insights, briefs, or drafts.
- Autoposting and real platform publishing integrations.
- Real metrics ingestion or AI analytics.
