# Demo

## Current Demo

The current demo is the local Vite app:

```bash
npm install
npm run dev
```

It shows the first working Glavred editorial cabinet:

`Редакционная модель -> SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief`

The app uses the `ui-design-systems/ui-kit/glavred-app` reference shape: sidebar,
topbar, cards, HITL gates, plan area, brief area, and placeholders for future sections.

## Demo Scenario

- Author: founder writing about practical AI adoption for small and medium businesses.
- Audience: entrepreneurs who need operational clarity rather than tool hype.
- Signal: several market posts discuss failed AI pilots caused by process gaps.
- Editorial opportunity: turn the pattern into a post about why AI projects fail when
  teams automate chaos.
- Expected flow: create or load an editorial model, add the signal, produce an insight
  card, place it into a weekly plan, and prepare an approvable post brief.
- Expected output: an approved post brief with thesis, conflict, rubric, audience,
  evidence, risks, sources, CTA, and approval status.
- Persistence: the approved brief should survive reload through local browser storage.

## Main User Flow

1. Open `Радар`.
2. Review or edit the source signal.
3. Click `Собрать инсайт`.
4. Click `В план`.
5. Approve the plan item.
6. Click `Подготовить фабулу`.
7. Edit the post brief if needed.
8. Click `Утвердить фабулу`.
9. Reload the page to confirm state persists.
10. Use `Сбросить демо` to restore the initial scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

Drafting, editorial checks, publication, and analytics are later demo extensions.
