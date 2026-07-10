# ADR: DraftRun Provider Input Dossier Boundary

## Status

Accepted

## Context

Live DraftRun diagnostics showed that slow or unstable provider-heavy operations
are not isolated to `materialPlan`. Several operations send very large prompt
inputs:

- `pairwiseRanking`: up to 626449 characters;
- `materialPlan`: up to 346264 characters;
- `draftCandidate`: up to 328276 characters;
- `alternativeAngleRoute` and `alternativeAngleCandidate`: above 320000
  characters;
- `llmValidation`: above 255000 characters.

The existing payload-budget layer is enforced only on representative operations.
Some child `AiRun` records contain nested `payloadBudget` data from earlier
artifacts, but the current provider call itself has no direct budget boundary.

This makes provider behavior slower, less predictable, and harder to diagnose. It
also weakens prompt focus because models receive full artifacts where they need a
task-specific working set.

## Decision

DraftRun provider-heavy operations must receive operation-specific provider-input
dossiers instead of raw full DraftRun artifacts.

The target flow is:

`DraftRun artifacts -> DraftRunContextAccessService -> DossierFactory -> ProviderInputBudgetGate -> PromptBuilder -> Provider`

Key rules:

- parent DraftRun artifacts remain rich and trace-visible;
- provider request payloads are compact projections;
- every provider-heavy child `AiRun` must show a direct `payloadBudget.profileId`
  or an explicit temporary debt entry;
- prompt builders must not receive full `rulePack`, `SourceLedger`,
  `materialPlan`, candidate pool, validation report, or final quality trace by
  default;
- context access is deterministic and provider-free;
- a future MCP/tool adapter may call the deterministic context service, but must not
  expose raw full DraftRun JSON to the model.

The implementation track is recorded in roadmap slices
`2.17.4.6.1.3.4` through `2.17.4.6.1.3.10`.

Slice `2.17.4.6.1.3.6` implements the deterministic boundary itself:

- provider-free `DraftRunContextAccessService`;
- typed planning, writer, review, ranking, revision, and final-quality dossiers;
- stable handles and controlled full-artifact resolution;
- explicit readiness, missing-required-input, trimming, suppression, and quality-risk
  fields;
- provider-free replay that refuses to claim runtime migration.

Actual prompt-builder/provider call sites remain separate migrations in slices
`2.17.4.6.1.3.7` through `2.17.4.6.1.3.9`.

## Consequences

Positive:

- provider inputs become bounded and explainable;
- runtime diagnostics can distinguish queue wait, provider wait, over-budget input,
  and model failure;
- prompt builders become smaller and more role-owned;
- later MCP/tool access has a deterministic backend to call;
- full diagnostic artifacts remain available without being sent wholesale to the
  provider.

Trade-offs:

- each operation needs explicit dossier tests to prove required information is not
  lost;
- initial migrations may expose quality assumptions that were previously hidden by
  large prompts;
- the first implementation slices must focus on trace and budget enforcement before
  reducing context aggressively.

## Alternatives considered

1. Increase model timeouts.
   Rejected as the primary fix. It hides the symptom and does not reduce context
   noise or cost.

2. Switch to larger-context models.
   Rejected as the primary fix. It makes the system more expensive and still leaves
   prompt focus uncontrolled.

3. Trim prompts manually per file.
   Rejected as the architectural answer. It would create one-off cuts without a
   reusable access and dossier boundary.

4. Add MCP immediately.
   Deferred. MCP or tool-calling can be useful, but it should wrap a deterministic
   context service. Without that service it would become another path to the same
   unbounded artifact dump.
