# ADR: Add Visual Guardrails for Operational UI

- Status: Accepted
- Date: 2026-06-12

## Context

The `Память автора -> Источники` source list regressed visually after a layout change:
source titles collapsed into narrow vertical text columns, actions remained visible but
the row became unreadable, and the autosave toast stayed visible as a permanent bottom
overlay.

Existing tests covered DOM presence and application behavior, but they did not inspect
real rendered dimensions in a browser. Wiki screenshots were generated, but screenshot
generation alone did not fail the build when a layout became unusable.

## Decision

Operational UI surfaces that introduce or materially change a catalog/list layout must
have browser-level visual smoke checks.

For now the baseline visual smoke checks are scripted with Playwright and run through:

```bash
npm run test:visual
```

The checks must verify at least:

- no persistent autosave/status toast is visible on initial render;
- catalog rows do not overflow horizontally;
- primary entity titles retain a usable width and do not collapse into tall narrow
  columns;
- row actions remain inside the row bounds;
- event toast appears after an explicit action and disappears automatically.

Operational entity catalogs must avoid dense multi-column CSS grids unless the layout
has real-browser checks for the target viewport. Prefer a stable row structure:

- header: entity type/title/status;
- metadata: separate wrapping line;
- actions: explicit row action area;
- details: expandable block below the row.

## Consequences

- UI regressions that DOM tests cannot see should fail before manual review.
- New operational catalog layouts need either to reuse existing checked patterns or add
  visual smoke coverage.
- Autosave/status messaging is event-driven and temporary; permanent bottom overlays
  are not used for local workspace status.

## Alternatives Considered

- Rely only on Testing Library DOM tests. Rejected because they cannot detect collapsed
  text columns or overflow.
- Rely only on documentation screenshots. Rejected because screenshots are artifacts,
  not assertions.
- Full pixel-perfect screenshot baselines for every screen. Deferred because the
  current need is structural guardrails, not exact pixel matching.
