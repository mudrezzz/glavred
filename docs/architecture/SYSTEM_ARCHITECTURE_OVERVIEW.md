# System Architecture Overview

## Current State

This repository has a brief-backed, frontend-first project foundation:

- React + Vite + TypeScript application shell.
- A small domain model for the editorial workflow and MVP perimeter.
- Vitest-based test baseline.
- Design handoff in `ui-design-systems/`.

The primary requirements file is `glavred.md`. It defines Glavred as an AI-native
editorial office for personal and expert media, not a generic post generator.

## Initial Boundaries

The first baseline keeps these responsibilities separate:

- `src/domain/`: domain concepts that should not depend on React, browser APIs, or
  infrastructure.
- `src/App.tsx`: temporary application shell that renders the brief-backed baseline.
- `ui-design-systems/`: reference design materials, not production source code.
- `demo/`: demo documentation and future demo assets.
- `docs/`: architecture, developer, contributor, user, and ADR documentation.

## Editorial Workflow Baseline

The current domain baseline models this loop:

`Editorial Radar -> Insight Cards -> Content Plan -> Post Brief -> Draft -> Editorial Checks -> Manual Export -> Learning Loop`

Approval gates are marked at:

- Content Plan
- Post Brief
- Editorial Checks

This model is deliberately small. It exists to establish testable domain separation,
not to claim final product behavior.

## MVP Perimeter From the Brief

The first MVP should grow around five modules:

- Editorial Bible: audience, positioning, fabula, rubrics, style, boundaries, and blog
  goals.
- Sources and Insights: connected materials become insight cards with editorial
  relevance and risk scoring.
- Content Plan: AI proposes a plan that the author can approve, edit, or reject.
- Post Brief: the author approves the thesis, conflict, structure, evidence, tone, and
  risks before drafting.
- Draft and Review: text is drafted and checked by style, anti-AI, fact-checking, and
  policy review roles.

## Expected Future Architecture

The next architecture pass should turn the MVP perimeter into explicit boundaries.
Likely boundaries include:

- Editorial bible and author profile.
- Signal ingestion and insight scoring.
- Planning and approval gates.
- Brief generation and approval.
- Draft/editing workspace.
- Release and analytics.
- AI provider integration layer.
- Persistence and account/workspace model.

These are candidate boundaries only. They must be narrowed in the next architecture
slice before implementation expands.

## Assumptions

- The first production UI will be implemented with React + Vite + TypeScript because the
  provided design handoff already uses React-style reference screens.
- The design handoff is a visual/product context source, not a replacement for
  `glavred.md`.
- GitHub repository creation is deferred until explicit user confirmation.
- Manual export is acceptable for the first product version because the brief allows
  publication to stay manual or export-based at MVP stage.

## Open Architecture Questions

- What is the first end-to-end product flow?
- Does the first version require backend persistence?
- Which AI provider and model access pattern should be used?
- Should release integrations be real in the first slice or represented as draft export?
- Should the first demo flow stop at an approved post brief or continue through draft
  and editorial checks?
