# Contributing

## Development Model

Work is organized by iterations and slices. Each slice should keep the product runnable,
tested, documented, and demonstrable.

Before implementation:

- Inspect the roadmap tracker with `python -m backend.app.roadmap next` and
  `python -m backend.app.roadmap show <slice-id>`.
- Use `ROADMAP.md` as the generated readable report, not as a manual edit target.
- Inspect the relevant docs.
- Inspect `glavred.md` when the task depends on product requirements.
- Keep the change as the smallest useful increment.

## Roadmap Changes

Roadmap source of truth is `docs/roadmap/slices.export.jsonl`; `ROADMAP.md` is
generated. Use:

```bash
python -m backend.app.roadmap add-slice ...
python -m backend.app.roadmap update-status <slice-id> Done
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
```

Commit the JSONL export and generated Markdown report together. Do not commit
`var/roadmap/roadmap.sqlite`.

## Local Setup

```bash
npm install
npm run dev
```

## Validation

Run targeted tests:

```bash
npm test
```

Run the build smoke test:

```bash
npm run smoke
```

## Documentation

When behavior, architecture, setup, commands, public APIs, demo behavior, or
user-facing flows change, update the relevant documentation in the same slice.

## Git

Create small commits with clear messages. Do not create or publish a GitHub repository
unless the user has explicitly confirmed it.
