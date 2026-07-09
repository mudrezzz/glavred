# Backend Architecture Target

Current as of Slice 2.17.4.6.0.7.

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

As of Slice 2.17.4.6.0.3, `backend/app/drafting` exists as the first target
bounded-context package. It contains package markers, package-local documentation,
narrow compatibility shims, the first provider-free step/JSON operation contracts,
and the behavior-preserving DraftRun workflow orchestration shell.

Implemented documentation:

- `backend/app/drafting/README.md`
- `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`
- `docs/developer/BACKEND_MODULE_TEMPLATE.md`
- `docs/adr/2026-07-05-backend-architecture-audit-program.md`

Implemented compatibility anchors:

- `backend.app.drafting.application.workflow.legacy_pipeline`
- `backend.app.drafting.domain.legacy_run`

These anchors re-export selected legacy DraftRun entrypoints without moving runtime
behavior. They must not become broad barrels for the whole legacy `draft_*`
namespace.

Implemented drafting contracts:

- `backend.app.shared.llm_operations`
  - `LlmOperationEnvelope`
  - `JsonOperationEnvelope`
  - `LlmOperationAttempt`
  - `LlmOperationResult`
  - `LlmOperationIncident`
  - `LlmOperationInputStats`
  - `LlmOperationTimeoutProfile`
  - `LlmOperationRetryPolicy`
  - `CURRENT_LLM_OPERATION_INVENTORY`
- `backend.app.drafting.application.steps.contracts`
  - `DraftStepContext`
  - `DraftStepTrace`
  - `DraftStepOutcome`
  - `DraftStep`
- `backend.app.drafting.application.steps.legacy_adapters`
  - `DraftPlanningStepOutcomeAdapter`
  - `DraftCandidateStepOutcomeAdapter`
- `backend.app.drafting.application.operations.json_contracts`
  - thin compatibility re-export of `backend.app.shared.llm_operations`

Implemented workflow orchestration:

- `backend.app.drafting.application.workflow.workflow`
  - `DraftWorkflow`
- `backend.app.drafting.application.workflow.state`
  - `DraftWorkflowState`
- `backend.app.drafting.application.workflow.registry`
  - `DraftWorkflowPhase`
  - `DraftStepRegistry`
- `backend.app.drafting.application.workflow.legacy_workflow`
  - thin factory that wires legacy DraftRun services into `DraftWorkflow`
- `backend.app.drafting.application.workflow.legacy_services`
  - migration-only dependency container preserving old default service wiring
- `backend.app.drafting.application.workflow.legacy_phase_builder`
  - behavior-preserving phase builder around the existing legacy DraftRun services
- `backend.app.application.draft_run_pipeline`
  - compatibility facade that keeps the previous public constructor and delegates to
    `DraftWorkflow`

Implemented operation safety repair:

- `backend.app.drafting.application.operations.timeout`
  - `TimedOperationRunner` and `OperationTimeoutError` for provider-heavy operation
    containment when a legacy service can otherwise leave a DraftRun step running.
- `backend.app.drafting.application.operations.evidence_interpretation_payload`
  - compact payload builder for `EvidenceInterpretation`, keeping full artifacts in
    the parent run while sending a bounded provider request.
- DraftRun provider-input payload budgeting:
  - `backend.app.drafting.application.operations.payload_budget_contracts`
    owns `PayloadBudgetProfile`, `SemanticInputContract`,
    `PayloadBudgetResult`, and the internal compaction DTO;
  - `backend.app.drafting.application.operations.payload_budget_profiles`
    owns execution-mode caps and per-operation profile selection;
  - `backend.app.drafting.application.operations.payload_semantic_contracts`
    owns `mustHave`, `shouldHave`, `diagnosticOnly`, and
    `neverSendToProvider` declarations;
  - `backend.app.drafting.application.operations.payload_compactors`
    owns role-specific artifact compaction classes for rules, ledgers,
    evidence, plans, candidates, reports, and trace context;
  - `backend.app.drafting.application.operations.payload_budget_policy`
    orchestrates profile selection, semantic contracts, compaction, stats, and
    budget incidents;
  - `backend.app.drafting.application.operations.payload_budget` remains a thin
    compatibility facade for legacy imports only;
  - `backend.app.drafting.application.operations.payload_budget_runtime`
    provides migration helpers for legacy flat services;
  - representative enforced operations attach `payloadBudget` metadata to child
    `AiRun.requestPayload`, attempts, and `operationEnvelope.payloadStats`;
  - over-budget compacted inputs map to `contextOverBudget` and hard cap breaches
    map to `payloadTooLarge`.
- Universal LLM operation governance:
  - shared envelope status taxonomy: `accepted`, `repaired`, `backupAccepted`,
    `fallback`, `notRun`, `failed`, `timeout`, `cancelled`, `stale`;
  - incident taxonomy: `providerTimeout`, `networkError`, `provider4xx`,
    `provider5xx`, `malformedJson`, `schemaFailure`, `payloadTooLarge`,
    `contextOverBudget`, `deterministicFallback`, `backupAccepted`,
    `notConfigured`, `staleOperation`, `cancelled`, `workerFailure`,
    `unknownProviderFailure`;
  - representative migrated operations:
    `evidenceInterpretation`, `editorialCritique`, `directedRevision`,
    `humanCommentRevision`, and `humanCommentRevisionQualityCheck`;
  - explicit inventory/allowlist for current unmigrated provider-heavy operations.
- DraftRun validation runtime budgeting:
  - `backend.app.drafting.application.operations.validation_runtime_budget`
    owns `ValidationRuntimeBudgetProfile`, `ValidationRuntimeBudgetPolicy`,
    `ValidationRuntimeGuard`, `ValidationRuntimeCounters`, and canonical validation
    stop-reason normalization;
  - validation progress records `runtimeBudget` inside the existing step artifact;
  - canonical validation stop reasons are `acceptedQuality`,
    `humanReviewRequired`, `budgetExhausted`, `maxIterations`, `noImprovement`, and
    `providerIncident`;
  - staleness inspection treats a validation step as slow-but-healthy while current
    operation heartbeat age stays inside the validation runtime budget.
- Legacy DraftRun Surface migration inventory:
  - `backend.app.drafting.application.migration.legacy_surface_inventory`
    classifies every current flat `backend/app/application/draft_*.py` and
    `deterministic_*.py` module before runtime migration;
  - each entry records `cluster`, `targetPackage`, `moduleDisposition`,
    `targetOwner`, `migrationSlice`, `compatibilityStrategy`, `publicHelpers`,
    and notes;
  - each public top-level helper records `publicHelperDisposition`, target
    visibility, target owner, and rationale.
- DraftRun context, evidence, and planning package migration:
  - `backend.app.drafting.application.artifacts` owns context payloads, run budget
    resolution, source ledger assembly/sections, article dossier, article memory,
    and context pack building;
  - `backend.app.drafting.application.evidence` owns source intent/research planning,
    public evidence retrieval/merge/synthesis, feasibility, post contract, rule
    registry, rule pack, evidence interpretation, and deterministic evidence
    fallbacks;
  - `backend.app.drafting.application.planning` owns material-plan retry
    orchestration, strategy, rhetorical plans, planning audit/result/prompt helpers,
    and deterministic planning/rhetorical fallback owners;
  - `backend.app.drafting.application.operations.json_step_adapter` is the bounded
    JSON provider-call adapter used by migrated provider-heavy services;
  - old `backend.app.application.*` imports for this migrated batch are compatibility
    shims only and architecture smoke rejects behavior reintroduced into them.
- DraftRun candidate, validation, revision, final quality, and HITL package
  migration:
  - `backend.app.drafting.application.generation` owns candidate direction,
    generation/provider execution, selection, publishability, candidate
    audit/prompts/results, alternative-angle challenger writing, deterministic
    candidate fallback, generation params, and prompt builder;
  - `backend.app.drafting.application.validation` owns deterministic validation,
    attribution requirements, LLM validation, editorial critique, validation report
    flow, alternative-angle route/tournament orchestration, validation step service,
    and operation safety;
  - `backend.app.drafting.application.revision` owns pairwise ranking, directed
    revision, ranking-revision orchestration, revision-loop policy/cycle execution,
    regression checks, rejected moves, and deterministic pairwise fallback;
  - `backend.app.drafting.application.final_quality` owns final quality contracts,
    deterministic assessment, final gate/evaluator/payloads, independent review,
    parser/prompts/service, and final repair loop;
  - `backend.app.drafting.application.hitl` owns post-run human-comment revision and
    human-comment revision quality check;
  - `backend.app.drafting.application.quality` owns trace-only per-run quality and
    fidelity reporting across technical completion, provider recovery, evidence
    fidelity, validation/final-gate issue lifecycle, editorial status, and
    clean/degraded/attention verdicts; `DraftRun.status=succeeded` is never used as
    quality proof by itself, open critical issues block trusted quality, and
    unresolved final-gate warnings cannot produce `cleanSuccess`;
  - old `backend.app.application.*` imports for this migrated batch are
    compatibility shims only, and provider-heavy migrated services use the bounded
    drafting JSON adapter instead of raw provider `.complete_json(...)`.
- Drafting validation package OOP cleanup:
  - Slice 2.17.4.6.0.8 turned validation parsing, prompts, trace payloads,
    operation failure mapping, attribution/evidence evaluation, validation artifact
    creation, editorial-critique report appending, and LLM/editorial attempt
    mapping into named component or policy owners;
  - validation services now keep orchestration responsibilities and delegate
    parser/prompt/trace/envelope mapping to those owners;
  - new high-severity validation public helper sprawl is an audit failure unless a
    ledger entry explicitly records owner, reason, guardrail, and repair slice.
- Drafting revision and final-quality package OOP cleanup:
  - Slice 2.17.4.6.0.9 turned revision pairwise payload mapping, ranking/revision
    candidate mapping, revision-loop policy, rejected-move policy, prompt building,
    acceptance decisions, and revision-loop config into named class owners;
  - final-quality deterministic assessment, attribution classification, final-gate
    payload construction, contract building, review parsing, and review prompt
    construction are also class-owned;
  - final-quality high findings are closed, and revision retains only medium
    service-size/package debt recorded in the audit ledger.
- Drafting HITL and provider operation surface cleanup:
  - Slice 2.17.4.6.0.10 keeps HITL services as orchestration owners and moves
    prompt building, version compaction, trace context, attempt records,
    provider-attempt execution, quality payload parsing, and deterministic quality
    overlay into named HITL components;
  - drafting operation support is split into `DraftingJsonOperationClient`,
    payload budget stats/profile owners, validation runtime progress/stop/incident
    policies, revision-loop payload factory, and role-owned payload compactors;
  - shared LLM operation governance is split into status/stat/incident/attempt/
    result/envelope/inventory owners while legacy import paths remain
    compatibility re-exports.
- Backend documentation and agent guardrail hardening:
  - backend docs, `AGENTS.md`, and repo-local skills now describe the post-`0.5`
    canonical package owners;
  - legacy backend files are classified as active compatibility facade, migrated
    thin shim, or remaining explicit debt;
  - `docs/developer/BACKEND_MODULE_TEMPLATE.md` is the module template and
    Provider-Heavy Review Checklist source;
  - architecture smoke requires those docs/skills fragments and keeps migrated shims
    import/re-export only through `npm run test:architecture`.
- Backend Architecture Audit and Debt Ledger:
  - `scripts/backend-architecture-audit.py` scans `backend/app` and `backend/tests`
    with Python AST and emits JSON or Markdown reports;
  - `docs/architecture/backend-architecture-debt-ledger.json` is the committed
    source of known backend debt with owner, severity, target shape, allowed-until
    slice, repair slice, guardrail, and evidence;
  - `docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md` is the current human-readable
    audit snapshot;
  - `npm run test:architecture` runs
    `python scripts/backend-architecture-audit.py --format json --ledger docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high`;
  - unledgered `critical` / `high` findings fail architecture smoke.
- Backend API/application/infrastructure surface cleanup:
  - Slice 2.17.4.6.0.11 moves roadmap tracker parsing/rendering/JSONL/service
    behavior behind `backend.app.roadmap` while preserving the old
    `backend.app.application.roadmap_tracker` compatibility import path;
  - upstream radar search planning, triage, payload construction, and external-run
    orchestration now live under `backend.app.upstream.application`; old
    `backend.app.application.upstream_radar_*` paths are compatibility shims only;
  - architecture audit distinguishes FastAPI route/dependency facades from public
    helper sprawl, and the current ledger has no high or stale findings.
- Backend medium architecture debt follow-up:
  - Slice 2.17.4.6.0.12 keeps the product runtime unchanged while closing the
    upstream/radar medium blocker that would otherwise affect the next search slices;
  - live benchmark evaluation is split into status, expectation, coverage, trace,
    and evaluator owners;
  - external radar runs delegate one-query execution, benchmark report attachment,
    and result status/unique policy to named components;
  - remaining medium debt is re-ledgered into explicit follow-up slices instead of
    staying attached to the completed `0.12` slice.
- Upstream search intent planning:
  - Slice 2.17.4.6.1 adds provider-free upstream domain contracts for `SearchPlan`,
    `SearchIntent`, `SearchQuery`, `SearchCampaignTrace`, and skipped search intents;
  - `backend.app.upstream.application.SearchIntentPlanner` owns deterministic query
    intent generation before provider search, while provider execution remains behind
    infrastructure adapters;
  - `RadarRun.searchPlan` stays backward-compatible through `queries[]` and
    `skippedIntents[]`, and adds campaign trace fields for source strategy, intent
    coverage, budget skips, and the rule that raw found material does not own
    topic/fabula decisions.

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

## Legacy DraftRun Surface OOP Migration Rule

Runtime migration from the Legacy DraftRun Surface is not a file move. It is an
ownership move.

Allowed `moduleDisposition` values are:

- `service`: a use-case or orchestration class.
- `policy`: a deterministic decision, fallback, gate, scoring, or safety rule
  owner.
- `component`: a builder, parser, mapper, compiler, resolver, evaluator, or trace
  collaborator.
- `dto`: provider-free result, contract, value object, or small factory surface.
- `privateHelper`: a helper that must become private to an owning module.
- `compatibilityShim`: a thin re-export only.
- `deleteAfterMigration`: no target behavior owner remains after call sites move.

Public top-level functions in migrated DraftRun code are not a default API shape.
Each legacy helper must have a `publicHelperDisposition`. Behavioral helpers with
collaborators, trace semantics, provider semantics, domain decisions, or multiple
callers become methods on a service, policy, or component. DTO/factory helpers are
allowed only when provider-free, small, documented, and explicitly listed. Pure
local helpers should be private.

The `deterministic_*` modules are fallback behavior, not a second package style.
They move into named fallback policy/service owners inside `backend/app/drafting`.
The next `0.4` and `0.5` slices must follow the `no cosmetic package moves` rule:
do not preserve the old flat public-helper surface under a new package path.

## Backend Architecture Audit Program

Architecture recovery is a recurring audit loop, not a completed one-time migration.
Slice `2.17.4.6.0.7` adds an automated backend architecture audit and a
machine-readable debt ledger. The audit detects:

- public top-level helper sprawl;
- procedural bounded packages that mirror legacy flat files;
- large modules and god services;
- raw `dict[str, Any]` request/result seams where typed DTOs or operation envelopes
  are expected;
- provider boundary leaks and raw `.complete_json(` calls outside allowed adapters;
- dependency-direction risks between API, application, domain, infrastructure, and
  shared packages;
- behavior inside migrated thin shims;
- tests that keep importing legacy/procedural owners instead of canonical package
  owners.

Known debt may remain only when the debt ledger records `debtId`, package, module,
smell type, severity, owner, target shape, allowed-until slice, repair slice,
guardrail, and notes. New unclassified high-severity smells should fail
`npm run test:architecture`.

The planned cleanup sequence after the audit is:

1. `2.17.4.6.0.8`: Drafting validation package OOP cleanup.
2. `2.17.4.6.0.9`: Drafting revision and final-quality OOP cleanup. Done.
3. `2.17.4.6.0.10`: Drafting HITL and provider operation surface cleanup. Done.
4. `2.17.4.6.0.11`: Backend API/application/infrastructure/upstream surface cleanup. Done.
5. `2.17.4.6.0.12`: Backend medium architecture debt follow-up. Done.
6. `2.17.4.6.0.12.1`: Backend API and infrastructure medium debt cleanup.
7. `2.17.4.6.0.12.2`: Drafting residual medium debt cleanup.
8. `2.17.4.6.0.12.3`: Backend test canonical import cleanup.

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

Use `docs/developer/BACKEND_MODULE_TEMPLATE.md` before adding or moving backend
modules. It defines service, policy, component, and DTO module roles; records the
migrated thin shim rule; and contains the Provider-Heavy Review Checklist for shared
operation governance, incident metadata, payload budget, timeout/runtime budget,
safe errors, and no raw provider calls.

Legacy backend files have three allowed statuses:

- active compatibility facade: the old path still owns compatibility wiring;
- migrated thin shim: import/re-export only, with no `def`, `class`, provider call,
  fallback logic, or trace mutation;
- remaining explicit debt: explicitly listed in the migration inventory or LLM
  operation inventory with owner, reason, and removal slice.

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

The universal operation envelope must serialize to trace-safe dict shape:
`operationId`, `operationKind`, `owner`, `status`, `attempts[]`, `aiRunIds[]`,
`inputStats`, `payloadStats`, `retryPolicy`, `timeoutProfile`, `incident`,
`safeError`, and `resultPayload`.

Fallback, deterministic fallback, backup-accepted, not-run, failed, timeout,
cancelled, and stale outcomes must carry `LlmOperationIncident` metadata with
incident type, severity, probable cause, follow-up flag, provider, model, attempt
label, safe error, and payload stats where available. Payload/input stats should at
least expose prompt character estimate, approximate token estimate when available,
rule/evidence/claim/source/candidate counts, model/model role, timeout profile,
retry policy, and generation parameters. Unknown exact counts must be explicit as
`0`, `None`, or an empty object rather than silently omitted in new migrated
operations.

DraftRun provider-heavy operations must also cross a provider-input budget boundary
before prompt message construction. Full DraftRun artifacts may stay in parent
storage and diagnostic trace, but provider request payloads must be compacted by a
named `PayloadBudgetProfile`. Semantic contracts must distinguish `mustHave`,
`shouldHave`, `diagnosticOnly`, and `neverSendToProvider` inputs. Child
`AiRun.requestPayload`, attempts, and nested operation envelopes must expose
`payloadBudget.profileId`, execution mode, limits, sent/trimmed counts, suppressed
fields, semantic inputs, quality risk, prompt char estimate, and approx token
estimate. Operations not yet wired must be explicitly debt-allowlisted in
`CURRENT_LLM_OPERATION_INVENTORY` with a removal slice.

The next provider-input target is the DraftRun dossier boundary documented in
`docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md` and ADR
`docs/adr/2026-07-09-draftrun-provider-input-dossier-boundary.md`. The payload
budget rule is not enough if prompt builders still receive full artifacts and only
record budget metadata indirectly. Every provider-heavy operation should receive a
task-specific dossier assembled through deterministic context access:

`DraftRun artifacts -> DraftRunContextAccessService -> DossierFactory -> ProviderInputBudgetGate -> PromptBuilder -> Provider`

The parent DraftRun keeps rich artifacts for storage, diagnostics, replay, and
human inspection. The provider gets a compact projection with handles back to the
rich artifacts. Prompt builders must not receive full `rulePack`, `SourceLedger`,
`materialPlan`, candidate pools, validation reports, or final-quality traces by
default. A temporary exception requires an explicit inventory/debt entry, direct
payload stats, and a removal slice.

Target dossier owners:

- `PlanningDossierFactory` for `materialPlan`, `strategy`, and `rhetoricalPlans`.
- `WriterDossierFactory` for `draftCandidate` and alternative-angle candidate prose.
- `ReviewDossierFactory` for `llmValidation` and `editorialCritique`.
- `RankingDossierFactory` for `pairwiseRanking`.
- `RevisionDossierFactory` for `directedRevision` and final repair.
- `FinalQualityDossierFactory` for independent final quality review.

Tool-mediated or MCP-style context access is a future adapter over the deterministic
context service, not a substitute for it. A tool server must not expose raw full
DraftRun JSON to the model.

DraftRun JSON LLM operations must keep using the universal JSON retry policy:
primary, repair, optional backup, then explicit fallback, not-run, or failed outcome.

Provider-heavy operations that can block the worker must also use an operation-level
timeout envelope, not only an HTTP client timeout. A timeout must be visible as a
failed attempt with a safe child `AiRun`, a failed nested operation, and a controlled
retry/backup/fallback path.

Live DraftRun quality/fidelity reporting must not collapse provider recovery into
editorial quality. A successful primary repair retry is normal recovery. Backup
success is accepted but diagnostic. Deterministic fallback lowers fidelity.
Unresolved critical findings, final-gate warning/critical status, weak evidence
coverage, rejected final repair, and size/over-budget problems are step-level quality
issues and must be visible in `qualityFidelity`, not inferred from
`DraftRun.status` alone.
Evidence interpretation owns its own fidelity policy. `rulePack` records
`evidenceInterpretationFidelity` with `sufficient`, `partial`, `weak`, or `missing`
coverage; quality and reliability reporters consume that structured verdict rather
than inferring trust from provider success alone.

Cross-run DraftRun provider reliability analytics must reuse structured
`qualityFidelity`, operation envelopes, payload/runtime budgets, and child `AiRun`
records. It must not parse prose diagnostics. A same-model retry that later accepts
is a reliability counter, not a failed quality result. Repeated backup, fallback,
timeout, malformed JSON, schema failure, open critical, or budget incidents must be
mapped to an explicit remediation decision: no action, watch with more runs, covered
by an existing slice, backlog fix, fix before trusting quality, or manual review.
The report must also expose `signalCoverage` so every raw child `AiRun`,
operation-envelope incident, retry, backup, fallback, and payload/runtime budget
incident is either counted or ignored with a concrete reason. Remediation decisions
that require fixes must reference concrete roadmap slices.

Validation and ranking/revision loops must additionally use the DraftRun validation
runtime budget guard. The guard records `runtimeBudget` in validation progress,
tracks wall-clock time, LLM calls, revision cycles, pairwise rounds, final-gate
repair cycles, consecutive non-improving attempts, current operation, heartbeat, and
incidents, and normalizes exit reasons to `acceptedQuality`, `humanReviewRequired`,
`budgetExhausted`, `maxIterations`, `noImprovement`, or `providerIncident`.

The Drafting v1 implementation of this contract is:

- new step implementations return `DraftStepOutcome`, not raw `dict[str, Any]`;
- legacy result dataclasses are adapted through narrow adapters until their owning
  runtime slices migrate;
- JSON retry attempts from `json_step_retry_policy.py` are converted into shared
  `LlmOperationAttempt` / compatibility `JsonOperationAttempt`;
- accepted, repaired, backup-accepted, fallback, not-run, failed, timeout,
  cancelled, and stale JSON outcomes are represented by shared `LlmOperationResult`
  / compatibility `JsonOperationResult`;
- all current provider-heavy operations must be migrated or recorded in
  `CURRENT_LLM_OPERATION_INVENTORY` with owner, module, operation kind, current
  status, reason not migrated, removal slice, expected incident coverage, payload
  budget status, policy id, reason not budgeted, and payload-budget removal slice;
- architecture smoke rejects new step-like `execute(...) -> dict[...]` contracts in
  `backend/app/drafting/application/steps`, new bounded-context raw
  `complete_json(...)` calls, and missing shared operation governance docs.

## Migration Sequence

1. Add this contract and architecture smoke stop-line.
2. Create `backend/app/drafting` skeleton and compatibility shims.
3. Introduce shared `DraftStep` and JSON operation contracts. Done.
4. Refactor DraftRun orchestration into a workflow registry. Done.
5. Add DraftRun provider-input payload budget policies. Done.
6. Add validation/revision runtime guard and canonical stop reasons. Done.
7. Move context/evidence/planning clusters. Done.
8. Move candidate/validation/revision/final quality clusters. Done.
9. Harden backend docs, agent guidance, and documentation smoke checks. Done.
10. Add Backend Architecture Audit and Debt Ledger. Done.
11. Clean migrated validation, revision/final-quality, HITL/provider, and remaining
   backend surfaces according to the audit ledger.
12. Move upstream radar/search into `backend/app/upstream` before expanding extraction
   and scoring.
13. Tighten allowlists after each cluster migration.
14. Retire `CURRENT_LLM_OPERATION_INVENTORY` entries as their owning slices migrate
   each provider-heavy operation behind the shared envelope.
15. Add provider-operation runtime guard coverage for all slow provider-heavy calls.
16. Enforce direct provider-input budgets on every provider-heavy child `AiRun`.
17. Add deterministic DraftRun context access and provider-input dossier factories.
18. Migrate planning, writer/alternative-angle, and review/ranking/final-gate
    operations from full-artifact prompt inputs to operation-specific dossiers.
19. Pilot tool-mediated context access only after the deterministic dossier boundary
    is in place.

## Review Checklist

Before adding a backend module:

- Which bounded context owns it?
- Is it domain, application, infrastructure, API, or shared?
- Does it need a new public contract, or can it use an existing one?
- Is there an architecture doc anchor?
- Does an existing service already own this responsibility?
- Can the behavior be tested at the owning layer without crossing API/UI boundaries?

Provider-heavy work must also pass the Provider-Heavy Review Checklist in
`docs/developer/BACKEND_MODULE_TEMPLATE.md`.
