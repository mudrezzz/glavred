# Drafting Backend Component Map

Current status: migration map for the `backend/app/drafting` bounded context.

This file is the implementation guide for moving legacy DraftRun modules in small,
behavior-preserving slices. It is not a promise that the listed modules have already
been migrated.

## Package Areas

| Target area | Owns | Legacy source clusters |
| --- | --- | --- |
| `domain` | Provider-free DraftRun entities, step keys, artifact DTOs, validation DTOs. | `backend/app/domain/draft_*.py` |
| `application/workflow` | Draft workflow sequencing, step registry, workflow state, progress handoff. `DraftWorkflow`, `DraftWorkflowState`, `DraftWorkflowPhase`, and `DraftStepRegistry` now own the behavior-preserving orchestration shell while legacy step services remain in place. | `draft_run_pipeline.py`, `draft_run_progress.py`, `draft_run_step_progress.py`, `draft_run_service.py` |
| `application/steps` | Step-level use cases with stable input/output contracts. `contracts.py` defines `DraftStepContext`, `DraftStepTrace`, `DraftStepOutcome`, and the `DraftStep` protocol. `legacy_adapters.py` converts the first legacy result shapes without changing runtime behavior. | context, source intent, public evidence, feasibility, rule pack, material plan, strategy, rhetorical plans, draft, validation |
| `application/operations` | Provider-neutral JSON and model operation contracts, attempts, safe errors, trace payloads, and bounded operation helpers. `json_contracts.py` defines `JsonOperationAttempt`, `JsonOperationResult`, and the `JsonLlmOperation` protocol. `timeout.py` and `evidence_interpretation_payload.py` protect the legacy evidence-interpretation operation during migration. | `json_step_retry_policy.py`, provider-heavy drafting services after adapter split |
| `application/artifacts` | Artifact serialization, payload mapping, compatibility readers. | `draft_run_payloads.py`, `draft_run_context_payloads.py`, step payload helpers |
| `infrastructure` | Drafting-specific infrastructure wiring and adapters when they cannot stay in root infrastructure. | Celery DraftRun wiring and provider factory wiring after ports exist |

## Migration Order

1. Keep this skeleton stable and add compatibility imports.
2. Introduce `DraftStep` and JSON operation contracts. Done in Slice 2.17.4.6.0.2.
3. Move `DraftRunPipeline` behind `DraftWorkflow` and `DraftStepRegistry`. Done in Slice 2.17.4.6.0.3.
4. Repair `EvidenceInterpretation` timeout/payload behavior before migrating planning.
   Done in Slice 2.17.4.6.0.3.1.
5. Move context, source ledger, feasibility, post contract, rule pack, and planning
   clusters.
6. Move candidate, validation, ranking, revision, final quality, and HITL clusters.
7. Tighten architecture smoke allowlists after each cluster is moved.

## Compatibility Anchors

Current shims:

- `backend.app.drafting.application.workflow.legacy_pipeline`
- `backend.app.drafting.domain.legacy_run`

These shims re-export existing legacy objects. They must not add behavior, state,
provider calls, persistence, or broad namespace mirroring.

Current adapters:

- `DraftPlanningStepOutcomeAdapter`: converts `DraftPlanningStepResult` to and from
  `DraftStepOutcome`.
- `DraftCandidateStepOutcomeAdapter`: converts `DraftCandidateGenerationResult` to
  and from `DraftStepOutcome` while preserving `final_draft` in `result_payload`.

## Workflow Orchestration

Implemented in Slice 2.17.4.6.0.3:

- `DraftWorkflow`: loads a run, marks it running, executes registered phases, and
  preserves the legacy success, blocked, and failure completion behavior.
- `DraftWorkflowState`: carries request, progress, intermediate artifacts, final draft,
  and stop flags between behavior-preserving phases.
- `DraftWorkflowPhase`: names one ordered workflow phase and points to the legacy
  phase implementation.
- `DraftStepRegistry`: stores the ordered phase list and rejects duplicate phase ids.
- `LegacyDraftWorkflowServices`: preserves the previous dependency defaults while
  individual services remain in legacy modules.
- `LegacyDraftWorkflowPhaseBuilder`: wraps the existing behavior-preserving step
  sequence as registered phases.
- `backend.app.application.draft_run_pipeline.DraftRunPipeline`: compatibility facade
  with the previous constructor and `execute(run_id)` API, delegating to `DraftWorkflow`.

This layer is a migration boundary only. Individual context, evidence, planning,
candidate, validation, revision, final-gate, and HITL services still live in the
legacy modules until their owning slices move them.

## Evidence Interpretation Safety

Implemented in Slice 2.17.4.6.0.3.1:

- `TimedOperationRunner` gives provider-heavy attempts an operation-level timeout
  envelope so a blocked provider call does not leave `rulePack` running forever.
- `EvidenceInterpretationPayloadCompactor` sends the strategy model a bounded
  evidence/contract/relevant-rule subset while preserving full artifacts on the
  parent DraftRun.
- Legacy `EvidenceInterpretationService` records timeout attempts as failed child
  `AiRun` records, fails the nested progress operation, then proceeds through the
  existing repair/backup/deterministic fallback path.
