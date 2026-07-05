# Drafting Backend Component Map

Current status: migration map and migrated runtime clusters for the
`backend/app/drafting` bounded context.

Use `docs/developer/BACKEND_MODULE_TEMPLATE.md` with this map. The template defines
the ownership header, service/policy/component/DTO roles, migrated thin shim rule,
and Provider-Heavy Review Checklist for shared operation governance, payload
budgets, runtime budgets, safe errors, and no raw provider calls. Keep this map and
`npm run test:architecture` aligned when package owners move.

This file is the implementation guide for moving legacy DraftRun modules in small,
behavior-preserving slices. The context/artifact, source/evidence,
evidence-contract, and planning clusters were migrated in Slice 2.17.4.6.0.4.
Candidate generation, validation, ranking/revision, final quality, and HITL were
migrated in Slice 2.17.4.6.0.5. Old flat paths remain compatibility shims only.
Legacy files are classified as active compatibility facade, migrated thin shim, or
remaining explicit debt; there is no fourth informal status for behavior hidden in a
legacy path.

Package migration did not automatically remove all internal procedural debt. Slice
2.17.4.6.0.7 adds the Backend Architecture Audit and Debt Ledger before more broad
backend feature work. The audit classifies public helper sprawl, procedural bounded
packages, raw dict contracts, provider boundary leaks, dependency-direction risks,
migrated-shim behavior, and tests that still mirror legacy owners. Run
`python scripts/backend-architecture-audit.py --format json --ledger
docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high`.
Known debt is in `docs/architecture/backend-architecture-debt-ledger.json`; the
current snapshot is `docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md`.

## Package Areas

| Target area | Owns | Legacy source clusters |
| --- | --- | --- |
| `domain` | Provider-free DraftRun entities, step keys, artifact DTOs, validation DTOs. | `backend/app/domain/draft_*.py` |
| `application/workflow` | Draft workflow sequencing, step registry, workflow state, progress handoff. `DraftWorkflow`, `DraftWorkflowState`, `DraftWorkflowPhase`, and `DraftStepRegistry` now own the behavior-preserving orchestration shell while legacy step services remain in place. | `draft_run_pipeline.py`, `draft_run_progress.py`, `draft_run_step_progress.py`, `draft_run_service.py` |
| `application/steps` | Step-level use cases with stable input/output contracts. `contracts.py` defines `DraftStepContext`, `DraftStepTrace`, `DraftStepOutcome`, and the `DraftStep` protocol. `legacy_adapters.py` converts the first legacy result shapes without changing runtime behavior. | context, source intent, public evidence, feasibility, rule pack, material plan, strategy, rhetorical plans, draft, validation |
| `application/operations` | Drafting compatibility imports and bounded operation helpers. `json_contracts.py` re-exports the shared `backend.app.shared.llm_operations` contract (`LlmOperationEnvelope`, `JsonOperationEnvelope`, attempts, incidents, input stats, retry policy, timeout profile). `json_step_adapter.py` is the bounded JSON provider-call adapter for migrated services. `timeout.py` and `evidence_interpretation_payload.py` protect the evidence-interpretation operation during migration. DraftRun provider-input budgets are role-owned by `payload_budget_contracts.py`, `payload_budget_profiles.py`, `payload_semantic_contracts.py`, `payload_compactors.py`, `payload_budget_policy.py`, and `payload_budget_runtime.py`; `payload_budget.py` is compatibility-only. `validation_runtime_budget.py` owns validation-loop runtime caps, heartbeat snapshots, counters, and canonical stop reasons. | `backend.app.shared.llm_operations`, `json_step_retry_policy.py`, provider-heavy drafting services after adapter split |
| `application/migration` | Planning-only migration inventories. `legacy_surface_inventory.py` records the Legacy DraftRun Surface, `moduleDisposition`, `publicHelperDisposition`, target owners, and the `no cosmetic package moves` rule for `draft_*` and `deterministic_*` modules. | `backend/app/application/draft_*.py`, `backend/app/application/deterministic_*.py` |
| `application/artifacts` | Context/run payloads, run budget resolution, source ledger assembly/sections, article dossier, article memory, and context pack building. | migrated context/source-ledger/article-memory modules |
| `application/evidence` | Source intent and research planning, public evidence retrieval/merge/synthesis, feasibility, post contract, rule registry, rule pack, evidence interpretation, and deterministic evidence fallbacks. | migrated source/evidence/contract/rule modules |
| `application/planning` | Material plan retry orchestration, material projection/accountability, strategy, rhetorical plans, planning audit/result/prompt helpers, and deterministic planning/rhetorical fallback owners. | migrated material/strategy/rhetorical modules |
| `application/generation` | Candidate direction, generation, provider execution, selection, publishability, candidate audit/prompts/results, alternative-angle challenger writing, deterministic candidate fallback, generation params, and prompt builder. | migrated candidate-generation modules |
| `application/validation` | Deterministic linter/evidence/attribution checks, LLM validation, editorial critique, validation report and alternative-angle route/tournament orchestration, validation step service, and operation safety. | migrated validation and alternative-angle orchestration modules |
| `application/revision` | Pairwise ranking, directed revision, ranking-revision orchestration, revision loop, revision policies, regression checks, rejected moves, and deterministic pairwise fallback. | migrated ranking/revision modules |
| `application/final_quality` | Final quality contract, deterministic assessment, final gate/evaluator/payloads, independent review, final repair loop, and parser/prompts/service. | migrated final quality modules |
| `application/hitl` | Human-comment revision and human-comment revision quality check services. | migrated HITL modules |
| `infrastructure` | Drafting-specific infrastructure wiring and adapters when they cannot stay in root infrastructure. | Celery DraftRun wiring and provider factory wiring after ports exist |

## Migration Order

1. Keep this skeleton stable and add compatibility imports.
2. Introduce `DraftStep` and JSON operation contracts. Done in Slice 2.17.4.6.0.2.
3. Move `DraftRunPipeline` behind `DraftWorkflow` and `DraftStepRegistry`. Done in Slice 2.17.4.6.0.3.
4. Repair `EvidenceInterpretation` timeout/payload behavior before migrating planning.
   Done in Slice 2.17.4.6.0.3.1.
5. Add shared LLM operation envelope, incident taxonomy, payload stats, and provider
   operation inventory. Done in Slice 2.17.4.6.0.3.2.
6. Add DraftRun provider-input payload budget policies. Done in Slice
   2.17.4.6.0.3.3.
7. Split the initial payload budget policy surface into role-owned architecture.
   Done in Slice 2.17.4.6.0.3.3.1.
8. Add validation/revision runtime budget guard and canonical stop reasons. Done in
   Slice 2.17.4.6.0.3.4.
9. Classify the Legacy DraftRun Surface before package moves. Done in Slice
   2.17.4.6.0.4.0. The inventory covers every current flat `draft_*` and
   `deterministic_*` application module, every public helper, `moduleDisposition`,
   `publicHelperDisposition`, target owner, and migration slice.
10. Move context, source ledger, feasibility, post contract, rule pack, and planning
   clusters. Done in Slice 2.17.4.6.0.4. Old paths remain thin shims and canonical
   imports point to `application/artifacts`, `application/evidence`,
   `application/planning`, and `application/operations`.
11. Move candidate, validation, ranking, revision, final quality, and HITL clusters.
    Done in Slice 2.17.4.6.0.5. Old paths remain thin shims and canonical imports
    point to `application/generation`, `application/validation`,
    `application/revision`, `application/final_quality`, and `application/hitl`.
12. Tighten architecture smoke allowlists after each cluster is moved. Done for the
    moved DraftRun application clusters; remaining follow-up is retiring legacy
    shims when external compatibility is no longer needed.
13. Add Backend Architecture Audit and Debt Ledger. Done in Slice 2.17.4.6.0.7.
14. Clean migrated validation, revision/final-quality, HITL/provider, and remaining
    backend surfaces according to the audit ledger. Planned in Slices
    2.17.4.6.0.8 through 2.17.4.6.0.11.

Package moves after step 9 must be owner moves, not `no cosmetic package moves`.
Behavior becomes service, policy, or component methods; small provider-free DTO
factory helpers may remain package-level only when explicitly listed.

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

This layer is a migration boundary only. Context, evidence, planning, generation,
validation, revision, final-gate, and HITL services now have canonical owners under
`backend.app.drafting.application`. Legacy application paths for moved modules are
thin import/re-export shims.

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

## Universal LLM Operation Governance

Implemented in Slice 2.17.4.6.0.3.2:

- `backend.app.shared.llm_operations` owns `LlmOperationEnvelope`,
  `JsonOperationEnvelope`, `LlmOperationAttempt`, `LlmOperationResult`,
  `LlmOperationIncident`, `LlmOperationInputStats`, `LlmOperationTimeoutProfile`,
  and `LlmOperationRetryPolicy`.
- `backend.app.drafting.application.operations.json_contracts` is compatibility-only
  and re-exports the shared contract.
- Representative migrated operations now record `operationEnvelope` or an equivalent
  nested shared envelope payload: `evidenceInterpretation`, `editorialCritique`,
  `directedRevision`, `humanCommentRevision`, and
  `humanCommentRevisionQualityCheck`.
- Current unmigrated provider-heavy operations are explicitly listed in
  `CURRENT_LLM_OPERATION_INVENTORY` with owner, current module, operation kind,
  migration status, reason not migrated, removal slice, and expected incident
  coverage.

## Provider-Input Payload Budgets

Implemented in Slice 2.17.4.6.0.3.3:

- `PayloadBudgetProfile`, `SemanticInputContract`, and `PayloadBudgetResult` define
  DraftRun provider-input budgets separately from rich artifact storage.
- `payloadBudget` trace metadata records profile id, execution mode, limits,
  sent/trimmed counts, suppressed fields, semantic inputs, quality risk,
  `promptCharEstimate`, and `approxTokenEstimate`.
- Representative enforced operations are `evidenceInterpretation`,
  `editorialCritique`, `directedRevision`, `humanCommentRevision`, and
  `humanCommentRevisionQualityCheck`.
- Remaining provider-heavy operations stay explicit payload-budget debt entries in
  `CURRENT_LLM_OPERATION_INVENTORY` until their owning migration slice wires the same
  boundary at runtime.
