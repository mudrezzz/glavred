# Drafting Backend Package

`backend/app/drafting` is the target bounded context for DraftRun backend code.

Current status: skeleton and compatibility shims only. Runtime behavior still lives
in the legacy flat modules under `backend/app/application/draft_*.py` and
`backend/app/domain/draft_*.py` until the migration slices move cohesive clusters.

## Ownership

The drafting context owns:

- DraftRun workflow and step registry;
- provider-neutral DraftRun step contracts;
- DraftRun artifacts and artifact mapping;
- JSON LLM operation contracts used by drafting steps;
- drafting validation, ranking, revision, final quality gate, and HITL revision
  orchestration once migrated.

The drafting context does not own:

- FastAPI route parsing or response formatting;
- SQLite repositories, Celery workers, OpenRouter adapters, or URL readers;
- upstream search/radar/source-signal discovery;
- portfolio users, projects, memberships, or workspace snapshots.

## Dependency Direction

Allowed direction:

```text
api -> drafting.application -> drafting.domain
drafting.application -> drafting.infrastructure ports/adapters
drafting.application -> backend.app.shared
backend.app.infrastructure -> drafting ports/contracts when needed
```

Forbidden:

- domain modules importing FastAPI, HTTP clients, SQLite, Celery, OpenRouter, or
  provider SDKs;
- API handlers owning provider calls, prompt construction, persistence, or workflow
  decisions;
- drafting modules creating upstream `FoundMaterial`, `SourceSignal`, plan slots, or
  publication variants.

## Module Header Rule

Every new non-`__init__.py` module under this package must start with:

```python
"""Owner: drafting.<layer>

Used by: <runtime or migration consumer>.
Does not own: <explicit non-responsibilities>.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""
```

The header is part of the architecture contract and is enforced by
`npm run test:architecture`.

## Compatibility Shims

Compatibility shims are intentionally narrow. They expose a small number of legacy
entrypoints so later slices can start importing from `backend.app.drafting` without
moving behavior and import call sites in the same diff.

Do not add broad barrels that mirror the entire legacy `draft_*` namespace.
