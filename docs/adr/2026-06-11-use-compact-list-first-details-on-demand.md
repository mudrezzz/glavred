# ADR: Use Compact List First, Details On Demand

## Status

Accepted

## Context

Topics and fabulas can grow. Showing every field for every entity creates a long,
hard-to-scan page and repeats the same information density problems as settings
forms.

## Decision

Entity catalogs use compact rows first. One row shows name, weight, status, rule count,
compatibility count, and validation badge. The author expands one entity to inspect
details and enters edit mode only for that entity.

## Consequences

Catalogs stay scannable with many topics or fabulas. Detail and edit affordances remain
available without making the default view heavy.

## Alternatives considered

- Large cards for every entity. Rejected because it does not scale.
- Tables with no expandable detail. Rejected because topics and fabulas need rich
  domain fields.
