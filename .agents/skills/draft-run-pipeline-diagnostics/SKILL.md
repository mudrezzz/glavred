---
name: draft-run-pipeline-diagnostics
description: Use when diagnosing a Glavred DraftRun or AI drafting pipeline result by run id, especially when the user asks why a generated post is bad, stuck, generic, source-free, over-sourced, selected incorrectly, or whether the pipeline should continue as planned.
---

# Draft Run Pipeline Diagnostics Skill

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
6. Compare actual trace to `DRAFT_RUN_PIPELINE_AS_IS.md` first, then to expected
   slice behavior in `ROADMAP.md`.
7. Decide one of:
   - behavior is acceptable for current slice, continue plan;
   - bugfix slice is needed before continuing;
   - roadmap slice should be amended because the architecture assumption was wrong.

## Diagnostic Checklist

Check these failure classes explicitly:

- **Execution**: run missing, failed, stale, pending steps, missing child `AiRun`.
- **Provider**: OpenRouter error, malformed JSON, timeout, fallbackUsed, partial branch failure.
- **Research**: source intent absent, research plan too vague, search disabled,
  failed URL/search attempts, irrelevant accepted citations, accepted evidence not
  synthesized into `EvidenceSynthesis`, or external claims missing from enriched
  `SourceLedger`.
- **Quality spine**: SourceLedger missing usable claims, feasibility incorrectly blocked
  or passed, PostContract too weak, RuleRegistry lacks enforceable rules.
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
