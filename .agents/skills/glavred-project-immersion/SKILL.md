---
name: glavred-project-immersion
description: Use when the user asks to get immersed in the Glavred project, start a new chat with project context, explain what the product is, where to look, what architecture/roadmap/tests/guardrails matter, or produce a concise onboarding brief before work.
---

# Glavred Project Immersion

## Goal

Build a compact, current, repository-grounded onboarding brief for Glavred so a new
chat can start productive work without re-learning the project from the user.

This skill is for orientation and task selection. Do not edit files unless the user
explicitly asks to continue into implementation.

## Required Reads

Read only what is needed for the requested depth, but always verify current state from
the repository rather than memory alone.

1. `AGENTS.md`.
2. Roadmap tracker:
   - `python -m backend.app.roadmap next`
   - `python -m backend.app.roadmap list --status Ready`
   - `python -m backend.app.roadmap show <next-slice-id>`
3. `README.md`.
4. Product source:
   - `glavred.md` if present;
   - otherwise state that the primary requirements file was not found.
5. Core architecture docs:
   - `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`
   - `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`
   - `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`
   - `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md` when upstream/radar work is next
   - `docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md` when SaaS/project work matters
6. Latest relevant ADRs in `docs/adr/`.
7. Work guides:
   - `docs/developer/DEVELOPER_GUIDE.md`
   - `docs/user/USER_GUIDE.md`
   - `demo/README.md`
   - `docs/roadmap/README.md`
8. Current repo state:
   - `git status --short --branch`
   - `git diff --stat`
   - `package.json` scripts

## Optional Reads

Load these only when relevant to the next slice:

- `backend/app/drafting/README.md`
- `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`
- project blueprints in `docs/architecture/*_PROJECT_BLUEPRINT.md`
- frontend design system entrypoint: `ui-design-systems/START-HERE.md`
- architecture smoke script: `scripts/architecture-smoke.mjs`

## Brief Output Format

Answer in Russian by default. Keep the brief high signal and short enough to fit at
the top of a new chat.

Use this structure:

1. **Одной строкой**: what Glavred is building.
2. **Что уже есть**: 4-6 bullets about major working product areas.
3. **Текущий roadmap**:
   - next Ready slice;
   - any In Progress/dirty work;
   - why this is the next task.
4. **Карта проекта**:
   - frontend;
   - backend;
   - drafting pipeline;
   - upstream/radar;
   - portfolio/auth/projects;
   - docs/ADR/roadmap;
   - tests and smoke checks.
5. **Где смотреть**: concrete paths with one-line purpose each.
6. **Жесткие правила**:
   - `ROADMAP.md` is generated; use tracker/export/render.
   - backend code must follow bounded contexts: `drafting`, `upstream`, `ai-runs`, `portfolio`, `roadmap`, `shared`.
   - new LLM/provider-heavy work must use the current operation governance rules or be tracked as debt.
   - frontend work must use `frontend-design-system` and `ui-design-systems/START-HERE.md`.
   - demo changes must stay realistic and project-scoped.
7. **Проверки**: relevant commands for the current slice.
8. **Риски сейчас**: 2-4 concrete active risks from roadmap/docs/git state.
9. **С чего начинать**: one recommended next action.

## Command Cheatsheet

Use these commands in the brief when relevant:

```bash
python -m backend.app.roadmap next
python -m backend.app.roadmap show <slice-id>
python -m backend.app.roadmap list --status Ready
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
npm run test:architecture
npm run smoke
npm test -- --run --pool=threads --maxWorkers=4
python -m pytest backend/tests
docker compose config --quiet
git diff --check
```

## Rules

- Do not present stale memory as current state. Verify tracker, docs, and git state.
- Do not manually edit `ROADMAP.md`; use tracker artifacts.
- Do not hide dirty worktree status. Say what is already modified.
- Do not start implementation during immersion unless the user explicitly asks.
- If the next slice is backend/LLM/DraftRun work, call out LLM operation governance,
  payload budgets, fallback incident handling, and architecture smoke obligations.
- If the next slice is UI work, call out design-system obligations before giving UI
  advice.
