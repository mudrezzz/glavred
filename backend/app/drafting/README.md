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

Use `docs/developer/BACKEND_MODULE_TEMPLATE.md` before adding or moving backend
modules. It contains the service/policy/component/DTO module templates, migrated
thin shim rules, and the Provider-Heavy Review Checklist for shared operation
governance, incidents, payload budgets, timeout/runtime budgets, safe errors, and no
raw provider calls in bounded application modules.

## Compatibility Shims

Compatibility shims are intentionally narrow. They expose legacy entrypoints while
call sites migrate.

Old paths moved in Slice 2.17.4.6.0.4 under `backend/app/application/*` are thin
import/re-export files only. They must not contain local functions, classes,
provider calls, fallback logic, or trace decisions. Do not add broad barrels that
mirror the entire legacy `draft_*` namespace.

Legacy backend files have three allowed statuses:

- active compatibility facade: the old path still owns compatibility wiring;
- migrated thin shim: import/re-export only, no behavior;
- remaining explicit debt: listed in the migration inventory or LLM operation
  inventory with owner, reason, and removal slice.

The recurring recovery layer is the Backend Architecture Audit and Debt Ledger from
Slice 2.17.4.6.0.7. Package migration alone does not prove internal OOP/SRP quality.
Use `.agents/skills/backend-architecture-audit/SKILL.md` and
`python scripts/backend-architecture-audit.py --format json --ledger
docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high`
when reviewing public helper sprawl, procedural bounded packages, raw
`dict[str, Any]` contracts, provider boundary leaks, dependency-direction risks,
migrated-shim behavior, or tests that still mirror legacy owners. Known debt is in
`docs/architecture/backend-architecture-debt-ledger.json`; the current snapshot is
`docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md`.

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
- `application/quality`: trace-only DraftRun quality/fidelity reporting. It
  distinguishes technical completion from provider retry/backup/fallback recovery,
  evidence coverage, unresolved validation/final-gate issues, editorial status, and
  the final clean/degraded/attention verdict.
- `application/reliability`: cross-run provider reliability analytics. It reads
  existing `qualityFidelity`, `operationEnvelope`, `payloadBudget`, `runtimeBudget`,
  and child `AiRun` records to count retry, backup, fallback, degradation, failure,
  timeout, malformed JSON, schema failure, and open critical patterns without
  parsing prose diagnostics.

Slice 2.17.4.6.0.8 cleaned the validation package after migration. Validation
prompt construction, LLM/editorial parsing, trace payloads, operation failure
mapping, attribution requirement resolution, evidence evaluation, validation
artifact creation, editorial report appending, and attempt/envelope mapping are now
owned by named classes. Do not add new public top-level helper functions to
`application/validation`; add behavior to the owning service, policy, or component
and let `npm run test:architecture` enforce the audit ledger.

Slice 2.17.4.6.0.9 cleaned the revision and final-quality packages after migration.
Revision pairwise payload mapping, candidate mapping, loop policy, rejected-move
policy, prompt builders, acceptance policy, and config caps are class-owned.
Final-quality assessment, attribution classification, final-gate payloads, contract
building, review parsing, and review prompts are class-owned. Do not add new public
top-level helper functions to `application/revision` or `application/final_quality`;
residual revision debt is medium service-size cleanup, not permission to restore
procedural helpers.

Slice 2.17.4.6.0.10 cleaned the HITL and provider-operation support packages.
Human-comment revision and quality services now own orchestration only; prompt
builders, version compaction, trace context, attempt trace records,
provider-attempt runners, quality payload parsing, and deterministic quality
overlay are class-owned components. Drafting operation support now uses
`DraftingJsonOperationClient`, `PayloadBudgetAttemptStatsExtractor`,
`PayloadBudgetProfileRegistry`, `ValidationProgressRuntimePresenter`,
`ValidationStopReasonPolicy`, `ValidationRuntimeBudgetIncidentFactory`,
`ValidationRevisionLoopPayloadFactory`, and split payload compactor modules
instead of public helper sprawl.

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
`backend.app.shared.llm_operations`. The shared package is split into role-owned
status, stat, incident, attempt, result, envelope factory, and inventory exporter
modules. The drafting import path
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

- `domain/provider_input_semantics.py`: provider-free `SemanticInputContract` shared
  by dossiers and payload budgeting.
- `payload_budget_contracts.py`: `PayloadBudgetProfile`, `PayloadBudgetResult`, and
  internal compaction DTOs; it re-exports the semantic contract for compatibility.
- `payload_budget_profiles.py`: per-operation, per-execution-mode caps for prompt chars,
  approximate tokens, rules, claims, evidence, candidates, source snippets, and prior
  drafts.
- `payload_semantic_contracts.py`: `mustHave`, `shouldHave`, `diagnosticOnly`, and
  `neverSendToProvider` fields.
- `payload_compactors.py`: compatibility facade over role-owned compactors for
  common counters, record projections, evidence/rules, artifacts/reports, and the
  DraftRun payload compactor orchestrator.
- `payload_budget_policy.py`: `DraftRunPayloadBudgetPolicy`, which returns compact
  provider input plus `inputStats`, `payloadStats`,
  trimmed/suppressed fields, quality risk, and optional `contextOverBudget` /
  `payloadTooLarge` incident metadata.
- `provider_input_budget_gate.py`: `ProviderInputBudgetGate`, the direct current-call
  boundary used before planning prompt builders.
- `provider_input_audit.py`: replayable classification for stored child
  `AiRun.requestPayload` records.
- `payload_budget.py`: compatibility facade for legacy imports only.

The full DraftRun artifacts remain in parent storage and trace. Only provider inputs
are compacted. Child `AiRun.requestPayload`, attempts, and `operationEnvelope` must
include `payloadBudget` metadata for every enforced operation. Operations not yet
wired must stay explicit debt entries in `CURRENT_LLM_OPERATION_INVENTORY`.

Slice 2.17.4.6.1.3.5 enforces this direct proof for `materialPlan`, `strategy`, and
`rhetoricalPlans`. The proof lives on the child `AiRun.requestPayload` as
`operationId`, `providerInput`, `payloadBudget`, `inputStats`, and `payloadStats`.
Use `python scripts/audit_draft_run_provider_inputs.py --run-id <DraftRun ID>
--format json` to replay the check. `directlyBudgeted` is the only clean budget
verdict; `overBudget`, `missingDirectBudget`, `nestedBudgetFalsePositive`, and
`explicitDebt` all require attention or a linked repair slice.

## Provider Input Dossier Boundary

Live DraftRun traces after the reliability slices showed that the payload-budget
rule must become stricter. A current provider call is not considered budgeted just
because it contains a previous artifact that itself contains `payloadBudget`
metadata. The current call needs its own direct profile and compact provider input.

The target track is documented in
`docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md` and ADR
`docs/adr/2026-07-09-draftrun-provider-input-dossier-boundary.md`.

Target flow:

```text
DraftRun artifacts -> DraftRunContextAccessService -> DossierFactory -> ProviderInputBudgetGate -> PromptBuilder -> Provider
```

Slice `2.17.4.6.1.3.6` introduces deterministic context access and
operation-specific dossier factories before migrating more prompt builders.
Implemented dossier owners include:

- planning dossiers for `materialPlan`, `strategy`, and `rhetoricalPlans`;
- writer dossiers for `draftCandidate` and alternative-angle candidate prose;
- review dossiers for `llmValidation` and `editorialCritique`;
- ranking dossiers for `pairwiseRanking`;
- revision dossiers for directed revision and final repair;
- final-quality dossiers for independent final gate review.

Prompt builders must not receive full `rulePack`, full `SourceLedger`, full
`materialPlan`, full candidate pools, full validation reports, or full final-quality
traces by default. A temporary exception must be explicit roadmap debt with a
removal slice.

The foundation is provider-free and currently lives in:

- `domain/provider_dossier.py` and `domain/provider_input_semantics.py` for typed
  contracts;
- `application/context` for deterministic compact reads and handle resolution;
- `application/dossiers` for policies, assembly, six factories, and replay;
- `scripts/audit_draft_run_provider_dossiers.py` for stored-run proof.

`readyForMigration` means factories, exclusions, and handles passed replay. It does
not by itself prove a provider call used a dossier. Slice `2.17.4.6.1.3.7` connects
the three planning call sites: `materialPlan`, `strategy`, and `rhetoricalPlans`.
Their workflow reads the current persisted run through `DraftRunContextAccessService`,
builds one operation-specific `PlanningDossier`, passes only the budgeted projection
to the prompt builder, and records `providerDossier.runtimeMigrated=true` on every
child `AiRun`. Other provider families remain scheduled for `3.8-3.9`, so replay
correctly reports `runtimeMigrationStatus=partiallyMigrated`.

## Validation Runtime Budget

DraftRun validation can be slow, but it must be bounded and trace-visible.
`validation_runtime_budget.py` is a compatibility facade over validation runtime
budget contracts, the runtime guard, stop-reason policy, incident factory, and
progress presenter. These owners expose `ValidationRuntimeBudgetProfile`,
`ValidationRuntimeBudgetPolicy`, `ValidationRuntimeGuard`,
`ValidationRuntimeCounters`, and canonical validation stop reasons.

The validation step writes `progress.runtimeBudget` into the existing step artifact.
It tracks execution mode, wall-clock budget, LLM-call count, revision cycles,
pairwise rounds, final-gate repair cycles, consecutive non-improving attempts,
current operation, heartbeat, slow-but-healthy state, incidents, and stop reason.
Canonical stop reasons are `acceptedQuality`, `humanReviewRequired`,
`budgetExhausted`, `maxIterations`, `noImprovement`, and `providerIncident`.

## Quality/Fidelity Report

`backend.app.drafting.application.quality` owns the per-run
`QualityFidelityReport`. The workflow stores it in
`validation.rankingRevision.qualityFidelity` and `complete.qualityFidelity` without
changing the public API, SQLite schema, prompts, or provider selection.

The report treats successful primary repair/retry as normal recovery. Backup model
success is accepted but diagnostic. Deterministic fallback is safe only where the
owning step already has a domain-safe fallback, and it lowers fidelity. Step-level
quality issues such as weak evidence coverage, open critical findings, final-gate
warnings, rejected final repair, or over-size final prose are evaluated separately
from LLM/provider incidents.

Validation and final-gate warning/critical findings are lifecycle-managed. Each
issue in `qualityFidelity.issueLifecycle.items` is `resolved`, `suppressed`,
`acceptedRisk`, or `open`. Open critical issues always block trusted editorial
quality. A final-gate warning without explicit resolution, suppression, or
accepted-risk semantics can produce `publishableWithCaution`, but not
`cleanSuccess`. `DraftRun.status=succeeded` only means the pipeline finished; it
does not mean the final text is editorially clean.

Evidence interpretation now writes `evidenceInterpretationFidelity` in the
`rulePack` artifact. The policy keeps retry/backup recovery separate from evidence
quality: accepted provider interpretation can remain `sufficient`, deterministic
fallback is always `weak`, and missing accepted evidence is `missing`/blocking for
trusted editorial quality.

## Provider Reliability Analytics

`backend.app.drafting.application.reliability` owns cross-run DraftRun provider
reliability analytics. It does not change DraftRun execution. It aggregates
structured signals already present in `qualityFidelity`, operation envelopes,
payload/runtime budgets, and child `AiRun` records.

Use:

```powershell
python scripts/analyze_draft_run_reliability.py --run-id <DraftRun ID> --run-id <DraftRun ID> --format markdown
```

The report contains two layers:

- `events`, `operationSummaries`, and `remediationItems` explain operation/model
  reliability and required follow-up.
- `signalCoverage` audits raw structured signals: child `AiRun`, operation-envelope
  incidents, retry/backup/fallback attempts, payload/runtime budget incidents, and
  ignored stats-only budget payloads with explicit reasons.

One run is useful for inspection but reports `insufficientData` for systemic
conclusions. Repeated same-model retry is a reliability signal, not a failed result.
Backup success is accepted but diagnostic. Deterministic fallback and open
validation/final-gate issues must become remediation items or explicit watch/no-action
decisions. Any `fixBacklogSlice` or `fixBeforeTrustingQuality` item must reference a
concrete roadmap slice, not a placeholder.

Incident classification is shared across quality and reliability layers. Provider
responses with no text content, missing required keys, invalid response shape, or
operation-specific contract mismatch are `schemaFailure`. JSON parse errors remain
`malformedJson`. `unknownProviderFailure` is reserved for genuinely unclassified
structured failures; old embedded stage summaries may be refined from matching child
`AiRun` errors during replay.

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
