# ROADMAP.md

## Product Vision

Glavred is an AI-native editorial service for expert bloggers, founders, consultants,
and teams who want to run a personal media system with editorial discipline.

The service should help an author move from source signals to insight cards, content
planning, approved briefs, drafts, editing checks, release, and analytics-driven
learning.

## Source Requirements

Primary requirements document:

- `glavred.md`

Current status:

- `glavred.md` exists but is empty.
- The `ui-design-systems/` handoff contains product/design context and is accepted as a
  secondary source only.
- Product requirements must be confirmed from `glavred.md` before architecture or
  feature implementation expands beyond foundation work.

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
  test baseline, and Git history.

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
  - Product requirements are blocked because `glavred.md` is empty.

### Slice 0.2: Requirements Recovery and Architecture Baseline

- Status: Ready
- Goal: Turn the filled source brief into the first implementation architecture.
- User value: Future slices can implement real product behavior instead of inferred
  placeholders.
- Scope:
  - Fill or replace `glavred.md` with the actual product brief.
  - Inspect `glavred.md` and `ui-design-systems/`.
  - Define the smallest complete product perimeter.
  - Update `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`.
  - Add ADRs for architecture choices if needed.
  - Define first realistic demo scenario.
- Out of scope:
  - Full implementation.
- Implementation notes:
  - Use `$architecture-design`.
  - Use `$roadmap-slice-planning` if the brief adds substantial scope.
- Tests:
  - Define test strategy for the first product flow.
- Docs:
  - Update README, roadmap, architecture overview, developer guide, user guide, and
    demo docs.
- Demo impact:
  - Select the first market-relevant demo flow.
- Acceptance criteria:
  - Product requirements are no longer blocked.
  - First implementation slice is clearly ready.
- Risks:
  - The brief may conflict with the design handoff.

### Slice 0.3: First Working Product Perimeter

- Status: Backlog
- Goal: Implement the smallest closed end-to-end Glavred flow.
- User value: A limited but working product can be demonstrated.
- Scope:
  - To be defined after Slice 0.2.
- Out of scope:
  - To be defined after Slice 0.2.
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
  - To be defined after Slice 0.2.

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

## Blocked Items

- Product-specific architecture and implementation are blocked until `glavred.md`
  contains the actual source brief.

## Open Questions

- What exact source requirements should be placed in `glavred.md`?
- Should the future GitHub repository be private or public?
- Which deployment target should be assumed for the first hosted version?
- Which AI/API providers are in scope for the first product slice?

## Next Recommended Task

Fill `glavred.md`, then start `Slice 0.2: Requirements Recovery and Architecture
Baseline`.
