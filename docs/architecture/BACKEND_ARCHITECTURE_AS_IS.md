# Backend Architecture AS IS

Current as of Slice 2.17.4.6.0.7.

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

The roadmap tracker now has a bounded split:
`backend/app/domain/roadmap_tracker.py` owns provider-free DTOs,
`backend/app/roadmap/*` owns parsing/rendering/JSONL/service behavior, and
`backend/app/infrastructure/sqlite_roadmap_repository.py` owns the local SQLite
cache adapter. The old `backend/app/application/roadmap_tracker.py` path is a
compatibility shim only.

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

The next backend recovery gap is broader than one package. Migrated bounded packages
can still contain procedural helper surfaces and repeated legacy naming patterns.
Slice 2.17.4.6.0.7 implements the Backend Architecture Audit and Debt Ledger to
classify this debt across the whole backend before product work resumes. The audit
command is `python scripts/backend-architecture-audit.py --format json --ledger
docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high`.
Its human-readable snapshot lives in
`docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md`. The first audit covers public
top-level functions, procedural bounded packages, large modules, raw
`dict[str, Any]` contracts, provider boundary leaks, dependency-direction risks,
behavior inside migrated shims, and tests that mirror legacy owners instead of
canonical owners.

## Upstream Radar Debt Inventory

Upstream search previously started to repeat the same flat shape:

- 4 legacy `backend/app/application/upstream_radar_*.py` paths remain as
  compatibility shims only.
- Active upstream radar behavior now lives under
  `backend/app/upstream/application`.
- The API entrypoint is `backend/app/api/radar_runs.py`.
- Provider search uses existing OpenRouter/web-search and URL-reader infrastructure.
- The product boundary is documented in
  `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md`, and the backend
  package boundary is implemented at the first application-service level.

Radar/upstream medium debt remains ledgered, but new search, extraction, scoring,
benchmark, or trace runtime must build on `backend/app/upstream`, not the legacy
application shims.

## High-Risk Modules

The largest backend files are a useful smell list, not an automatic failure list:

| Lines | File | Risk |
| ---: | --- | --- |
| 325 | `backend/app/drafting/application/planning/material_plan_retry_orchestrator.py` | Complex retry/orchestration logic outside a drafting package. |
| 291 | `backend/app/infrastructure/sqlite_portfolio_repository.py` | Persistence adapter may need split by table/use-case if it grows further. |
| 350+ | `backend/app/upstream/application/external_run_service.py` | First upstream runner has a package boundary; medium line-count debt is ledgered. |
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
- Backend Architecture Audit and Debt Ledger checks requiring
  `scripts/backend-architecture-audit.py`,
  `docs/architecture/backend-architecture-debt-ledger.json`,
  `docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md`, the audit ADR, and the
  `backend-architecture-audit` skill. Architecture smoke runs the audit with
  `--fail-on-unledgered high`, so new unclassified `critical` / `high` backend debt
  fails even when ordinary tests pass.
- Drafting validation package OOP cleanup from Slice 2.17.4.6.0.8:
  `backend/app/drafting/application/validation` now exposes class-owned parser,
  prompt-builder, trace-builder, failure-mapper, attribution/evidence, artifact,
  report-appender, and attempt-mapper components instead of public helper sprawl.
  The audit ledger records only medium residual line-count/package debt for this
  package; validation high findings are closed.
- Drafting revision and final-quality package OOP cleanup from Slice 2.17.4.6.0.9:
  `backend/app/drafting/application/revision` now routes pairwise payload mapping,
  ranking/revision candidate mapping, revision-loop policy, rejected-move policy,
  prompt building, acceptance, and config caps through class-owned components.
  `backend/app/drafting/application/final_quality` now routes deterministic
  assessment, attribution classification, final-gate payloads, contract building,
  review parsing, and review prompt construction through class-owned components.
  Final-quality audit findings for this package are closed; revision keeps only
  medium line-count/package debt for future service-size cleanup.
- Drafting HITL and provider operation surface cleanup from Slice 2.17.4.6.0.10:
  `backend/app/drafting/application/hitl` now keeps human-comment revision and
  quality services as orchestration owners while prompt building, version
  compaction, trace context, attempt records, provider-attempt execution, quality
  parsing, and deterministic quality overlay live in named components. Drafting
  operation helpers are split into class-owned JSON client, payload budget stats,
  profile registry, runtime progress presenter, stop-reason/incident policies,
  revision-loop payload factory, and role-owned payload compactors. Shared
  `backend/app/shared/llm_operations` is split into statuses, stats, incidents,
  attempts, result policy, result incidents, envelope factory, and inventory
  exporter modules with compatibility re-exports. The audit ledger no longer has
  stale or high `repairSlice=2.17.4.6.0.10` debt.
- Backend API/application/infrastructure surface cleanup from Slice 2.17.4.6.0.11:
  roadmap tracker behavior now lives in `backend/app/roadmap`, upstream radar
  behavior now lives in `backend/app/upstream/application`, API route/dependency
  facades are treated separately from public helper sprawl, and the audit ledger
  reports `0` high findings, `0` unledgered findings, and `0` stale keys. Remaining
  medium debt is explicit in `docs/architecture/backend-architecture-debt-ledger.json`
  and assigned to `2.17.4.6.0.12`.

Still missing after this slice:

- Full migration of every provider-heavy operation behind the shared envelope.
- Runtime payload-budget wiring for the remaining legacy provider-heavy operations.
- OOP cleanup of medium API, infrastructure, upstream, generation,
  artifacts/evidence/planning, and residual validation/revision line-count surfaces
  flagged by the audit ledger.
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
