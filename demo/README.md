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

## Main User Flow

1. Open `Память автора`.
2. Review seeded notes and `Как система поняла автора`.
3. Add a new thought, link reaction, or manual correction.
4. Open `Радар`.
5. Review or edit the source signal.
6. Click `Собрать инсайт`.
7. Click `В план`.
8. Approve the plan item.
9. Click `Подготовить фабулу`.
10. Edit the post brief if needed.
11. Click `Утвердить фабулу`.
12. Open `Редактура`.
13. Click `Написать драфт`.
14. Review checks and editor notes.
15. Edit the draft text.
16. Click `Утвердить текст`.
17. Open `Выпуск`.
18. Click `Подготовить выпуск`.
19. Review target, checklist, final text, and Markdown preview.
20. Complete the checklist and click `Готово к выпуску`.
21. Click `Скопировать текст` or `Скачать Markdown`.
22. Open `Аналитика`.
23. Click `Подготовить аналитику`.
24. Enter manual metrics and editorial conclusions.
25. Click `Зафиксировать выводы`.
26. Reload the page to confirm state persists.
27. Use `Сбросить демо` to restore the seeded AI Product Manager scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

The next demo extension is topics and fabulas as structured editorial entities:

- topic cards with purpose, audience value, rules, and weight ranges;
- fabula cards with dramaturgy, proof requirements, and weight ranges;
- a default all-enabled topic/fabula compatibility matrix;
- routing the current production flow through those entities.

Real provider calls, API keys, platform metrics, publication automation, and backend
sync remain later steps.
