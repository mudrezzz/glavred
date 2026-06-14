# ADR: Use Canonical Cabinet Primitives for Front-End Surfaces

## Status

Accepted.

## Context

Glavred has several dense operational screens: author memory, editorial model,
signals, planning, editing, release and analytics. Some screens started to drift:
similar actions used different button colors, entity toolbars used different
hierarchies, and metadata rows broke when optional data such as `lastRunAt` was
missing.

This made screens look locally assembled instead of belonging to one product system.

## Decision

The front end uses canonical cabinet primitives:

- Major section headers use a shared card pattern: label/title/description on the
  left, metric cards aligned to the right edge.
- Entity list toolbars use a compact everyday pattern: count and short description on
  the left, ordinary action button on the right.
- Button taxonomy is explicit:
  - white secondary buttons are for ordinary work actions, such as `+ Radar`,
    `+ Topic`, `Edit`, `Open`, `Cancel` and non-destructive navigation;
  - red primary buttons are reserved for validation, approval, commit and lifecycle
    actions, such as `Check`, `Approve`, `Save`, `Collect insight` and final HITL
    steps.
- Entity rows reserve stable metadata slots. Optional metadata must render a visible
  fallback instead of leaving a layout hole.
- New large front-end surfaces must either reuse these primitives or introduce a new
  ADR and corresponding design-smoke checks.

## Consequences

- Ordinary create actions no longer compete visually with validation or approval
  actions.
- Sections and list screens become easier to scan because count, action and metadata
  positions are predictable.
- The `npm run test:design` suite now checks the most important primitives: header
  metric alignment, entity toolbar action taxonomy, radar metadata slots and
  main/right layout boundaries.

## Alternatives Considered

- Continue tuning each screen independently. Rejected: this already produced visual
  drift.
- Make all important actions red. Rejected: it removes the distinction between
  ordinary work and validation/HITL commit actions.
