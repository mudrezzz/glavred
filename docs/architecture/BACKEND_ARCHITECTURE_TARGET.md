# Backend Architecture Target

Current as of Slice 2.17.4.6.0.3.1.

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

Implemented compatibility anchors:

- `backend.app.drafting.application.workflow.legacy_pipeline`
- `backend.app.drafting.domain.legacy_run`

These anchors re-export selected legacy DraftRun entrypoints without moving runtime
behavior. They must not become broad barrels for the whole legacy `draft_*`
namespace.

Implemented drafting contracts:

- `backend.app.drafting.application.steps.contracts`
  - `DraftStepContext`
  - `DraftStepTrace`
  - `DraftStepOutcome`
  - `DraftStep`
- `backend.app.drafting.application.steps.legacy_adapters`
  - `DraftPlanningStepOutcomeAdapter`
  - `DraftCandidateStepOutcomeAdapter`
- `backend.app.drafting.application.operations.json_contracts`
  - `JsonOperationAttempt`
  - `JsonOperationResult`
  - `JsonLlmOperation`

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

Provider-heavy operations that can block the worker must also use an operation-level
timeout envelope, not only an HTTP client timeout. A timeout must be visible as a
failed attempt with a safe child `AiRun`, a failed nested operation, and a controlled
retry/backup/fallback path.

The Drafting v1 implementation of this contract is:

- new step implementations return `DraftStepOutcome`, not raw `dict[str, Any]`;
- legacy result dataclasses are adapted through narrow adapters until their owning
  runtime slices migrate;
- JSON retry attempts from `json_step_retry_policy.py` are converted into
  `JsonOperationAttempt`;
- accepted, fallback, not-run, and failed JSON outcomes are represented by
  `JsonOperationResult`;
- architecture smoke rejects new step-like `execute(...) -> dict[...]` contracts in
  `backend/app/drafting/application/steps`.

## Migration Sequence

1. Add this contract and architecture smoke stop-line.
2. Create `backend/app/drafting` skeleton and compatibility shims.
3. Introduce shared `DraftStep` and JSON operation contracts. Done.
4. Refactor DraftRun orchestration into a workflow registry. Done.
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
