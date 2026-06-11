# ADR: Keep Editorial Entity Layouts Contained

## Status

Accepted

## Context

Topic, fabula, and matrix screens can contain long names, long rules, multiple
metadata chips, and wide compatibility tables. If rows use rigid columns and detail
blocks do not wrap or scroll, text escapes the card and the author loses context.

## Decision

Editorial entity layouts must be containment-first:

- compact rows wrap names and metadata instead of overflowing;
- preview/detail areas wrap text and use one shared scroll container when content is
  long;
- edit forms keep every input inside the entity container;
- compatibility matrices use a horizontal scroll container;
- matrix first columns stay sticky so the topic name remains visible while scrolling.

## Consequences

The setup UI remains usable with realistic long editorial entities. Future tables,
catalogs, validator evidence views, and archive lists should follow the same
containment rules.

## Alternatives considered

- Fixed equal-width columns everywhere. Rejected because they break with realistic
  content.
- Independent scrollbars inside every field. Rejected because nested scrolling makes
  review and editing harder.
