# Contributing

## Development Model

Work is organized by iterations and slices. Each slice should keep the product runnable,
tested, documented, and demonstrable.

Before implementation:

- Inspect `ROADMAP.md`.
- Inspect the relevant docs.
- Inspect `glavred.md` when the task depends on product requirements.
- Keep the change as the smallest useful increment.

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
