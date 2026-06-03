# ROADMAP.md

## Product Vision

Glavred is an AI-native editorial office for expert bloggers, founders, consultants,
authors, and teams who want to run a personal media system with editorial discipline.

The service should help an author move from source signals to insight cards, content
planning, approved post briefs, drafts, editorial checks, manual export or release, and
analytics-driven learning. Its central promise is not "AI writes better", but "the
author gains a repeatable editorial system".

## Source Requirements

Primary requirements document:

- `glavred.md`

Current status:

- `glavred.md` is filled and accepted as the source of truth.
- The `ui-design-systems/` handoff contains product/design context and remains a
  secondary source.
- The first architecture and implementation slices should be derived from the five MVP
  modules in the source brief.

## Status Legend

- `Backlog`: known but not ready or not prioritized
- `Ready`: ready to implement
- `In Progress`: currently being worked on
- `Blocked`: cannot proceed without clarification or dependency
- `Done`: completed and validated

## Current Iteration

### Iteration 0: Project Foundation

Goal:

- Establish repository structure, documentation, architecture baseline, demo baseline,
  test baseline, Git history, and brief-backed product direction.

Status:

- `Done`

## Slice Backlog

### Slice 0.1: Bootstrap Project Structure

- Status: Done
- Goal: Create initial project structure and documentation control files.
- User value: The project can be developed consistently in future sessions without
  re-explaining the process.
- Scope:
  - Keep `AGENTS.md` as project operating instructions.
  - Create React/Vite/TypeScript baseline.
  - Create baseline domain workflow model.
  - Create unit and smoke test infrastructure.
  - Update `README.md`, `ROADMAP.md`, architecture docs, contributor docs, developer
    docs, user docs, and demo docs.
  - Initialize Git and create an initial local commit.
- Out of scope:
  - GitHub repository creation.
  - Production product logic.
  - Final architecture decisions before `glavred.md` is filled in.
- Implementation notes:
  - Use React + Vite + TypeScript because the provided design handoff already uses
    React-like reference screens.
  - Keep domain workflow separate from UI from the first slice.
- Tests:
  - Unit tests for the editorial workflow.
  - UI smoke test for the baseline app.
  - Build smoke test.
- Docs:
  - Baseline docs must explain source requirements status and next task.
- Demo impact:
  - Demo docs point to the current local app and design references.
- Acceptance criteria:
  - Repository contains a runnable frontend baseline. Done.
  - Test command passes. Done: `npm test`.
  - Build command passes. Done: `npm run smoke`.
  - Dependency audit passes. Done: `npm audit --audit-level=moderate`.
  - Git is initialized with an initial commit. Done.
- Risks:
  - Superseded by Slice 0.2 after the source brief was filled.

### Slice 0.2: Brief-Backed Bootstrap Update

- Status: Done
- Goal: Update the project foundation from the filled source brief.
- User value: Future slices can start from real product direction instead of blocked
  placeholders.
- Scope:
  - Accept `glavred.md` as the primary source requirements document.
  - Update the domain baseline to reflect the brief's editorial loop.
  - Capture the first five MVP modules.
  - Update README, roadmap, architecture overview, developer guide, user guide, and
    demo docs.
  - Keep GitHub repository creation deferred.
- Out of scope:
  - Full product architecture.
  - Backend persistence.
  - AI provider integration.
  - Real ingestion, drafting, publication, or analytics.
- Implementation notes:
  - Keep the foundation frontend-first with framework-independent domain logic.
  - Model manual export in the first loop because the brief allows publication to stay
    manual in the first version.
- Tests:
  - Unit tests for the updated editorial workflow.
  - UI smoke test for the brief-backed foundation screen.
- Docs:
  - Updated required baseline docs.
- Demo impact:
  - Demo docs now describe the first realistic founder-blog scenario.
- Acceptance criteria:
  - Product requirements are no longer blocked. Done.
  - MVP perimeter is clear. Done.
  - Test command passes. Done: `npm test`.
  - Build command passes. Done: `npm run smoke`.
  - Dependency audit passes. Done: `npm audit --audit-level=moderate`.
- Risks:
  - The source brief is broad, so the first implementation slice still needs an
    architecture pass before feature work.

### Slice 0.3: Architecture Baseline for the First Product Perimeter

- Status: Ready
- Goal: Define the smallest closed end-to-end product perimeter from the MVP modules.
- User value: Implementation can begin from explicit boundaries, objects, and flows.
- Scope:
  - Use the source brief and design handoff.
  - Define domain objects for editorial bible, source signal, insight card, content
    plan item, post brief, draft, and editorial check.
  - Decide whether the first implementation slice needs local persistence.
  - Create or update ADRs for architecture choices.
  - Define the first realistic demo scenario in implementation terms.
- Out of scope:
  - AI integration.
  - Full source ingestion.
  - Autoposting.
- Implementation notes:
  - Use `$architecture-design`.
  - Use `$roadmap-slice-planning` if the architecture pass changes slice order.
- Tests:
  - Define the validation strategy for the first product flow.
- Docs:
  - Update architecture overview, ADRs, developer guide, demo docs, and roadmap.
- Demo impact:
  - First demo should show an expert author's blog moving from a signal to an approved
    post brief or draft.
- Acceptance criteria:
  - First implementation slice is clearly ready.
  - Architecture boundaries are documented.
- Risks:
  - Overbuilding the editorial bible before the user can reach a first useful output.

### Slice 0.4: First Working Product Perimeter

- Status: Backlog
- Goal: Implement the smallest closed end-to-end Glavred flow.
- User value: A limited but working product can be demonstrated.
- Scope:
  - To be defined in Slice 0.3.
- Out of scope:
  - To be defined in Slice 0.3.
- Implementation notes:
  - Use `$slice-implementation`.
- Tests:
  - Unit, integration, smoke, and possibly e2e tests for the selected flow.
- Docs:
  - Update README, developer guide, user guide, demo docs, and roadmap.
- Demo impact:
  - Demo should show the selected working flow.
- Acceptance criteria:
  - Product can run and demonstrate the first meaningful flow.
- Risks:
  - To be defined in Slice 0.3.

## Completed Slices

### Slice 0.1: Bootstrap Project Structure

- Completed: 2026-06-03
- Result:
  - Created React/Vite/TypeScript application baseline.
  - Added framework-independent editorial workflow domain model.
  - Added Vitest and Testing Library baseline tests.
  - Updated README, roadmap, architecture overview, ADRs, contributor guide,
    developer guide, user guide, and demo docs.
  - Confirmed GitHub repository creation is deferred.
  - Initialized local Git repository and created the initial baseline commit.
- Validation:
  - `npm test`: passed.
  - `npm run smoke`: passed.
  - `npm audit --audit-level=moderate`: passed with 0 vulnerabilities.

### Slice 0.2: Brief-Backed Bootstrap Update

- Completed: 2026-06-03
- Result:
  - Accepted filled `glavred.md` as primary source requirements.
  - Updated the domain workflow baseline to the brief-backed editorial loop.
  - Captured the five MVP modules from the brief.
  - Updated README, roadmap, architecture overview, developer guide, user guide, and
    demo docs.
  - Kept GitHub repository creation deferred.
- Validation:
  - `npm test`: passed.
  - `npm run smoke`: passed.
  - `npm audit --audit-level=moderate`: passed with 0 vulnerabilities.

## Blocked Items

- None for bootstrap.

## Open Questions

- Should the future GitHub repository be private or public?
- Which deployment target should be assumed for the first hosted version?
- Which AI/API providers are in scope for the first product slice?
- Should the first product flow stop at approved post brief, or continue to draft and
  editorial checks?
- Should the first implementation store state in local browser storage, mocked fixtures,
  or a backend-backed workspace?

## Next Recommended Task

Start `Slice 0.3: Architecture Baseline for the First Product Perimeter`.
