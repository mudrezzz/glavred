# Use Single-Column Lists for Operational Entity Catalogs

## Status

Accepted

## Context

Glavred has several operational catalogs: author sources, topics, fabulas, future
platforms, formats, content design records, validators, and archive entries. These
entities are not marketing cards or visual gallery items. The author scans them,
compares state, expands details, and performs actions.

The `Память автора -> Источники` screen originally used a two-column card layout. It
looked inconsistent with the newer `Темы` and `Фабулы` UX, made long titles and
status metadata harder to compare, and reintroduced a layout pattern we decided to
avoid for editable editorial entities.

## Decision

Operational entity catalogs must use a single-column, list-first layout:

- one entity per row;
- key metadata visible in the row;
- details available on demand by expanding the row;
- actions attached to the row;
- long titles and metadata must wrap inside the row instead of overflowing;
- multi-column card grids are not used for editable or reviewable editorial entities.

Two-column cards remain acceptable only for non-operational visual galleries or
dashboard summaries where the user is not primarily comparing, editing, or reviewing
entities.

## Consequences

- `Память автора -> Источники` uses the same list/detail pattern as topics and fabulas.
- Future catalogs should reuse this pattern before inventing a new layout.
- The UI remains denser and more predictable for long expert-content entities.
- Tests should prefer structural checks for list rows and detail expansion instead of
assuming card grids.
