---
name: draft-run-pipeline-autofix
description: Use when asked to run a Glavred DraftRun, diagnose it against the current ROADMAP.md expectations, decide whether issues are already covered by upcoming roadmap slices, automatically implement small non-architectural repair patches, and repeat the run/fix cycle up to a bounded limit. Triggers include "прогони и сам исправь", "pipeline autofix", "запусти диагностику с автокоррекцией", "сам прогони, сравни с roadmap и исправь", or similar requests.
---

# Draft Run Pipeline Autofix Skill

## Goal

Run a bounded quality loop for the Glavred drafting pipeline:

1. launch a fresh `DraftRun`;
2. wait for completion or stale/failure;
3. diagnose the trace;
4. compare the result with `ROADMAP.md`;
5. either report that the issue is already expected, implement a small repair patch,
   or stop with an architecture/roadmap-change report.

Use this skill only when the user explicitly wants the agent to both run and repair
the pipeline. For a single run without repairs, use `$draft-run-pipeline-evaluation`.
For an existing run id, use `$draft-run-pipeline-diagnostics`.

## Hard Limits

- Maximum correction cycles: **5**.
- Do not silently exceed the loop limit. If the fifth cycle still fails, report the
  remaining issue and recommend the next slice.
- Do not implement architectural shifts inside this skill. Stop and write a roadmap
  correction proposal instead.
- Do not call `/api/drafts/generate` as a timeout fallback for a live `DraftRun`.
- Do not commit or push unless the user explicitly asks.

## Required Inputs

Use the current application state by default. If the task needs a specific post,
ask the user only when the target cannot be inferred from the UI/workspace.

Before the first run, inspect:

- `git status --short --branch`;
- `ROADMAP.md`;
- current backend health;
- whether frontend/backend/worker/Redis are reachable.

## Cycle Workflow

Repeat the following until accepted, blocked by architecture scope, or 5 cycles are
used.

### 1. Launch And Wait

Use `$draft-run-pipeline-evaluation` workflow:

- launch a fresh `DraftRun` through the UI when practical, or through
  `POST /api/draft-runs` when a valid prepared payload is available;
- capture the parent `DraftRun ID`;
- wait using:
  `python .agents/skills/draft-run-pipeline-evaluation/scripts/wait_for_draft_run.py <DraftRun ID>`;
- never replace a live queued/running run with compatibility generation.

### 2. Diagnose

Use `$draft-run-pipeline-diagnostics` workflow:

- run:
  `python .agents/skills/draft-run-pipeline-diagnostics/scripts/analyze_draft_run.py <DraftRun ID>`;
- inspect SQLite directly when the helper does not expose enough detail;
- inspect only implicated code and docs.

### 3. Compare With Roadmap

Classify every problem:

- **Expected roadmap gap**: the problem is already explicitly covered by the next
  planned slice or a nearby backlog item.
- **Small implementation defect**: bug, missing trace surface, wrong fallback,
  prompt/normalizer bug, minor UI trace issue, missing test/docs update.
- **Architecture shift**: requires changing pipeline shape, adding new durable
  storage, new provider category, new product flow, new data ownership, or changing
  accepted architecture decisions.

### 4. Decide

Use this decision table:

- If the result matches current slice expectations, stop and report success.
- If defects are real but already covered by upcoming roadmap slices, stop and
  report the run result plus the exact roadmap slice that should address them.
- If defects are small and not covered, implement a narrow patch in the current
  branch:
  - update code;
  - add/update tests;
  - update `ROADMAP.md`, SAO, developer/user/demo docs as needed;
  - run targeted and relevant regression checks;
  - start the next cycle.
- If defects imply an architecture shift, do not patch. Write a concise report with:
  - observed run id and symptoms;
  - why the current roadmap cannot absorb it;
  - proposed roadmap adjustment;
  - affected docs/ADR areas.

## Patch Discipline

When implementing small repairs:

- Keep the patch scoped to the diagnosed defect.
- Prefer role-owned modules over growing near-limit files.
- Preserve current `DraftRun` contracts unless the user explicitly approved a new
  slice that changes them.
- Update architecture smoke baselines only for real new files or intentional limits.
- Add a roadmap note for the repair, either as a small repair slice or as a result
  note under the active slice.
- Run at minimum:
  - targeted tests for touched code;
  - `npm run test:architecture`;
  - `git diff --check`.
- Run broader regression when the patch touches shared pipeline behavior or UI trace.

## Final Report

Answer in Russian unless asked otherwise. Include:

- number of cycles used;
- all created `DraftRun ID`s;
- final status and quality judgment;
- whether issues were expected, fixed, or escalated;
- patches made, files/docs touched, and tests run;
- remaining risks and the next roadmap slice.

If the loop stops because the issue is already covered by roadmap, say that clearly
and do not implement duplicate work.
