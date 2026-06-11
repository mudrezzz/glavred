# ADR: Use Read/Edit/Save/Cancel For Editorial Entities

## Status

Accepted

## Context

Some earlier editorial setup controls applied changes immediately while author memory
used explicit edit and save actions. This made the product feel inconsistent and made
important editorial changes too easy to apply accidentally.

## Decision

Important editorial entities use read mode, explicit edit mode, `Сохранить`, and
`Отменить`. This applies to project profile, editorial rules, topics, fabulas, and the
compatibility matrix. Autosave still persists the workspace after a committed change.

## Consequences

Authors can explore edits without committing them. Tests can assert committed state
instead of intermediate draft state. Minor low-risk text fields may still use direct
editing only when the surrounding workflow already makes the commit boundary clear.

## Alternatives considered

- Immediate persistence for every field. Rejected for important setup entities.
- A global page-level save button. Rejected because small entity-level commits are
  clearer and easier to test.
