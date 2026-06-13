# Glavred

Glavred is an AI-native editorial office for expert authors, founders, consultants,
and teams who want to run a personal media system without losing the author's own
position.

The product is not positioned as an AI copywriter. Its core job is to help the author
capture raw thoughts, reactions, corrections, and released work, turn them into a
transparent author position model, and use that model to plan, validate, draft, and
release content.

The current repository contains the first working local-first editorial cabinet. It
implements author memory, evidence-backed author-position assertions, and an editable
production flow from source signal to insight card, broadcast content grid, approved
post brief, deterministic draft, editorial checks, approved final text, manual release
package, copy/Markdown export, and captured editorial learning note.

`Память автора` is now the main entry point: titleless thought capture, optional local
file attachments, local link previews, targeted corrections, search/filtering, lazy
feed loading, long-note collapse, edit/delete actions, memory summary, and browser
voice-input fallback are available before any production workflow starts.

The same author-memory workspace now includes a local-first external-source shell:
`Лента`, `Источники`, `Очередь разбора`, and `Архив`. It uses deterministic mock
candidates for the AI Product Manager demo, supports filtering, grouping, individual
review actions, `Добавить все`, archive-safe bulk acceptance, and undo for the latest
bulk action. Unreviewed and archive-only material does not change the author-position
assertions.

`Редакционная модель` now behaves like the workspace of a virtual publishing project:
an explicit project profile, editable atomic rules for author/audience/position/style/
goals/boundaries, compact topic and fabula lists, a topic-fabula compatibility matrix,
and a deterministic validation panel on every tab. Validation is explicit: the author
clicks `Проверить`, gets a saved snapshot, and sees `Требует повторной проверки` after
committed setup changes. Topics and fabulas can be added or deleted directly from their
lists; deletion removes compatibility matrix links but does not rewrite already-created
production artifacts. Legacy rubric/fabula fields remain available only for storage and
service compatibility. Slice 1.2 replaces the earlier ad-hoc setup check with a common
validator baseline: the manual `Проверить` action now saves a `ValidatorRun`, and each
validator returns a score, red/yellow/green status, evidence, and suggested fixes.

`План` now shows a broadcast grid rather than a single content-plan card. Slots carry
date, platform, format, topic, fabula, priority, approval status, manual override state,
and advisory weight warnings. The standalone sidebar item `Фабулы` was removed:
editorial fabulas live inside `Редакционная модель`, while a concrete `Фабула поста`
remains an internal production step opened from an approved plan slot.

Attached files are stored as local demo evidence only. Real document parsing,
extraction, OCR, and AI analysis are explicitly deferred.

The current product circle re-centers the system around author memory and
validator-backed editorial entities before adding real AI provider integration.

## Source Requirements

Primary source requirements file: `glavred.md`.

Current status: `glavred.md` remains the historical product brief. The active June
2026 product revision is documented in the architecture docs and roadmap. The existing
design handoff is a secondary visual/product reference.

## Product Direction

The durable product loop is now:

`Author Memory -> Author Position Model -> Editorial System -> Content Production -> Release -> Learning`

The existing source-signal workflow remains useful, but it is a production layer, not
the product center. Source signals, radar findings, archive imports, analytics notes,
and manual corrections all become material for the author memory.

The revised core modules are:

- Author Memory: free internal feed of thoughts, links, reactions, corrections, and
  learning events.
- External Sources and Import Review: local source settings shell, review queue, bulk
  import, and archive-safe handling for large historical archives.
- Author Position Model: transparent, evidence-backed model of how the author thinks
  and writes.
- Topics and Fabulas: addable/removable editorial entities with weights,
  compatibility matrix, rules, and validators.
- Content Design Records: durable project-wide content decisions, similar to ADRs for
  software projects.
- Audience, goal, metrics, platforms, and formats: structured rules, not freeform
  text boxes.
- Validators: formal checks with score, status, evidence, and fix guidance.
- Context Chat: topbar-triggered assistant with `Чат` and `Подсказки` modes. It is
  synchronized with the selected product section, answers local deterministic questions,
  opens safe draft forms, and never calls AI providers or saves changes automatically.

Current working flow: the first implementation still reaches a captured editorial
learning note and uses local-first browser persistence before backend, real metrics
ingestion, autoposting, or AI provider integration.

Permanent demo example: a Telegram blog by an AI Product Manager who shares research
experience building AI-B2B products. The demo starts with author notes about workflow
risk, evals, trust, adoption, and confidence boundaries, then routes the same example
through the existing production flow.

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

Run browser visual smoke checks:

```bash
npm run test:visual
```

Update user wiki screenshots:

```bash
npm run docs:screenshots
```

Publish the GitHub Wiki from `docs/wiki/`:

```bash
npm run docs:wiki:publish
```

## Documentation

- [Roadmap](ROADMAP.md)
- [Author position concept](docs/architecture/AUTHOR_POSITION_CONCEPT.md)
- [External source import concept](docs/architecture/EXTERNAL_SOURCE_IMPORT_CONCEPT.md)
- [System architecture overview](docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md)
- [Architecture decision records](docs/adr/README.md)
- [Contributor guide](docs/contributor/CONTRIBUTING.md)
- [Developer guide](docs/developer/DEVELOPER_GUIDE.md)
- [User guide](docs/user/USER_GUIDE.md)
- [Demo](demo/README.md)
- [GitHub Wiki](https://github.com/mudrezzz/glavred/wiki)
- [Wiki source](docs/wiki/Home.md)

## Development Model

This project is developed iteratively through small slices. Each slice should leave the
product runnable, tested, documented, and demonstrable.

GitHub repository: `https://github.com/mudrezzz/glavred` (public).
