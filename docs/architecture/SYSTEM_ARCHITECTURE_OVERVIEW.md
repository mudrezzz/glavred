# System Architecture Overview

## Product Context

Glavred is an AI-native editorial office for personal and expert media. The product is
not a generic post generator: it helps an author build editorial discipline by moving
from source signals to selected topics, approved post intentions, drafts, checks, and
learning.

The primary requirements source is `glavred.md`. The design handoff in
`ui-design-systems/` is a secondary visual and product reference. The product-facing
term for the author's durable rules is **Редакционная модель** / `EditorialModel`.

## Current Product Perimeter

The current working product perimeter reaches a captured editorial learning note:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

This is intentionally smaller than the full product loop. Real AI provider calls,
publication automation, backend sync, and real metrics ingestion are future slices.
The current flow keeps the brief's core idea intact: the author approves the intention
before text is written, reviews deterministic draft/check outputs before final
approval, prepares copy/Markdown for manual release, and captures manual editorial
learning.

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
- `Drafting`: turns an approved post brief into a deterministic editable draft.
- `EditorialChecks`: models style, anti-AI, fact-check, and policy checks plus editor
  notes before final approval.
- `ReleasePackaging`: turns approved final text into platform targets, Markdown
  preview, release checklist, and manual export status.
- `AnalyticsPrep`: turns an exported release package into manual metric fields and an
  editorial learning note.
- `HitlApprovals`: enforces human approval gates for plan items, post briefs, and
  final text, plus release readiness and learning capture gates.
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

These contracts are implemented in TypeScript for the first local-first flow.

- `EditorialModel`: author, audience, positioning, fabula, rubrics, style rules,
  forbidden topics, goals.
- `SourceSignal`: type, title, source, capturedAt, summary, rawNote.
- `InsightCard`: source signal, why it matters, audience relevance, author position,
  rubric, urgency, score, banality risk, fact gaps.
- `ContentPlanItem`: insight, platform, date, priority, format, expected effect,
  approval status.
- `PostBrief`: thesis, conflict, author position, evidence, examples, structure, CTA,
  risks, sources, approval status.
- `PostDraft`: brief, title, body, version, draft status, updated time.
- `EditorialCheck`: type, title, check status, summary, findings.
- `EditorNote`: agent, tone, text, target.
- `FinalText`: draft, title, body, approval status, approved time.
- `ReleasePackage`: final text, targets, Markdown, checklist, release status, updated
  time.
- `EditorialLearningNote`: release package, manual metrics, editorial conclusions,
  analytics status, updated time, captured time.
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
7. The author approves the post brief.
8. `Drafting` creates a deterministic editable draft from the approved brief.
9. `EditorialChecks` returns style, anti-AI, fact-check, and policy checks plus editor
   notes.
10. The author edits the draft and approves the final text through the third HITL gate.
11. `ReleasePackaging` creates a manual release package for Telegram and LinkedIn.
12. The author completes a release checklist and copies text or downloads Markdown.
13. `AnalyticsPrep` creates a manual metrics and editorial learning workspace.
14. The author captures the editorial learning note.
15. `LocalWorkspaceStore` persists the workspace so the learning note survives
   reload.

## Extension Points

- Source ingestion adapters can later replace manual signal entry.
- AI provider adapters can later replace deterministic insight, planning, briefing,
  drafting, and check services.
- Backend persistence can replace `LocalWorkspaceStore` behind the same workspace
  store interface.
- Platform publication APIs can attach after the manual release package.
- Real analytics ingestion can replace manual metric entry behind the analytics prep
  shape.

## Testing Strategy

Current validation covers:

- Unit tests for domain transitions and approval rules.
- Unit tests for deterministic scoring, planning, briefing, drafting, editorial check,
  release packaging, and analytics prep services.
- Integration tests for local workspace save/load.
- UI smoke tests for the source signal to captured editorial learning note flow.
- Manual demo acceptance for the founder-blog scenario.

## Known Trade-offs

- Deterministic draft and check outputs are useful for a controlled demo, but they do
  not validate real AI quality yet.
- Local-first persistence avoids backend scope, but it is not suitable for multi-device
  or team collaboration.
- Manual export is intentionally limited: it gives operational readiness and Markdown,
  not real platform publishing.
- Analytics prep uses manual metrics, so it is useful for workflow shape but not yet a
  live dashboard.
- Manual source entry is narrow, but it makes the radar and scoring concepts usable
  before real ingestion exists.

## Open Questions

- Which AI provider and model access pattern should be used after deterministic
  services are replaced?
- Which hosted deployment target should be used after local-first development?
- Should the first backend persistence slice preserve the local workspace format or
  introduce a migration layer?
