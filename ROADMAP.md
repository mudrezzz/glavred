# ROADMAP.md

## Product Vision

Glavred is an AI-native editorial office for expert bloggers, founders, consultants,
authors, and teams who want to run a personal media system with editorial discipline.

The service helps an author move from source signals to insight cards, content
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
- Product-facing terminology uses **Редакционная модель** / `EditorialModel`.

## Status Legend

- `Backlog`: known but not ready or not prioritized
- `Ready`: ready to implement
- `In Progress`: currently being worked on
- `Blocked`: cannot proceed without clarification or dependency
- `Done`: completed and validated

## Current Iteration

### Iteration 1: First Product Perimeter

Goal:

- Deliver the first working Glavred flow from source signal to approved final text
  with local-first persistence.

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

- Status: Done
- Goal: Define the smallest closed end-to-end product perimeter from the MVP modules.
- User value: Implementation can begin from explicit boundaries, objects, and flows.
- Scope:
  - Use the source brief and design handoff.
  - Define the first flow from source signal to approved post brief.
  - Define conceptual domain objects for `EditorialModel`, `SourceSignal`,
    `InsightCard`, `ContentPlanItem`, `PostBrief`, and `WorkspaceStore`.
  - Choose local-first persistence for the first implementation slice.
  - Create ADRs for the approved-brief endpoint, local-first persistence, and
    deterministic placeholder services before AI integration.
  - Define the first realistic demo scenario in implementation terms.
- Out of scope:
  - Runtime implementation of the domain contracts.
  - Backend persistence.
  - AI integration.
  - Full source ingestion.
  - Draft generation and editorial checks.
  - Autoposting.
- Implementation notes:
  - The first flow stops at approved `PostBrief`.
  - Use deterministic services and fixtures in Slice 0.4 before real AI providers.
  - Keep domain, application services, infrastructure adapters, and React UI separated.
- Tests:
  - Existing regression only for this docs/ADR slice.
  - Validation completed with `npm test` and `npm run smoke`.
- Docs:
  - Updated architecture overview, ADRs, developer guide, demo docs, and roadmap.
- Demo impact:
  - Demo is specified as founder-blog scenario: a practical AI adoption author turns a
    repeated market signal about failed AI pilots into an approved post brief.
- Acceptance criteria:
  - First implementation slice is clearly ready. Done.
  - Architecture boundaries are documented. Done.
  - ADRs capture the three key decisions. Done.
  - Terminology uses `EditorialModel` / "Редакционная модель". Done.
- Risks:
  - The approved-brief endpoint is less visually complete than a draft demo, but it
    keeps the first implementation focused on the product's core editorial control.

### Slice 0.4: First Working Flow to Approved Post Brief

- Status: Done
- Goal: Implement the first closed Glavred flow from source signal to approved post
  brief.
- User value: A user can create a limited but real editorial workflow and preserve it
  locally.
- Scope:
  - Add TypeScript domain contracts for `EditorialModel`, `SourceSignal`,
    `InsightCard`, `ContentPlanItem`, `PostBrief`, and workspace state.
  - Add deterministic application services for turning the demo signal into an insight
    card, a plan item, and a post brief.
  - Add a local workspace store backed by browser `localStorage`, with fixtures as the
    initial empty/demo state.
  - Build a Russian-language UI flow for the founder-blog demo scenario:
    - view or edit the editorial model;
    - add or load the source signal;
    - review the insight card;
    - place it into the content plan;
    - generate and approve the post brief.
  - Keep the UI aligned with the "quiet editorial office" design handoff.
- Out of scope:
  - Real AI calls.
  - Real RSS, Telegram, YouTube, website, CRM, or document ingestion.
  - Backend, auth, team work, and multi-device sync.
  - Draft generation, style editing, anti-AI checks, fact-checking, policy review,
    publication, analytics, and learning loop.
- Implementation notes:
  - Use `src/domain/` for domain objects and pure transitions.
  - Use application services for deterministic scoring, planning, and briefing.
  - Use an infrastructure adapter for `localStorage`; do not call browser storage from
    domain code.
  - Keep approval statuses explicit for plan items and post briefs.
- Tests:
  - Unit tests for domain transitions and approval rules.
  - Unit tests for deterministic scoring/planning/briefing services.
  - Integration tests for local workspace save/load.
  - UI smoke tests for the signal to approved post brief flow.
  - Run `npm test`, `npm run smoke`, and targeted tests introduced by the slice.
- Docs:
  - Update README, architecture overview if boundaries change, developer guide, user
    guide, demo docs, and roadmap.
- Demo impact:
  - Demo should let the user reach an approved post brief from the founder-blog
    scenario.
- Acceptance criteria:
  - User can start from the demo signal and end with an approved post brief. Done.
  - Approved state survives page reload through local storage. Done.
  - No real AI or backend dependency is required. Done.
  - Tests and smoke build pass. Done.
- Risks:
  - Local storage shape may need migration when backend persistence arrives.
  - Deterministic services may look too scripted; copy should make clear this is the
    first working product perimeter.

### Slice 0.5: Draft and Editorial Checks

- Status: Done
- Goal: Extend the approved brief into a draft and editorial review workspace.
- User value: The product can demonstrate the next approval gate: final text review.
- Scope:
  - Add runtime contracts for `PostDraft`, `EditorialCheck`, `EditorNote`, and
    `FinalText`.
  - Generate a deterministic draft from approved `PostBrief`.
  - Model style, anti-AI, fact-checking, and policy checks.
  - Add editor notes and final text approval gate.
  - Make `Редактура` an active product section.
  - Preserve draft/check/final state in local storage with fallback for Slice 0.4
    workspaces.
- Out of scope:
  - Real AI provider integration.
  - Autoposting, manual export implementation, and analytics.
- Implementation notes:
  - Build on the approved `PostBrief` object from Slice 0.4.
  - Warnings do not block final approval because the human editor remains in control.
- Tests:
  - Unit tests for draft generation, editorial checks, final approval, and revision.
  - Storage tests for old workspace normalization and final text persistence.
  - UI smoke tests for final text approval and persistence after reload.
- Docs:
  - Updated README, architecture overview, user guide, developer guide, demo docs, and
    roadmap.
- Demo impact:
  - Demo moves from approved brief to reviewed and approved final text.
- Acceptance criteria:
  - User can approve a final text after seeing editor notes and risks. Done.
  - Approved final text survives reload. Done.
  - `npm test` and `npm run smoke` pass. Done.
- Risks:
  - Draft quality cannot be validated until AI integration is introduced.

### Slice 0.6: Manual Export and Release Prep

- Status: Ready
- Goal: Let the user prepare an approved final text for manual release.
- User value: The current editorial loop becomes practically usable because the
  approved text can be copied/exported with release metadata.
- Scope:
  - Activate `Выпуск` as a working section.
  - Show approved final text, platform, release checklist, and manual export actions.
  - Add deterministic platform adaptation metadata for Telegram and LinkedIn without
    changing the text body automatically.
  - Add release readiness status and local persistence.
  - Keep analytics as a placeholder.
- Out of scope:
  - Autoposting.
  - Real platform APIs.
  - Backend, auth, team work, and AI provider integration.
- Tests:
  - Unit tests for release readiness transitions.
  - Storage tests for release state.
  - UI tests for opening `Выпуск`, viewing approved final text, and marking manual
    export ready.
- Docs:
  - Update README, user guide, developer guide, demo docs, and roadmap.
- Demo impact:
  - Demo reaches "approved final text ready for manual release".
- Acceptance criteria:
  - User can move from approved final text to a release-ready manual export state.
  - State survives reload.
  - Tests and smoke build pass.
- Risks:
  - Without real publication APIs, release value is limited to operational readiness
    and copy/export convenience.

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

### Slice 0.3: Architecture Baseline for the First Product Perimeter

- Completed: 2026-06-03
- Result:
  - Defined the first product perimeter from source signal to approved post brief.
  - Chose local-first persistence for the first implementation slice.
  - Chose deterministic services and fixtures before AI provider integration.
  - Documented component responsibilities, dependency direction, conceptual interfaces,
    extension points, test strategy, and demo flow.
  - Created ADRs for the key architectural decisions.
  - Standardized product-facing terminology on `EditorialModel` / "Редакционная
    модель".
- Validation:
  - `npm test`: passed.
  - `npm run smoke`: passed.

### Slice 0.4: First Working Flow to Approved Post Brief

- Completed: 2026-06-03
- Result:
  - Replaced the foundation screen with a production React/TypeScript editorial cabinet
    aligned with the `glavred-app` design reference.
  - Added TypeScript domain contracts for editorial model, signal, insight card, plan
    item, post brief, workspace state, and approval status.
  - Added deterministic services for insight, planning, and briefing.
  - Added local-first workspace persistence through browser `localStorage`.
  - Added editable Russian-language sections for `Редакционная модель`, `Радар`,
    `План`, and `Фабулы`.
  - Added polished placeholders for `Редактура`, `Выпуск`, and `Аналитика`.
  - Added unit, integration, and UI smoke tests for the first flow.
- Validation:
  - `npm test`: passed.
  - `npm run smoke`: passed.

### Slice 0.5: Draft and Editorial Checks

- Completed: 2026-06-03
- Result:
  - Added runtime contracts for post drafts, editorial checks, editor notes, final
    text, draft status, check type, and check status.
  - Added deterministic draft generation from approved post briefs.
  - Added deterministic style, anti-AI, fact-check, and policy checks plus editor
    notes.
  - Activated `Редактура` with tabs for `Фабула`, `Драфт`, and `Финал`.
  - Added manual draft editing and final text approval through HITL Gate 3.
  - Extended local-first persistence with backward-compatible normalization for Slice
    0.4 workspaces.
  - Updated README, architecture overview, developer guide, user guide, demo docs, and
    roadmap.
- Validation:
  - `npm test`: passed.
  - `npm run smoke`: passed.

## Blocked Items

- None.

## Open Questions

- Which deployment target should be assumed for the first hosted version?
- Which AI/API providers are in scope after deterministic services are replaced?
- Should the eventual backend preserve the local workspace schema or introduce a
  migration layer?

## Next Recommended Task

Start `Slice 0.6: Manual Export and Release Prep`.
