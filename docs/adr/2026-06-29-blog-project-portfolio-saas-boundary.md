# ADR: Blog Project Portfolio as the SaaS Boundary

## Status

Accepted

## Context

Glavred has grown from a single local-first editorial workspace into a drafting and
learning system with author memory, editorial models, DraftRun traceability, HITL
versions, and editorial learning notes.

The next product move is SaaS-shaped: users need authorization, more than one
project, and several independent blogs with different audiences, platforms, author
memory, editorial models, and benchmarks. At the same time, the product must not
collapse into a generic account shell or a platform autoposting tool. The core value
remains an AI-native editorial office that preserves and applies the author's
position.

The current implementation stores one local workspace. It is not safe to bolt
authentication, multi-platform posting, and benchmarks directly onto that singleton
workspace because project memory, learning notes, platform rules, and generated
drafts would become ambiguous.

## Decision

The next product boundary is `BlogProject`, not "workspace" and not "platform".

The target hierarchy is:

`UserAccount -> BlogProject -> Author Memory / Editorial Model / Publication Channels -> Content Production -> Platform Variants -> Learning`

Key rules:

- A `BlogProject` represents one independent blog/media system.
- Author memory, editorial rules, topics, fabulas, sources, plan, drafts, final
  decisions, and learning notes are project-scoped by default.
- A user may own or access several `BlogProject` records.
- The demo/benchmark portfolio should include two users and three blogs:
  - `AI Design Patterns`;
  - `Каша из топора`;
  - `Блог Главреда`.
- Platform/channel settings live below the project as `PublicationChannel` records.
- One editorial idea may later produce several platform variants, but topic/fabula
  concepts must stay reusable until a platform-specific post contract is resolved.
- Backend auth and persistence should wrap this project model rather than rewrite the
  DraftRun pipeline first.
- Autoposting remains later than channel modeling, variant generation, and manual
  publication-log readiness.

## Consequences

- The first implementation slices should create a local multi-account/project shell
  before introducing full backend auth.
- The current singleton `WorkspaceState` should be migrated into a project-scoped
  workspace map such as `workspacesByProjectId`.
- Demo data becomes a maintainable portfolio and benchmark suite, not one permanent
  AI Product Manager fixture.
- Benchmark evaluation can compare project isolation, author-memory leakage, platform
  adaptation, and drafting quality across blogs.
- Publication channels can evolve into adapters later without coupling fabulas to
  Telegram, LinkedIn, Dzen, or any other platform.

## Alternatives considered

- Add real backend auth first, keeping one workspace per account.
  - Rejected because it would create a SaaS shell around a singleton product model and
    postpone the actual multi-blog domain boundary.
- Add autoposting/platform integrations first.
  - Rejected because the product still needs explicit channel contracts, platform
    variants, and human approval before delivery adapters should matter.
- Duplicate fabulas per platform.
  - Rejected because the project already treats `Signal X Topic X Fabula` as reusable
    until final plan/contract resolution.
