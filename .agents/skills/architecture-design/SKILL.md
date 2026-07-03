---
name: architecture-design
description: Use when designing or revising project architecture based on user input, requirements documents, ROADMAP.md, and files in the repository root. Applies object-oriented design, clear component boundaries, ADRs, and iterative slice-based architecture planning. Do not use for ordinary small code edits.
---

# Architecture Design Skill

## Goal

Design or revise the architecture so the project can grow iteratively through small, working slices.

## Inputs

Use the following sources, in this order:

1. User instructions in the current task.
2. The source requirements document specified by the user.
3. If no requirements file was specified, search the repository root for likely requirements files:
   - `SPEC.md`
   - `SPECIFICATION.md`
   - `REQUIREMENTS.md`
   - `PRD.md`
   - `TASK.md`
   - `TZ.md`
   - `ТЗ.md`
   - files containing "requirements", "spec", "prd", "task", "тз", or "задание".
4. `ROADMAP.md`.
5. Existing architecture docs.
   - For Glavred DraftRun/drafting architecture, include
     `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`.
6. Existing code structure.

## Process

1. Identify the product goal and primary user value.
2. Identify the smallest closed product perimeter that can work end-to-end.
3. Define the first architectural circle: the minimal complete product.
4. Define later expansion circles.
5. Propose module boundaries using OOP and single-responsibility principles.
6. Separate domain, application, infrastructure, UI, persistence, integration, and testing concerns where applicable.
7. Identify architectural risks.
8. Record meaningful decisions as ADRs.
9. For every new architecture rule, define how it is enforced:
   - update SAO with the rule and ownership boundary;
   - add or update an ADR;
   - add an automated smoke check when practical, or a mandatory workflow checklist
     when automation would be brittle.
10. For backend architecture, enforce OOP/SRP boundaries explicitly:
    - API routes are thin transport adapters;
    - domain modules are provider-free and persistence-free;
    - application services own use cases and orchestration;
    - infrastructure adapters own OpenRouter, database, queue, file, publication, and
      `langgraph-document-ai-platform` calls;
    - no 2-3k line backend files, god services, or boilerplate-only packages.
    - new DraftRun backend code belongs under `backend/app/drafting`, new upstream
      radar/search/signal backend code belongs under `backend/app/upstream`, and
      shared provider-neutral operation helpers belong under `backend/app/shared`
      only when genuinely cross-context.
11. For Glavred drafting architecture, preserve the quality spine:
    `DraftRunContext -> RuleRegistrySnapshot -> SourceLedger -> FeasibilityGate ->
    PostContract -> RulePack -> MaterialPlan -> RhetoricalPlans -> DraftCandidates ->
    Linter/Validators -> Ranking -> DirectedRevision -> Regression -> HumanDecision`.
    Do not design validator/revision slices before claim provenance and post-contract
    artifacts are explicit.

## Required outputs

Update or create:

- `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`
- `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` for DraftRun pipeline changes,
  plus regenerated `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf`
- relevant ADR files under `docs/adr/`
- `ROADMAP.md` if architecture affects iterations or slices
- smoke-check or workflow-checklist coverage for each new architecture rule

## Architecture document should include

- Product context
- Major components
- Responsibilities of each component
- Data flow
- Dependency direction
- Extension points
- Testing strategy
- Demo implications
- Known trade-offs
- Open questions

## ADR format

Use this filename pattern:

`docs/adr/YYYY-MM-DD-short-decision-title.md`

Use this structure:

```markdown
# ADR: <Decision title>

## Status

Proposed | Accepted | Superseded

## Context

## Decision

## Consequences

## Alternatives considered
```

## Completion checklist

Before finishing:

- Architecture supports iterative slice delivery.
- No component has unclear ownership.
- Test ownership mirrors production ownership; app-flow tests live beside the owning
  feature and `src/App.test.tsx` remains shell-only.
- Backend ownership mirrors production ownership: routes, use cases, domain policies,
  adapters, settings, and tests are separate roles.
- OpenRouter is treated as the default backend LLM provider target, but provider
  details stay outside React, domain objects, and API handlers.
- Important trade-offs are documented.
- New architecture rules have ADR + SAO coverage and either automated checks or a
  mandatory workflow checklist.
- `ROADMAP.md` reflects architectural work.
- Follow-up tasks are small enough to implement as slices.
