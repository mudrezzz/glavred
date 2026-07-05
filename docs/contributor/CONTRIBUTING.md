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

## Backend Architecture

Backend work follows the recovery contract in:

- `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`
- `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`
- `docs/developer/BACKEND_MODULE_TEMPLATE.md`
- `docs/adr/2026-07-03-backend-bounded-contexts-and-operation-contracts.md`

Do not add new DraftRun or Radar runtime modules to the flat legacy namespaces
`backend/app/application/draft_*.py`, `backend/app/domain/draft_*.py`, or
`backend/app/application/upstream_radar_*.py`. Use `backend/app/drafting` or
`backend/app/upstream` for new work. New bounded-context modules need ownership
docstrings and must keep API, application, domain, infrastructure, and shared
responsibilities separate.

Legacy backend files have three allowed statuses:

- active compatibility facade: old entrypoint still owns compatibility wiring;
- migrated thin shim: import/re-export only, with no `def`, `class`, provider call,
  fallback logic, or trace mutation;
- remaining explicit debt: listed in the migration inventory or operation inventory
  with owner, reason, and removal slice.

Before changing provider-heavy code, use the Provider-Heavy Review Checklist in
`docs/developer/BACKEND_MODULE_TEMPLATE.md`: shared operation governance, incidents,
payload budgets, timeout/runtime budgets, safe errors, and no raw provider calls in
bounded application modules. Run `npm run test:architecture` for backend changes.

When backend package quality is under review or a change may introduce new structural
debt, run the backend architecture audit workflow in
`.agents/skills/backend-architecture-audit/SKILL.md`. The audit separates known
ledgered debt from new unclassified smells such as public helper sprawl, procedural
bounded packages, raw dict contracts, provider boundary leaks, dependency-direction
risks, and migrated-shim behavior.

## Git

Create small commits with clear messages. Do not create or publish a GitHub repository
unless the user has explicitly confirmed it.
