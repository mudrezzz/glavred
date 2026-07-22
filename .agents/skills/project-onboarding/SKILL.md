---
name: project-onboarding
description: Use at the start of a new Codex chat or when asked to continue an existing project, take the next task, inspect project status, or resume from the roadmap tracker. Reconstructs context from repository files without requiring the user to re-explain the project.
---

# Project Onboarding Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Quickly understand the project state and select the next appropriate action from repository context.

## Process

1. Read `AGENTS.md`.
2. Read tracker state with `python -m backend.app.roadmap next/list/show`; read generated `ROADMAP.md` for context.
3. Read `README.md`.
4. Read the source requirements document if identifiable.
5. Inspect:
   - `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`
   - `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` when backend DraftRun,
     drafting quality, LLM role, validation, ranking, revision, or trace work is
     active or next in `ROADMAP.md`
   - `docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md` when RadarRun, upstream search,
     coverage, benchmark, or trace-page work is active or next in `ROADMAP.md`
   - `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md` when upstream
     signal extraction, scoring, candidate assembly, plan, or DraftRun handoff work
     is active or next in `ROADMAP.md`
   - latest ADRs
   - latest architecture ADRs and active architecture guardrails
   - developer docs
   - user docs
   - demo docs
6. Inspect the project structure and test structure.
7. If backend work is present or planned, inspect:
   - `.env.example`;
   - backend ADRs;
   - `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`;
   - `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`;
   - `backend/app/drafting/README.md`;
   - `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`;
   - `docs/developer/BACKEND_MODULE_TEMPLATE.md`;
   - backend sections in the SAO and developer guide;
   - backend tests and architecture smoke backend baselines, including
     `npm run test:architecture`.
8. Identify the current iteration, active slice, next ready task, blocked tasks, and open questions.

## When asked to "take the next task"

Do not ask the user to repeat project context.

Instead:

1. Determine the next `Ready` task from `python -m backend.app.roadmap next`.
2. If there is an `In Progress` task, prefer continuing it unless it is blocked.
3. If no task is ready, propose the smallest next slice based on requirements and current architecture.
4. Update the tracker before starting implementation if the selected task needs clarification, then render/export.
5. Before selecting a product slice, account for current file-size limits, near-limit
   warnings, module ownership, and feature dependency guardrails.
6. Before selecting a backend slice, account for OpenRouter environment requirements,
   OOP/SRP backend boundaries, file-size guardrails, and provider/library dependency
   hygiene. Distinguish active compatibility facade, migrated thin shim, and
   remaining explicit debt before treating a legacy file as an owner. If backend
   package quality or structural debt is part of the next task, use
   `.agents/skills/backend-architecture-audit/SKILL.md`.
7. For tests, Docker, browser acceptance, and live provider checks, use
   `.agents/skills/remote-docker-testing/SKILL.md`. Run its `doctor` during onboarding;
   never start local Glavred Docker without an explicit user request.
8. For complex pipeline slices, check that the slice follows
   `AS IS -> Change Intent -> TO BE -> DoD -> Implementation -> AS IS Update`.
   If runtime order, trace shape, provider input, retry/backup/fallback,
   quality/fidelity, budgets, diagnostics, async/staleness, or search coverage
   changes, a TO BE document or documented exception is required before
   implementation.

## Required output before implementation

Provide a short project state summary:

- Current product goal
- Current iteration
- Active or next slice
- Relevant files
- Risks or blockers
- Intended validation commands
- Architecture guardrails that affect the selected slice
- For backend slices, the current `.env.example` contract and OpenRouter/provider
  boundary assumptions
- For DraftRun/backend slices, the canonical package owner under
  `backend/app/drafting`, whether any touched legacy file is a migrated thin shim,
  and the expected `npm run test:architecture` obligation
- For complex pipeline slices, AS IS sources, TO BE necessity, Definition of Done,
  proof evidence, and expected AS IS update outcome

Then continue with the task unless the task is genuinely blocked.

## Completion checklist

Before finishing onboarding:

- The next task is identified.
- The reason for selecting it is clear.
- Relevant docs and requirements were inspected.
- Any ambiguity is recorded in the tracker/export and rendered into `ROADMAP.md`.
