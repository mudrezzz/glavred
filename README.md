# Glavred

Glavred is an AI-native editorial office for expert authors, founders, consultants,
and teams who want to run a personal media system instead of producing isolated posts
by hand.

The product is not positioned as an AI copywriter. Its core job is to create editorial
discipline: source signals become insight cards, insight cards become a plan, the plan
becomes approved post briefs, briefs become drafts, drafts pass editorial checks, and
the results feed the next cycle.

The current repository is a brief-backed project foundation. It contains a minimal
React/Vite application, a small domain baseline for the editorial workflow, test
infrastructure, documentation, demo notes, and the design handoff supplied in
`ui-design-systems/`.

## Source Requirements

Primary source requirements file: `glavred.md`.

Current status: `glavred.md` is filled and is the source of truth for product
direction. The existing design handoff is a secondary visual/product reference.

## Product Direction

The source brief defines Glavred as an AI-native editorial system for a personal or
expert blog. The durable editorial loop is:

`Editorial Radar -> Insight Cards -> Content Plan -> Post Brief -> Draft -> Editorial Checks -> Manual Export -> Learning Loop`

Human approval gates are expected at content plan approval, post brief approval, and
final editorial checks.

The first MVP perimeter is:

- Editorial Bible
- Sources and Insights
- Content Plan
- Post Brief
- Draft and Review

## Quick Start

```bash
npm install
npm run dev
```

Run tests:

```bash
npm test
```

Run the smoke build:

```bash
npm run smoke
```

## Documentation

- [Roadmap](ROADMAP.md)
- [System architecture overview](docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md)
- [Architecture decision records](docs/adr/README.md)
- [Contributor guide](docs/contributor/CONTRIBUTING.md)
- [Developer guide](docs/developer/DEVELOPER_GUIDE.md)
- [User guide](docs/user/USER_GUIDE.md)
- [Demo](demo/README.md)

## Development Model

This project is developed iteratively through small slices. Each slice should leave the
product runnable, tested, documented, and demonstrable.

GitHub repository creation is intentionally deferred until the user confirms it.
