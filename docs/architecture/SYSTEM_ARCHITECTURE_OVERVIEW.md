# System Architecture Overview

## Product Context

Glavred is an AI-native editorial office for personal and expert media. The product is
not a generic post generator and not a source-signal compiler. It helps an author
capture raw thoughts, reactions, corrections, archive material, and post-release
learning, turn them into a transparent author position model, and use that model to
plan, validate, draft, and release content.

The primary requirements source is `glavred.md`. The design handoff in
`ui-design-systems/` is a secondary visual and product reference. The June 2026 product
revision adds `AuthorMemory` and `AuthorPositionModel` as the conceptual center of the
system. The existing **Редакционная модель** / `EditorialModel` should evolve into a
set of structured, validator-backed editorial entities rather than remain a single
configuration block.

The revised product concept is documented in
`docs/architecture/AUTHOR_POSITION_CONCEPT.md`.

The external source and import-review concept is documented in
`docs/architecture/EXTERNAL_SOURCE_IMPORT_CONCEPT.md`.

The revised signal and broadcast planning concept is documented in
`docs/architecture/SIGNALS_AND_BROADCAST_PLANNING_CONCEPT.md`.

## Strategic Product Model

The durable model is:

`AuthorMemory -> AuthorPositionModel -> EditorialSystem -> Signals -> ContentProduction -> Release -> Learning`

- `AuthorMemory`: a lightweight internal feed of thoughts, reactions, links,
  corrections, small local attachments, archive notes, and post-release learning. It
  must allow loose stream-of-consciousness input.
- `AuthorPositionModel`: a transparent, evidence-backed digest of that memory:
  persona, style, audience, goals, metrics, topics, fabulas, platforms, formats,
  Content Design Records, and validators.
- `EditorialSystem`: structured rules, weights, compatibility matrices, and
  validation contracts that describe how the author publishes.
- `Signals`: radar findings and manually supplied material from author memory,
  archives, external sources, and manual input.
- `ContentProduction`: the downstream layer: approved signals, post candidates,
  broadcast slots, post briefs, drafts, checks, release, and analytics prep.

The main product risk is generic AI compilation. Glavred avoids it by making the
author's own position explicit, editable, evidence-backed, and continuously validated.

## Current Implemented Perimeter

The current implemented perimeter now starts with author memory and reaches a captured
editorial learning note:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> RadarDefinition -> reviewed SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

The source-to-release part remains useful as a production layer. It is no longer the
conceptual center of the product. Author memory, author-position assertions,
structured topics/fabulas, validator results, and reviewed signals now sit above that
flow; future slices should route post candidates and calendar slots through them.

Slice 1.5 adds the first local-first `Сигналы` workspace: demo radars, found signals,
manual review actions, and a read-only `Кандидаты постов` preview. The deeper planning
model still needs Slice 1.6 candidate assemblies before expanding the calendar UI.

Real AI provider calls, publication automation, backend sync, and real metrics
ingestion remain future slices. The near-term priority is not provider integration; it
is making the author's own position explicit enough that AI can later assist without
turning the product into generic content generation.

## Major Components

- `AuthorMemory`: captures raw author notes, reactions, links, archive annotations,
  manual corrections, rejected angles, draft revisions, and post-release learning
  events.
- `AuthorPositionModel`: aggregates memory into transparent rules and assertions about
  persona, style, audience, goals, topics, fabulas, platforms, and formats. Every
  assertion should have evidence.
- `ProjectProfile`: names the virtual publishing project and carries setup status and
  top-level context for the editorial cabinet.
- `EditorialRules`: stores atomic rules for author, audience, positioning, style,
  anti-AI patterns, goals, and forbidden topics. These are the validator-ready
  successor to large editorial settings textareas.
- `EditorialModel`: compatibility aggregate for author, audience, positioning, legacy
  fabula, legacy rubrics, style rules, forbidden topics, and blog goals. Legacy fields
  remain available to downstream services while the UI moves toward structured rules.
- `TopicCatalog`: stores editable topic cards with purpose, audience value, author
  stance, rules, forbidden angles, status, and advisory weight ranges for planning.
- `FabulaCatalog`: stores reusable post dramaturgy patterns with structure, conflict,
  proof requirements, rules, status, advisory weight ranges, and compatibility with
  topics.
- `ContentDesignRecords`: stores durable content decisions that apply across posts,
  similar to ADRs in software projects.
- `PlatformProfiles`: stores platform and format rules, local validator requirements,
  and planning weights.
- `ValidatorFramework`: evaluates entities and production artifacts, returning score,
  status, evidence, and fix guidance.
- `ContextChat`: topbar-triggered, tabbed overlay assistant synchronized with the active
  product section and internal tab. The current implementation is deterministic,
  provider-free, supports local chat replies and suggestions, and can open safe draft
  flows for structured entities without saving changes automatically.
- `SignalsWorkspace`: reviews radar findings and manually supplied material before it
  can become a post concept.
- `EditorialRadar`: configurable source procedure inside `Сигналы`. Radar output is
  fuel for author memory and content production, not the only source of posts.
- `ExternalSourceSettings`: stores planned or connected source configurations for
  Telegram, social profiles, blogs, documents, article archives, and manual uploads.
- `ImportReviewQueue`: holds imported candidates before they affect author memory,
  archive, or author-position assertions.
- `ImportCandidateGroups`: groups large imports by source, date, tag, duplicate
  cluster, evidence risk, or status so the author can review patterns instead of
  every item.
- `BulkImportActions`: records reversible bulk choices such as `Добавить все`,
  accepting selected items into archive, or ignoring selected items as evidence.
- `ArchiveRecords`: stores accepted historical posts and long-form materials with
  provenance and evidence policy.
- `PostCandidateAssembly`: combines a reviewed signal with topic, fabula, audience,
  value, goal, platform, and format options before a post concept is approved.
- `InsightScoring`: turns a reviewed source signal into an insight card with relevance,
  urgency, banality risk, fact gaps, suggested topic, and suggested author position.
- `ContentPlanning`: describes broadcast demand and calendar status: tempo, period,
  publishing days/times, candidate count requirements, platform/date/topic/fabula/
  format, approval status, manual override state, and advisory conflicts.
- `Briefing`: turns an approved plan item into a post brief with thesis, conflict,
  author position, evidence, examples, structure, CTA, risks, sources, and approval
  status.
- `Drafting`: turns an approved post brief into an editable draft.
- `EditorialChecks`: models style, anti-AI, fact-check, and policy checks plus editor
  notes before final approval.
- `ReleasePackaging`: turns approved final text into platform targets, Markdown
  preview, release checklist, and manual export status.
- `AnalyticsPrep`: turns an exported release package into manual metric fields and an
  editorial learning note.
- `AIProviderBoundary`: defines how future provider-backed services can replace
  deterministic application services without leaking provider details into React or
  domain code.
- `LocalWorkspaceStore`: loads and saves the current workspace state in browser
  storage for the first implementation circles.

## Dependency Direction

Dependencies must point inward:

`React UI -> application services -> domain model`

Infrastructure adapters sit at the edge:

`React UI -> application services -> WorkspaceStore adapter -> localStorage`

Future provider integration follows the same rule:

`React UI -> application service -> provider boundary -> infrastructure provider adapter`

Domain code must not import React, browser APIs, storage APIs, future AI providers, or
network clients. React components render state and trigger application service methods.
Application services orchestrate domain operations, call adapters, and decide whether
to use deterministic fallback or provider-backed behavior.

## Frontend UX Architecture

Slice 1.1.1 fixes the editorial setup UX and records reusable frontend decisions:

- Product screens reuse existing cabinet controls before adding new patterns.
- Editorial settings are structured rules, not freeform textareas.
- Important entities use read/edit/save/cancel instead of immediate hidden commits.
- Setup workflows use a single main column and a right-side validation panel.
- Page headers must come from explicit project/profile entities, not anonymous domain
  quotes.
- Topic and fabula catalogs use compact rows with details on demand.
- Validation is a first-class surface on every editorial setup tab.
- Editorial setup validation is explicit: the author clicks `Проверить`, then sees a
  validation snapshot. Saved setup changes mark that snapshot as stale until the next
  run.
- Editorial catalogs and matrices must contain realistic long content: wrap labels,
  use shared scroll areas for long details, and keep matrix row context visible with a
  sticky topic column during horizontal scroll.
- Context chat uses a collapsible overlay, not a permanent third column beside existing
  right-side panels. It must stay covered by visual smoke checks.

These rules are captured in ADRs under `docs/adr/` and should guide future validator
and context-chat implementation.

## Conceptual Domain Interfaces

Current implemented production contracts:

- `AuthorNote`: free author thought, link reaction, or manual correction.
- `AuthorAttachment`: optional local demo file attached to an author note, with file
  name, MIME type, size, data URL, creation date, and local-only marker.
- `AuthorMemoryEvent`: normalized memory event with detected author signals.
- `AuthorPositionAssertion`: evidence-backed inferred statement about persona, style,
  audience, topic, or principle.
- `EvidenceLink`: link from a position assertion back to source notes.
- `ProjectProfile`: name, description, and setup status for the current editorial
  project.
- `EditorialRule`: group, title, statement, active/paused status, and optional evidence
  note id.
- `ValidatorDefinition`: validator id, title, description, and supported target types.
- `ValidatorResult`: validator id, target, red/yellow/green status, score, summary,
  evidence, and suggested fixes.
- `ValidatorRun`: saved manual validation snapshot with run id, setup revision,
  checked timestamp, and validator results. UI marks it stale when the setup revision
  changes.
- `EditorialValidationSummary`: compatibility summary derived from the latest
  `ValidatorRun`.
- `EditorialModel`: compatibility aggregate for author, audience, positioning, fabula,
  rubrics, style rules, forbidden topics, goals.
- `Topic`: editable topic card with purpose, audience value, author stance, rules,
  forbidden angles, active/paused status, and advisory weight range.
- `Fabula`: editable dramaturgy card with structure, proof requirements, rules,
  active/paused status, and advisory weight range.
- `TopicFabulaMatrixEntry`: compatibility toggle between one topic and one fabula.
- Topic/fabula helpers create local drafts, commit new entities, delete entities, and
  keep matrix links normalized. Added entities get default enabled links; deleted
  entities remove their matrix links without rewriting existing production artifacts.
- `SourceSignal`: type, title, source, capturedAt, summary, rawNote.
- Future `RadarDefinition`: source, scope, acceptance policy, trigger mode, status,
  last run, and notes.
- Future `PostCandidate`: candidate assembly of signal, topic, fabula, audience,
  value, goal, platform, format, confidence, risks, and approval status.
- `InsightCard`: source signal, why it matters, audience relevance, author position,
  rubric, urgency, score, banality risk, fact gaps.
- `ContentPlanItem`: insight, platform, date, priority, format, expected effect,
  approval status, topic/fabula link, manual override state, and warning links.
- `ContentPlanSettings`: local-first tempo and format settings for the broadcast grid.
- `PlanWeightWarning`: advisory warning when the grid diverges from topic/fabula
  weights, matrix compatibility, or required slot fields.
- `PostBrief`: thesis, conflict, author position, evidence, examples, structure, CTA,
  risks, sources, approval status.
- `PostDraft`: brief, title, body, version, draft status, updated time.
- `EditorialCheck`: type, title, check status, summary, findings.
- `EditorNote`: agent, tone, text, target.
- `FinalText`: draft, title, body, approval status, approved time.
- `ReleasePackage`: final text, targets, Markdown, checklist, release status, updated
  time.
- `EditorialLearningNote`: release package, manual metrics, editorial conclusions,
  analytics status, updated time, captured time.
- `WorkspaceStore`: load and save current local workspace state.

Future author-position contracts:

- `ContentDesignRecord`: durable content rule with rationale, scope, status, evidence,
  and validator impact.
- `PlatformProfile`: platform, formats, format rules, weight range, and compatibility
  with fabulas.
- `ContextChatSession`: active section, messages, proposed structured changes, and
  approval state.
- `AuthorExternalSource`: source settings for Telegram, social, blog/site, document,
  article archive, or manual upload.
- `ImportedMemoryCandidate`: imported item waiting for review, grouping, or bulk
  action.
- `ImportCandidateGroup`: grouped candidate set used for large archives.
- `BulkImportSelection`: selected candidates by explicit ids or active filter.
- `BulkImportAction`: reversible record of a group operation.
- `ArchiveRecord`: accepted historical material with provenance and evidence policy.
- `Provenance`: source, original link or file reference, import date, acceptance date,
  acceptance mode, and author reason.
- `EvidencePolicy`: whether imported material can support assertions, is archive-only,
  or is ignored as evidence.

## Conceptual AI Provider Interfaces

These interfaces are documented for future implementation and are not runtime
TypeScript contracts in Slice 0.8:

- `AiProviderAdapter`: infrastructure-side adapter that performs provider-specific
  calls for one capability.
- `DraftGenerationRequest`: approved `PostBrief`, `EditorialModel` or future
  `AuthorPositionModel`, optional previous learning context, locale, output
  constraints, and caller context.
- `DraftGenerationResult`: title, draft body, notes, risks, provider metadata, and a
  shape that can be mapped into `PostDraft`.
- `PromptTemplate`: stable prompt layers and variables used by the application service
  before calling an adapter.
- `ProviderRunMetadata`: provider name, model name if known, run id if available,
  latency, token estimates when available, and fallback status.
- `ProviderError`: normalized error information that does not expose SDK-specific
  exceptions to React or domain code.
- `AiFallbackPolicy`: rules for when to use deterministic fallback, including disabled
  provider mode, missing configuration, provider error, invalid result, or local demo
  mode.

## Validator Architecture

Validators are a common product layer, not only draft checks.

Slice 1.2 implements the first setup-only validator runner:
`runEditorialSetupValidators(workspace)`. It is deterministic and provider-free.
The first validators are:

- `author-position-clarity`;
- `anti-ai-style-coverage`;
- `audience-value-fit`;
- `goal-consistency`;
- `topic-fabula-coverage`.

They should evaluate:

- author position;
- persona and alter ego;
- style and anti-AI quality;
- audience value;
- goal fit;
- topic rules;
- fabula rules;
- platform and format rules;
- Content Design Record compliance;
- uniqueness against archive;
- evidence quality and fact gaps.

Each validator result should include status, score, summary, evidence, and suggested
fixes. The UI should show compact colored indicators with progressive disclosure into
evidence and remediation.

## First Demo Data Flow

The permanent demo scenario is a Telegram blog by an AI Product Manager who shares
research experience building AI-B2B products:

1. The workspace opens on `AuthorMemory` with six seeded notes about workflow risk,
   evals as a product function, failed demo magic, GTM/adoption correction, enterprise
   trust, and confidence boundaries.
2. `createAuthorMemoryEvent` normalizes notes into memory events with detected signals.
3. `inferAuthorPositionAssertions` shows evidence-backed assertions about the author's
   persona, style, audience, topics, and product principle.
4. The author can add another thought, link reaction, file-backed note, or manual
   correction. Attached files are supporting material only; they are not parsed or
   analyzed in the current perimeter.
5. Future external source settings can describe the author's Telegram channel,
   interview notes, blog archive, and talks. Imported candidates must go through review
   or bulk archive acceptance before they influence memory or assertions.
6. `Сигналы` shows demo radars for author memory, archive, external sources, and
   manual research.
7. The author reviews found signals, then approves, archives, rejects, or corrects a
   signal before it becomes production material.
8. The approved signal becomes the compatibility `sourceSignal` for downstream flow.
9. `InsightScoring` produces an `InsightCard`.
10. `ContentPlanning` currently creates a Telegram broadcast grid prototype.
11. The author approves a slot and post brief through HITL gates.
12. `Drafting` creates an editable research-note draft.
13. `EditorialChecks` returns style, anti-AI, fact-check, and policy checks plus editor
   notes.
14. The author approves final text, prepares a manual Telegram release package, and
   captures analytics learning.

## Extension Points

- Author memory can ingest notes, links, archive posts, corrections, and analytics
  learning before production artifacts are created.
- External source import can add candidates to a review queue, but unreviewed material
  must not strengthen author-position assertions.
- Reviewed source material can become `SourceSignal`; unreviewed imports and archive
  records remain source material until the author or an acceptance policy promotes
  them.
- Post candidate assembly can later replace direct plan-slot generation while keeping
  current `contentPlanItems` as a compatibility layer.
- Bulk import can accept many historical items into archive, while preserving
  provenance, acceptance mode, and evidence policy.
- Source ingestion adapters can later replace manual signal entry.
- Validator adapters can later replace deterministic checks while preserving
  evidence-backed `ValidatorResult` contracts.
- Context chat can open draft flows for structured entities, but should not bypass
  explicit author review and save/cancel actions.
- AI provider adapters can later replace deterministic insight, planning, briefing,
  drafting, and check services after author position and validators exist.
- Backend persistence can replace `LocalWorkspaceStore` behind the same workspace store
  interface.
- Platform publication APIs can attach after the manual release package.
- Real analytics ingestion can replace manual metric entry behind the analytics prep
  shape.

## Testing Strategy

Current validation covers:

- Unit tests for author memory event creation and evidence-backed assertions.
- Unit tests for domain transitions and approval rules.
- Unit tests for deterministic scoring, planning, briefing, drafting, editorial check,
  release packaging, and analytics prep services.
- Integration tests for local workspace save/load.
- UI smoke tests for the source signal to captured editorial learning note flow.
- Manual demo acceptance for the founder-blog scenario.

For the author-position product circle, add:

- Unit tests for author note classification and evidence linking.
- Unit tests for topic/fabula weight ranges and compatibility matrix behavior.
- Unit tests for validator score/status aggregation.
- Integration tests for local persistence of author memory and position entities.
- UI smoke tests for the author memory feed, topic/fabula cards, and validator
  indicators.

For later AI-assisted drafting, add:

- Unit tests for deterministic fallback selection.
- Unit tests for a mock drafting adapter.
- Contract tests for `DraftGenerationResult -> PostDraft` mapping.
- Failure tests proving provider errors return deterministic fallback.
- UI smoke coverage proving an AI-assisted draft still follows the existing HITL flow.

## Known Trade-offs

- The current `EditorialModel` is too coarse for the revised concept. It should be
  migrated carefully into smaller entities without breaking the existing demo flow.
- Author memory must stay loose enough for stream-of-consciousness input, while the
  position model must be structured enough for validation.
- Validator indicators can become noisy if every rule is shown at once. The UI needs
  progressive disclosure from colored status to evidence.
- Local-first persistence avoids backend scope, but it is not suitable for multi-device
  or team collaboration.
- Provider selection is intentionally deferred. This keeps AI integration from being
  attached to an underdeveloped author-position model.

## Open Questions

- Which author memory event types should be implemented first: raw thoughts,
  link-reactions, radar corrections, archive annotations, or release learning?
- Should topic/fabula/platform weights initially be advisory only, or should they
  produce hard validation failures in the content plan?
- How much of the context chat should be implemented before real AI provider calls?
- Which hosted deployment target should be used after local-first development?
- Should the first backend persistence slice preserve the local workspace format or
  introduce a migration layer?
