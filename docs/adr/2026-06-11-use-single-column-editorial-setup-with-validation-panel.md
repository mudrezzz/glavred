# ADR: Use Single-Column Editorial Setup With Validation Panel

## Status

Accepted

## Context

The two-column editorial setup grid made the interface look like a settings dump and
made rule-level validation hard to follow. The user needs a workflow, not a wall of
text boxes.

## Decision

Editorial setup screens use a main single-column workflow plus a right-side validation
panel. Blocks appear vertically: project/rules, topics, fabulas, or matrix in the main
column; deterministic or future AI validation appears in the side panel.

## Consequences

The screen has one reading direction, validation is always visible, and future context
chat can reuse the right-side area without redesigning the page. On narrow screens,
the validation panel stacks below the main workflow.

## Alternatives considered

- Two-column card grids. Rejected for setup workflows because they reduce scanability
  and create nested-card clutter.
- Full-width validation below the page. Rejected because validation must be visible
  while the author edits.
