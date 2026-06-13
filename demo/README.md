# Demo

## Current Demo

The current demo is the local Vite app:

```bash
npm install
npm run dev
```

It shows the first working Glavred editorial cabinet:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> InsightCard -> BroadcastContentPlan -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

The app uses the `ui-design-systems/ui-kit/glavred-app` reference shape: sidebar,
topbar, cards, HITL gates, plan area, brief area, editorial review area, manual release
area, analytics prep area, and the new author memory workspace.

## Permanent Demo Scenario

- Format: Telegram blog.
- Author: AI Product Manager.
- Subject: research experience building AI-B2B products in the current market.
- Audience: AI PM, founders, CPO/product leaders, and B2B SaaS teams.
- Position: AI-B2B product value comes from workflow, evals, trust loop, adoption, and
  deployment economics, not from demo magic.
- Source signal: AI-B2B pilots often fail between impressive demo and regular user
  adoption.
- Expected output: an approved Telegram research note packaged for manual export and
  followed by captured editorial learning.

## Seeded Author Memory

The demo starts with six notes:

- workflow risk instead of model choice;
- evals as a product function;
- reaction to demo magic failing after pilot;
- manual correction from support automation to GTM/adoption;
- enterprise trust through evidence and rollback;
- customer interview reaction about confidence boundaries.

The app shows inferred author-position assertions with evidence links back to these
notes.

The author memory workspace also demonstrates the hardened UX: titleless capture,
optional title reveal, local file attachments, local link preview, targeted correction
from assertions and evidence, search/filtering, lazy loading, long-note collapse,
edit/delete actions, summary counters, and a browser voice-input fallback.

The demo also includes a topbar `Помощник` overlay with `Чат` and `Подсказки` modes. It
is synchronized with the current section, answers deterministic local questions,
suggests next steps for the AI Product Manager demo, and can open draft forms for
rules, topics, and fabulas. It does not call AI providers and does not save changes
without the normal `Сохранить` action.

## Structured Editorial Model

`Редакционная модель` now opens as a virtual publishing workspace for the same AI Product Manager blog. The top profile is `TG-блог AI Product Manager`, with the description `Исследовательский блог о построении AI-B2B продуктов`.

The `Издательство` tab contains atomic demo rules for author, audience, position, style, goals, and forbidden topics. The right-side validation panel starts as `Еще не проверено`; click `Проверить` to create the deterministic `ValidatorRun`. The panel then shows validator cards with score, red/yellow/green status, evidence, and suggested fixes. After saving setup changes, the panel marks that snapshot as `Требует повторной проверки` until the next manual run.

Demo topics:

- AI product discovery;
- Evals & quality loop;
- Enterprise trust & rollout;
- GTM/adoption economics;
- Workflow automation architecture.

Demo fabulas:

- Исследовательская заметка;
- Разбор мифа;
- Практический фреймворк;
- Postmortem пилота;
- Позиционный манифест.

The compatibility matrix starts with every pair enabled. The author can turn off
specific topic/fabula combinations and see warnings when a topic or fabula can no
longer participate in planning.

The demo also supports creating a custom topic or fabula from the list toolbar. New
entities stay as local drafts until `Сохранить`, then appear in the compatibility
matrix with enabled links by default. Deleting an entity removes its matrix links; use
`Пауза` instead when an entity should remain available for later.

## Broadcast Content Plan

`План` now opens as a broadcast grid for the AI Product Manager Telegram blog. The demo
seed contains two weeks of slots with dates, Telegram as the local-first platform,
formats, topics, fabulas, approval status, manual override state, and advisory
weight/matrix warnings.

This is a useful Slice 1.4 prototype, but it is not the final planning model. Slice
1.5 now adds `Сигналы`: radar settings, found signals, and explicit signal review.
The next demo evolution should add post candidate assemblies. After that, `План` can
become a real calendar with publishing tempo, period, days/times, candidate counts,
and readiness statuses.

The standalone sidebar item `Фабулы` is removed. Editorial fabulas are edited inside
`Редакционная модель -> Фабулы`. A concrete `Фабула поста` is still part of production:
approve a plan slot, click `Подготовить фабулу поста`, edit the post brief, and use
`Вернуться в план` when needed.

## External Sources Scenario

The import layer is implemented as a local-first UI shell around the same AI Product
Manager demo. It uses mock candidates and a source list only; no real API, backend,
crawler, OAuth, or AI analysis is connected.

Demo source examples:

- Telegram channel archive with about 1,000 historical posts about AI-B2B product
  work.
- Customer interview notes about pilot-to-adoption friction.
- Blog/site essays about evals, trust loops, and enterprise rollout.
- A talk document about AI product discovery and confidence boundaries.
- Manual upload of research notes and screenshots.

The UX does not require reviewing every archived Telegram post. The import queue can
filter and group candidates, then allow `Выбрать все по фильтру` and `Добавить все`.
For large archives, the safe default is accepting material into archive, not
immediately strengthening the live author-position model.

## Visual Walkthrough

The visual user walkthrough is published in the GitHub Wiki:

- `https://github.com/mudrezzz/glavred/wiki`

The source pages live in `docs/wiki/`, and screenshots are generated from the real
local app:

```bash
npm run docs:screenshots
```

The wiki covers the same AI Product Manager demo: author memory, production flow,
manual release, and analytics learning note.

If the GitHub Wiki has not been initialized yet, GitHub redirects the URL back to the
repository. Create the first temporary Wiki page in the web UI once, then run
`npm run docs:wiki:publish`.

## Main User Flow

1. Open `Память автора`.
2. Review seeded notes and `Как система поняла автора`.
3. Add a quick thought without a title, or reveal `+ Заголовок` when needed.
4. Use `+ Файл` to attach a small research note or screenshot as supporting material.
5. Switch to `Реакция на ссылку`, paste a URL, and confirm the local link preview.
6. Use `Корректировать` from an assertion or evidence item to create a targeted manual
   correction.
7. Try search, type filters, `Показать еще`, long-note expansion, edit, and delete.
8. Open `Источники`, inspect demo source rows, then open `Очередь разбора`.
9. Filter candidates, use `Выбрать все по фильтру`, confirm `Добавить все`, inspect
   `Архив`, and try `Отменить последнее групповое действие`.
10. Accept one candidate through `В память` to see it become an active memory note.
11. Open `Редакционная модель`, inspect `Издательство`, project profile, structured rules, and the right-side validation panel.
12. Open `Темы`, add a custom topic, save it, expand a row, edit or delete one entity.
13. In `Редакционная модель`, open `Фабулы`, add a custom fabula, save it, then inspect its compatible topics.
14. Open `Матрица`, toggle one compatibility pair, then use `Сохранить матрицу` or `Отменить`.
15. Open `Сигналы`.
16. Inspect `Радары`.
17. Open `Найденные сигналы`.
18. Approve, archive, reject, or edit one signal.
19. Open `Кандидаты постов` to see the Slice 1.6 preview.
20. Return to `Найденные сигналы` and click `Собрать инсайт`.
21. Click `В план`.
22. Review the broadcast grid, expand a slot, optionally edit it with `Сохранить` or
    `Отменить`, and approve one slot.
23. Click `Подготовить фабулу поста`.
24. Edit the post brief if needed.
25. Click `Утвердить фабулу`.
26. Open `Редактура`.
27. Click `Написать драфт`.
28. Review checks and editor notes.
29. Edit the draft text.
30. Click `Утвердить текст`.
31. Open `Выпуск`.
32. Click `Подготовить выпуск`.
33. Review target, checklist, final text, and Markdown preview.
31. Complete the checklist and click `Готово к выпуску`.
32. Click `Скопировать текст` or `Скачать Markdown`.
33. Open `Аналитика`.
34. Click `Подготовить аналитику`.
35. Enter manual metrics and editorial conclusions.
36. Click `Зафиксировать выводы`.
37. Reload the page to confirm state persists.
38. Use `Сбросить демо` to restore the seeded AI Product Manager scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

Validator indicators for topics, fabulas, author position, and production artifacts are
the next product layer after the structured editorial model.

Real provider calls, API keys, platform metrics, publication automation, and backend
sync remain later steps. Real attachment parsing and AI analysis are also deferred.
