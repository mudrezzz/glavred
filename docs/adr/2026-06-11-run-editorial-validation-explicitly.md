# ADR: Run Editorial Validation Explicitly

## Status

Accepted

## Context

Editorial setup is filled gradually. Live validation while the author is still adding
rules, topics, fabulas, and matrix links can produce noisy intermediate conclusions and
make the product feel like it is judging unfinished work.

## Decision

Editorial setup validation must be triggered explicitly by the author through a
`Проверить` action. The validation panel may show the latest saved validation snapshot,
but it must mark the result as stale after committed setup changes. It must not present
fresh conclusions while the author is typing or before the author asks for a review.

## Consequences

The author controls when feedback is generated. Future AI validators and context chat
can reuse the same interaction model: propose feedback after an explicit validation
run, not on every keystroke.

## Alternatives considered

- Live validation after every state change. Rejected because it creates premature and
  noisy feedback.
- Validate only at final publishing time. Rejected because setup problems should be
  visible before content production depends on them.
