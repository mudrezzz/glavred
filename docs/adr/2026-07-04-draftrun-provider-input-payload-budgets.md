# ADR: DraftRun provider-input payload budgets

## Status

Accepted

## Context

DraftRun artifacts are intentionally rich: they preserve source ledgers, rule
registries, validation reports, revision traces, and child `AiRun` audits. That is
useful for diagnostics, but it is unsafe as provider input. A provider-heavy LLM
operation needs the semantic subset for its job, not the full accumulated artifact
dump.

Slice 2.17.4.6.0.3.2 introduced the universal LLM operation envelope and incident
taxonomy. The next missing boundary is the input budget immediately before prompt
message construction.

## Decision

DraftRun LLM operations must use a named provider-input payload budget policy or be
listed as a debt exception in `CURRENT_LLM_OPERATION_INVENTORY`.

The DraftRun-owned policy layer lives under
`backend/app/drafting/application/operations/`:

- `PayloadBudgetProfile` defines operation id, operation kind, execution mode, prompt
  character cap, approximate token budget, and count caps for rules, claims,
  evidence, candidates, source snippets, and prior drafts.
- `SemanticInputContract` separates `mustHave`, `shouldHave`, `diagnosticOnly`, and
  `neverSendToProvider` inputs.
- `PayloadBudgetResult` returns compact provider input plus `inputStats`,
  `payloadStats`, trimmed/suppressed metadata, quality risk, and an optional incident.

The full artifacts remain in parent DraftRun storage and trace. Only the provider
request payload is curated. The policy is applied immediately before
`build_*_messages(...)`, not inside OpenRouter adapters.

Representative enforced operations in this slice are:

- `evidenceInterpretation`;
- `editorialCritique`;
- `directedRevision`;
- `humanCommentRevision`;
- `humanCommentRevisionQualityCheck`.

Other current provider-heavy operations remain explicit payload-budget debt until
their owning migration slice wires the same policy into runtime.

## Consequences

- Child `AiRun.requestPayload`, attempts, and nested `operationEnvelope.payloadStats`
  can show what was sent, what was trimmed, and why.
- `promptCharEstimate` and `approxTokenEstimate = ceil(chars / 4)` are available for
  diagnosis without changing public API contracts or SQLite schema.
- Over-budget compacted inputs record `contextOverBudget`; hard-cap breaches record
  `payloadTooLarge`.
- Quality regressions from over-trimming become visible through `qualityRisk` and
  trimmed counts instead of being hidden in generic model output.

## Alternatives considered

- Tune every prompt manually. Rejected because the problem is an architectural input
  boundary, not prompt prose quality.
- Trim inside the provider adapter. Rejected because adapters do not know DraftRun
  semantic contracts and would hide what was trimmed from operation traces.
- Migrate every provider-heavy operation in one slice. Rejected because it would mix a
  guardrail boundary with broad behavior migration. Debt entries keep the remaining
  operations explicit.
