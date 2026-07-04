# Backend Architecture AS IS

Current as of Slice 2.17.4.6.0.3.2.

This document records the backend state before the recovery refactor. It is factual:
it describes what exists now, including debt. The target shape is documented in
`docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`.

## Current Package Shape

The backend currently uses four broad packages:

| Package | Current role | AS IS risk |
| --- | --- | --- |
| `backend/app/api` | FastAPI routes and request mapping. | Mostly thin, but route growth can still pull in orchestration if unchecked. |
| `backend/app/domain` | Provider-free DTOs and domain entities. | Drafting domain is represented as many flat `draft_*` files. |
| `backend/app/application` | Use cases, orchestration, prompt builders, parsing, fallbacks, and many helper modules. | This is the main pressure point: DraftRun and upstream radar code are mixed in one flat namespace. |
| `backend/app/infrastructure` | SQLite repositories, OpenRouter adapters, Celery worker wiring, URL reader, and provider edges. | Some workflow wiring is still draft-specific and will need a drafting boundary. |

The roadmap tracker already has a better split:
`backend/app/domain/roadmap_tracker.py`, `backend/app/application/roadmap_tracker.py`,
and `backend/app/infrastructure/sqlite_roadmap_repository.py`. That split is the
model for future bounded contexts.

## DraftRun Debt Inventory

DraftRun is the largest backend subsystem. It is functionally mature, but its file
layout is no longer navigable.

Current inventory:

- 110 flat `backend/app/application/draft_*.py` modules.
- 26 flat `backend/app/domain/draft_*.py` modules.
- DraftRun orchestration still enters through `backend/app/application/draft_run_pipeline.py`.
- Worker/runtime wiring lives in `backend/app/infrastructure/draft_run_*` modules.
- Tests are numerous and useful, but mirror the flat module names rather than a bounded context.

This is not acceptable as target architecture. The flat files are temporarily
allowlisted as legacy debt so behavior can remain stable while the package migration
is done slice by slice.

## Upstream Radar Debt Inventory

Upstream search has started to repeat the same shape:

- 4 flat `backend/app/application/upstream_radar_*.py` modules.
- The API entrypoint is `backend/app/api/radar_runs.py`.
- Provider search uses existing OpenRouter/web-search and URL-reader infrastructure.
- The product boundary is documented in
  `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md`, but the backend
  package boundary is not yet implemented.

Radar/upstream must move into its own bounded context before more search, extraction,
scoring, benchmark, or trace runtime is added.

## High-Risk Modules

The largest backend files are a useful smell list, not an automatic failure list:

| Lines | File | Risk |
| ---: | --- | --- |
| 417 | `backend/app/application/roadmap_tracker.py` | Large but bounded to one CLI/use-case area. |
| 348 | `backend/app/application/draft_human_comment_quality_service.py` | Provider-heavy quality logic in flat DraftRun namespace. |
| 325 | `backend/app/application/material_plan_retry_orchestrator.py` | Complex retry/orchestration logic outside a drafting package. |
| 322 | `backend/app/application/draft_human_comment_revision_service.py` | Post-run writer workflow in flat DraftRun namespace. |
| 291 | `backend/app/infrastructure/sqlite_portfolio_repository.py` | Persistence adapter may need split by table/use-case if it grows further. |
| 265 | `backend/app/application/draft_editorial_critique_service.py` | Provider-heavy critique step in flat DraftRun namespace. |
| 235 | `backend/app/application/upstream_radar_external_run_service.py` | First upstream runner already large enough to justify a package boundary. |

The recovery goal is not to split every large file immediately. The goal is to stop
adding new modules in the old locations, then migrate cohesive clusters.

## Provider-Heavy Operation Inventory

Slice 2.17.4.6.0.3.2 adds `backend/app/shared/llm_operations` as a factual AS IS
contract layer while most DraftRun provider-heavy services still live in flat legacy
modules. The shared package now owns `LlmOperationEnvelope`, `JsonOperationEnvelope`,
attempt/result DTOs, incident taxonomy, input/payload stats, retry policy, timeout
profile, and `CURRENT_LLM_OPERATION_INVENTORY`.

Representative migrated operations now emit `operationEnvelope` or an equivalent
nested shared envelope payload:

- `evidenceInterpretation`;
- `editorialCritique`;
- `directedRevision`;
- `humanCommentRevision`;
- `humanCommentRevisionQualityCheck`.

Other provider-heavy operations are still legacy debt, but they are explicitly
listed in the inventory with owner, current module, operation kind, migration status,
reason not migrated, removal slice, and expected incident coverage.

## Current Guardrails

Already enforced:

- Frontend file-size and feature-boundary limits.
- Backend line limits for selected known files.
- Domain/API forbidden imports for provider, database, queue, and HTTP libraries.
- SAO required-fragment checks.
- Exact allowlists for existing flat DraftRun/Radar modules.
- Required backend module ownership header for new bounded-context modules.
- Shared LLM operation envelope, incident taxonomy, and operation inventory checks.

Still missing after this slice:

- Full migration of every provider-heavy operation behind the shared envelope.
- Upstream/radar bounded package migration.
- Dedicated infrastructure watchdog for worker-level stalls outside protected
  operation envelopes.

## Recovery Rule

Until the migration is complete:

1. Legacy flat DraftRun/Radar files may be edited when necessary.
2. New DraftRun/Radar backend modules must not be added to the flat legacy locations.
3. New backend runtime code for DraftRun belongs under `backend/app/drafting`.
4. New backend runtime code for radar/search/signal upstream belongs under
   `backend/app/upstream`.
5. New cross-cutting helper code belongs under `backend/app/shared` only when it is
   genuinely shared by more than one bounded context.
6. API routes stay thin; provider, persistence, queue, and workflow logic stay out of
   route handlers.
