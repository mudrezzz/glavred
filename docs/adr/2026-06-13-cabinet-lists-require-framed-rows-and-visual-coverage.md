# ADR: Cabinet lists require framed rows and visual coverage

## Status

Accepted

## Context

Working cabinet screens contain many operational entities: author notes, sources, radars, signals, topics, fabulas, plan slots and post candidates. When a new list is rendered as loose text, transparent buttons or unframed metadata, the user cannot tell which controls belong to which entity. This breaks the product's editorial-cabinet design language and makes review impossible.

## Decision

All operational entity lists in the cabinet UI must use framed rows or cards:

- each entity row owns its metadata, detail preview and actions inside one visible container;
- collapsed rows must preserve readable title width and stable metadata/chip layout;
- expanded details must remain inside the same row/card;
- status and risk chips must not wrap by letters or become tall badges;
- filter toolbars for entity lists must be framed and visually separate from rows;
- large entity lists use the shared sequence `filter card -> search -> list/group
  toggle -> framed rows -> bottom-left actions`;
- a large entity list must not put a hero/summary block above the filter card when the
  first user task is filtering or reviewing entities;
- every new major list screen must have visual smoke coverage before acceptance.

## Consequences

New UI slices must add `data-testid` hooks for important rows and include visual checks for frames, overflow and chip sizing. The visual smoke suite becomes part of the product quality gate, not only a regression aid.

## Alternatives considered

- Rely only on unit tests. Rejected because DOM presence tests do not catch layout collapse.
- Allow each screen to choose its own list style. Rejected because the cabinet needs consistent scanning and editing patterns.
