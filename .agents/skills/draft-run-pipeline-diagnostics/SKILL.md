---
name: draft-run-pipeline-diagnostics
description: Use when diagnosing a Glavred DraftRun or AI drafting pipeline result by run id, especially when the user asks why a generated post is bad, stuck, generic, source-free, over-sourced, selected incorrectly, or whether the pipeline should continue as planned.
---

# Draft Run Pipeline Diagnostics Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Diagnose one Glavred drafting run with the same method every time, using local
SQLite trace data and current pipeline code. The output must explain what happened,
why the result is good or bad, what should be fixed, and whether the roadmap should
continue unchanged or get an intermediate repair slice.

## Inputs

Require one of:

- parent `DraftRun ID`;
- child `AiRun ID`, then find or ask for the parent `DraftRun ID` when the pipeline
  decision depends on sibling calls.

Do not diagnose from screenshots alone when a run id is available.

## Standard Workflow

1. Inspect repo state:
   - `git status --short --branch`
   - note whether there are uncommitted pipeline changes that may affect the run.
2. Read `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` to establish the current
   expected pipeline shape before judging the trace.
   For backend/DraftRun architecture drift, also read
   `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`,
   `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`,
   `backend/app/drafting/README.md`,
   `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`, and
   `docs/developer/BACKEND_MODULE_TEMPLATE.md`.
3. Extract run trace with the helper script:
   - `python .agents/skills/draft-run-pipeline-diagnostics/scripts/analyze_draft_run.py <DraftRun ID>`
4. If the helper reports missing or ambiguous data, query SQLite directly:
   - parent DB: `var/glavred-draft-runs.sqlite3`
   - child AI DB: `var/glavred-ai-runs.sqlite3`
5. Inspect current code only for the components implicated by the trace:
   - source intent / public evidence;
   - source ledger / feasibility / post contract;
   - rule registry / material plan / strategy / rhetorical plans;
   - draft candidates / scoring / selection;
   - fallback behavior.
   - shared LLM operation envelopes and inventory:
     `backend.app.shared.llm_operations` and `CURRENT_LLM_OPERATION_INVENTORY`.
   Prefer the canonical package owner under `backend/app/drafting` for migrated
   DraftRun code. A legacy `backend/app/application/*` file may be an active
   compatibility facade, migrated thin shim, or remaining explicit debt; behavior in
   a migrated thin shim is a guardrail bug, not the owner to patch.
6. Compare actual trace to `DRAFT_RUN_PIPELINE_AS_IS.md` first, then to expected
   slice behavior in `ROADMAP.md`.
7. Decide one of:
   - behavior is acceptable for current slice, continue plan;
   - bugfix slice is needed before continuing;
   - roadmap slice should be amended because the architecture assumption was wrong.

## Diagnostic Checklist

Check these failure classes explicitly:

- **Execution**: run missing, failed, stale, pending steps, missing child `AiRun`.
- **Provider**: OpenRouter error, malformed JSON, timeout, fallbackUsed, partial branch
  failure. For JSON-producing LLM steps, verify `primary`, `primary-repair`, and
  optional `backup` attempts before accepting fallback/not-run/failed as expected.
  A successful same-model retry or repair attempt is normal recovery, not a result
  quality failure. Backup model success is accepted but diagnostic. Deterministic
  fallback lowers fidelity only where the owning step already has a domain-safe
  fallback.
  For local live diagnostics, take OpenRouter configuration from `.env` without
  printing secret values. Do not report "missing key" merely because Docker was not
  running or another project's containers were active; start the Glavred compose stack
  when needed and diagnose the actual provider/runtime response.
  Inspect `generationParams` (`generationParamProfile`, `temperature`, `topP`) for
  writer, revision, JSON repair, and another-angle calls before judging model quality.
  For migrated operations, inspect `operationEnvelope`, `incident`, `inputStats`,
  `payloadStats`, `retryPolicy`, and `timeoutProfile`. Classify failures by
  `incidentType`: `providerTimeout`, `networkError`, `provider4xx`, `provider5xx`,
  `malformedJson`, `schemaFailure`, `payloadTooLarge`, `contextOverBudget`,
  `deterministicFallback`, `backupAccepted`, `notConfigured`, `staleOperation`,
  `cancelled`, `workerFailure`, or `unknownProviderFailure`.
  When `payloadStats.payloadBudget` exists, verify `profileId`, execution mode,
  prompt char estimate, approx token estimate, sent/trimmed counts, suppressed
  fields, semantic inputs, and `qualityRisk` before blaming the model. If
  `contextOverBudget` or `payloadTooLarge` repeats, scan the inventory for other
  operations with the same `budgetPolicyId` or `payloadBudgetStatus=debtAllowlisted`
  and escalate a payload-boundary slice when the pattern is systemic.
- **Research**: source intent absent, research plan too vague, search disabled,
  failed URL/search attempts, irrelevant accepted citations, accepted evidence not
  synthesized into `EvidenceSynthesis`, or external claims missing from enriched
  `SourceLedger`.
- **Quality spine**: SourceLedger missing usable claims, feasibility incorrectly blocked
  or passed, PostContract too weak, RuleRegistry lacks enforceable rules.
- **Quality/Fidelity verdict**: inspect `qualityFidelity` in
  `validation.rankingRevision` and `complete`. Treat `DraftRun.status=succeeded` as
  technical completion only. Use `technicalStatus`, `providerRecoveryStatus`,
  `evidenceFidelity`, `issueLifecycle`, `editorialStatus`, and `overallVerdict` to
  decide whether the result is clean, recovered, degraded, or needs attention.
  Every validation or final-gate warning/critical issue should have lifecycle status
  `resolved`, `suppressed`, `acceptedRisk`, or `open`. `open critical` means quality
  cannot be trusted. `finalGateWarning` means the result is at most
  `publishableWithCaution` unless the trace shows explicit resolution, suppression,
  or accepted-risk semantics.
- **Cross-run provider reliability**: when the question is whether retries, backup,
  fallback, malformed JSON, timeout, schema failure, payload-budget, or open critical
  signals are systemic, run
  `python scripts/analyze_draft_run_reliability.py --run-id <DraftRun ID> --run-id <DraftRun ID>`.
  One run can prove what happened, but it is `insufficientData` for systemic
  conclusions. The report's remediation ledger must map every non-clean signal to
  no action, watch, existing slice, backlog fix, fix before trusting quality, or
  manual review. Also inspect `signalCoverage`: every child `AiRun`, operation
  envelope incident, retry, backup, fallback, payload/runtime budget incident, or
  stats-only ignored budget payload must be covered or ignored with a concrete
  reason. `fixBacklogSlice` and `fixBeforeTrustingQuality` entries must point to
  concrete roadmap slices, not placeholders.
- **Planning**: material plan ignores public evidence, `usableEvidenceCandidates`
  missing, `availableEvidence` empty without `rejectionReasons`, repair/backup attempts
  absent, emergency fallback used too early, strategy is generic, rhetorical plans do
  not differ meaningfully, size contract ignored.
- **Drafting**: candidates are generic, technical artifacts leak into prose, raw JSON or
  Python object dumps appear, citations are stuffed in mechanically, source names are
  used without synthesized claims.
- **Selection**: fallback candidate selected over viable provider candidate, identical
  scores, scoring ignores readability/source/fallback, selected candidate contradicts
  trace warnings, scorecard publishability fields missing or showing unexpected
  `eligible / penalized / excluded` decisions.
- **UI/trace**: trace hides the important decision, scorecard unreadable, missing
  DraftRun ID, child runs not linked.
- **HITL revisions**: human-comment revision created a version without
  `qualityCheck`, quality check is `notRun` without attempts, missed comment intents
  are hidden, source markers regressed, internal pipeline jargon leaked into the
  public version, or warnings are treated as blocking when they should be diagnostic.
- **Incident blast radius**: if the same `incidentType` repeats across attempts,
  candidates, or steps, scan `CURRENT_LLM_OPERATION_INVENTORY` for migrated and
  allowlisted operations with the same expected incident coverage. Escalate an
  architecture/guardrail slice when the pattern is systemic rather than isolated to
  one prompt or provider response.
- **Slow background vs stuck**: treat a run as slow-but-alive when timestamps,
  progress operations, or child `AiRun` creation continue to advance. Treat it as
  stuck only when the parent step has no progress past the expected operation budget
  and no timeout/stale/cancelled incident or worker error explains the delay.
  For `validation`, inspect `progress.runtimeBudget`: profile id, execution mode,
  limits, used counters, `lastHeartbeatAt`, `currentOperationId`,
  `currentOperationStartedAt`, `slowButHealthy`, `stopReason`, `exhausted`, and
  incidents. A validation run is slow-but-alive when the current operation age is
  inside `runtimeBudget.limits.staleAfterSeconds`; it is stuck when that operation
  exceeds the runtime stale budget without a `budgetExhausted`, `providerIncident`,
  `staleOperation`, `cancelled`, or worker failure explanation.
- **Validation stop reason**: read canonical `revisionLoop.stopReason` and
  `finalDecision.stopReason` before judging outcome. Expected values are
  `acceptedQuality`, `humanReviewRequired`, `budgetExhausted`, `maxIterations`,
  `noImprovement`, and `providerIncident`; use `detailStopReason` for legacy local
  details such as `editorially-improved`, `no-fresh-angle`, or provider failure text.

## Output Format

Answer in Russian unless the user asks otherwise.

Use this structure:

1. **Короткий вывод**: one paragraph with the main diagnosis.
2. **Что произошло по шагам**: concise ordered list from trace.
3. **Что пошло не так**: concrete root causes, not vague quality comments.
4. **Почему это произошло**: link symptoms to current code/pipeline behavior.
5. **Что исправляем**: smallest next slice or exact roadmap adjustment.
6. **Что не является багом**: only if something is expected for the current slice.
7. **Как проверить после фикса**: repeatable run/trace checks.

Prefer concrete ids, step names, error strings, candidate ids, and scores. Do not
hide bad output behind polite abstractions.

## Rules

- Do not treat planned search tasks as proof. Only accepted public evidence or ledger
  claims can support drafting.
- When public evidence exists, check `EvidenceSynthesis` and enriched
  `SourceLedger`; raw snippets alone are not enough to prove downstream grounding.
- When enriched ledger has usable claims, `MaterialPlan` must show selected evidence
  or explicit rejection reasons, plus retry attempts before deterministic fallback.
- Any JSON-producing provider step must follow ADR
  `2026-06-27-llm-json-steps-use-universal-retry-policy`: primary role model,
  repair prompt, optional backup model, then explicit domain-safe fallback/not-run/
  failed. A single malformed JSON response is not enough to declare a branch failed.
- For migrated provider-heavy operations, never diagnose from `fallbackUsed` alone.
  Read the shared `operationEnvelope`: operation status, attempts, child `AiRun` ids,
  incident taxonomy, safe error, timeout profile, retry policy, and payload/input
  stats. Fallback/not-run/failed/timeout/cancelled/stale without incident metadata is
  a guardrail bug.
- For enforced payload-budget operations, inspect `payloadBudget` in the child
  `AiRun.requestPayload`, the attempt, and `operationEnvelope.payloadStats`. Full
  `ruleRegistrySnapshot`, full `sourceLedger`, full validation reports, full
  candidate pools, or full revision traces in provider messages without a matching
  budget profile are architecture bugs.
- Backup success is not silent success. It is an accepted payload with
  `backupAccepted` incident metadata and should trigger a blast-radius check if it
  repeats.
- Provider not configured should appear as `notRun` with `notConfigured` incident
  unless the operation already owns a domain-safe deterministic fallback; in that
  fallback case, verify the deterministic fallback incident and publication
  guardrails.
- If public prose contains internal names like `SourceLedger`, `publicEvidence`,
  `RuleRegistry`, `PostContract`, or `validators`, treat it as a writer/revision bug
  unless the text explicitly reframes the term for the reader.
- When diagnosing final quality, inspect
  `validation.rankingRevision.finalQualityGate` before judging the whole candidate
  pool. Check its `finalQualityContract`, independent model review attempts, repair
  goals, bounded repair cycles, accepted/rejected decisions, and final source. It
  shows whether the delivered final draft passed public-prose checks, whether a final
  repair ran, and why that repair was accepted or rejected. A rejected final repair
  is not silent failure: it must remain visible as a safety-preserving decision, and
  the unresolved warning/critical must remain visible in `qualityFidelity.issueLifecycle`.
- When a run has `qualityFidelity.providerRecoveryStatus=retryRecovered`, do not
  recommend prompt/model fixes from that single run unless the accepted payload is
  itself bad. Repeated retry/backup/fallback patterns across many runs belong to the
  provider reliability analytics report, not one-run quality diagnosis.
- For evidence interpretation, inspect `rulePack.evidenceInterpretationFidelity`
  before judging evidence quality. `retry-recovered` and `backup-accepted` are
  provider recovery signals; `deterministic-fallback`, `partial`, `weak`, or
  `missing` evidence fidelity are quality/follow-up signals.
- For attribution issues, distinguish actionable missing-source findings from
  diagnostic handoff noise. Inspect `finalQualityGate.attributionReview`,
  `actionableAttributionFindings`, `diagnosticAttributionNoise`, and finding metadata
  such as `expectedAttributionMarkers`, `matchedAttributionMarkers`,
  `resolvedClaimIds`, `unresolvedAttributionRequirements`, and `suppressedReason`.
  Empty expected markers or `evidence.attribution.diagnostic` are not prose-quality
  failures by themselves; they mean a material-plan attribution requirement could not
  be mapped to concrete claim provenance.
- For post-run human-comment revisions, inspect `PostDraft.versions[].qualityCheck`
  and the child `AiRun` with
  `requestPayload.draftRunStep = "humanCommentRevisionQualityCheck"`. The check is
  diagnostic, not blocking: `warning` or `critical` must be shown to the editor, while
  `notRun` means the version still exists but compliance could not be reviewed after
  retries.
- Do not accept emergency fallback text as publication-quality unless the trace proves
  all provider paths are unavailable and the fallback passed publishability checks.
- Read `selectionStatus`, `selectionPenalty`, `selectionReasons`, and `publishable`
  in draft scorecards before judging why a candidate won or was blocked.
- Do not recommend validators/revision before the quality spine has the required
  evidence/contract/rule artifacts for that run.
- Do not change code during pure diagnosis unless the user explicitly asks to implement
  a fix.
- If the issue is a roadmap gap, propose a small intermediate slice and keep the rest
  of the plan intact.
- If diagnostics implicate backend architecture, distinguish canonical package owner
  from legacy shim before recommending a fix. Behavior in a migrated thin shim,
  missing shared operation governance, raw provider calls in bounded packages, or
  missing `npm run test:architecture` coverage should be reported as a guardrail bug.
