# ADR: Use Deterministic Services Before AI Integration

## Status

Accepted

## Context

The source brief assumes AI agents for scouting, analysis, planning, briefing, writing,
style editing, anti-AI cleanup, fact-checking, policy review, distribution, and growth
analysis. The first working perimeter only needs to prove the flow from signal to
approved post brief.

Real AI integration would introduce provider choice, model prompts, API keys, cost,
latency, error handling, factuality concerns, and evaluation before the product's domain
shape is stable.

## Decision

Slice 0.4 will model AI-like behavior with deterministic application services and
fixtures. These services will produce insight, plan, and brief outputs from the demo
scenario without calling external AI providers.

## Consequences

- The first implementation is testable, repeatable, and inexpensive.
- AI provider selection remains an explicit later decision.
- Service interfaces should be shaped so future AI adapters can replace deterministic
  implementations.
- The first demo must not imply real AI generation is already implemented.

## Alternatives considered

- Integrate an AI provider immediately: closer to the long-term product, but premature
  and harder to test reliably.
- Use static UI fixtures only: simpler, but it would not exercise application service
  boundaries.
