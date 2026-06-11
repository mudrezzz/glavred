# ADR: Make Validation A First-Class UX Surface

## Status

Accepted

## Context

The product depends on validators: author position, style, anti-AI quality, audience
value, topic/fabula consistency, and later archive uniqueness. Validation cannot be a
hidden background process or a late report.

## Decision

Every editorial setup tab shows a validation panel. Slice 1.1.1 uses deterministic
demo validation, but the UX contract is stable: summary status, colored indicators,
evidence or rationale, and actionable recommendations.

## Consequences

Future validator framework work has a clear UI surface. Authors can see why the system
is concerned and what to fix before generated content depends on the setup.

## Alternatives considered

- Validate only on submit. Rejected because setup is iterative.
- Show validator output only inside future chat. Rejected because validation must be
  visible even without chat.
