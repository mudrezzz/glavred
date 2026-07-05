# Drafting Backend Package

`backend/app/drafting` is the target bounded context for DraftRun backend code.

Current status: behavior-preserving workflow orchestration shell, provider-free step
and JSON operation contracts, payload/runtime guardrails, Legacy DraftRun Surface
migration inventory, and the main DraftRun application package migrations. Context,
source/evidence, planning, candidate generation, validation, ranking/revision, final
quality, and HITL behavior now live under this bounded context. Old flat
`backend/app/application/*` paths for migrated runtime modules are compatibility
shims only.

## Ownership

The drafting context owns:

- DraftRun workflow and step registry;
- provider-neutral DraftRun step contracts;
- DraftRun artifacts and artifact mapping;
- source/evidence acquisition, evidence contracts, and planning services;
- JSON LLM operation compatibility imports used by drafting steps;
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

Compatibility shims are intentionally narrow. They expose legacy entrypoints while
call sites migrate.

Old paths moved in Slice 2.17.4.6.0.4 under `backend/app/application/*` are thin
import/re-export files only. They must not contain local functions, classes,
provider calls, fallback logic, or trace decisions. Do not add broad barrels that
mirror the entire legacy `draft_*` namespace.

## Legacy DraftRun Surface Migration

`backend.app.drafting.application.migration.legacy_surface_inventory` is the
planning source for moving the flat Legacy DraftRun Surface. It lists every current
`backend/app/application/draft_*.py` and `deterministic_*.py` module with a target
cluster, target package, `moduleDisposition`, target owner, migration slice, and
compatibility strategy. It also lists every public top-level helper with
`publicHelperDisposition`, target visibility, and rationale.

The migration rule is `no cosmetic package moves`: do not move a procedural flat
module into this package while preserving anonymous public helper sprawl. Behavior
with collaborators, trace semantics, provider semantics, state, or repeated callers
must become methods on named service, policy, or component owners. Small
provider-free DTO/factory helpers may remain package-level only when explicitly
listed and documented. `deterministic_*` modules must move into fallback
policy/service owners, not into a new flat deterministic package.

Slice 2.17.4.6.0.4 migrated 68 early modules into:

- `application/artifacts`: run/context payloads, source ledger, article dossier,
  article memory, and context packs;
- `application/evidence`: source intent, research planning, public evidence,
  synthesis, feasibility, post contract, rule registry, rule pack, and evidence
  interpretation;
- `application/planning`: material plan, strategy, rhetorical plans, retry/audit
  collaborators, and deterministic planning/rhetorical fallback owners;
- `application/operations/json_step_adapter.py`: bounded JSON provider adapter for
  migrated provider-heavy services.

Slice 2.17.4.6.0.5 migrated the late DraftRun modules into:

- `application/generation`: candidate direction/generation/provider/selection,
  candidate audit/prompts/results, publishability, deterministic candidate fallback,
  alternative-angle challenger writing, generation params, and prompt builder;
- `application/validation`: deterministic validation, attribution requirements,
  LLM validation, editorial critique, validation report flow, alternative-angle
  route/tournament orchestration, validation step service, and operation safety;
- `application/revision`: pairwise ranking, directed revision, ranking-revision
  orchestration, revision loop, revision policies, regression checks, rejected
  moves, and deterministic pairwise fallback;
- `application/final_quality`: final quality contract, deterministic assessment,
  final gate, independent review, payload helpers, and repair loop;
- `application/hitl`: post-run human-comment revision and revision quality check.

## Unified Step Contract

New DraftRun step code should implement the provider-free contract in
`backend.app.drafting.application.steps.contracts`:

- `DraftStepContext`: normalized run id, step key, request payload, prior artifacts,
  and step metadata.
- `DraftStepTrace`: trace-safe operation name, child `AiRun` ids, attempts, warnings,
  and metadata.
- `DraftStepOutcome`: one standard result envelope with status, artifact payload,
  child `AiRun` ids, safe error, trace, and optional result payload.
- `DraftStep`: protocol whose `execute(...)` returns `DraftStepOutcome`.

Do not add new step services whose public `execute(...)` returns raw
`dict[str, Any]`. If legacy code still returns a bespoke dataclass, add a narrow
adapter in `application/steps` and keep the old runtime behavior unchanged until the
owning migration slice moves it.

## JSON Operation Contract

Drafting JSON LLM operations should use the shared provider-neutral contract in
`backend.app.shared.llm_operations`. The drafting import path
`backend.app.drafting.application.operations.json_contracts` remains a thin
compatibility re-export during migration:

- `LlmOperationEnvelope` / `JsonOperationEnvelope`: trace-safe operation result
  payload with operation identity, owner, status, attempts, `AiRun` ids, input
  stats, payload stats, retry policy, timeout profile, incident, safe error, and
  result payload.
- `LlmOperationAttempt` / `JsonOperationAttempt`: one primary, repair, backup,
  fallback, not-run, failed, timeout, cancelled, or stale attempt with model, label,
  child `AiRun` id, safe error, incident, and model-role metadata.
- `LlmOperationResult` / `JsonOperationResult`: one accepted, repaired,
  backup-accepted, fallback, not-run, failed, timeout, cancelled, or stale operation
  result.
- `LlmOperationIncident`: provider-neutral incident taxonomy covering
  `providerTimeout`, `malformedJson`, `schemaFailure`, `deterministicFallback`,
  `backupAccepted`, `notConfigured`, and related provider/worker failures.
- `JsonLlmOperation`: protocol for future operation services.

The existing `backend.app.application.json_step_retry_policy` remains the retry
sequence source during migration. New operation code should convert those attempts
into the shared envelope rather than inventing another trace shape. Current
provider-heavy operations must either be migrated or explicitly listed in
`backend.app.shared.llm_operations.inventory.CURRENT_LLM_OPERATION_INVENTORY` with
owner, reason, removal slice, and expected incident coverage.

Provider-heavy operations must be bounded by operation-level timeouts when a stuck
call would otherwise leave a DraftRun step running. `TimedOperationRunner` is the v1
containment helper. It does not replace provider/http timeouts; it guarantees that
the workflow can record a safe failed attempt and proceed to repair, backup, or
fallback.

`EvidenceInterpretationPayloadCompactor` is the first compact provider-input helper.
It keeps full `rulePack` artifacts in the parent run but sends only the contract,
accepted evidence, external claims, synthesis, and relevant rule subset to the
strategy model.

## Payload Budget Policy

DraftRun provider-heavy operations must cross the DraftRun payload budget layer
before `build_*_messages(...)` creates provider messages. The implementation is
split by role under `backend.app.drafting.application.operations`:

- `payload_budget_contracts.py`: `PayloadBudgetProfile`,
  `SemanticInputContract`, `PayloadBudgetResult`, and internal compaction DTOs.
- `payload_budget_profiles.py`: per-operation, per-execution-mode caps for prompt chars,
  approximate tokens, rules, claims, evidence, candidates, source snippets, and prior
  drafts.
- `payload_semantic_contracts.py`: `mustHave`, `shouldHave`, `diagnosticOnly`, and
  `neverSendToProvider` fields.
- `payload_compactors.py`: role-owned artifact compactors for rules, source ledger,
  evidence, material plan, candidates, validation reports, and trace context.
- `payload_budget_policy.py`: `DraftRunPayloadBudgetPolicy`, which returns compact
  provider input plus `inputStats`, `payloadStats`,
  trimmed/suppressed fields, quality risk, and optional `contextOverBudget` /
  `payloadTooLarge` incident metadata.
- `payload_budget.py`: compatibility facade for legacy imports only.

The full DraftRun artifacts remain in parent storage and trace. Only provider inputs
are compacted. Child `AiRun.requestPayload`, attempts, and `operationEnvelope` must
include `payloadBudget` metadata for every enforced operation. Operations not yet
wired must stay explicit debt entries in `CURRENT_LLM_OPERATION_INVENTORY`.

## Validation Runtime Budget

DraftRun validation can be slow, but it must be bounded and trace-visible.
`validation_runtime_budget.py` owns `ValidationRuntimeBudgetProfile`,
`ValidationRuntimeBudgetPolicy`, `ValidationRuntimeGuard`,
`ValidationRuntimeCounters`, and canonical validation stop reasons.

The validation step writes `progress.runtimeBudget` into the existing step artifact.
It tracks execution mode, wall-clock budget, LLM-call count, revision cycles,
pairwise rounds, final-gate repair cycles, consecutive non-improving attempts,
current operation, heartbeat, slow-but-healthy state, incidents, and stop reason.
Canonical stop reasons are `acceptedQuality`, `humanReviewRequired`,
`budgetExhausted`, `maxIterations`, `noImprovement`, and `providerIncident`.

## Workflow Orchestration

`backend.app.drafting.application.workflow` owns the new DraftRun orchestration
shell:

- `DraftWorkflow` executes an ordered registry of phases.
- `DraftWorkflowState` carries the request, progress object, intermediate artifacts,
  final draft, and stop flags between phases.
- `DraftWorkflowPhase` wraps one behavior-preserving phase.
- `DraftStepRegistry` keeps phase ordering explicit and rejects duplicate phase ids.
- `LegacyDraftWorkflowServices` keeps old dependency defaults in one migration-only
  container.
- `LegacyDraftWorkflowPhaseBuilder` adapts the old step sequence into registered
  phases while individual services are migrated later.

The legacy `backend.app.application.draft_run_pipeline.DraftRunPipeline` class is
still the runtime compatibility entrypoint. It keeps the old constructor and
`execute(run_id)` method, then delegates to `DraftWorkflow`. Do not add new step
logic to the facade.
