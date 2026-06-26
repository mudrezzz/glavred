---
name: draft-run-pipeline-evaluation
description: Use when asked to run a fresh Glavred DraftRun end-to-end, generate or capture the DraftRun ID, wait for queued execution, then diagnose the whole drafting pipeline result. Triggers include "запусти тестовый DraftRun", "прогони pipeline evaluation", "сгенерируй DraftRun и оцени", "контрольный прогон генерации", or "сам запусти, дождись и проведи диагностику".
---

# Draft Run Pipeline Evaluation Skill

## Goal

Run one real drafting attempt and evaluate it. This skill changes product state and
may call OpenRouter/web search through the backend. Use it only when the user asks
for a fresh run, not when they only provide an existing `DraftRun ID`.

For existing ids, use `$draft-run-pipeline-diagnostics` directly.

## Workflow

1. **Preflight**
   - Run `git status --short --branch` and note uncommitted changes.
   - Check backend health: `Invoke-RestMethod http://localhost:8000/api/health`.
   - If the run will use the UI, confirm the frontend is reachable at the current app
     URL, usually `http://localhost:5176`.
   - If backend/worker/Redis are not running, diagnose infrastructure first. Do not
     treat missing services as a bad drafting result.

2. **Record baseline**
   - Record current time.
   - Optionally inspect latest rows in `var/glavred-draft-runs.sqlite3` so a new run can
     be identified if the UI does not expose the id.

3. **Start the run**
   - Preferred path: use the app UI in `Редактура -> Рабочий стол`.
   - Select the intended post.
   - Open `Фабула`.
   - Click `Утвердить фабулу`.
   - Capture the displayed `DraftRun ID` from the generation state, AI trace panel, or
     `/ai-runs` link.
   - If the user provides a prepared request payload, API launch through
     `POST /api/draft-runs` is allowed. Do not invent a full workspace payload from
     memory.

4. **Wait for completion**
   - Use:
     `python .agents/skills/draft-run-pipeline-evaluation/scripts/wait_for_draft_run.py <DraftRun ID>`
   - Poll until `succeeded`, `failed`, or a long-running/stale diagnostic state.
   - Do not call `/api/drafts/generate` as a timeout fallback for a live `DraftRun`.

5. **Diagnose**
   - Run the diagnostics helper:
     `python .agents/skills/draft-run-pipeline-diagnostics/scripts/analyze_draft_run.py <DraftRun ID>`
   - Then follow `$draft-run-pipeline-diagnostics` for the full analysis: inspect
     implicated code, compare with `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`
     and `ROADMAP.md`, and decide if the plan continues or needs a repair slice.

## What to Report

Answer in Russian unless asked otherwise. Include:

- exact `DraftRun ID`;
- whether it was started through UI or API;
- elapsed time and terminal status;
- key step outcomes and child `AiRun` failures/fallbacks;
- quality judgment of final draft;
- root causes;
- next action: continue roadmap, add repair slice, or fix infrastructure.

## Failure Discipline

- If `POST /api/draft-runs` never creates a run, this is launch/infrastructure failure.
- If a run exists and is `queued/running`, do not silently replace it with compatibility
  generation.
- If a run is stale, report stale status, current step, last progress, and trace link.
- If the final draft is bad, diagnose from artifacts and candidate selection, not from
  subjective reading alone.

## Useful Phrases

- `Запусти тестовый DraftRun и проведи диагностику`
- `Прогони полный pipeline evaluation`
- `Сгенерируй DraftRun для текущего поста, дождись завершения и оцени результат`
- `Проверь пайплайн end-to-end: запуск, ожидание, диагностика`
- `Сделай контрольный прогон генерации и скажи, можно ли двигаться дальше`
