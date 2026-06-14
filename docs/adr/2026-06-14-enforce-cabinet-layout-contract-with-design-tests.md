# ADR: Enforce Cabinet Layout Contract with Design Tests

## Status

Accepted.

## Context

Glavred is a dense operational cabinet. User-facing screens reuse patterns such as
section headers, stat cards, tabs, side panels, entity rows, edit forms, and action
footers.

Several UI regressions were not caught by ordinary unit tests or build smoke:

- a local section header diverged from the `Редакционная модель` header pattern;
- counters inside tabs were rendered as plain text;
- main content overlapped the right panel;
- form controls and grouped sections used inconsistent widths;
- action buttons touched each other because no formal gap rule existed.

These are not cosmetic issues. In an editorial workflow they make entity ownership and
available actions ambiguous.

## Decision

The cabinet UI has a formal layout contract:

- major sections use the existing project/profile header pattern or an explicitly
  documented derivative;
- cards and panels must have visible internal padding;
- tabs with counts use the shared red badge/count pattern;
- normal right panels are grid columns, not overlays, and must not overlap main
  content;
- main/side grid screens must keep a measurable gutter between the content column
  and the right panel; for dense entity workspaces this is at least 28px;
- direct working blocks inside the main column, such as filters, entity rows and
  toolbars, must not overflow into the right-panel gutter even when their internal
  controls have long labels;
- metric blocks inside project/profile-style headers align to the right edge of the
  header card, so they visually relate to the right-side operational column;
- overlay behavior is reserved for components that are explicitly designed as overlays,
  such as the context chat;
- action groups have a measurable gap between buttons;
- edit forms keep base fields and grouped rule/source sections aligned to the same
  working width;
- horizontal overflow on operational screens is a failure.

The repository must keep a design-system smoke test alongside runtime tests:

- `npm run test:design` checks layout invariants across key cabinet screens;
- `npm run test:visual` remains for high-risk screen-specific visual behavior;
- new large cabinet screens should add design-smoke coverage before being considered
  done.

## Consequences

- UI regressions become visible before manual review.
- New screens must reuse existing layout primitives instead of inventing local
  one-off shells.
- The design checks are not pixel-perfect screenshot tests; they measure structural
  constraints that should remain stable across responsive layouts.
- When a new legitimate layout pattern appears, the ADR and design-smoke script should
  be updated together.

## Alternatives Considered

- Rely only on manual screenshot review. Rejected: it allowed repeated layout drift.
- Use strict screenshot diffs. Deferred: useful later, but too brittle for the current
  local-first demo while the design system is still evolving.
