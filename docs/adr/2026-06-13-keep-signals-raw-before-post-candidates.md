# ADR: Keep Signals Raw Before Post Candidates

## Status

Accepted

## Context

Slice 1.5 introduced `Сигналы`, but the first implementation mixed two product
layers: raw radar findings and post candidate assemblies.

That makes planning brittle. A found signal should answer "what did we find and why is
it potentially useful?" It should not already decide topic, fabula, audience, and value.

## Decision

`SourceSignal` is treated as raw material from a radar.

The primary signal fields are:

- radar provenance;
- captured date;
- title/finding;
- summary;
- evidence sources and quotes;
- raw note;
- search/duplicate-risk note;
- duplicate risk;
- review status;
- author correction.

Topic, fabula, target audience, value, goal, platform, and format are assigned in the
next layer: `PostCandidate`.

Temporary compatibility fields may remain in runtime objects while the existing
downstream flow is migrated, but `Найденные сигналы` UI must not present those fields as
the signal's responsibility.

## Consequences

- `Найденные сигналы` filters by radar, status, duplicate risk, evidence/source, date,
  and search text, not by topic/fabula.
- Approving a signal means "allow this material to become a post candidate", not
  "approve a post concept".
- Slice 1.6 must introduce candidate assemblies as
  `Signal + Topic + Fabula + Audience + Value + Goal`.
- The plan/calendar should not fill slots directly from raw signals.

## Alternatives considered

- Continue assigning topic/fabula on `SourceSignal`. Rejected because that makes a raw
  finding indistinguishable from a post concept.
- Remove compatibility fields immediately. Deferred because existing insight, plan,
  brief, release, and analytics services still use `sourceSignal` until candidate
  assemblies are implemented.
