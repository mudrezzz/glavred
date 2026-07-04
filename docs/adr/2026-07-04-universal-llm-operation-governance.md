# ADR: Universal LLM Operation Governance

Date: 2026-07-04

## Status

Accepted

## Context

DraftRun, HITL revision, and future upstream/radar workflows all run provider-heavy
operations. Before this slice, each operation recorded attempts, fallback, and
provider errors in local shapes. That made diagnostics hard: a failed generated post
could show `fallbackUsed=true`, malformed JSON, a timeout, or no run at all without a
shared incident class or payload budget evidence.

## Decision

Introduce `backend/app/shared/llm_operations` as the provider-neutral contract layer
for LLM/provider-heavy operations. The shared contract defines:

- `LlmOperationEnvelope` / `JsonOperationEnvelope`;
- `LlmOperationAttempt` and `LlmOperationResult`;
- `LlmOperationIncident` with incident taxonomy;
- `LlmOperationInputStats`, `LlmOperationTimeoutProfile`, and
  `LlmOperationRetryPolicy`;
- an explicit inventory/allowlist for current provider-heavy operations.

The envelope serializes a trace-safe payload with `operationId`, `operationKind`,
`owner`, `status`, `attempts`, `aiRunIds`, `inputStats`, `payloadStats`,
`retryPolicy`, `timeoutProfile`, `incident`, `safeError`, and `resultPayload`.

Fallback, not-run, failed, timeout, cancelled, and stale outcomes require incident
metadata. Backup success is represented with `backupAccepted` incident metadata while
preserving an accepted result payload. Not-configured provider paths must be visible
as `notRun` where no domain-safe deterministic fallback exists.

`backend/app/drafting/application/operations/json_contracts.py` remains a thin
compatibility re-export so existing imports keep working during migration.

## Consequences

- New bounded-context provider-heavy code must use the shared envelope or be added to
  the explicit inventory with owner, reason, removal slice, and expected incident
  coverage.
- Diagnostics can classify `providerTimeout`, `networkError`, `provider4xx`,
  `provider5xx`, `malformedJson`, `schemaFailure`, `payloadTooLarge`,
  `contextOverBudget`, `deterministicFallback`, `backupAccepted`, `notConfigured`,
  `staleOperation`, `cancelled`, `workerFailure`, and
  `unknownProviderFailure`.
- Architecture smoke blocks new raw `complete_json(...)` calls in bounded contexts
  and checks that shared governance docs/contracts stay present.
- This slice migrates representative operations only: evidence interpretation,
  editorial critique, directed revision, HITL revision, and HITL quality check.
  Other current operations remain in the allowlist until their owning migration
  slices.
