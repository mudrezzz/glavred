# ADR: Radar Evidence Delivery and Source Posture

- Status: Accepted
- Date: 2026-07-23
- Slice: `2.17.4.7.1.1.1`

## Context

RadarRun previously treated a requirement as covered when its query executed, even
when no suitable result was read or used by a signal. Source credibility was also
evaluated twice: a provider-backed radar criterion could pass while the deterministic
quality check still classified the publisher as unknown or interested.

## Decision

Search coverage is split into seven typed delivery stages:

`planned -> queryExecuted -> resultFound -> selectedForRead -> readableEvidence -> usedBySignal -> corroborated`

`discoveredRequirementIds` records query lineage. `supportedRequirementIds` records
deterministic evidence-target fit. Only supported requirements compete for read
coverage. A required requirement is delivered only when readable evidence is used by
a review-eligible signal.

Source posture has two independent axes:

- ownership: `independent | firstParty | vendor | unknown`;
- claim support: `singleSource | corroborated | contradicted | notChecked`.

One backend policy owns both axes. Provider output may provide semantic evidence but
cannot promote deterministically first-party or vendor provenance to independent.
Source-credibility criteria are reconciled with this assessment before the final
recommendation.

## Consequences

- Executed search and delivered evidence are visible separately.
- A vendor page returned by a benchmark query does not become independent evidence.
- Two URLs from one publisher do not count as corroboration.
- Useful first-party cases remain reviewable, but reported outcomes without
  corroboration carry caution.
- Search calls, read caps, provider budgets, API endpoints and SQLite schema do not
  change.

## Alternatives Rejected

- Treat query lineage as evidence fit: preserves the false guarantee.
- Let the scoring model decide ownership: not reproducible and can contradict known
  provenance.
- Add a separate corroboration provider call: unnecessary cost and outside the
  current bounded search contract.
