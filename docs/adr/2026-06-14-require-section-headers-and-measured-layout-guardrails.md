# ADR: Require Section Headers and Measured Layout Guardrails

## Status

Accepted.

## Context

Operational cabinet screens can look formally “tested” while still being hard to read:
tabs may replace the section header, action buttons may touch metadata, side panels may
overlap main content, and compact rows may degrade into unstable pseudo-tables.

This happened in `Сигналы`: the product logic was correct, but the UI did not clearly
show where the author was, what belonged to a radar or signal, and which actions were
part of the current entity.

## Decision

Every major workspace must have an explicit section header before local tabs:

- section name;
- short user-facing purpose;
- compact status counters when useful.

Operational entity rows must not rely on fragile equal-width table layouts unless the
screen is a real table. Default pattern:

- framed row/card;
- stable left identity area;
- flexible body;
- metadata/actions grouped inside the same entity container;
- expanded details remain inside the same card;
- footer actions have measured spacing and a separating border.

Visual smoke tests for new or repaired large workspaces must check more than
horizontal overflow:

- section header exists;
- main and side columns do not overlap;
- entity row has a visible frame/background;
- status chips do not wrap;
- action buttons have at least an 8px gap;
- side-panel actions have enough top spacing;
- edit forms do not overflow their card;
- expanded details stay inside the parent entity card.

## Consequences

- Product sections remain understandable even before the user reads every tab.
- Design-system drift becomes easier to catch in automated visual checks.
- Screens with dense operational data can still be compact, but must not become
ambiguous or visually fragile.
- Visual tests become stricter and may require updates when layout patterns change.
