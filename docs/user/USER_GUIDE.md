# User Guide

Glavred currently provides the first local-first editorial cabinet.

The current app lets you move from a source signal to an insight card, a content plan
item, and an approved post brief. Work is saved in browser local storage.

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
- Reload the page and keep the local workspace state.
- Reset the demo scenario from the topbar.

## Not Yet Supported

- Real source ingestion.
- Real AI-generated insights, briefs, or drafts.
- Draft editing and editorial checks.
- Publishing integrations.
- Analytics.
