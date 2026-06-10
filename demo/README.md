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
optional title reveal, local link preview, targeted correction from assertions and
evidence, search/filtering, lazy loading, long-note collapse, edit/delete actions,
summary counters, and a browser voice-input fallback.

## Main User Flow

1. Open `Память автора`.
2. Review seeded notes and `Как система поняла автора`.
3. Add a quick thought without a title, or reveal `+ Заголовок` when needed.
4. Switch to `Реакция на ссылку`, paste a URL, and confirm the local link preview.
5. Use `Корректировать` from an assertion or evidence item to create a targeted manual
   correction.
6. Try search, type filters, `Показать еще`, long-note expansion, edit, and delete.
7. Open `Радар`.
8. Review or edit the source signal.
9. Click `Собрать инсайт`.
10. Click `В план`.
11. Approve the plan item.
12. Click `Подготовить фабулу`.
13. Edit the post brief if needed.
14. Click `Утвердить фабулу`.
15. Open `Редактура`.
16. Click `Написать драфт`.
17. Review checks and editor notes.
18. Edit the draft text.
19. Click `Утвердить текст`.
20. Open `Выпуск`.
21. Click `Подготовить выпуск`.
22. Review target, checklist, final text, and Markdown preview.
23. Complete the checklist and click `Готово к выпуску`.
24. Click `Скопировать текст` or `Скачать Markdown`.
25. Open `Аналитика`.
26. Click `Подготовить аналитику`.
27. Enter manual metrics and editorial conclusions.
28. Click `Зафиксировать выводы`.
29. Reload the page to confirm state persists.
30. Use `Сбросить демо` to restore the seeded AI Product Manager scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

The next demo extension should first design external author-memory sources and import
review without connecting real APIs. Topics and fabulas as structured editorial
entities remain the next product layer after that planning work.

Real provider calls, API keys, platform metrics, publication automation, and backend
sync remain later steps.
