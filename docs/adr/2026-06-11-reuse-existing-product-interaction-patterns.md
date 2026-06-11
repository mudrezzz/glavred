# ADR: Reuse Existing Product Interaction Patterns

## Status

Accepted

## Context

Slice 1.1 introduced a `Редакционная модель` interface that visually diverged from
the already accepted `Память автора` patterns. This created inconsistent tabs,
controls, and page rhythm inside the same product shell.

## Decision

New product screens must reuse established cabinet patterns before introducing new
ones. Internal tabs use `.tabs` and `.tab`. Entity cards, action buttons, status chips,
and side panels must follow the current product system unless a new pattern is
explicitly documented.

## Consequences

The UI becomes more predictable and easier to extend. New deviations require a clear
reason and, when they affect multiple screens, an ADR or design-system update.

## Alternatives considered

- Let every slice invent local controls. Rejected because it caused inconsistent UX.
- Freeze all UI patterns. Rejected because the product still needs to evolve.
