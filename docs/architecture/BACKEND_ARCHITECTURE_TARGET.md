# Backend Architecture Target

Current as of Slice 2.17.4.6.0.

This document is the target package contract for backend work. New backend runtime
code should follow this contract unless a roadmap slice explicitly records a
temporary exception.

## Target Package Map

```text
backend/app/
  api/
  ai_runs/
  drafting/
  upstream/
  portfolio/
  roadmap/
  shared/
  infrastructure/
  settings.py
```

The current code is not fully migrated to this shape. The recovery track moves one
bounded context at a time while preserving behavior.

## Implemented Package Boundaries

As of Slice 2.17.4.6.0.1, `backend/app/drafting` exists as the first target
bounded-context package. It contains package markers, package-local documentation,
and narrow compatibility shims only.

Implemented documentation:

- `backend/app/drafting/README.md`
- `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`

Implemented compatibility anchors:

- `backend.app.drafting.application.workflow.legacy_pipeline`
- `backend.app.drafting.domain.legacy_run`

These anchors re-export selected legacy DraftRun entrypoints without moving runtime
behavior. They must not become broad barrels for the whole legacy `draft_*`
namespace.

## Context Ownership

| Context | Owns | Does not own |
| --- | --- | --- |
| `api` | FastAPI routes, auth/session dependency use, request/response mapping. | Provider calls, prompt construction, SQLite access, Celery, workflow decisions. |
| `ai_runs` | AI audit use cases and provider-neutral run metadata. | Drafting step semantics or provider execution. |
| `drafting` | DraftRun workflow, step contracts, artifacts, JSON LLM operations, validation/ranking/revision/final gate orchestration. | Upstream discovery, portfolio persistence, raw provider adapters, route handlers. |
| `upstream` | Source registry, radar runs, search campaigns, found material, signal extraction/scoring, candidate assembly policies. | Draft text generation, publication variants, provider adapters, React read models. |
| `portfolio` | Users, projects, memberships, project lifecycle, workspace snapshot use cases. | Editorial content generation or provider search. |
| `roadmap` | Tracker CLI/domain/application/repository. | Product runtime, DraftRun, radar execution. |
| `shared` | Cross-context provider-neutral operation contracts, safe errors, retry metadata, trace helpers. | Domain-specific prompts, provider-specific adapters, one-context convenience helpers. |
| `infrastructure` | OpenRouter, SQLite repositories, Celery, URL reader, filesystem/network adapters. | Domain invariants, use-case decisions, API request parsing. |

## Dependency Direction

Allowed direction:

```text
api -> bounded-context application -> bounded-context domain
bounded-context application -> infrastructure ports/adapters
bounded-context application -> shared
infrastructure -> bounded-context ports/contracts when needed
```

Forbidden:

- Domain importing FastAPI, HTTP clients, SQLite, Celery, OpenRouter, or provider SDKs.
- API routes importing OpenRouter adapters, SQLite repositories, Celery tasks, or URL
  readers directly.
- Drafting importing upstream UI/read-model code.
- Upstream creating `SourceSignal`, `PostCandidate`, plan slots, or DraftRuns during
  raw retrieval unless the slice is explicitly about that handoff.
- Shared becoming a dumping ground for one-context helpers.

## Backend Module Header

New modules under `backend/app/drafting`, `backend/app/upstream`, or
`backend/app/shared` must start with an ownership docstring:

```python
"""Owner: drafting.application.workflow

Used by: DraftRun workflow registry.
Does not own: provider adapters, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""
```

The goal is not ceremony. The header lets a new contributor understand why the file
exists and where it fits before editing it.

## Operation Contract

Provider-heavy operations should expose a stable application-level result instead of
raw provider exceptions or ad hoc dictionaries.

Minimum contract:

- typed input DTO or explicit request object;
- typed success/failure result;
- attempt list with model/provider/attempt label/status;
- safe error message and machine-readable failure reason;
- trace payload safe for persistence;
- no secrets, headers, raw tokens, or provider-specific exceptions outside
  infrastructure.

DraftRun JSON LLM operations must keep using the universal JSON retry policy:
primary, repair, optional backup, then explicit fallback, not-run, or failed outcome.

## Migration Sequence

1. Add this contract and architecture smoke stop-line.
2. Create `backend/app/drafting` skeleton and compatibility shims.
3. Introduce shared `DraftStep` and JSON operation contracts.
4. Refactor DraftRun orchestration into a workflow registry.
5. Move context/evidence/planning clusters.
6. Move candidate/validation/revision/final quality clusters.
7. Move upstream radar/search into `backend/app/upstream` before expanding extraction
   and scoring.
8. Tighten allowlists after each cluster migration.

## Review Checklist

Before adding a backend module:

- Which bounded context owns it?
- Is it domain, application, infrastructure, API, or shared?
- Does it need a new public contract, or can it use an existing one?
- Is there an architecture doc anchor?
- Does an existing service already own this responsibility?
- Can the behavior be tested at the owning layer without crossing API/UI boundaries?
