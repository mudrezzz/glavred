# Drafting Backend Component Map

Current status: migration map for the `backend/app/drafting` bounded context.

This file is the implementation guide for moving legacy DraftRun modules in small,
behavior-preserving slices. It is not a promise that the listed modules have already
been migrated.

## Package Areas

| Target area | Owns | Legacy source clusters |
| --- | --- | --- |
| `domain` | Provider-free DraftRun entities, step keys, artifact DTOs, validation DTOs. | `backend/app/domain/draft_*.py` |
| `application/workflow` | Draft workflow sequencing, step registry, workflow state, progress handoff. | `draft_run_pipeline.py`, `draft_run_progress.py`, `draft_run_step_progress.py`, `draft_run_service.py` |
| `application/steps` | Step-level use cases with stable input/output contracts. | context, source intent, public evidence, feasibility, rule pack, material plan, strategy, rhetorical plans, draft, validation |
| `application/operations` | Provider-neutral JSON and model operation contracts, attempts, safe errors, trace payloads. | `json_step_retry_policy.py`, provider-heavy drafting services after adapter split |
| `application/artifacts` | Artifact serialization, payload mapping, compatibility readers. | `draft_run_payloads.py`, `draft_run_context_payloads.py`, step payload helpers |
| `infrastructure` | Drafting-specific infrastructure wiring and adapters when they cannot stay in root infrastructure. | Celery DraftRun wiring and provider factory wiring after ports exist |

## Migration Order

1. Keep this skeleton stable and add compatibility imports.
2. Introduce `DraftStep` and JSON operation contracts.
3. Move `DraftRunPipeline` behind `DraftWorkflow` and `DraftStepRegistry`.
4. Move context, source ledger, feasibility, post contract, rule pack, and planning
   clusters.
5. Move candidate, validation, ranking, revision, final quality, and HITL clusters.
6. Tighten architecture smoke allowlists after each cluster is moved.

## Compatibility Anchors

Current shims:

- `backend.app.drafting.application.workflow.legacy_pipeline`
- `backend.app.drafting.domain.legacy_run`

These shims re-export existing legacy objects. They must not add behavior, state,
provider calls, persistence, or broad namespace mirroring.
