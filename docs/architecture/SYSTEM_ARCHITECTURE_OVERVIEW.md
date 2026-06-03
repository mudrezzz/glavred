# System Architecture Overview

## Product Context

Glavred is an AI-native editorial office for personal and expert media. The product is
not a generic post generator: it helps an author build editorial discipline by moving
from source signals to selected topics, approved post intentions, drafts, checks, and
learning.

The primary requirements source is `glavred.md`. The design handoff in
`ui-design-systems/` is a secondary visual and product reference. The product-facing
term for the author's durable rules is **Редакционная модель** / `EditorialModel`.

## First Product Perimeter

The first working product perimeter stops at an approved post brief:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief`

This is intentionally smaller than the full product loop. Draft generation, style
editing, anti-AI checks, fact-checking, policy review, publication, and analytics are
future slices. Stopping at the approved brief keeps the first product useful while
preserving the brief's core idea: the author approves the intention before any text is
written.

## Major Components

- `EditorialModel`: owns author, audience, positioning, fabula, rubrics, style rules,
  forbidden topics, and blog goals. It is the context used to evaluate every signal,
  plan item, and brief.
- `EditorialRadar`: accepts manually added source signals in the first implementation.
  Real RSS, Telegram, website, YouTube, CRM, and document ingestion are extension
  points, not part of the first product perimeter.
- `InsightScoring`: turns a source signal into an insight card with relevance, urgency,
  banality risk, fact gaps, suggested rubric, and suggested author position.
- `ContentPlanning`: turns selected insight cards into plan items with platform, date,
  priority, format, expected effect, and approval status.
- `Briefing`: turns an approved plan item into a post brief with thesis, conflict,
  author position, evidence, examples, structure, CTA, risks, sources, and approval
  status.
- `HitlApprovals`: enforces human approval gates for plan items and post briefs.
- `LocalWorkspaceStore`: loads and saves the current workspace state in browser storage
  for the first implementation slice.

## Dependency Direction

Dependencies must point inward:

`React UI -> application services -> domain model`

Infrastructure adapters sit at the edge:

`React UI -> application services -> WorkspaceStore adapter -> localStorage`

Domain code must not import React, browser APIs, storage APIs, future AI providers, or
network clients. Application services orchestrate domain operations and call adapters.
React components render state and trigger application service methods.

## Conceptual Domain Interfaces

Slice 0.3 documents these contracts only; Slice 0.4 will implement them in TypeScript.

- `EditorialModel`: author, audience, positioning, fabula, rubrics, style rules,
  forbidden topics, goals.
- `SourceSignal`: type, title, source, capturedAt, summary, rawNote.
- `InsightCard`: source signal, why it matters, audience relevance, author position,
  rubric, urgency, score, banality risk, fact gaps.
- `ContentPlanItem`: insight, platform, date, priority, format, expected effect,
  approval status.
- `PostBrief`: thesis, conflict, author position, evidence, examples, structure, CTA,
  risks, sources, approval status.
- `WorkspaceStore`: load and save current local workspace state.

## First Demo Data Flow

The first realistic demo scenario is a founder writing about practical AI adoption for
small and medium businesses:

1. The workspace starts with an `EditorialModel` for an author whose fabula is that AI
   value comes from process redesign, not tool collecting.
2. The author adds a `SourceSignal`: several market posts discuss failed AI pilots
   caused by process gaps.
3. `InsightScoring` produces an `InsightCard`: "AI pilots fail when teams automate
   chaos", with relevance, suggested rubric, banality risk, and fact gaps.
4. `ContentPlanning` creates a `ContentPlanItem` for a Telegram or LinkedIn post.
5. The author approves or adjusts the plan item through a HITL gate.
6. `Briefing` creates a `PostBrief` with thesis, conflict, evidence, structure, risks,
   and sources.
7. The author approves the post brief. The first product flow ends here.
8. `LocalWorkspaceStore` persists the workspace so the approved brief survives reload.

## Extension Points

- Source ingestion adapters can later replace manual signal entry.
- AI provider adapters can later replace deterministic insight, planning, and briefing
  services.
- Draft and review services can extend from approved `PostBrief` without changing the
  earlier flow.
- Backend persistence can replace `LocalWorkspaceStore` behind the same workspace
  store interface.
- Publication and analytics can attach after approved draft/release states.

## Testing Strategy

Slice 0.3 itself is documentation and ADR work, so validation is existing regression:

- `npm test`
- `npm run smoke`

Slice 0.4 should add:

- Unit tests for domain transitions and approval rules.
- Unit tests for deterministic scoring/planning/briefing services.
- Integration tests for local workspace save/load.
- UI smoke tests for the source signal to approved post brief flow.
- Manual demo acceptance for the founder-blog scenario.

## Known Trade-offs

- Approved brief is less visually complete than draft generation, but it reaches the
  product's core differentiator earlier: approving the intention before writing.
- Local-first persistence avoids backend scope, but it is not suitable for multi-device
  or team collaboration.
- Deterministic services keep the first slice testable and cheap, but real AI quality
  remains unvalidated until a later integration slice.
- Manual source entry is narrow, but it makes the radar and scoring concepts usable
  before real ingestion exists.

## Open Questions

- Which AI provider and model access pattern should be used after deterministic
  services are replaced?
- Which hosted deployment target should be used after local-first development?
- Should the first backend persistence slice preserve the local workspace format or
  introduce a migration layer?
