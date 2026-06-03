# Demo

## Current Demo

The current demo is the local Vite app:

```bash
npm install
npm run dev
```

It shows the brief-backed Glavred project foundation and the modeled editorial loop:

`Editorial Radar -> Insight Cards -> Content Plan -> Post Brief -> Draft -> Editorial Checks -> Manual Export -> Learning Loop`

It also shows the first MVP perimeter:

- Editorial Model
- Sources and Insights
- Content Plan
- Post Brief
- Draft and Review

## First Realistic Demo Scenario

Use this scenario for Slice 0.4:

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

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

Implement enough of the scenario above for a user to move from a source signal to an
approved post brief. Drafting, editorial checks, publication, and analytics are later
demo extensions.
