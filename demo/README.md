# Demo

## Current Demo

The current demo is the local Vite app:

```bash
npm install
npm run dev
```

It shows the first working Glavred editorial cabinet:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

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

## External Sources Scenario

The import layer is implemented as a local-first UI shell around the same AI Product
Manager demo. It uses mock candidates and source cards only; no real API, backend,
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
8. Open `Источники`, inspect demo source cards, then open `Очередь разбора`.
9. Filter candidates, use `Выбрать все по фильтру`, confirm `Добавить все`, inspect
   `Архив`, and try `Отменить последнее групповое действие`.
10. Accept one candidate through `В память` to see it become an active memory note.
11. Open `Радар`.
12. Review or edit the source signal.
13. Click `Собрать инсайт`.
14. Click `В план`.
15. Approve the plan item.
16. Click `Подготовить фабулу`.
17. Edit the post brief if needed.
18. Click `Утвердить фабулу`.
19. Open `Редактура`.
20. Click `Написать драфт`.
21. Review checks and editor notes.
22. Edit the draft text.
23. Click `Утвердить текст`.
24. Open `Выпуск`.
25. Click `Подготовить выпуск`.
26. Review target, checklist, final text, and Markdown preview.
27. Complete the checklist and click `Готово к выпуску`.
28. Click `Скопировать текст` or `Скачать Markdown`.
29. Open `Аналитика`.
30. Click `Подготовить аналитику`.
31. Enter manual metrics and editorial conclusions.
32. Click `Зафиксировать выводы`.
33. Reload the page to confirm state persists.
34. Use `Сбросить демо` to restore the seeded AI Product Manager scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

Topics and fabulas as structured editorial entities are the next product layer after
the local import shell.

Real provider calls, API keys, platform metrics, publication automation, and backend
sync remain later steps. Real attachment parsing and AI analysis are also deferred.
