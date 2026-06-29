# SaaS Blog Portfolio Architecture

Current as of Slice 2.17.0: SaaS Blog Portfolio Architecture.

This document defines the product and technical boundary for moving Glavred from one
local editorial workspace to a SaaS-ready portfolio of independent blogs. It is a
target architecture document for upcoming slices. It does not describe current runtime
behavior yet.

Related decision: `docs/adr/2026-06-29-blog-project-portfolio-saas-boundary.md`.

## 1. Product intent

Glavred should not become "one account with one content generator". The SaaS layer
must preserve the product's core frame: an AI-native editorial office where each blog
has its own memory, position model, editorial discipline, channels, production flow,
publication readiness, and learning loop.

The target hierarchy is:

```text
UserAccount
  -> ProjectMembership
    -> BlogProject
      -> Author Memory
      -> Editorial Model
      -> Publication Channels
      -> Signals / Plan / Editorial Work Queue
      -> Publication Groups
        -> Platform Variants
          -> DraftRun / Draft Versions / Final Decision
      -> Learning Notes
```

The key domain boundary is `BlogProject`. A project is one independent blog or media
system, not a technical workspace and not a platform.

## 2. Why this boundary comes before auth

Implementing login first would create a SaaS shell around the current singleton
workspace. That would leave the real product question unresolved: where does one blog
end and another begin?

Slice 2.17 therefore starts with:

1. architecture;
2. local multi-account/project shell;
3. demo portfolio;
4. backend auth/persistence;
5. publication channels;
6. multi-target variants;
7. multi-platform DraftRun contract;
8. benchmark runner.

This order keeps the implementation concentric. First the product can show several
independent blogs locally; then the backend can persist the already-understood domain.

## 3. Domain contracts

The concrete TypeScript/Python shapes will be added in later slices, but the ownership
and invariants are fixed here.

### `UserAccount`

Future authenticated principal.

Core fields:

```ts
interface UserAccount {
  id: string;
  displayName: string;
  email?: string;
  avatarUrl?: string;
  status: 'active' | 'disabled';
  createdAt: string;
}
```

Ownership:

- owns personal account identity;
- does not own blog content directly;
- accesses blog content through `ProjectMembership`.

### `ProjectMembership`

Link between a user and a blog project.

```ts
interface ProjectMembership {
  id: string;
  userId: string;
  projectId: string;
  role: 'owner' | 'editor' | 'viewer';
  status: 'active' | 'invited' | 'disabled';
}
```

V1 can keep only owner semantics, but the contract should not prevent team work later.

### `BlogProject`

One independent blog/media system.

```ts
interface BlogProject {
  id: string;
  ownerUserId: string;
  title: string;
  description: string;
  language: string;
  status: 'active' | 'archived';
  benchmarkRole?: 'demo' | 'privateBenchmark' | 'real';
  createdAt: string;
  updatedAt: string;
}
```

Project-scoped data:

- author notes and author memory events;
- author-position assertions;
- editorial rules, topics, fabulas, validators, and matrix;
- external sources, import candidates, archive records;
- radars, source signals, post candidates;
- content plan settings and plan items;
- editorial work items;
- DraftRun links and generated drafts;
- final decisions, version history, and editorial learning notes;
- publication channels and platform variants.

Invariant: project-scoped data from one blog must not influence another blog unless a
future explicit cross-project import/export action is added.

### `PublicationChannel`

Project-owned publishing destination.

```ts
interface PublicationChannel {
  id: string;
  projectId: string;
  platform: 'telegram' | 'linkedin' | 'dzen' | 'site' | 'other';
  title: string;
  handleOrUrl?: string;
  language: string;
  audience: string;
  role: 'primary' | 'repurpose' | 'experiment' | 'archive';
  defaultPublicationSizeProfileId?: string;
  publishingMode: 'manual' | 'adapterPlanned' | 'connected';
  status: 'active' | 'paused';
}
```

Channel is not the same as platform. A project may have two Telegram channels, or a
LinkedIn profile plus a LinkedIn newsletter. Platform-specific constraints resolve
through channel settings and `PostContract`, not by duplicating fabulas.

### `PublicationGroup`

Shared editorial idea that may produce one or more channel variants.

```ts
interface PublicationGroup {
  id: string;
  projectId: string;
  sourceWorkItemId: string;
  sharedBriefId: string;
  targetChannelIds: string[];
  status: 'drafting' | 'review' | 'ready' | 'released' | 'archived';
}
```

The group keeps the shared idea, source/evidence context, topic, fabula, and editorial
intent. It does not own the final text for every channel.

### `PlatformVariant`

Per-channel production state for one publication group.

```ts
interface PlatformVariant {
  id: string;
  publicationGroupId: string;
  projectId: string;
  channelId: string;
  draftRunId?: string;
  postContractId?: string;
  draftId?: string;
  finalVersionId?: string;
  readinessStatus: 'notStarted' | 'drafting' | 'needsReview' | 'approved' | 'ready';
}
```

Variant-scoped data:

- platform-specific post contract;
- publication size contract;
- draft candidates and selected final draft;
- HITL version history;
- final quality gate result;
- visual decision if platform-specific;
- release readiness and publication log entries.

## 4. Scope ownership table

| Data | Scope | Notes |
| --- | --- | --- |
| login identity | user | future backend auth |
| display preferences | user | later slice |
| author notes | project | default; no cross-blog leakage |
| editorial learning notes | project | accepted notes influence only their project |
| topics/fabulas | project | reusable across channels within one blog |
| publication size profiles | project/channel | defaults can be project-wide, selected per channel/contract |
| source signals | project | may come from project-specific radars/imports |
| content plan items | project | target channels added in later slice |
| shared post brief | publication group | one editorial idea |
| draft versions | platform variant | each channel can diverge |
| final decisions | platform variant | user can approve Telegram v2 and Dzen v1 separately |
| publication attempts | platform variant/channel | adapters write log entries |
| benchmark scenario | project | public fixtures or private gitignored pack |

## 5. Storage transition plan

### Current state

Current runtime has one `WorkspaceState` persisted through `LocalWorkspaceStore`.

### Slice 2.17.1 target

Wrap the current workspace in a local portfolio store:

```ts
interface PortfolioState {
  activeUserId: string;
  activeProjectId: string;
  users: UserAccount[];
  projects: BlogProject[];
  memberships: ProjectMembership[];
  workspacesByProjectId: Record<string, WorkspaceState>;
}
```

Migration rule:

- if old storage contains one `WorkspaceState`, wrap it into one `BlogProject`;
- keep old normalization as fallback;
- selected project hydrates the existing app shell;
- switching project swaps the workspace object and saves under the project id.

### Slice 2.17.3 target

Backend persistence should mirror the same boundary:

```text
/api/users/me
/api/projects
/api/projects/{projectId}
/api/projects/{projectId}/workspace
```

Backend route handlers stay thin. Project persistence belongs in application services.
The backend should not introduce a second domain shape that conflicts with the local
portfolio store.

## 6. UI / UX target

### Local portfolio shell

Top-level app flow:

1. choose demo/current user;
2. choose blog project;
3. enter the existing editorial cabinet for that project.

The first implementation should be restrained:

- topbar project switcher;
- project dashboard when no project is selected;
- visible project chips/cards;
- no complex organization/admin surface.

### Project dashboard

Each project card should show:

- title;
- language;
- primary channels;
- status;
- latest active production item;
- pending learning notes or quality risks when useful.

### Inside a project

Existing sections stay familiar:

- Author Memory;
- Editorial Model;
- Signals;
- Plan;
- Editing;
- Release;
- Analytics.

All sections read/write only the active project workspace.

## 7. Multi-platform publishing model

The first multi-platform implementation should not be a hidden monolithic DraftRun.
Use readable linked variants:

```text
Shared editorial idea
  -> PublicationGroup
    -> Telegram PlatformVariant -> Telegram DraftRun / versions / final
    -> Dzen PlatformVariant     -> Dzen DraftRun / versions / final
```

Shared:

- source signal;
- topic;
- fabula;
- approved brief;
- source/evidence context where safe;
- author position and project rules.

Per variant:

- channel;
- size profile;
- post contract;
- draft text;
- validation;
- HITL versions;
- final quality gate;
- visual/readiness/publication state.

This preserves the existing rule that `Signal X Topic X Fabula` is reusable until
platform/channel constraints are resolved in the final contract layer.

## 8. Planned demo and benchmark portfolio

The portfolio should include two users and three blogs.

### User A / Blog 1: `AI Design Patterns`

Purpose:

- aggregate scattered AI engineering/product practice into durable design patterns;
- reduce hype and identify what actually works;
- build the author's reputation as someone who deeply understands AI systems.

Likely channels:

- LinkedIn articles/newsletter as primary;
- optional Telegram companion notes.

Benchmark expectations:

- English-capable;
- research-heavy;
- explicit pattern naming;
- avoids "new tool appeared" hype;
- uses external evidence and practical examples;
- produces systematic synthesis, not a hot take.

### User A / Blog 2: `Каша из топора`

Purpose:

- author's RevOps/Product Marketing philosophy;
- ironic, opinionated, practical;
- Telegram-native cadence.

Likely channels:

- Telegram primary.

Benchmark expectations:

- strong author stance;
- irony and living voice;
- does not become a consulting memo;
- practical field observations;
- can reuse author memory without borrowing the AI Design Patterns voice.

### User B / Blog 3: `Блог Главреда`

Purpose:

- explain the product philosophy behind Glavred;
- show practical editorial methods and situations;
- describe why AI-native editorial discipline matters.

Likely channels:

- Telegram primary;
- Dzen as first long-form adaptation benchmark;
- LinkedIn can be added later for B2B/product reach.

Benchmark expectations:

- product narrative without generic marketing;
- build-in-public clarity;
- practical editorial advice;
- multi-platform adaptation from one idea to Telegram + Dzen.

## 9. Benchmark rules

The portfolio benchmark should evaluate:

- project isolation;
- author voice preservation;
- channel adaptation;
- research depth handling;
- source integration;
- final quality gate behavior;
- HITL revision usefulness;
- editorial learning note quality.

Private real inputs should not be committed to the public repository. The target split:

- public sanitized fixtures under normal demo fixtures;
- private gitignored benchmark pack for real notes, posts, or source material.

## 10. Architecture guardrails for implementation

Future implementation slices must follow these rules:

1. Do not add project switching by filtering one global workspace in UI only.
   Storage/domain must represent project ownership.
2. Do not make `PublicationChannel` a string alias for platform.
3. Do not duplicate fabulas per platform.
4. Do not let accepted `editorialLearning` notes influence other projects.
5. Do not add backend auth before project boundaries are testable locally.
6. Do not wire autoposting before channels, variants, manual readiness, and
   publication-log semantics exist.
7. Do not hide multiple platform variants inside one opaque DraftRun until separate
   variant traces have proven the contract.

## 11. Tests expected in implementation slices

Slice 2.17.1 should include:

- storage migration from singleton workspace to `PortfolioState`;
- project switching isolation tests;
- UI app-flow test for selecting user/project;
- regression that current demo workspace still opens after reset.

Slice 2.17.2 should include:

- seeded portfolio completeness tests;
- no cross-project memory inference tests;
- UI smoke for seeing all three blogs.

Slice 2.17.5/2.17.6 should include:

- shared brief plus separate variant state tests;
- per-channel draft/final approval tests;
- DraftRun context includes project/channel/variant identity.

## 12. Open decisions for later slices

- Which auth provider or dev auth mode should be used in 2.17.3?
- Whether `AI Design Patterns` should be LinkedIn newsletter-first or standalone
  site/blog-first.
- Whether Dzen should be implemented before LinkedIn adaptation for `Блог Главреда`.
- Whether user-level memory should ever exist, or whether all author memory should
  remain project-scoped until explicit cross-project import is designed.
