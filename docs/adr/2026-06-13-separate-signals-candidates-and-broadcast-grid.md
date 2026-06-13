# ADR: Separate Signals, Post Candidates, and Broadcast Grid

## Status

Accepted

## Context

Slice 1.4 introduced a broadcast grid in `План`. The first implementation is useful as
a local-first planning prototype, but it still lets the plan appear as if posts can be
generated directly from topics, fabulas, and weights.

That is not the intended product model. The author needs a system where raw material
is discovered, reviewed, corrected, and assembled into post concepts before a calendar
slot can become real work.

## Decision

We separate three responsibilities:

- `Сигналы`: radar findings and manually supplied material from author memory,
  archives, external sources, and manual input.
- `Кандидаты постов`: proposed combinations of signal, topic, fabula, audience, value,
  goal, platform, and format.
- `План`: broadcast demand and calendar status: tempo, period, publishing days/times,
  candidate requirements, and slot readiness.

`План` should not continue growing as a full calendar product until `Сигналы` and
`Кандидаты постов` exist. The next implementation slices should first create a
signals/radar workspace, then post candidate assemblies, then return to deeper planning
settings and calendar views.

The current broadcast grid remains valid as a prototype and compatibility layer, but
it is not the final planning architecture.

## Consequences

- `Радар` should evolve into `Сигналы`.
- Radars become configurable sources and procedures inside `Сигналы`, not a single
  source-card step.
- Calendar slots can be empty, waiting for signal approval, filled with candidates,
  approved as a concept, in production, ready, or published.
- Signal corrections and candidate corrections become author-memory evidence.
- Archive material is a signal source, so archive/uniqueness work should follow the
  signal planning correction rather than precede it.
- Future AI/provider usage can be budget-aware: radars run when the plan has a
  deficit, not continuously.

## Alternatives considered

- Continue enriching `План` directly with calendar UI. Rejected because it would
  produce a better-looking schedule without the material and HITL layer needed to fill
  it.
- Treat every found signal as a plan slot. Rejected because a publishable post concept
  is a combination of signal, topic, fabula, audience, value, and goal, not just a
  source event.
- Put candidate generation inside `Редакционная модель`. Rejected because the model
  defines constraints and weights; it should not own production material.
