# ADR: Publication Channel Does Not Own Project Audience

## Status

Accepted

## Context

Slice 2.17.4 introduced project-scoped `PublicationChannel` so a blog can describe
where it publishes: Telegram, LinkedIn, Dzen, site, or another destination.

The first channel model also carried `audience`. That duplicated the editorial
audience already owned by the project editorial model and created an ambiguous
handoff for DraftRun context: the generator could accidentally read audience from
the channel card instead of the central editorial contract.

The problem became visible during the `Северная стена` project rework. The project
audience belongs to the editorial model and publisher positioning, while the channel
only says where the blog is published and which platform/profile constraints apply.

## Decision

`PublicationChannel` does not own project audience.

Audience ownership is:

- project-level source: active `WorkspaceState.editorialRules` in the `audience`
  group;
- compatibility summary: `WorkspaceState.editorialModel.audience`, derived from
  rules where possible and used only as a legacy fallback;
- post-level override: `PostBrief.audience`;

`PublicationChannel` owns destination data and channel constraints:

- platform;
- title;
- handle or URL;
- language;
- role;
- publishing mode;
- status;
- default publication size profile.

Legacy snapshots may still contain `PublicationChannel.audience`, but new UI and
DraftRun context ignore it. Channel editing does not expose audience. DraftRun context
uses `PostBrief.audience || editorialRules(audience) || legacy EditorialModel.audience`
and never reads channel audience.

## Consequences

- Channel cards and forms stay focused on destination setup.
- The editable publisher rules remain the single project-level source for audience.
- Legacy `EditorialModel` summary fields stay available for old snapshots and narrow
  compatibility APIs, but they must be derived from rules during normalization when
  rules exist.
- DraftRun prompt context is easier to audit because audience does not depend on the
  selected channel.
- Future per-channel nuance must be modeled as platform adaptation notes, channel
  constraints, or platform variants, not as a second audience source.
- Old workspace snapshots remain readable during the transition.

## Alternatives considered

- Keep audience on channels: rejected because it duplicates editorial settings and
  creates hidden generation drift.
- Auto-copy editorial audience into every channel: rejected because copied fields
  become stale and look editable.
- Add full per-channel audience segmentation now: rejected as premature before
  platform variants and multi-target generation are implemented.
