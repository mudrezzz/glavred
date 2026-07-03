# ADR: Upstream Search and Signal Boundary

## Status

Accepted

## Context

Glavred has invested heavily in downstream drafting: approved post concepts can move
through planning, workbench preparation, DraftRun, validation, revision, final quality
gate, HITL versions, and learning notes. The upstream side is weaker. Radars,
source signals, and post candidates exist, but the app still depends on seeded or
manually reviewed material and a mechanical candidate assembly path.

The project now needs a real upstream boundary before continuing multi-platform
downstream work. Otherwise platform variants will multiply weak ideas instead of
helping authors find better material.

## Decision

Glavred's upstream flow is:

`SourceRegistry -> RadarRun -> FoundMaterial -> SourceSignal -> SignalScore -> PostCandidate -> Plan -> DraftRun`

`DraftRun` is downstream. It may enrich evidence for one approved brief, but it is
not the first place where the product discovers what to write about.

`SourceSignal` remains raw/reviewed material. It does not own topic, fabula, target
audience, value, goal, platform, format, or publication channel. Those decisions
belong to `PostCandidateAssembly` and planning.

The current blind Cartesian candidate pairing in `createPostCandidates` is legacy v1
fallback behavior until Slice 2.17.4.8 replaces it with explainable candidate
assembly.

Provider-backed search, URL reading, extraction, and review live behind
application/infrastructure adapters. React components render upstream state and collect
human decisions; domain modules stay provider-free.

## Consequences

- Future radar execution must produce `FoundMaterial` and traceable `RadarRun`
  artifacts before source signals.
- Future signal scoring must explain editorial fit before candidate assembly.
- Future post candidates must explain why a `Signal x Topic x Fabula` match works or
  was rejected.
- Multi-platform planning remains valid, but it waits until upstream can produce
  stronger candidate inputs.
- Existing `RadarDefinition`, `SourceSignal`, and `PostCandidate` compatibility shapes
  remain valid during migration.

## Alternatives considered

- Move all public research into DraftRun. Rejected because it hides discovery inside
  the final drafting run and makes candidate quality impossible to inspect before
  planning.
- Put topic/fabula suggestions back onto `SourceSignal`. Rejected because it repeats
  the earlier layer confusion fixed by the raw-signal ADR.
- Build multi-platform variants first. Deferred because variant work increases the
  cost and surface area of weak upstream ideas.

