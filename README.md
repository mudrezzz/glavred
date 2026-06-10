# Glavred

Glavred is an AI-native editorial office for expert authors, founders, consultants,
and teams who want to run a personal media system without losing the author's own
position.

The product is not positioned as an AI copywriter. Its core job is to help the author
capture raw thoughts, reactions, corrections, and released work, turn them into a
transparent author position model, and use that model to plan, validate, draft, and
release content.

The current repository contains the first working local-first editorial cabinet. It
implements an editable flow from source signal to insight card, content plan item,
approved post brief, deterministic draft, editorial checks, and approved final text,
manual release package, copy/Markdown export, and captured editorial learning note,
plus tests, documentation, demo notes, and the design handoff supplied in
`ui-design-systems/`.

The next product circle re-centers the system around author memory and validator-backed
editorial entities before adding real AI provider integration.

## Source Requirements

Primary source requirements file: `glavred.md`.

Current status: `glavred.md` is filled and is the source of truth for product
direction. The existing design handoff is a secondary visual/product reference.

## Product Direction

The durable product loop is now:

`Author Memory -> Author Position Model -> Editorial System -> Content Production -> Release -> Learning`

The existing source-signal workflow remains useful, but it is a production layer, not
the product center. Source signals, radar findings, archive imports, analytics notes,
and manual corrections all become material for the author memory.

The revised core modules are:

- Author Memory: free internal feed of thoughts, links, reactions, corrections, and
  learning events.
- Author Position Model: transparent, evidence-backed model of how the author thinks
  and writes.
- Topics and Fabulas: editable editorial entities with weights, compatibility matrix,
  rules, and validators.
- Content Design Records: durable project-wide content decisions, similar to ADRs for
  software projects.
- Audience, goal, metrics, platforms, and formats: structured rules, not freeform
  text boxes.
- Validators: formal checks with score, status, evidence, and fix guidance.
- Context Chat: right-side assistant synchronized with the selected product section.

Current working flow: the first implementation still reaches a captured editorial
learning note and uses local-first browser persistence before backend, real metrics
ingestion, autoposting, or AI provider integration.

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
- [Author position concept](docs/architecture/AUTHOR_POSITION_CONCEPT.md)
- [System architecture overview](docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md)
- [Architecture decision records](docs/adr/README.md)
- [Contributor guide](docs/contributor/CONTRIBUTING.md)
- [Developer guide](docs/developer/DEVELOPER_GUIDE.md)
- [User guide](docs/user/USER_GUIDE.md)
- [Demo](demo/README.md)

## Development Model

This project is developed iteratively through small slices. Each slice should leave the
product runnable, tested, documented, and demonstrable.

GitHub repository: `https://github.com/mudrezzz/glavred` (private).
