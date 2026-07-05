# Backend Architecture AS IS

Current as of Slice 2.17.4.6.0.6.

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
- 13 flat `backend/app/application/deterministic_*.py` modules.
- 26 flat `backend/app/domain/draft_*.py` modules.
- DraftRun orchestration still enters through `backend/app/application/draft_run_pipeline.py`.
- Worker/runtime wiring lives in `backend/app/infrastructure/draft_run_*` modules.
- Tests are numerous and useful, but mirror the flat module names rather than a bounded context.

Slice 2.17.4.6.0.4 migrates 68 early DraftRun application modules into
`backend/app/drafting/application/artifacts`,
`backend/app/drafting/application/evidence`,
`backend/app/drafting/application/planning`, and
`backend/app/drafting/application/operations`. Their old `backend/app/application/*`
paths remain compatibility shims only: import/re-export, no local `def`, no `class`,
no provider calls, and no fallback logic. The flat counts above still include those
shims because the compatibility files remain on disk until downstream call sites and
external imports no longer need them.

Slice 2.17.4.6.0.5 migrates the late DraftRun application modules into
`backend/app/drafting/application/generation`,
`backend/app/drafting/application/validation`,
`backend/app/drafting/application/revision`,
`backend/app/drafting/application/final_quality`, and
`backend/app/drafting/application/hitl`. Their old flat paths are also
compatibility shims only. Candidate generation, LLM validation, editorial critique,
alternative-angle routing/tournament, pairwise ranking, directed revision,
revision-loop policy, final quality gate/review/repair, and human-comment revision
behavior are no longer active behavior in the flat application namespace.

This is not acceptable as target architecture. The flat files are temporarily
allowlisted as legacy debt so behavior can remain stable while the package migration
is done slice by slice.

## Legacy DraftRun Surface

Slice 2.17.4.6.0.4.0 adds a decision-complete migration inventory at
`backend/app/drafting/application/migration/legacy_surface_inventory.py`. The
inventory is the source of truth for the flat DraftRun application surface before
runtime module moves begin.

Each current `draft_*` and `deterministic_*` module is classified by closed
`cluster`, target package, `moduleDisposition`, target owner, migration slice,
compatibility strategy, and notes. Each public top-level helper is listed with
`publicHelperDisposition`, target visibility, target owner, and rationale.

The factual AS IS rule is: legacy public functions are not accepted as anonymous
package API. They are migration debt that must become private helpers, methods on
service/policy/component owners, provider-free DTO/factory helpers, thin
compatibility shims, or delete-after-migration leftovers. `deterministic_*` modules
must target named fallback policy/service owners under `backend/app/drafting`; they
must not become a parallel flat package. Future package moves follow the explicit
`no cosmetic package moves` rule.

Slice 2.17.4.6.0.4 applies that rule to the first runtime batch. Artifact/context,
source/evidence acquisition, evidence contract, and planning modules now have
owner-owned modules under `backend.app.drafting.application`. Architecture smoke
enforces both sides: migrated legacy files must stay thin shims, while not-yet-moved
legacy files must stay covered by the inventory.

Slice 2.17.4.6.0.5 applies the same rule to candidate, validation,
ranking/revision, final quality, and HITL modules. Architecture smoke now also
requires the new late-stage packages, rejects behavior reintroduced into migrated
legacy shims, rejects raw provider `.complete_json(...)` in migrated bounded
services, and fails bounded modules that expose large public-helper surfaces without
a named service/policy/component/DTO owner.

Slice 2.17.4.6.0.6 hardens the process surface around this migration. Backend docs,
`AGENTS.md`, and repo-local skills now point to canonical package owners after the
`0.4`/`0.5` migrations and to `docs/developer/BACKEND_MODULE_TEMPLATE.md`. Legacy
files now have three explicit statuses: active compatibility facade, migrated thin
shim, or remaining explicit debt. Architecture smoke verifies that the docs and
skills keep this wording, so new contributor/agent workstreams cannot silently treat
flat legacy paths as normal behavior owners.

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
| 325 | `backend/app/drafting/application/planning/material_plan_retry_orchestrator.py` | Complex retry/orchestration logic outside a drafting package. |
| 291 | `backend/app/infrastructure/sqlite_portfolio_repository.py` | Persistence adapter may need split by table/use-case if it grows further. |
| 235 | `backend/app/application/upstream_radar_external_run_service.py` | First upstream runner already large enough to justify a package boundary. |
| 220+ | `backend/app/drafting/application/*` migrated DraftRun modules | Some owner modules remain intentionally large after behavior-preserving migration; follow-up refactors should split by service/policy/component role, not move behavior back to flat legacy paths. |

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

## DraftRun Provider-Input Payload Budgets

Slice 2.17.4.6.0.3.3 adds the DraftRun-specific provider-input boundary under
`backend/app/drafting/application/operations/`. Slice 2.17.4.6.0.3.3.1 splits the
initial `payload_budget.py` surface into role-owned modules:
`payload_budget_contracts.py`, `payload_budget_profiles.py`,
`payload_semantic_contracts.py`, `payload_compactors.py`,
`payload_budget_policy.py`, and `payload_budget_runtime.py`. The original
`payload_budget.py` path is now a thin compatibility facade only. Rich parent
DraftRun artifacts still remain available for storage and diagnostics, but enforced
provider-heavy operations now pass compacted input into prompt builders and attach
`payloadBudget` metadata to child `AiRun.requestPayload`, attempts, and
`operationEnvelope.payloadStats`.

The enforced representative operations are:

- `evidenceInterpretation`;
- `editorialCritique`;
- `directedRevision`;
- `humanCommentRevision`;
- `humanCommentRevisionQualityCheck`.

`CURRENT_LLM_OPERATION_INVENTORY` now also records `payloadBudgetStatus`,
`budgetPolicyId`, `reasonNotBudgeted`, and `payloadBudgetRemovalSlice`. Operations
not yet wired at runtime remain debt-allowlisted rather than silently sending full
artifacts.

## Current Guardrails

Already enforced:

- Frontend file-size and feature-boundary limits.
- Backend line limits for selected known files.
- Domain/API forbidden imports for provider, database, queue, and HTTP libraries.
- SAO required-fragment checks.
- Exact allowlists for existing flat DraftRun/Radar modules.
- Required backend module ownership header for new bounded-context modules.
- Shared LLM operation envelope, incident taxonomy, and operation inventory checks.
- DraftRun payload budget policy checks and representative runtime wiring checks.
- DraftRun payload budget architecture checks that keep `payload_budget.py` thin
  and require role-owned contract, profile, semantic contract, compactor, and policy
  modules.
- DraftRun validation runtime budget checks requiring `ValidationRuntimeGuard`,
  `ValidationRuntimeBudgetProfile`, `runtimeBudget`, and canonical stop reasons:
  `acceptedQuality`, `humanReviewRequired`, `budgetExhausted`, `maxIterations`,
  `noImprovement`, and `providerIncident`.
- Legacy DraftRun Surface inventory checks requiring every current
  `backend/app/application/draft_*.py` and `deterministic_*.py` module, and every
  public top-level helper in those modules, to be classified by owner and migration
  disposition.
- Migrated DraftRun shim checks requiring moved `backend/app/application/*` files to
  remain bounded import/re-export compatibility surfaces with no behavior.
- Backend documentation and agent strict-mode checks requiring the canonical package
  map, backend module template, Provider-Heavy Review Checklist, migrated thin shim
  wording, active compatibility facade wording, remaining explicit debt wording, and
  `npm run test:architecture` obligations in docs, `AGENTS.md`, and relevant skills.

Still missing after this slice:

- Full migration of every provider-heavy operation behind the shared envelope.
- Runtime payload-budget wiring for the remaining legacy provider-heavy operations.
- Upstream/radar bounded package migration.
- Dedicated infrastructure watchdog for worker-level stalls outside protected
  operation envelopes and validation runtime-budget heartbeats.

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
