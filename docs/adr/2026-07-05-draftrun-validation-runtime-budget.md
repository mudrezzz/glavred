# ADR: DraftRun validation loop uses runtime budget guard

## Status

Accepted

## Context

DraftRun validation can legitimately run for many minutes because it may execute LLM
validation, editorial critique, alternative-angle generation, pairwise ranking,
directed revisions, regression checks, and final quality review. A fixed short stale
threshold misclassifies healthy background work as stuck, while an unbounded loop can
hide provider failures or repeated non-improving revisions.

## Decision

The validation stage has a DraftRun-local runtime budget guard. It records
`runtimeBudget` in the existing validation step artifact progress payload, not in new
SQLite columns or API response fields. The guard tracks wall-clock time, LLM calls,
revision cycles, pairwise rounds, final-gate repair cycles, consecutive
non-improving attempts, current operation, heartbeat timestamps, incidents, and
canonical stop reasons.

The canonical validation stop reasons are `acceptedQuality`,
`humanReviewRequired`, `budgetExhausted`, `maxIterations`, `noImprovement`, and
`providerIncident`. Legacy internal reasons remain as detail metadata when useful.

## Consequences

- Long validation is healthy while operation progress stays inside the runtime
  budget.
- Staleness diagnostics inspect validation `runtimeBudget` before marking a running
  DraftRun stuck.
- Validation and revision loops cannot continue without budget accounting.
- The slice does not change prompt text, model selection, DraftRun step order,
  endpoint contracts, or SQLite schema.

## Alternatives considered

- Add a global worker watchdog only. Rejected for this slice because diagnostics need
  operation-level budget semantics inside validation artifacts.
- Add new API fields. Rejected because the existing step artifact payload already is
  the trace surface.
- Stop validation at a short interactive timeout. Rejected because background DraftRun
  execution is allowed to be slow when progress is visible.
