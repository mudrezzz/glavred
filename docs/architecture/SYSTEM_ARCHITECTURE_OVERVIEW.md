# System Architecture Overview

## Current State

This repository has a frontend-first project foundation:

- React + Vite + TypeScript application shell.
- A small domain model for the editorial workflow.
- Vitest-based test baseline.
- Design handoff in `ui-design-systems/`.

The primary requirements file is `glavred.md`, but it is currently empty. Product
architecture beyond the foundation is intentionally not finalized yet.

## Initial Boundaries

The first baseline keeps these responsibilities separate:

- `src/domain/`: domain concepts that should not depend on React, browser APIs, or
  infrastructure.
- `src/App.tsx`: temporary application shell that renders the current baseline.
- `ui-design-systems/`: reference design materials, not production source code.
- `demo/`: demo documentation and future demo assets.
- `docs/`: architecture, developer, contributor, user, and ADR documentation.

## Editorial Workflow Baseline

The current domain baseline models this loop:

`Sources -> Insights -> Plan -> Brief -> Draft -> Editing -> Release -> Analytics`

Approval gates are marked at:

- Plan
- Brief
- Editing

This model is deliberately small. It exists to establish testable domain separation,
not to claim final product behavior.

## Expected Future Architecture

After `glavred.md` is filled in, the architecture should be revised around the first
working product perimeter. Likely boundaries include:

- Editorial bible and author profile.
- Signal ingestion and insight scoring.
- Planning and approval gates.
- Brief generation and approval.
- Draft/editing workspace.
- Release and analytics.
- AI provider integration layer.
- Persistence and account/workspace model.

These are candidate boundaries only. They must be validated against the source brief.

## Assumptions

- The first production UI will be implemented with React + Vite + TypeScript because the
  provided design handoff already uses React-style reference screens.
- The design handoff is a visual/product context source, not a requirements substitute.
- GitHub repository creation is deferred until explicit user confirmation.

## Open Architecture Questions

- What is the first end-to-end product flow?
- Does the first version require backend persistence?
- Which AI provider and model access pattern should be used?
- Should release integrations be real in the first slice or represented as draft export?
