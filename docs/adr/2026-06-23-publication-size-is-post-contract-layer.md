# ADR: Publication size is a post contract layer

## Status

Accepted

## Context

Glavred combines `Signal X Topic X Fabula` across platforms. Some publication-size
constraints come from a platform and publication kind, while some size pressure comes
from dramaturgy. Hard-linking fabulas to platforms would create duplicate fabulas and
make the topic/fabula matrix harder to maintain. Putting size on `PostCandidate` would
also pollute the concept layer with delivery constraints.

## Decision

Publication size is resolved after planning, inside the DraftRun quality spine:

1. `ContentPlanSettings.publicationSizeProfiles` stores editable demo profiles.
2. `ContentPlanItem.publicationSizeProfileId` may lock a slot to one profile.
3. `Fabula.sizeIntent` stores only dramaturgical scale: `compact`, `standard`, or
   `deep`.
4. Backend resolves these inputs into `PostContract.publicationSizeContract`.
5. `RuleRegistrySnapshot` emits deterministic rules for hard max length, target range,
   paragraph/section range, and density.

Future validators, lints, and revision steps must consume the size rules by id from
`RuleRegistrySnapshot`; they must not re-derive length policy from prompt prose.

## Consequences

- `PostCandidate` does not regain `format` or size fields.
- Fabulas are not duplicated per platform.
- Plan settings can evolve platform/kind profiles without changing candidate or
  fabula semantics.
- Slice 2.11.1 does not enforce length yet; it creates the machine-readable contract
  for future validators and rhetorical plans.
