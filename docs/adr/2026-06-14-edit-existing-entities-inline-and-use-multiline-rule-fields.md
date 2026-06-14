# ADR: Edit Existing Entities Inline and Use Multiline Rule Fields

## Status

Accepted

## Context

Operational cabinet screens contain editable entity lists: radars, topics, fabulas,
signals, plan slots, archive records, and future post candidates. A user expects the
edit form to appear where the action was triggered. Rendering a duplicate edit form at
the top of the list breaks orientation, especially for long lists.

Radars also contain structured search rules and source descriptions. These are not
short scalar values. They may contain instructions, URLs, API/MCP notes, keyword sets,
or future provider constraints. One-line inputs make these values unreadable and
encourage shallow configuration.

## Decision

- Editing an existing entity opens the edit UI inside that entity row/card.
- Creating a new entity may use a temporary draft form above the list if the list
  toolbar is the source of the action.
- Existing entity edit mode must not create a detached duplicate form elsewhere on
  the page.
- Structured rule statements, search instructions, source descriptions, and similar
  long values use multiline `textarea` controls.
- Short scalar values such as titles, statuses, type selectors, and compact numeric
  settings may remain one-line controls.
- Design-system smoke tests must cover inline editing for large operational lists when
  the screen introduces a new edit pattern.

## Consequences

- Users keep spatial orientation while editing a long list.
- Radar configuration can carry realistic search instructions without cramped fields.
- Future entity catalogs should reuse inline read/edit/save/cancel behavior before
  introducing new edit surfaces.
- Visual/design smoke tests become part of the UX contract, not optional polish.

