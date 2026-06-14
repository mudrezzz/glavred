# ADR: Measure Disclosure Stability and Form Rhythm

## Status

Accepted.

## Context

Operational cabinet screens contain expandable entity rows, sticky side panels,
section headers, filter toolbars, and editing forms. A visually small regression can
make the product feel unstable:

- expanding or collapsing a row can move the whole workspace horizontally;
- metric cards can drift away from the section header's right edge on wide screens;
- labels and controls in dense forms can touch each other;
- right panels can appear to overlap main content even when no page-level horizontal
  overflow is detected.

These issues are not reliably caught by build tests or by checking one static
screenshot.

## Decision

Design-system smoke tests must measure layout invariants for disclosure-heavy
screens:

- expanding and collapsing an entity row must not change the horizontal geometry of
  the section header, tabs, main/side grid, toolbar, or entity row;
- scroll containers reserve scrollbar gutter so centered cabinet content does not
  shift when page height changes;
- section-header metrics align to the right edge of the header card on desktop and
  wide desktop viewports;
- main-column children in a main/right-panel grid must stay inside the main column
  and keep the required gutter before the right panel;
- editor forms keep a measurable vertical rhythm between top-level fields;
- labels inside grouped controls keep a measurable gap before the input/select.

The current enforcement lives in `npm run test:design`.

## Consequences

- Disclosure regressions become automated failures instead of manual review findings.
- New cabinet sections should add layout-stability checks when they introduce
  expandable rows or a main/right-panel grid.
- These checks are structural, not pixel-perfect screenshot diffs. They should stay
  resilient while still rejecting overlap, drift, missing spacing, and unstable
  disclosure behavior.

## Alternatives Considered

- Rely on visual screenshots only. Rejected because a single screenshot does not
  compare expanded and collapsed states.
- Add strict screenshot diffs. Deferred because the design system is still evolving
  and structural invariants are a better fit for the current stage.
