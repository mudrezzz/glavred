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

The current queued drafting pipeline is documented as a maintained AS IS technical map
in `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`, with a generated quick-view PDF at
`docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf`. DraftRun planning, implementation,
diagnostics, and roadmap work should use that document as the current pipeline source
before changing or judging drafting behavior.

Slice-level target designs can add a separate TO BE map before implementation. The
target for Slice 2.15.3 is documented in
`docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.md`, with a generated PDF at
`docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.pdf`.

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

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> RadarDefinition -> reviewed SourceSignal -> approved PostCandidate -> InsightCard -> ContentPlanItem -> EditorialWorkItem -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

`FinalText` and `ReleasePackage` are compatibility artifacts from the one-post manual
export perimeter. The target editorial chain is now
`Фабула -> Драфт -> Визуал -> readyForRelease -> PublicationLogEntry`: all preparation
happens in `Редактура`, and `Выпуск` becomes a delivery log for ready posts.

The source-to-release part remains useful as a production layer. It is no longer the
conceptual center of the product. Author memory, author-position assertions,
structured topics/fabulas, validator results, and reviewed signals now sit above that
flow; future slices should route post candidates and calendar slots through them.

Slice 1.6 adds the first working `Кандидаты постов` layer: deterministic assemblies
from approved source signals and active topic/fabula pairs, compare cards, and one
approved candidate that becomes the current concept for insight creation. Slice 1.7
turns that layer into a cabinet-grade review list: filter card, full-width search,
list/group toggle, framed candidate rows, bottom-left approve/edit/reject actions,
inline editing, rejection, full-width evidence, and grouped review by signal, topic,
status, or risk. The deeper planning model still needs request-more controls and
broadcast settings before expanding the calendar UI.
Slice 1.5.8 refines radars into separate trigger rules, search sources, source
discovery mode, and editorial filters. Filters evaluate author, audience, positioning,
goals, forbidden topics, and topics; style remains a later drafting/review concern.
Filtered signals stay visible for human review instead of being deleted automatically.
Slice 1.9 adds the first production queue in `Редактура`: approved plan slots become
stable `EditorialWorkItem` records, the screen starts with the shared large-list
pattern, and the selected item hydrates the selected-post workbench through
compatibility fields.
Slice 1.10 removes the extra `Подготовить фабулу поста` handoff. Approving a slot in
`План` now creates or updates the stable editorial work item and prepares its initial
`PostBrief` immediately. `Редактура` is organized as `Посты` plus `Рабочий стол`:
the first tab manages the production queue, while the second edits one selected post
inside the workbench.

Slice 1.10.4 makes the `Фабула` stage editable inside that workbench. The workbench
shows read-only candidate and slot context, but `PostBrief` remains a production
artifact with only brief fields. Editing an approved fabula returns the selected work
item to stage `brief` and invalidates stale draft, checks, notes, final text, release
package, and learning note before the author approves the fabula again.

The Slice 1.10.5-1.11 roadmap corrects the remaining production boundary. `Финал`
should disappear as a user-facing workbench tab; text approval belongs in `Драфт`.
After text approval, `Редактура` adds a `Визуал` stage and marks the post
`readyForRelease` only after text and visual decisions are complete. `Выпуск` then
owns publication attempts, statuses, external links, and platform errors; it does not
edit text, visual, candidate context, or brief artifacts.

Slice 1.10.6 implements the first `Визуал` foundation as local selected-post state:
`PostVisual` stores the chosen mode (`generate`, `memeSearch`, `memeRemix`, or
`noVisual`), one user-facing visual brief, compatibility fields for future adapters,
and approval status. The workbench deliberately exposes only one Russian `Бриф`
field for `generate`, `memeSearch`, and `memeRemix`; `noVisual` has no extra field.
Slice 1.10.6.1 adds the review contract around that state: deterministic
`PostVisualVariant` placeholders are prepared from the current mode and brief, one
variant must be selected before visual approval, and editing the mode or brief resets
variants, selection, and approval. `noVisual` remains the only shortcut that can be
approved without variants.
Slice 1.10.6.2 makes `memeRemix` explicitly two-step: `PostVisualMemeReference`
stores deterministic meme-reference options, `selectedMemeReferenceId` chooses the
intermediate meme, and final remix `PostVisualVariant` options are prepared only
after that reference is selected. Selecting a meme reference is not visual approval;
approval still requires a selected final remix variant.
Real image generation, internet meme search, and hybrid meme-based image
transformation remain adapter-backed future slices; React workbench code stores the
decision contract only.

Slice 2.3 introduces the first real AI provider call for draft generation only.
Publication automation, backend workspace sync, real metrics ingestion, image
generation, meme search, document analysis, and broader provider coverage remain
future slices. Provider-backed output still enters the same HITL workflow and never
approves editorial artifacts automatically.

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
- Slice 1.5.1 correction: `EditorialRadar` owns atomic search rules and optional
  search sources. `SourceSignal` remains raw material with radar provenance, date,
  finding, evidence, search note, duplicate risk, and review status. Topic/fabula/
  audience/value matching starts in `PostCandidateAssembly`, not in the signal review
  UI.
- Slice 1.5.8 correction: `EditorialRadar` also owns source discovery mode and
  editorial filters. The deterministic filter service returns per-filter status, score,
  summary, and evidence on `SourceSignal`; React renders those results but does not
  implement scoring logic.
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
- `PostCandidateAssembly`: combines an approved source signal with topic, fabula,
  audience, value, goal, platform, thesis, evidence summary, confidence, and risks
  before a post concept is approved. It does not own `format`; fabula is the
  candidate's editorial shape, while format remains a broadcast-planning concern.
  Candidate filtering, grouping, and inline edit state are UI/application concerns
  under `src/features/signals`; edit/reject transitions remain domain-level
  post-candidate operations.
- `InsightScoring`: turns an approved candidate, or a reviewed source signal fallback,
  into an insight card with relevance, urgency, banality risk, fact gaps, topic, fabula,
  and suggested author position.
- `ContentPlanning`: describes broadcast demand and calendar status: tempo, period,
  explicit publish slots, fallback publishing days/times, candidate count
  requirements, platform/date/time/topic/fabula, approval status, manual override
  state, and advisory conflicts.
- `EditorialWorkQueue`: stores approved posts as production work items. Each work
  item keeps its source slot/candidate context plus its own brief, draft, checks,
  editor notes, and final text. Slot approval creates or updates the work item and
  prepares the initial brief automatically. The target item lifecycle is brief,
  draft, visual, and ready state; final text, release package, and analytics learning
  note remain compatibility fields until implementation slices replace them. The queue
  replaces the singleton production mental model while allowing current single-post
  editors to be reused as selected-item workbenches.
- `Briefing`: turns an approved plan item into a post brief with thesis, conflict,
  author position, evidence, examples, structure, CTA, risks, sources, and approval
  status. The selected-post workbench can edit those brief fields; candidate and slot
  context is assembled separately from workspace entities and is displayed read-only.
- `Drafting`: turns an approved post brief into an editable draft and owns text
  approval in the target UX.
- `EditorialChecks`: models style, anti-AI, fact-check, and policy checks plus editor
  notes before text approval.
- `VisualPreparation`: selected-post stage for one visual brief, visual mode,
  deterministic or adapter-backed variants, selected variant, approval state, or
  explicit `без визуала`. It owns the local review contract; provider-backed
  generation/search/remix adapters attach later.
- `ReleaseLog`: future delivery layer that records ready posts, publication attempts,
  platform statuses, external links, adapter errors, and retry notes. The existing
  manual release package remains compatibility behavior until this model replaces it.
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

## Backend AI Execution Architecture

Backend work starts as an AI execution layer, not as a broad workspace rewrite. The
frontend remains a local-first product surface until a backend slice explicitly moves a
specific capability behind an HTTP boundary.

The target backend structure is:

- `backend/app/api/`: thin HTTP routes, request/response mapping, and no prompt,
  provider, persistence, or workflow logic.
- `backend/app/domain/`: provider-free entities, value objects, policies, and
  invariants.
- `backend/app/application/`: use-case services, orchestration, prompt-independent
  request/result contracts, fallback decisions, and audit boundaries.
- `backend/app/infrastructure/`: OpenRouter, database, queue, file storage,
  `langgraph-document-ai-platform`, and platform-specific adapters.
- `backend/app/workflows/`: workflow composition only when a real slice needs
  multi-step execution; no empty boilerplate packages.
- `backend/app/settings.py`: typed environment configuration and secret-safe
  validation.
- `backend/tests/`: unit, contract, and smoke tests that mirror backend ownership.

Slice 2.1 implements the first concrete backend perimeter:

- `backend/app/main.py`: FastAPI application factory.
- `backend/app/__main__.py`: local server entrypoint used by `npm run dev:backend`.
- `backend/app/settings.py`: typed settings loaded from `.env` / environment.
- `backend/app/api/health.py`: `/health` and `/api/health` routes.
- `backend/app/api/dependencies.py`: request-time application service wiring.
- `backend/app/application/health_service.py`: liveness/readiness orchestration.
- `backend/app/domain/health.py`: provider-free health value objects.
- `backend/app/infrastructure/openrouter_config.py`: OpenRouter configuration status
  evaluation without a provider call.

Slice 2.2 adds the first durable AI execution audit contract without executing a
provider:

- `backend/app/domain/ai_run.py`: provider-agnostic `AiRun` entity and capability,
  provider, and status enums.
- `backend/app/api/ai_runs.py`: thin `/api/ai-runs` routes for creating audit
  records, reading one run, and listing recent runs.
- `backend/app/application/ai_run_service.py`: audit use case, payload redaction,
  stable timestamping, and repository port.
- `backend/app/infrastructure/sqlite_ai_run_repository.py`: local SQLite audit
  repository using stdlib `sqlite3`.

`AI_RUN_AUDIT_DB_PATH` points to the local SQLite file, defaulting to
`var/glavred-ai-runs.sqlite3`. `var/` is ignored by Git. The repository creates its
directory and schema on first use; no ORM, migration framework, queue, auth, prompt
execution, or workspace sync exists in Slice 2.2.

Slice 2.3 adds the first provider-backed production path:

- `backend/app/api/drafts.py`: thin `POST /api/drafts/generate` route.
- `backend/app/domain/draft_generation.py`: provider-free draft request/result
  contracts.
- `backend/app/application/draft_generation_service.py`: OpenRouter-or-fallback
  orchestration and AI run audit creation.
- `backend/app/application/deterministic_draft_service.py`: deterministic fallback
  draft generation.
- `backend/app/infrastructure/openrouter_draft_adapter.py`: OpenRouter chat
  completions HTTP call and provider response parsing.
- `src/infrastructure/backendDraftClient.ts`: browser-to-backend draft request mapper.
- `src/app/productionDraftActions.ts`: workspace patch builder for backend-generated
  drafts.

The backend dependency rule is:

`api -> application -> domain`

Infrastructure is injected at the edge:

`application -> infrastructure ports/adapters`

OpenRouter is the default LLM provider target for the backend execution layer. The
runtime contract is documented in `.env.example`; developer secrets live only in local
ignored `.env` files. Provider keys, provider SDKs, and provider-specific metadata must
not leak into React components, domain objects, or API route logic.

Slice 2.15.1 adds role-based model selection for DraftRun without changing prompt
semantics. `backend/app/domain/draft_model_roles.py` defines provider-free role and
selection DTOs. `backend/app/application/draft_model_role_resolver.py` maps
`research`, `strategy`, `writer`, `review`, `critic`, and `anotherAngle` to configured
environment models, falling back to `OPENROUTER_DEFAULT_MODEL` when a role is empty.
Backup retries still use `OPENROUTER_BACKUP_MODEL`; public search still uses
`OPENROUTER_WEB_SEARCH_MODEL`.

ADR `docs/adr/2026-06-27-llm-json-steps-use-universal-retry-policy.md` makes JSON
retry discipline a project-wide architecture rule, not a DraftRun-only convention.
Every LLM step that requires structured JSON must use the bounded attempt sequence
`primary -> primary-repair -> optional backup -> fallback | not-run | failed`.
The shared retry engine belongs in application code; each owning service still owns
its schema, parser, validation criteria, and repair prompt. New LLM JSON workflows in
DraftRun, author memory, document import, release, analytics, or future pipelines must
not do direct single-call-then-fallback parsing. Slice 2.15.6.3 completed the DraftRun
migration for the remaining writer candidate and alternative-angle challenger prose
paths; new JSON provider calls must start from this policy.

Current recommended DraftRun role defaults are operational presets, not product
requirements: writer `openai/gpt-5.1`, technical JSON backup
`openai/gpt-4.1-mini`, critic/final gate `google/gemini-2.5-pro`, and another-angle
`qwen/qwen3.7-max`. Writer owns public prose, backup owns low-temperature JSON repair,
critic owns strict editorial challenge, final gate owns independent acceptance of the
delivered post, and another-angle remains creative divergence rather than technical
backup or another writer alias. Writer, revision, JSON repair, final gate, and
another-angle calls also carry role-specific generation params in child `AiRun` audit
payloads so diagnostics can separate model choice from temperature/top-p policy.

The Slice 2.1 health surface is intentionally configuration-only. `/api/health`
reports whether OpenRouter is locally configured and never returns API keys or calls
OpenRouter.

The Slice 2.2 AI run surface is audit-only. `POST /api/ai-runs` records a durable
`recorded` run for `draftGeneration`, `visualGeneration`, `memeSearch`, or
`documentImport`, stores sanitized JSON payloads, and returns the created record.
`GET /api/ai-runs/{id}` and `GET /api/ai-runs` read audit records newest-first. The
API never returns provider secrets or the absolute SQLite path. `/api/health` reports
`aiRunAudit: { configured: true, storage: "sqlite" }` only.

The Slice 2.3 draft surface is synchronous and non-streaming. `POST
/api/drafts/generate` accepts an approved brief and editorial model context, calls
OpenRouter only from infrastructure, validates JSON `{ title, body }`, maps it to the
existing `PostDraft` shape, and records a succeeded `AiRun`. Missing configuration,
provider errors, and invalid provider output fall back to deterministic drafting and
record `fallbackUsed: true`. The frontend still stores workspace state locally; it
uses the backend only for draft generation and keeps a local emergency fallback if the
backend itself is unreachable.

Slice 2.3.2 makes AI execution observable. Every backend draft run stores a full
local sanitized trace in `AiRun` JSON payloads:

- `requestPayload`: capability input, prompt messages, provider request summary,
  model, temperature, and response format.
- `resultPayload`: generated draft id/title/body/version/status, provider response
  id/model/usage when available, fallback flag, and safe error context.

The trace is intentionally local development audit data. API keys, authorization
headers, secret env values, and absolute local paths must never be stored or returned.
React workspace state stores only lightweight `PostDraft.generation` metadata:
source, `AiRun` id, provider, model, fallback flag, created time, and optional error.
The full prompt/body trace remains behind `GET /api/ai-runs/{id}`. Provider-backed
slices must include this observability surface before they are considered complete.
The `Редактура -> Рабочий стол` UI also treats draft generation as asynchronous work:
after `Утвердить фабулу`, the draft tab shows a pending state, duplicate approval is
blocked, and the completed draft shows whether it came from OpenRouter, backend
fallback, or frontend local emergency fallback.

Slice 2.3.3 adds a separate frontend debug page for this trace: `/ai-runs`.
It is not part of the main editorial cabinet navigation. Slice 2.8.1 turns that
page into a trace workbench for one child `AiRun`: feature-owned parser modules
convert known audit payloads into semantic sections, prompt messages, provider/
fallback summary cards, and wrapped JSON. Slice 2.8.1.1 promotes the page to a
parent `DraftRun` workbench: the page first calls `GET /api/draft-runs/{id}`;
only if that returns `404` does it call `GET /api/ai-runs/{id}`. For parent
runs, it loads all child `AiRun` records and renders the logical timeline
`context -> rulePack -> materialPlan -> strategy -> draft -> validation ->
complete`, with LLM calls nested under the owning logical step.

Raw JSON remains available for auditability, but it is not the primary analysis
surface. The top-level workbench tabs are canonical `.tabs .tab`: `Трейс` for
timeline/details and `Смысловой результат` for material plan, strategy, draft
candidates, scorecard, selected candidate, and final draft artifacts. Slice 2.12.2
adds derived read-model nodes inside the existing `draft` step for candidates,
deterministic scoring, and final selection; these nodes are UI/debug projections
from `draft.artifactPayload`, not new durable backend steps. Slice 2.12.2.1 renders
the deterministic scorecard as a comparison table over
`draft.artifactPayload.selection.scorecard` instead of a generic long text field, so
candidate scoring remains inspectable without changing orchestration. The page lives under
`src/features/ai-runs`; the child-call HTTP mapper remains
`src/infrastructure/aiRunTraceClient.ts`, while parent timeline aggregation lives
in `src/infrastructure/runTraceClient.ts`. This keeps trace inspection separate
from production draft generation and avoids expanding the near-limit draft client.

Slice 2.4 introduces the first durable queued drafting runner. The current
`/api/drafts/generate` endpoint remains a useful compatibility/provider-integration
surface, but the primary draft path starts a long-running `DraftRun`:

- `DraftRun` is the parent orchestration record for one post-drafting attempt.
- `DraftRunStep` records named stages such as context build, rule-pack compilation,
  material planning, draft strategy, candidate generation, validation, revision, and
  result selection.
- `AiRun` remains the audit record for one provider call inside a `DraftRun`.
- Rule packs and validators are first-class application/domain concepts; they must not
  be hidden as one large prompt.
- `POST /api/draft-runs` creates a durable run and dispatches a Celery task.
- `GET /api/draft-runs/{id}` and `/events` expose a polling read-model with steps,
  artifacts, error, and final draft when ready.
- SQLite stores orchestration state in `DRAFT_RUN_DB_PATH`
  (`var/glavred-draft-runs.sqlite3` by default).
- Celery and Redis run under infrastructure modules only. API handlers do not own task
  bodies, queue logic, SQL, or provider calls.

The target drafting pipeline is:

`EditorialWorkItem -> DraftRunContext -> SourceIntent -> seed SourceLedger -> ResearchPlan -> PublicResearch -> EvidenceExtraction -> enriched SourceLedger -> EvidenceSynthesis -> FeasibilityGate -> PostContract -> RuleRegistrySnapshot -> RulePack -> EvidenceInterpretation -> MaterialPlan -> RhetoricalPlans -> DraftCandidates -> InitialValidation -> EditorialCritique -> AlternativeAngleTournament -> FinalValidation -> PairwiseRanking -> IterativeRevisionLoop -> FinalQualityGate -> SelectedDraft -> HumanDecision`

This order is intentional. Future drafting work must not jump directly from
multi-candidate generation to a generic validator loop. Validators and revisions need
a source ledger and a post contract first: otherwise they cannot know which claims are
allowed, which inferences are forbidden, or which editorial invariants must survive a
rewrite. They also need public evidence when the approved fabula asks the runner to
use external sources; otherwise validators can only inspect an internally grounded but
dry draft. ADR
`2026-06-20-drafting-quality-requires-source-ledger-and-post-contract` records this
rule.
ADR `2026-06-23-drafting-requires-public-evidence-research` records the public
evidence research layer.

Slice 2.13 implements the first report-only validator layer. The existing
`validation` step now stores a `DraftValidationReport` for every draft candidate,
including the selected candidate. The deterministic linter checks size/shape,
contract and CTA signals, source attribution, rejected-evidence misuse, forbidden
moves, raw artifact leakage, and publishability consistency. Findings carry
validator ids, severity, rule ids, claim ids, evidence excerpts, and repair guidance,
but they do not alter `finalDraft` selection until the ranking/revision slices consume
them. Attribution validation is deterministic and claim-level: source-backed claims
are checked against markers derived from their own provenance, including source title,
domain, author/person names, organization names, and source labels. Matching one
source marker does not satisfy unrelated claims.

Slice 2.13.3 adds the second, provider-backed validation layer without changing
ranking, revision, or `finalDraft`. The same `validation` step keeps the
deterministic `DraftValidationReport` and adds a sibling `llmValidationReport`.
The LLM validator checks every candidate with one structured JSON call per
candidate. It consumes the enriched SourceLedger, PostContract, RuleRegistry,
MaterialPlan, candidate text, and deterministic findings, then writes report-only
findings for source grounding, publisher/author fit, topic/fabula fit,
coherence/compression, and audience value. If OpenRouter is not configured, the
LLM report is `not-run` instead of fake fallback findings. If JSON is malformed,
the validator follows the same primary, repair, optional backup-model retry
discipline before marking the candidate validation unavailable.

Slice 2.13.3.1 normalizes that report before ranking/revision uses it. Actionable
LLM issues remain in `findings[]`; positive/pass notes such as `No repair needed`
move to `observations[]` and do not increase warning counts. The `/ai-runs`
workbench also reads enriched evidence from the `publicEvidence` artifact and nested
selected/rejected evidence from `materialPlan`, so the trace reflects the actual
handoff from retrieval to planning.

Slice 2.14 makes validation actionable without adding new DraftRun steps or SQLite
tables. The existing `validation` artifact gains `rankingRevision`: pairwise ranking,
one directed revision instruction, the revised candidate when a provider returns one,
a deterministic regression guard, and the final decision. The implementation is split
across role-owned modules:

- `backend/app/domain/draft_ranking_revision.py`: provider-free DTOs.
- `backend/app/application/deterministic_pairwise_ranking.py`: local fallback ranking.
- `backend/app/application/draft_pairwise_ranking_prompts.py` and
  `backend/app/application/draft_pairwise_ranking_service.py`: OpenRouter JSON
  pairwise ranking with retry discipline.
- `backend/app/application/draft_directed_revision_prompts.py` and
  `backend/app/application/draft_directed_revision_service.py`: one-shot directed
  revision, without deterministic fake rewrites.
- `backend/app/application/draft_revision_instruction_builder.py`: actionable
  finding projection into repair goals.
- `backend/app/application/draft_revision_regression.py`: deterministic regression
  checks before accepting a revised candidate.
- `backend/app/application/draft_final_quality_assessment.py`: deterministic public
  prose heuristics for final-draft acceptance.
- `backend/app/application/draft_final_quality_gate.py`: final public-prose
  acceptance and one-shot repair handoff after the revision loop.
- `backend/app/application/draft_ranking_revision_mapping.py`: small conversion and
  final-decision formatting helpers.
- `backend/app/application/draft_ranking_revision_service.py`,
  `backend/app/application/draft_ranking_revision_result.py`, and
  `backend/app/application/draft_validation_ranking_bridge.py`: narrow orchestration
  between validation, ranking, revision, final quality gate, and the final draft
  decision.
- `backend/app/application/draft_model_role_resolver.py`: role-based model selection
  policy for research, strategy, writer, review, critic, and alternative-angle roles.
- `backend/app/application/draft_generation_params.py`: role/attempt generation
  parameter normalization for writer, revision, JSON repair, and another-angle calls.
- `backend/app/application/draft_provider_error_utils.py`: safe provider error and
  raw response excerpt extraction for child `AiRun` audit records.
- `backend/app/infrastructure/draft_run_pipeline_validation_services.py`: wiring for
  validation, ranking, and directed revision dependencies.

The pipeline sets `finalDraft` after `validation + rankingRevision`. If the revised
candidate regresses on deterministic critical/warning counts, hard size limits, raw
artifact leakage, or attribution markers, the original ranked winner remains the
final draft and the rejected revision stays in trace.

Slice 2.15 turns the one-shot repair into a bounded improvement loop. Slice 2.15.6
deepens that loop from validator cleanup into editorial optimization. The same
`validation.rankingRevision` payload now contains `revisionLoop`, and no new DraftRun
step or SQLite table is introduced. The loop limit is `DRAFT_REVISION_MAX_ITERATIONS`
with default `3` and runtime-safe minimum `1`. Each cycle builds validator repair
goals plus editorial goals from `EditorialCritiqueReport`, `EvidenceInterpretation`,
`alternativeAngleTournament`, material-plan gaps, and prior rejected moves. Directed
revision receives those goals, anti-regression constraints, context packs, and rejected
moves. The review model then compares previous-best vs revised candidate across
explicit dimensions: idea strength, tension, reader value, author stance, source
integration, structure, and validator health. The loop accepts a revision only when it
resolves a targeted validator/editorial goal or clearly wins on editorial dimensions
without deterministic or attribution regression. Rejected revisions remain in trace as
structured `rejectedMoves`, and their constraints feed the next cycle. `finalDraft` is
selected from the final best candidate after the loop, and `/ai-runs?runId=...` shows
cycles, editorial goals, dimension scores, accepted/rejected attempts, unresolved goals,
rejected moves, final source, and stop reason.

Slice 2.15.6.4.1 makes the last machine acceptance layer contract-driven and
independent before the draft returns to the editor. `validation.rankingRevision.finalQualityGate`
evaluates the delivered final candidate, not the whole candidate pool, for public-prose
quality, internal pipeline jargon, source-dump risk, source integration, author voice,
and reader value. It builds a `FinalQualityContract` from editorial/fabula/post
constraints and runs an independent `finalGate` model review. If the gate returns
`warning` or `critical`, it can run bounded writer repair cycles through the existing
directed-revision service; the count is controlled by `DRAFT_FINAL_REPAIR_MAX_ITERATIONS`.
A repair becomes the new `finalDraft` only when deterministic regression checks pass
and the gate findings improve; otherwise the previous best draft remains final and the
rejected repair stays visible in trace.

Final quality ownership is intentionally split:

- `backend/app/application/draft_final_quality_contract.py`: provider-free
  `FinalQualityContract` assembly from editorial/fabula/post constraints.
- `backend/app/application/draft_final_quality_gate.py`: thin final-gate composition
  boundary between contract, evaluator, and repair loop.
- `backend/app/application/draft_final_quality_gate_evaluator.py`: deterministic plus
  independent final-gate report assembly.
- `backend/app/application/draft_final_quality_gate_payloads.py`: status, decision,
  and payload helper functions.
- `backend/app/application/draft_final_quality_repair_loop.py`: bounded final repair
  cycle orchestration.
- `backend/app/application/draft_final_quality_review_prompts.py`: final-gate JSON
  prompt shape.
- `backend/app/application/draft_final_quality_review_parser.py`: final-gate JSON
  response normalization.
- `backend/app/application/draft_final_quality_review_service.py`: provider-backed
  independent final-gate review with universal JSON retry policy.
- `backend/app/application/source_research_plan_sanitizer.py`: deterministic cleanup
  that prevents non-URL named sources from becoming URL-read tasks.

Slice 2.15.6.1 hardens the same loop against late provider-heavy operation failures.
Validation progress writes now merge `artifactPayload.progress` into the existing
partial validation artifact instead of replacing it with a progress-only object.
Validation child `AiRun` ids are appended to the parent `DraftRun` while operations
complete, so a partially completed trace remains inspectable before final completion.
Provider-heavy validation operations such as editorial critique, alternative-angle
candidate generation, pairwise ranking, and directed revision are wrapped by safe
operation helpers. If a late revision cycle fails after a previous best candidate
exists, the operation is marked `failed`, the loop records `provider-failed` or
`operation-failed`, and the run finalizes with the previous best draft instead of
remaining `running/stale`.

Revision-loop ownership is intentionally split:

- `backend/app/domain/draft_revision_loop.py`: provider-free trace DTOs for loop
  cycles and final loop report.
- `backend/app/application/draft_revision_loop_config.py`: settings normalization for
  the bounded iteration limit.
- `backend/app/application/draft_revision_goal_evaluator.py`: deterministic comparison
  of repair goals against validation before/after.
- `backend/app/application/draft_pairwise_ranking_payloads.py`: provider-response
  normalization for pairwise ranking decisions, attempts, and editorial dimension
  scores.
- `backend/app/application/draft_editorial_revision_goals.py`: deterministic projection
  of critique, evidence interpretation, alternative-angle lessons, and rejected moves
  into editorial improvement goals.
- `backend/app/application/draft_editorial_revision_evaluator.py`: deterministic read
  of pairwise editorial-dimension decisions into resolved/unresolved/regressed goals.
- `backend/app/application/draft_revision_rejected_moves.py`: structured rejected-move
  and anti-regression constraint projection for the next cycle.
- `backend/app/application/draft_revision_loop_policy.py`: deterministic acceptance,
  stop-reason, failed-cycle, and constraint helpers.
- `backend/app/application/draft_revision_loop_cycle_runner.py`: thin executor for one
  revision, deterministic regression, and old-vs-new pairwise comparison operation.
- `backend/app/application/draft_revision_loop_service.py`: bounded orchestration
  across instruction building, directed revision, deterministic regression, old-vs-new
  pairwise comparison, editorial goal evaluation, rejected moves, and final best
  selection.
- `backend/app/application/draft_validation_operation_safety.py`: safe mapping of
  provider-heavy validation operation exceptions into failed operation trace results.
- `backend/app/application/draft_run_step_progress_payload.py`: tiny artifact merge
  helpers used by progress writes that must preserve partial validation payloads.

Slice 2.15.3 adds `EvidenceInterpretation` inside the existing `rulePack` artifact,
without a new DraftRun step or SQLite table. Accepted public evidence still becomes
external ledger claims through `EvidenceSynthesis`, but writing and material planning
no longer receive those claims as a flat citation list. The strategy role now turns
evidence into structured implications, tensions, usable examples, limits, forbidden
overclaims, reader-value hooks, and rejected evidence uses. Material planning and
writer prompts consume this interpretation first, while raw snippets remain available
only as provenance/debug data. The trace workbench shows the interpretation artifact,
provider attempts, model role, fallback status, and the resulting dossier/context-pack
cards.

Slice 2.15.4 activates the prosecutor/editor critic role inside the existing
`validation` artifact, still without a new DraftRun step or SQLite table. The critic
uses `DRAFT_CRITIC_MODEL` and the `critic` ContextPack to review every draft
candidate for idea strength, tension, author stance, source integration, generic AI
prose, unsupported leaps, and reader value. The resulting
`validation.editorialCritiqueReport` is report-only in this slice: it is stored in
trace and ArticleDossier, but it does not yet change pairwise ranking, revision, or
`finalDraft`. This keeps the architecture boundary explicit: validators check
contract compliance; critic attacks editorial quality.

Slice 2.15 exposed the next architectural correction: stronger drafts require an
editorial lab, not only more validation and repair. Glavred must not treat a bad
final draft as a reporting problem. The pipeline must create better conditions for a
strong idea to emerge. ADR
`2026-06-26-drafting-needs-editorial-lab-context-memory-and-model-roles` records this
decision.

The next drafting-quality layer is:

`ArticleDossier + ContextPacks + Editorial Roles + Model Portfolio`

This layer sits around the existing quality spine. It does not replace
`SourceLedger`, `PostContract`, or `RuleRegistry`; it consumes them. Its purpose is to
prevent two failure modes:

- losing accumulated research/critique context by passing only the latest artifact;
- flooding models with raw DraftRun JSON until they drift into generic prose.

Current ownership boundaries:

- `ArticleDossier`: DraftRun-local memory of the article, including evidence cards,
  interpreted implications, tensions, angle attempts, critique notes, rejected moves,
  open questions, and decisions. Slice 2.15.2 implements provider-free DTOs in
  `backend/app/domain/draft_article_memory.py` and deterministic extraction in
  `backend/app/application/draft_article_dossier_builder.py`.
- `ContextPackBuilder`: application-owned selectors that build task-specific context
  for each role, such as researcher, strategist, writer, critic, reviewer, and
  another-angle generator. Slice 2.15.2 implements this in
  `backend/app/application/draft_context_pack_builder.py`, with
  `backend/app/application/draft_article_memory_service.py` as the thin pipeline
  wrapper.
- `ModelRoleConfig`: settings/application layer that maps role names to model ids.
  `DEFAULT` and `BACKUP` remain technical fallback concepts, while writer, critic,
  review, research, strategy, and another-angle roles can intentionally use different
  providers or model families.
- `EditorialCritic` / prosecutor role: a provider-backed critique service that attacks
  blandness, forced sources, missing author stance, weak tension, generic AI prose,
  and unearned claims.
- `EvidenceInterpretation`: a synthesis step that turns public evidence into
  editorial implications before writer prompts can cite or use it.
- `AlternativeAngle`: a role that proposes genuinely different post routes instead of
  retrying the same prompt with the same assumptions. It is active in the validation
  phase as a one-challenger tournament: critique plus dossier produce an alternative
  route, the writer executes it, and final validation/ranking compare the merged pool.

`ArticleDossier` and `ContextPack` are not workspace persistence, not long-term RAG,
and not a vector store. They live inside existing DraftRun JSON artifacts and child
`AiRun.requestPayload` traces. Existing services may consume the role-specific pack
as compact structured input, but they must not reconstruct provenance from raw trace
blobs.

Slice 2.15.6.2 adds a DraftRun budget contract. `Fabula.researchDepth`
(`light`, `standard`, `deep`, `marketResearch`) expresses editorial research depth,
while backend `DRAFT_RUN_EXECUTION_MODE` (`smoke`, `standard`, `full`) expresses the
execution profile. `backend/app/domain/draft_run_budget.py` and
`backend/app/application/draft_run_budget_resolver.py` resolve an effective
`DraftRunBudget` and store it in the `context` artifact. Downstream source planning,
public evidence retrieval, external-ledger merge, material-plan projection, draft
candidate generation, and smoke revision limits consume that budget. Skipped or
trimmed tasks remain trace-visible as budget decisions and never become proof.

Future slices must preserve this distinction: validators and revision loops judge and
repair drafts, while the editorial lab creates and maintains the intellectual
material from which better drafts are written.

Slice 2.5 implements the first context builder without moving workspace persistence
to the backend. React builds an immutable `draftContext` snapshot from the selected
`EditorialWorkItem` and sends it with `POST /api/draft-runs`. The snapshot includes
approved brief, plan slot, post candidate when available, source signal, topic,
fabula, publisher rules, project profile, editorial model, and up to 10
author-position assertions sorted by confirmed status and confidence. Missing linked
entities are recorded in `missingContext` instead of failing the run. The worker's
`context` step normalizes this snapshot into a compact summary for trace/debug and
later rule-pack compilation.

`PostBrief` must not absorb these source fields; it remains the author-approved
production brief.

Slice 2.6 implements the first explicit rule-pack boundary. The worker no longer
stores a placeholder `rulePack` step: it compiles the normalized context summary into
a provider-free `RulePack` artifact with hard constraints, soft constraints, evidence
requirements, dramaturgy requirements, topic-fit requirements, a quality rubric, and
forbidden moves. Missing context is copied into rule-pack warnings instead of failing
the run. This keeps later material planning and prompt work from reading one large
prompt blob.

Rule-pack ownership is intentionally split:

- `backend/app/domain/draft_rule_pack.py` defines provider-free DTOs only.
- `backend/app/application/draft_rule_pack_compiler.py` orchestrates compilation.
- `backend/app/application/draft_rule_pack_from_registry.py` maps selected registry
  rules back into the compatibility `RulePack` payload.
- `backend/app/application/draft_rule_pack_sections.py` maps source context into
  rule-pack categories.
- `backend/app/application/draft_run_pipeline.py` only calls the compiler and writes
  `steps[1].artifactPayload`.

Slice 2.11 upgrades this boundary into a machine-readable registry without changing
the DraftRun step order or SQLite schema. The worker still writes a top-level
compatibility `RulePack` payload in the `rulePack` step, but that payload now includes
`ruleRegistrySnapshot`. Validators and directed revisions must consume rule ids from
that snapshot instead of anonymous prose constraints.

Rule-registry ownership is intentionally split:

- `backend/app/domain/draft_rule_registry.py` defines provider-free registry DTOs.
- `backend/app/application/draft_rule_registry_compiler.py` orchestrates registry
  compilation from context, SourceLedger, FeasibilityReport, and PostContract.
- `backend/app/application/draft_rule_registry_contract.py` maps PostContract claims,
  obligations, CTA, thesis, and forbidden moves into rules.
- `backend/app/application/draft_rule_registry_sections.py` maps brief, publisher,
  topic, fabula, source-ledger, candidate, and source-signal inputs into registry
  rules.

Slice 2.12.3 implements `SourceIntent` and `ResearchPlan`. Approved brief sources are
now normalized before feasibility: URLs, named sources, human-language research
requests, proof needs, framing hints, and exclusions become a typed research plan.
Slice 2.12.3.1 moves source defaults up into `Fabula.researchStrategy`: editorial
model fabulas can use `auto` source discovery hints or manual instructions, while
`PostBrief.sources` remains the approved runtime override for one post. DraftRun
context carries the fabula policy for diagnostics, but the `sourceIntent` step still
uses only the approved `PostBrief.sources`.
Slice 2.12.4 adds `publicEvidence` immediately after `sourceIntent`: exact URL tasks
are read through an infrastructure URL reader. Slice 2.12.4.1 adds an optional
OpenRouter server-tool search path for general research tasks: when
`OPENROUTER_WEB_TOOLS_ENABLED=true`, `findPublicSources` and `verifyClaim` tasks call
`openrouter:web_search`, create child `AiRun` records, and turn returned citations
into `PublicEvidenceItem` candidates. When the flag or provider config is missing,
the same tasks remain explicit `notConfigured` attempts. Slice 2.12.4.2 repairs
the query boundary: search uses the human task instruction plus post context, while
technical target ids stay only as trace links. Returned citations pass a conservative
relevance guard; rejected citations remain in trace and cannot become evidence
candidates. Slice 2.12.5 synthesizes accepted `PublicEvidenceItem` records into
`EvidenceSynthesis` and merges them into an enriched `SourceLedger` before
`feasibility`, `postContract`, `RuleRegistry`, planning, rhetorical plans, and draft
candidates. Failed, skipped, disabled, or rejected attempts stay as warnings and never
become proof.

Slice 2.7 implements the first OpenRouter-assisted planning steps inside the queued
runner. The worker's `materialPlan` step consumes context summary plus `RulePack` and
produces evidence inventory, missing evidence, risky claims, grounding plan, source
notes, and open questions. The `strategy` step consumes context summary, `RulePack`,
and material plan, then produces thesis angle, opening move, argument sequence,
fabula usage, CTA plan, forbidden moves, and tone notes. Both steps create child
`AiRun` audit records; missing provider configuration, provider errors, or invalid
JSON use deterministic fallback and mark `fallbackUsed=true`. After Slice 2.12.5.1,
`materialPlan` has a stricter rule: it receives `usableEvidenceCandidates` projected
from the enriched `SourceLedger`, `PostContract`, and `RuleRegistry`; if it returns
empty evidence without concrete rejection reasons, the backend retries with a repair
prompt, then optional `OPENROUTER_BACKUP_MODEL`, and only then records deterministic
emergency fallback.

Slice 2.13.2 applies the same fallback discipline to `rhetoricalPlans`: malformed
JSON, wrong shape, or too few plans trigger a primary repair retry, then optional
backup-model retry, and only then deterministic fallback. Each provider attempt is a
child `AiRun`, and the `rhetoricalPlans` artifact stores an `attempts[]` trace.
After Slice 2.15.6.3, the same universal JSON attempt contract also covers writer
draft candidates and alternative-angle challenger prose. Directed revision,
editorial critique, LLM validation, pairwise ranking, material planning, and evidence
interpretation already use the same shared attempt policy.

Planning ownership is split:

- `backend/app/domain/draft_planning.py` defines provider-free planning DTOs.
- `backend/app/application/draft_material_plan_service.py` owns material-plan step
  orchestration.
- `backend/app/application/material_plan_evidence_projection.py`,
  `backend/app/application/material_plan_accountability.py`,
  `backend/app/application/material_plan_retry_policy.py`, and
  `backend/app/application/material_plan_retry_orchestrator.py` own material-plan
  evidence handoff, accountability, and retry behavior.
- `backend/app/application/draft_strategy_service.py` owns draft-strategy step
  orchestration.
- `backend/app/application/draft_planning_prompts.py` owns prompt messages.
- `backend/app/application/draft_planning_audit.py` owns sanitized child `AiRun`
  traces.
- `backend/app/infrastructure/openrouter_json_adapter.py` owns generic provider JSON
  calls.
- `backend/app/application/openrouter_public_search_service.py` owns public-evidence
  search task orchestration and child `AiRun` audit.
- `backend/app/infrastructure/openrouter_web_search_adapter.py` owns the OpenRouter
  `openrouter:web_search` server-tool HTTP call and citation parsing.
- `backend/app/infrastructure/draft_run_pipeline_factory.py` owns worker-time wiring.

Slice 2.8 turns the worker's `draft` step into multi-candidate generation. The
worker creates deterministic candidate directions from `DraftStrategy`, asks
OpenRouter for one JSON draft candidate per direction when configured, falls back per
candidate when a provider call fails, stores all candidates in
`steps[4].artifactPayload`, and writes only the selected candidate to
`DraftRun.finalDraft`. Slice 2.12.4.3 adds a publishability guard before that write:
emergency `deterministicFallback` candidates are diagnostic artifacts unless they pass
the same publishability checks as provider candidates. If at least one provider
candidate is publishable, fallback candidates are excluded or heavily penalized and
cannot become the final draft. If no candidate is publishable, the run completes as a
quality-blocked `DraftRun` with `status=succeeded`, `finalDraft=null`, and
`complete.blockedBy=draftCandidateSelection`; this must not trigger compatibility or
local fallback.

Candidate ownership is split:

- `backend/app/domain/draft_candidates.py` defines provider-free candidate, score, and
  selection DTOs.
- `backend/app/application/draft_candidate_direction_service.py` owns deterministic
  direction policy.
- `backend/app/application/draft_candidate_generation_service.py` owns draft-candidate
  step orchestration and child `AiRun` creation.
- `backend/app/application/draft_candidate_selection_service.py` owns deterministic v1
  candidate scoring.
- `backend/app/application/draft_candidate_publishability.py` owns provider-free
  publishability, fallback-exclusion, raw-artifact, mojibake, and rewrite-needed
  checks for candidate selection.
- `backend/app/application/draft_candidate_prompts.py` owns candidate prompt messages.
- `backend/app/application/draft_candidate_audit.py` owns sanitized child `AiRun`
  traces.
- `backend/app/application/deterministic_draft_candidate_service.py` owns candidate
  fallback generation.
- `backend/app/application/draft_run_draft_step_service.py` owns the legacy
  deterministic draft-step fallback when candidate generation is not wired.

Validation ownership is split:

- `backend/app/domain/draft_validation.py` defines provider-free validation report,
  candidate report, finding, and status DTOs.
- `backend/app/domain/draft_llm_validation.py` defines provider-free LLM validation
  report, candidate report, and attempt DTOs.
- `backend/app/domain/draft_editorial_critique.py` defines provider-free editorial
  critique report, candidate critique, observation, and attempt DTOs.
- `backend/app/domain/draft_model_roles.py` defines provider-free DraftRun model-role
  and model-selection DTOs.
- `backend/app/application/draft_validation_linter.py` owns deterministic local
  checks for size, contract signals, evidence, rules, and publishability.
- `backend/app/application/draft_attribution_markers.py` owns deterministic
  source-marker extraction and per-claim attribution matching for external ledger
  claims.
- `backend/app/application/draft_validator_orchestrator.py` owns candidate iteration
  and report assembly.
- `backend/app/application/draft_llm_validation_service.py` owns report-only
  provider-backed validation orchestration.
- `backend/app/application/draft_llm_validation_prompts.py` owns validator prompt
  messages.
- `backend/app/application/draft_llm_validation_audit.py` owns sanitized child
  `AiRun` traces for validator attempts.
- `backend/app/application/draft_llm_validation_parser.py` normalizes provider JSON
  into standard validation findings.
- `backend/app/application/draft_llm_validation_observations.py` owns positive/pass
  observation detection so non-actionable LLM notes do not become warning findings.
- `backend/app/application/draft_editorial_critique_service.py` owns report-only
  provider-backed prosecutor/editor critique orchestration.
- `backend/app/application/draft_editorial_critique_prompts.py`,
  `draft_editorial_critique_parser.py`, and `draft_editorial_critique_audit.py` own
  critic prompt shape, provider JSON normalization, and sanitized child `AiRun`
  traces.
- `backend/app/application/draft_validation_step_service.py` composes deterministic
  validation, LLM validation, editorial critique, and ranking/revision into the
  existing `validation` step artifact.
- `backend/app/application/draft_validation_step.py` remains a compatibility bridge
  for older deterministic-only validation call sites.

Slice 2.12 inserts `RhetoricalPlans` between `DraftStrategy` and `DraftCandidates`.
The worker now writes a separate `rhetoricalPlans` step artifact, and candidate
generation consumes that artifact instead of inventing its own directions. Each draft
candidate must reference the `rhetoricalPlanId` it executes.

Rhetorical-plan ownership is split:

- `backend/app/domain/draft_rhetorical_plan.py` defines provider-free plan DTOs.
- `backend/app/application/draft_rhetorical_plan_service.py` is the thin step facade.
- `backend/app/application/draft_rhetorical_plan_retry.py` owns OpenRouter JSON retry
  attempts and deterministic fallback discipline.
- `backend/app/application/json_step_retry_policy.py` owns the reusable attempt
  sequence for JSON-producing LLM steps.
- `backend/app/application/draft_rhetorical_plan_prompts.py` owns plan prompt
  messages.
- `backend/app/application/draft_rhetorical_plan_audit.py` owns sanitized child
  `AiRun` traces.
- `backend/app/application/deterministic_rhetorical_plan_service.py` owns fallback
  plan generation.
- `backend/app/application/deterministic_rhetorical_plan_step_service.py` owns the
  compatibility step adapter used when provider-backed planning is not wired.

Slice 2.12.1 fixes the orchestration discipline for long-running queued runs.
Provider-backed steps can legitimately take longer than the old frontend polling
timeout. A created `DraftRun` in `queued` or `running` state remains the primary
source of truth and must not be replaced by `/api/drafts/generate` simply because the
polling window elapsed. Long-running steps (`materialPlan`, `strategy`,
`rhetoricalPlans`, and `draft`) are written as `running` before the provider or
application call starts. Child `AiRun` ids are persisted after each step completes,
not only at final run completion. `GET /api/draft-runs/{id}` computes
`isStale`, `staleReason`, and `lastProgressAt` from existing timestamps; stale means
"no progress for five minutes", not automatic failure and not permission to silently
fallback. Celery task time limits are allowed to mark a real timeout as `failed` with
a safe error.

Slice 2.14.1 extends that contract with artifact-level operation progress. Long
steps can write `artifactPayload.progress` while they are still running:
`currentOperationId`, `operations[]`, status, timestamps, target/query, safe error,
notes, and child `AiRun ID` when available. `publicEvidence` records URL/search/
skip/synthesis operations, `draft` records candidate-generation operations, and
`validation` records deterministic lint, per-candidate LLM validation, pairwise
ranking, directed revision, and regression guard operations. These writes reuse the
existing step update path, move `draft_runs.updated_at`, and make the main workbench
and `/ai-runs` show what is actually happening inside a long step.

Slice 2.15.6.1 refines progress writes for validation specifically: running operation
updates must preserve already-built deterministic/LLM/critic/tournament/ranking
artifacts, and a failed late operation must be visible as a nested failed operation
with the previous best final decision when such a candidate exists.

Validator scoring and revision loops remain later work; Slice 2.8 selection is a
deterministic first-pass scorecard, Slice 2.9 adds internal provenance, and the next
quality correction adds drafting-time public evidence before validators.

The post-2.8 drafting quality spine is now:

- `RuleRegistrySnapshot`: selected machine-readable rules with ids, scope, priority,
  severity, observable criteria, validator type, examples, and repair policy.
- `SourceIntent`: normalized approved-fabula source requests: URLs, search-query
  hints, required proof, optional proof, and framing-only material.
- `SourceLedger`: atomic claims from the signal, candidate, approved brief, author
  correction, and author-position evidence. It stores provenance, confidence, allowed
  use, risks, and forbidden inferences.
- `ResearchPlan`: what the runner should read, search, verify, or avoid before prose
  generation.
- `PublicEvidenceItem`: one extracted external claim with source, confidence, allowed
  use, and risk notes.
- `EvidenceSynthesis`: how public material confirms, qualifies, contradicts, or fails
  to support the intended post.
- `FeasibilityReport`: a pre-writing decision that marks the run as feasible,
  feasible with constraints, needing research, needing human decision, or infeasible.
- `PostContract`: locked editorial invariants for the post: thesis, audience value,
  CTA, allowed claims, forbidden moves, platform constraints, and fabula obligations.
- `RhetoricalPlan`: one possible route for writing the same contract, including
  planned moves, claims to use, claims to avoid, and CTA route.
- `DeterministicLinter` and `ValidatorReport`: implemented report-only checks over
  candidates, `SourceLedger`, `PostContract`, `RuleRegistry`, and `MaterialPlan`.
- `PairwiseRanking`, `DirectedRevision`, and `RegressionReport`: the later quality
  loop. These artifacts must consume the source ledger and post contract; they must
  not reconstruct provenance or invariants from generated text alone.

Slice 2.9 implements the first seed `SourceLedger` inside
`steps[0].artifactPayload.sourceLedger`. The ledger is not a new `DraftRunStepKey` and
does not require a SQLite schema change. It records deterministic claim ids, source
provenance, allowed use, confidence, risks, forbidden inferences, and missing-context
warnings before rule-pack/material-plan/draft work. The public-evidence layer extends
this ledger: approved-brief sources become `SourceIntent`, then `ResearchPlan`,
public evidence extraction, and `EvidenceSynthesis`, before feasibility and
post-contract decisions are treated as final.

Slice 2.10 inserts two logical steps after `context/sourceLedger` and before
`rulePack`: `feasibility` and `postContract`. `FeasibilityReport` decides whether the
post can be written safely from the available ledger claims. Only `feasible` and
`feasible_with_constraints` continue into prose generation. `needs_research`,
`needs_human_decision`, and `infeasible` complete the `DraftRun` as a successful
quality-blocked run: `DraftRun.status=succeeded`, `finalDraft=null`, and
`complete.status=blocked`. The frontend must show this as "post stopped before
generation" and must not trigger compatibility or local fallback. `PostContract`
locks thesis, audience, value, goal, CTA, slot/platform, allowed claim ids, forbidden
moves, evidence obligations, fabula obligations, and risk notes for all later
strategy, candidate, validator, ranking, and revision slices.

Slice 2.10.1 calibrates the first feasibility gate against a real false-block case:
`DraftRun d5d17b60-a711-485f-923e-91a93f263f12` had source signal, topic, fabula,
brief evidence, and source evidence, but the `EditorialWorkItem` had no
`postCandidateId`. Candidate linking now uses a shared selector during plan-slot
approval and DraftRun context building. If the candidate link is missing but source
signal evidence, approved brief evidence, topic, and fabula are present, feasibility
continues as `feasible_with_constraints`. If candidate recovery is ambiguous or the
source context is weak, the run still stops as a quality-blocked human-decision case.

Slice 2.11.1 adds the first publication-size contract without coupling fabulas to
platforms. `ContentPlanSettings.publicationSizeProfiles` stores editable demo profiles
such as Telegram post, LinkedIn post, and LinkedIn article. A plan slot may lock one
profile through `ContentPlanItem.publicationSizeProfileId`; otherwise the settings
default or platform demo default is used. `Fabula.sizeIntent` stores only dramaturgical
scale (`compact`, `standard`, `deep`) and never means "this fabula is for Telegram".
The backend resolves these inputs into `PostContract.publicationSizeContract`, then
`RuleRegistrySnapshot` emits deterministic size rules for hard max length, target
range, paragraph/section range, and density. `PostCandidate` stays a concept and does
not regain `format` or size fields.

The public-evidence research layer has its own ownership boundary:

- `backend/app/domain/draft_source_intent.py` defines provider-free `SourceIntent` and
  `ResearchPlan` DTOs;
- `backend/app/domain/draft_public_evidence.py` defines provider-free
  `PublicEvidenceBatch`, attempts, items, and warnings;
- `backend/app/application/public_evidence_retrieval_service.py` executes the public
  evidence step through application ports and marks unconfigured search honestly;
- `backend/app/application/public_evidence_query_builder.py` builds search queries
  from human research instructions and post context instead of technical target ids;
- `backend/app/application/public_evidence_relevance.py` applies deterministic
  relevance filtering before citations become public evidence candidates;
- `backend/app/application/public_evidence_ports.py` defines URL/search ports and
  search result contracts for the public-evidence step;
- `backend/app/application/disabled_public_search_adapter.py` owns the explicit
  `notConfigured` fallback when search is disabled;
- `backend/app/application/openrouter_public_search_service.py` executes configured
  OpenRouter search tasks and records child `AiRun` audit;
- `backend/app/infrastructure/public_url_reader.py` owns direct URL HTTP reads and
  lightweight text extraction;
- `backend/app/infrastructure/openrouter_web_search_adapter.py` owns OpenRouter
  `openrouter:web_search` HTTP calls and citation parsing;
- `backend/app/application/source_intent_normalizer.py` owns deterministic
  line-by-line classification;
- `backend/app/application/source_research_plan_service.py` owns the OpenRouter /
  fallback research-plan step orchestration;
- `backend/app/application/source_research_prompts.py` owns research-plan prompt
  messages;
- `backend/app/application/source_research_audit.py` owns sanitized child `AiRun`
  traces;
- `backend/app/application/deterministic_source_research_plan_service.py` and
  `backend/app/application/deterministic_source_research_step_service.py` own local
  fallback planning;
- `backend/app/domain/draft_evidence_synthesis.py` defines provider-free
  `EvidenceSynthesis` and external evidence claim DTOs;
- `backend/app/application/deterministic_external_evidence_synthesis.py`,
  `backend/app/application/deterministic_external_evidence_synthesis_step_service.py`,
  and `backend/app/application/external_evidence_synthesis_prompts.py` own fallback
  synthesis and prompt construction;
- `backend/app/application/external_evidence_synthesis_service.py` owns OpenRouter
  synthesis, while `backend/app/application/draft_public_evidence_step_service.py`
  coordinates retrieval, synthesis, and merge for the `publicEvidence` step;
- `backend/app/application/source_ledger_external_evidence_merger.py` merges accepted
  public evidence into the enriched source ledger;
- `backend/app/infrastructure/draft_run_pipeline_provider_services.py` owns
  provider-backed DraftRun dependency wiring for public evidence;
- infrastructure adapters should own URL reading, web search, browser/search APIs,
  external source retrieval, and provider-specific evidence extraction calls;
- React should only send approved brief sources and show compact progress/trace links;
  it must not call web search or provider APIs directly.

Concrete queued drafting files:

- `backend/app/domain/draft_run.py`
- `backend/app/domain/draft_run_steps.py`
- `backend/app/domain/draft_feasibility.py`
- `backend/app/domain/draft_post_contract.py`
- `backend/app/domain/publication_size.py`
- `backend/app/domain/draft_rule_registry.py`
- `backend/app/domain/draft_evidence_synthesis.py`
- `backend/app/domain/draft_evidence_interpretation.py`
- `backend/app/api/draft_runs.py`
- `backend/app/api/draft_generation_contracts.py`
- `backend/app/application/draft_run_service.py`
- `backend/app/application/draft_run_pipeline.py`
- `backend/app/application/draft_run_progress.py`
- `backend/app/application/draft_run_step_progress.py`
- `backend/app/application/draft_run_step_progress_payload.py`
- `backend/app/application/draft_run_staleness.py`
- `backend/app/application/draft_run_payloads.py`
- `backend/app/application/draft_run_context_payloads.py`
- `backend/app/application/draft_run_context_builder.py`
- `backend/app/application/draft_source_ledger_builder.py`
- `backend/app/application/draft_source_ledger_sections.py`
- `backend/app/application/draft_public_evidence_step_service.py`
- `backend/app/application/deterministic_external_evidence_synthesis.py`
- `backend/app/application/deterministic_external_evidence_synthesis_step_service.py`
- `backend/app/application/external_evidence_synthesis_prompts.py`
- `backend/app/application/external_evidence_synthesis_service.py`
- `backend/app/application/source_ledger_external_evidence_merger.py`
- `backend/app/application/evidence_interpretation_service.py`
- `backend/app/application/evidence_interpretation_prompts.py`
- `backend/app/application/evidence_interpretation_audit.py`
- `backend/app/application/deterministic_evidence_interpretation.py`
- `backend/app/application/deterministic_evidence_interpretation_step_service.py`
- `backend/app/application/evidence_interpretation_context_cards.py`
- `backend/app/infrastructure/draft_run_pipeline_provider_services.py`
- `backend/app/application/draft_feasibility_gate.py`
- `backend/app/application/draft_feasibility_policy.py`
- `backend/app/application/draft_post_contract_builder.py`
- `backend/app/application/publication_size_contract_resolver.py`
- `backend/app/application/draft_quality_gate.py`
- `backend/app/application/draft_rule_pack_compiler.py`
- `backend/app/application/draft_rule_pack_sections.py`
- `backend/app/application/draft_rule_registry_size.py`
- `backend/app/application/draft_material_plan_service.py`
- `backend/app/application/draft_strategy_service.py`
- `backend/app/application/draft_candidate_generation_service.py`
- `backend/app/application/draft_candidate_direction_service.py`
- `backend/app/application/draft_candidate_selection_service.py`
- `backend/app/application/draft_candidate_publishability.py`
- `backend/app/application/draft_validation_linter.py`
- `backend/app/application/draft_validator_orchestrator.py`
- `backend/app/application/draft_validation_step.py`
- `backend/app/application/draft_planning_prompts.py`
- `backend/app/application/draft_planning_audit.py`
- `backend/app/application/draft_candidate_prompts.py`
- `backend/app/application/draft_candidate_audit.py`
- `backend/app/application/deterministic_draft_candidate_service.py`
- `backend/app/application/draft_run_pipeline_ports.py`
- `backend/app/application/draft_run_draft_step_service.py`
- `backend/app/application/deterministic_draft_planning_service.py`
- `backend/app/application/deterministic_draft_planning_step_services.py`
- `backend/app/application/draft_llm_validation_service.py`
- `backend/app/application/draft_llm_validation_prompts.py`
- `backend/app/application/draft_llm_validation_audit.py`
- `backend/app/application/draft_llm_validation_parser.py`
- `backend/app/application/draft_validation_step_service.py`
- `backend/app/application/draft_validation_operation_safety.py`
- `backend/app/domain/draft_run_steps.py`
- `backend/app/domain/draft_run_context.py`
- `backend/app/domain/draft_source_ledger.py`
- `backend/app/domain/draft_feasibility.py`
- `backend/app/domain/draft_post_contract.py`
- `backend/app/domain/draft_rule_pack.py`
- `backend/app/domain/draft_planning.py`
- `backend/app/domain/draft_candidates.py`
- `backend/app/domain/draft_validation.py`
- `backend/app/domain/draft_llm_validation.py`
- `backend/app/domain/draft_model_roles.py`
- `backend/app/application/draft_model_role_resolver.py`
- `backend/app/application/draft_generation_params.py`
- `backend/app/application/draft_provider_error_utils.py`
- `backend/app/infrastructure/openrouter_json_adapter.py`
- `backend/app/infrastructure/draft_run_pipeline_factory.py`
- `backend/app/infrastructure/sqlite_draft_run_repository.py`
- `backend/app/infrastructure/celery_app.py`
- `backend/app/infrastructure/celery_draft_run_dispatcher.py`
- `backend/app/infrastructure/draft_run_tasks.py`
- `src/infrastructure/draftRunClient.ts`
- `src/infrastructure/draftRunRequestPayload.ts`
- `src/application/draftRunContext.ts`
- `src/application/postCandidateLinking.ts`

The Dockerized local stack is an execution wrapper around the same boundaries:

- `docker/backend.Dockerfile` builds only the FastAPI backend and Python dependencies.
- `docker/frontend.Dockerfile` builds only the Vite frontend and Node dependencies.
- `compose.yaml` wires frontend, backend, Redis, and Celery worker services; publishes
  `8000`, `5176`, and local Redis; injects `.env` values at runtime; and mounts
  `./var` for SQLite audit/run state.
- `.dockerignore` excludes `.env`, local caches, `node_modules`, build outputs, and
  audit data from the Docker build context.

Docker does not change ownership rules. API handlers remain thin, provider calls stay
under `backend/app/infrastructure`, workspace state remains local-first, and future DB,
queue, or worker services must be added as separate Compose services behind explicit
application/infrastructure boundaries.

`langgraph-document-ai-platform` is a future infrastructure/workflow dependency behind
a Glavred-owned facade. It may produce import-review candidates, document analysis, or
workflow results, but it must not write author-position assertions, source signals, or
production artifacts without an application service and HITL transition.

Backend OOP/SRP guardrails:

- classes and modules own one role: route, use case, domain policy, adapter, mapper, or
  test fixture;
- no 2-3k line backend files, no god services, and no boilerplate-only packages;
- no provider calls from API handlers, React, or domain modules;
- no direct `langgraph-document-ai-platform` imports outside the backend
  infrastructure/workflow facade;
- every backend slice adds or updates backend tests and `npm run test:architecture`
  smoke coverage for file size, ownership, and forbidden imports;
- every new backend architecture rule needs ADR + SAO coverage and either an automated
  check or an agent workflow checklist.

## React UI Architecture

The React implementation has been extracted from the initial fast-exploration
god-file. As of Slice 1.5.14, `src/App.tsx` is a small composition root. Shell,
navigation, topbar/sidebar, context-chat overlay, shared icon, weight range editor,
persistence/autosave/reset, high-level workspace orchestration, `Author Memory`,
`Editorial Model`, `Signals`, and the production flow feature entrypoints now live
outside `App.tsx`. This is the new baseline for future feature work.

Target structure:

- `src/app/`: app shell, topbar/sidebar, navigation, context-chat overlay and scope,
  and workspace controller.
- `src/features/author-memory`: author memory feed, assertions, import queue, and
  archive UI.
- `src/features/editorial-model`: project profile, rules, topics, fabulas, matrix, and
  setup validation UI.
- `src/features/signals`: radar setup, found signals, signal review, and post
  candidate entry points.
- `src/features/plan`: broadcast grid, planning settings, and future calendar UI.
  Plan-specific filter/group/edit/calendar state stays in role-owned plan modules.
  The current settings UI owns an explicit mini-calendar for selected publish slots;
  recurring day/time fields are fallback defaults, not the visible planning control.
  The broadcast grid also has a calendar view that reuses the same week/month/quarter
  calendar model, shows filtered candidate counts per date, and renders the same slot
  rows below a selected date instead of creating a second card pattern.
- `src/features/briefing`: compatibility post-brief workbench. Future slices should
  fold this into the selected post inside `src/features/editing` rather than keep
  brief editing as a separate top-level workflow destination.
- `src/features/editing`: editorial work queue and selected-post workbench. It owns
  the `Посты / Рабочий стол` tabs, lists approved posts first, lets the author return
  a work item to candidates, and owns the selected-post preparation stages. The target
  stage model is `Фабула -> Драфт -> Визуал -> readyForRelease`; `Финал` remains only a
  compatibility approved-text artifact, not a user-facing workbench tab.
- `src/features/release`: publication log and delivery history. It should list ready
  posts and publication attempts, then show status, external links, adapter errors, and
  retry notes. It must not become a text, visual, checklist, or package-preparation
  workbench.
- `src/features/analytics`: manual metrics and editorial learning note UI.
- `src/features/context-chat`: collapsible context assistant overlay, deterministic
  suggestions, and future provider-backed chat adapter boundary.
- `src/shared/ui`: reusable cabinet primitives such as shell sections, panels, framed
  rows, tabs, badges, fields, action groups, metric cards, and empty states.
- `src/shared/format`: labels, dates, status text, source names, and other formatting
  helpers.

React dependency direction is:

`features -> shared/application/domain`

There is no feature -> feature dependency. If two features need the same visual
primitive, it belongs in `src/shared/ui`. If two features need the same business action,
it belongs in application/domain services. If app-level wiring is needed, it belongs in
`src/app/`.

`App.tsx` is a composition root only. It imports `useWorkspaceController`
from `src/app/useWorkspaceController.ts` and must not import `LocalWorkspaceStore`.
It may connect the app shell, workspace controller, and feature entry components, but
new large `*View`, `*Editor`, `*Panel`, `*Card`, `*Header`, `*Sidebar`, `*Topbar`, or
`*Overlay` implementations must not be added there. Domain/application logic must not
be written inside JSX.

Architecture smoke tests enforce the baseline:

- `src/App.tsx <= 350` lines after Slice 1.5.14.
- `src/App.test.tsx <= 300` lines and covers app shell/navigation only.
- Large `App.tsx` UI declarations `<= 1`.
- Required app/shared extraction files, `src/features/author-memory/AuthorMemoryView.tsx`,
  `src/features/signals/SignalsView.tsx`, and
  `src/features/editorial-model/EditorialModelView.tsx` must exist.
- Production flow entrypoints must exist:
  `src/features/plan/PlanView.tsx`, `src/features/briefing/BriefView.tsx`,
  `src/features/editing/EditView.tsx`, `src/features/release/ReleaseView.tsx`, and
  `src/features/analytics/AnalyticsView.tsx`.
- `src/App.tsx` must not import or instantiate `LocalWorkspaceStore`.
- `src/App.tsx` must not contain signals feature internals such as `RadarEditor`,
  `SignalsSidePanel`, `RadarView`, or radar/signal label helpers.
- `src/App.tsx` must not contain editorial-model internals such as `TopicEditor`,
  `FabulaEditor`, `TopicFabulaMatrixView`, `EditorialValidationPanel`, or
  editorial setup helper factories.
- `src/App.tsx` must not contain author-memory internals such as `AuthorNoteCard`,
  `AssertionCard`, `ExternalSourcesView`, `ImportQueueView`, `ArchiveView`, or
  author-memory/import helper functions.
- `src/App.tsx` must not contain production-flow internals such as `PlanView`,
  `BriefView`, `EditView`, `ReleaseView`, `AnalyticsView`, `HitlGate`, `FieldInput`,
  `CheckCard`, or `FinalTextView` implementations.
- The React UI architecture ADR and this SAO section must exist.

Every extraction slice must lower these limits. The target after the extraction chain
is now met for `App.tsx`; future slices should keep it at composition-root size and
avoid moving feature behavior back into it.

### Test ownership guardrails

Tests follow the same ownership model as production code:

- `src/App.test.tsx` is the app-shell smoke test. It must not contain feature-flow
  helpers such as `goToSignals`, `createApprovedBrief`, `createExportedRelease`, or
  deep form assertions. Feature workflows move to feature-owned `*AppFlow.test.tsx`
  files.
- Feature app-flow tests live beside the feature they exercise:
  `src/features/signals/SignalsAppFlow.test.tsx`,
  `src/features/author-memory/AuthorMemoryAppFlow.test.tsx`,
  `src/features/editorial-model/EditorialModelAppFlow.test.tsx`,
  `src/features/plan/PlanAppFlow.test.tsx`,
  `src/features/editing/EditorialWorkbenchAppFlow.test.tsx`,
  `src/features/release/ReleaseAppFlow.test.tsx`,
  `src/features/analytics/AnalyticsAppFlow.test.tsx`, and
  `src/features/context-chat/ContextChatAppFlow.test.tsx`.
- `src/test-support` is a narrow helper layer for repeated user-flow navigation only.
  It must not hide business rules, assert product outcomes, or become a page-object
  framework.
- Architecture smoke tracks app-flow tests and major test-support files with the same
  near-limit summary used for production files. Adding behavior to a near-limit test
  requires splitting the test by feature/workflow in the same slice.

### Large-file guardrails

The next architecture risk is no longer `App.tsx`; it is large domain, application,
fixture, and feature files. Architecture smoke now tracks current large-file baselines:

- `src/app/useWorkspaceController.ts <= 220`
- `src/app/useWorkspacePersistence.ts <= 170`
- `src/app/useContextChatController.ts <= 220`
- `src/app/useSignalsWorkspaceActions.ts <= 180`
- `src/app/useProductionFlowActions.ts <= 260`
- `src/app/releaseExport.ts <= 90`
- `src/features/author-memory/AuthorMemoryView.tsx <= 320`
- `src/features/author-memory/useMemoryFeedController.ts <= 280`
- `src/features/author-memory/useImportReviewController.ts <= 300`
- `src/features/author-memory/MemoryFeedTab.tsx <= 260`
- `src/features/author-memory/MemorySidePanel.tsx <= 140`
- `src/features/author-memory/MemoryDialogs.tsx <= 120`
- `src/domain/editorialWorkspace.ts <= 170`
- `src/features/editorial-model/EditorialModelView.tsx <= 220`
- `src/fixtures/demoWorkspace.ts <= 120`
- `src/features/signals/SignalsView.tsx <= 180`
- `src/features/signals/useSignalsController.ts <= 280`
- `src/features/signals/RadarsTab.tsx <= 220`
- `src/features/signals/RadarCard.tsx <= 240`
- `src/features/signals/FoundSignalsTab.tsx <= 220`
- `src/features/signals/SourceSignalCard.tsx <= 260`
- `src/features/signals/SignalsHeader.tsx <= 100`
- `src/features/signals/SignalsTabs.tsx <= 80`
- `src/features/signals/PostCandidatesPreviewTab.tsx <= 120`
- `src/features/signals/PostCandidateCard.tsx <= 130`
- `src/features/signals/PostCandidateCardParts.tsx <= 40`
- `src/features/signals/PostCandidatesToolbar.tsx <= 120`
- `src/features/signals/PostCandidateGroupList.tsx <= 110`
- `src/features/signals/PostCandidateEditForm.tsx <= 110`
- `src/features/signals/PostCandidateEditContext.tsx <= 70`
- `src/features/signals/usePostCandidatesController.ts <= 60`
- `src/features/signals/postCandidateFilters.ts <= 80`
- `src/application/postCandidateService.ts <= 120`
- `src/application/editorialServices.ts <= 20`
- `src/domain/editorial-model/transitions.ts <= 20`
- `src/domain/editorial-model/rules.ts <= 50`
- `src/domain/editorial-model/validation.ts <= 460`
- `src/domain/editorial-model/catalog.ts <= 190`
- `src/features/author-memory/ImportViews.tsx <= 20`
- `src/features/author-memory/ImportQueueView.tsx <= 150`
- `src/features/author-memory/ImportQueueToolbar.tsx <= 120`
- `src/features/author-memory/ImportQueueBulkBar.tsx <= 130`
- `src/features/author-memory/ImportCandidateGroupList.tsx <= 140`
- `src/features/author-memory/ImportCandidateList.tsx <= 120`
- `src/features/author-memory/ImportQueueEmptyState.tsx <= 60`
- `src/features/editorial-model/EditorialModelParts.tsx <= 20`
- `src/features/editorial-model/TopicsTab.tsx <= 310`
- `src/features/editorial-model/FabulasTab.tsx <= 310`
- `src/features/signals/RadarEditor.tsx <= 270`
- `src/fixtures/demoImports.ts <= 410`

These are temporary ceilings, not acceptable target sizes. domain/application/fixtures/feature files must shrink through the 1.5.x refactoring chain. Product slices that add new user-facing UI are deferred until the large-file guardrails are lowered through bounded-context decomposition.

The refactoring direction is:

- domain types and transitions have moved from `editorialWorkspace.ts` into
  bounded-context modules;
- application services have moved from `editorialServices.ts` into workflow-specific
  services;
- demo data has moved from `demoWorkspace.ts` into scenario/context fixtures;
- large feature entrypoints have started moving internal tabs, panels, cards, forms, dialogs, and
  local helpers into feature-local files;
- feature modules still obey `no feature -> feature`.

Feature entrypoints stay thin. `AuthorMemoryView`, `EditorialModelView`, and
`SignalsView` are composition surfaces for their feature, not owners of every tab,
dialog, editor, row, side panel, and helper. Feature-local internals now live in
role-owned files such as:

- `src/features/author-memory/ExternalSourcesView.tsx`,
  `ImportQueueView.tsx`, `ImportQueueToolbar.tsx`, `ImportQueueBulkBar.tsx`,
  `ImportCandidateGroupList.tsx`, `ImportCandidateList.tsx`,
  `ImportQueueEmptyState.tsx`, `CandidateCard.tsx`, `ArchiveView.tsx`, and
  `BulkActionDialog.tsx`;
- `src/features/author-memory/useMemoryFeedController.ts`,
  `useImportReviewController.ts`, `MemoryFeedTab.tsx`, `MemorySidePanel.tsx`,
  and `MemoryDialogs.tsx`;
- `src/features/editorial-model/ProjectProfileHeader.tsx`,
  `PublisherRulesView.tsx`, `TopicsTab.tsx`, `FabulasTab.tsx`, and
  `MatrixTab.tsx`;
- `src/features/signals/useSignalsController.ts`, `SignalsHeader.tsx`,
  `SignalsTabs.tsx`, `RadarsTab.tsx`, `RadarCard.tsx`, `FoundSignalsTab.tsx`,
  `SourceSignalCard.tsx`, `PostCandidatesPreviewTab.tsx`, `PostCandidateCard.tsx`,
  `PostCandidateCardParts.tsx`, `PostCandidatesToolbar.tsx`,
  `PostCandidateGroupList.tsx`, `PostCandidateEditForm.tsx`,
  `PostCandidateEditContext.tsx`, `usePostCandidatesController.ts`,
  `postCandidateFilters.ts`, `RadarEditor.tsx`, and `SignalsSidePanel.tsx`.

Stateful feature orchestration belongs in feature-local hooks, not entrypoints.
After Slice 1.5.25, `AuthorMemoryView` composes the active memory tab, side panel,
and dialogs. Feed/composer/edit/delete/correction state lives in
`useMemoryFeedController`; import queue, archive, selection, bulk action, and undo
state lives in `useImportReviewController`.

After Slice 1.5.26, `SignalsView` composes the signals header, tabs, and active
workspace tab. Radar/signal expanded state, edit drafts, filters, summaries, and
derived lists live in `useSignalsController`; tab/entity rendering lives in
feature-local modules.

After Slice 1.5.27, `ImportQueueView` is also only a queue-tab composition root.
Queue filters and view mode live in `ImportQueueToolbar`; selection and bulk actions
live in `ImportQueueBulkBar`; list/group/empty rendering lives in
`ImportCandidateList`, `ImportCandidateGroupList`, and `ImportQueueEmptyState`.

After Slice 1.5.28, `useWorkspaceController` is only the app-level public facade.
Persistence/autosave/reset/toast live in `useWorkspacePersistence`; context-chat
state and suggestions live in `useContextChatController`; radar/signal mutations live
in `useSignalsWorkspaceActions`; downstream production callbacks live in
`useProductionFlowActions`; clipboard/download browser edges live in `releaseExport`.
New app-level action groups must be added to role-owned hooks, not back into the
controller facade.

Domain transitions are role-owned. `src/domain/editorial-model/transitions.ts`
is a compatibility barrel only; rules, setup validation, and topic/fabula catalog
transitions live in `rules.ts`, `validation.ts`, and `catalog.ts`. New transition
logic should be added to the role-owned file first, then re-exported only when
backward-compatible imports require it.

Source comments are required for domain ownership, invariants, legacy compatibility,
deterministic stubs, and future provider/backend boundaries. Comments should not
describe obvious JSX or restate simple assignments.

### Architecture drift prevention

Architecture rules are part of the delivery system, not only historical notes. A new
architecture rule is accepted only when it is recorded in an ADR, reflected in this
SAO, and backed by either an automated smoke check or an explicit mandatory agent
workflow checklist.

`npm run test:architecture` now reports both hard failures and warning-level drift
signals:

- hard line-count limits for `App.tsx`, `App.test.tsx`, and tracked large
  app/feature/domain/application/fixture files remain blocking;
- near-limit files are any tracked files at or above 85% of their limit and are listed
  at the end of a successful architecture smoke run;
- new behavior must not be added to a near-limit file unless the same slice includes a
  refactor step that moves behavior into a role-owned module;
- export-count warnings are observation-only for now and identify large tracked files
  whose public surface may need a facade or a split;
- `src/features/*` modules cannot import other features directly or through a root
  features barrel; cross-feature code belongs in `src/shared/*`,
  `src/application/*`, `src/domain/*`, or app-level composition.

Every product or refactor slice must include architecture preflight before
implementation. The preflight checks planned files against file-size limits, module
ownership, dependency direction, and design-system ownership. ROADMAP entries for new
product slices must include `Architecture impact`, and future agents must run
`npm run test:architecture` before completing refactor, domain, application, app, or
frontend slices.

The agent workflow is also enforced through `.agents/skills`: slice implementation,
roadmap planning, architecture design, regression strategy, frontend design-system,
and project onboarding now include the guardrails from ADR
`2026-06-16-architecture-drift-is-prevented-by-agent-and-smoke-guardrails`.

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
- Disclosure-heavy lists must be layout-stable: expanding or collapsing an entity row
  adds vertical detail inside the same frame and must not move the header, tabs,
  main/right grid, toolbar, or row horizontally.
- Existing entity edit mode must open inside the selected entity row/card. Top-of-list
  draft forms are acceptable for new entities, but editing an existing entity cannot
  create a duplicate form detached from the row the author clicked.
- Structured search instructions, source descriptions, and other long rule-like values
  use multiline controls. One-line inputs are reserved for short titles, labels, and
  compact scalar settings.
- Dense editor forms must keep measurable vertical rhythm between fields and between
  labels and controls; grouped controls cannot collapse into neighboring labels.
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
- `PostCandidate`: candidate assembly of signal, topic, fabula, audience, value, goal,
  platform, title, thesis, evidence summary, confidence, risks, and approval status.
  Legacy persisted candidate `format` values are ignored during workspace
  normalization.
- `InsightCard`: source signal, why it matters, audience relevance, author position,
  rubric, urgency, score, banality risk, fact gaps.
- `ContentPlanItem`: insight, platform, date, time, priority, fabula-derived format,
  expected effect, approval status, topic/fabula link, manual override state, and
  warning links.
- `ContentPlanSettings`: local-first period, tempo, publishing days/times, candidate
  limits, default platform, and signal-selection policy for the broadcast grid.
- `PlanWeightWarning`: advisory warning when the grid diverges from topic/fabula
  weights, matrix compatibility, or required slot fields.
- `PostBrief`: thesis, conflict, author position, evidence, examples, structure, CTA,
  risks, sources, approval status.
- `PostDraft`: brief, title, body, version, draft status, updated time.
- `EditorialCheck`: type, title, check status, summary, findings.
- `EditorNote`: agent, tone, text, target.
- `FinalText`: draft, title, body, approval status, approved time.
- `ReleasePackage`: compatibility/manual-export surface with final text, targets,
  Markdown, checklist, release status, and updated time. It is not the future source of
  truth for release state.
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
- `ReadyPost`: read/projection model produced by `Редактура` when a post has approved
  text and either an approved visual or explicit `без визуала` mode.
- `PublicationLogEntry`: delivery log record for a ready post, publication attempt,
  external link, status, adapter error, retry note, or manual/exported publication
  event.
- `PublicationAdapter`: infrastructure boundary for future Telegram/social/blog
  delivery integrations. Adapters write publication log entries; they do not edit
  editorial artifacts.

## Conceptual AI Provider Interfaces

These interfaces are documented for future implementation and are not runtime
TypeScript contracts in Slice 0.8. After Slice 2.3.4, drafting is modeled as a
multi-step run rather than a single provider request:

- `AiProviderAdapter`: infrastructure-side adapter that performs provider-specific
  calls for one capability or one `DraftRunStep`.
- `DraftRunContext`: provider-free DTO assembled from the selected work item,
  approved brief, plan slot, post candidate, source signal, topic, fabula, publisher
  rules, and future author-memory evidence.
- `SourceIntent`: normalized approved-brief source requests, URL seeds, search hints,
  required proof, optional proof, and framing-only material.
- `RuleRegistrySnapshot`: selected drafting rules with ids, scope, priority, severity,
  observable criteria, validator type, examples, and repair policy.
- `SourceLedger`: claim/provenance inventory built from source signal, candidate,
  brief, author corrections, author-position evidence, and later public evidence.
- `ResearchPlan`: explicit plan for what to read, search, verify, or avoid before
  prose generation.
- `PublicEvidenceItem`: external claim extracted from URL/search/source material with
  provenance, confidence, allowed use, and extraction notes.
- `EvidenceSynthesis`: reconciliation of public evidence with signal, fabula, and
  author position before feasibility and contract decisions.
- `EvidenceInterpretation`: editorial meaning extracted from accepted evidence:
  implications, tensions, examples, limits, forbidden overclaims, reader-value hooks,
  and rejected evidence uses for material planning and writing.
- `FeasibilityReport`: pre-writing decision that can stop a run before unsafe prose is
  generated.
- `PostContract`: locked editorial intent and constraints that later strategy,
  candidate, validator, and revision steps must preserve.
- `RulePack`: explicit hard constraints, soft constraints, evidence requirements,
  dramaturgy requirements, topic-fit requirements, and quality rubric.
- `MaterialPlan`: what evidence exists, what is missing, which claims are risky, and
  how the post should stay grounded.
- `DraftStrategy`: thesis, opening, argument sequence, fabula use, CTA, and forbidden
  moves before prose generation.
- `RhetoricalPlan`: one route for applying the post contract and fabula to the same
  source ledger.
- `DraftCandidate`: one generated title/body/rationale/risk attempt.
- `DeterministicLinter`: hard local checks before provider-backed validation.
- `ValidatorResult`: narrow quality result for publisher rules, topic fit, fabula fit,
  evidence grounding, anti-AI style, forbidden topics, audience value, structure, or
  claim risk.
- `PairwiseRanking`: traceable comparison of draft candidates.
- `RevisionAttempt`: targeted correction instruction plus resulting candidate.
- `RegressionReport`: post-revision re-check proving whether the repair improved or
  damaged the candidate.
- `PromptTemplate`: stable prompt layers and variables used by application step
  services before calling an adapter.
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
8. Approved signals produce 2-3 deterministic post candidates in `Кандидаты постов`.
9. The author approves one candidate; it becomes `postCandidate` and its signal becomes
   the compatibility `sourceSignal` for downstream flow.
10. `InsightScoring` produces an `InsightCard` from the approved candidate.
11. `ContentPlanning` saves grid settings, creates publish-window slots from the
   current date, and fills the hybrid grid with deterministic topic/fabula ideas.
12. The author approves a slot; the slot enters the editorial work queue as a
   selected production work item and receives an initial post fabula/brief.
13. Inside `Редактура -> Рабочий стол`, the author chooses a post, approves the
   fabula/brief, reviews the draft, and approves the post text in `Драфт`.
14. `Drafting` creates an editable research-note draft, and `EditorialChecks` returns
   style, anti-AI, fact-check, and policy checks plus editor notes.
15. The next stage is `Визуал`: the author chooses `Сгенерировать`, `Найти мем`,
   `Мем + генерация`, or `без визуала`, fills one `Бриф` field when a visual is
   needed, and approves the visual decision. Slice 1.10.7 then turns a completed
   visual decision into `readyForRelease`.
16. `Выпуск` becomes a publication log for ready posts and publication attempts.
   Until platform integrations exist, any manual export package remains compatibility
   behavior rather than the conceptual release model.

## Extension Points

- Author memory can ingest notes, links, archive posts, corrections, and analytics
  learning before production artifacts are created.
- External source import can add candidates to a review queue, but unreviewed material
  must not strengthen author-position assertions.
- Reviewed source material can become `SourceSignal`; unreviewed imports and archive
  records remain source material until the author or an acceptance policy promotes
  them.
- Post candidate assembly now feeds insight creation and supports local edit/reject
  review; later slices should add request-more variants and calendar slot binding while
  keeping current `contentPlanItems` as a compatibility layer.
- Approved plan slots become editorial work items immediately on slot approval.
  `Редактура` should operate on a selected work-item id so one post can move through
  fabula, draft, visual, and ready state without overwriting another approved post.
  `Выпуск` should consume ready posts and write publication log entries; it should not
  edit production artifacts.
- Bulk import can accept many historical items into archive, while preserving
  provenance, acceptance mode, and evidence policy.
- Source ingestion adapters can later replace manual signal entry.
- Validator adapters can later replace deterministic checks while preserving
  evidence-backed `ValidatorResult` contracts.
- Context chat can open draft flows for structured entities, but should not bypass
  explicit author review and save/cancel actions.
- AI provider adapters can later replace deterministic insight, planning, briefing,
  drafting, and check services after author position and validators exist.
- Backend AI execution starts with OpenRouter-backed application services behind thin
  HTTP routes. It should first replace one deterministic use case, then expand through
  audited `AiRun` records and adapter-backed workflows.
- `langgraph-document-ai-platform` can later analyze documents and archives behind a
  backend facade. Its output must enter Glavred as review candidates, not as direct
  domain mutations.
- Backend persistence can replace `LocalWorkspaceStore` behind the same workspace store
  interface.
- Platform publication APIs should attach through `PublicationAdapter` and write
  `PublicationLogEntry` records for ready posts. The manual release package is only a
  compatibility bridge.
- Real analytics ingestion can replace manual metric entry behind the analytics prep
  shape.

## Testing Strategy

Current validation covers:

- Unit tests for author memory event creation and evidence-backed assertions.
- Unit tests for domain transitions and approval rules.
- Unit tests for deterministic scoring, planning, briefing, drafting, editorial check,
  release packaging, and analytics prep services.
- Integration tests for local workspace save/load.
- Feature-owned app-flow tests for source signals, author memory, editorial model,
  planning, editing, release, analytics, and context chat.
- `src/App.test.tsx` is limited to app shell/navigation coverage.
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

For backend slices, add:

- Unit tests for settings, domain policies, application services, and adapters.
- Contract tests for API response shapes and provider result normalization.
- Failure tests for missing OpenRouter configuration, provider errors, invalid model
  output, and deterministic fallback.
- Architecture smoke checks for backend file-size limits, dependency direction,
  forbidden provider imports, and `.env.example` drift.
- No backend slice is complete until `npm run test:architecture` passes.

## Known Trade-offs

- The current `EditorialModel` is too coarse for the revised concept. It should be
  migrated carefully into smaller entities without breaking the existing demo flow.
- Author memory must stay loose enough for stream-of-consciousness input, while the
  position model must be structured enough for validation.
- Validator indicators can become noisy if every rule is shown at once. The UI needs
  progressive disclosure from colored status to evidence.
- Local-first persistence avoids backend scope, but it is not suitable for multi-device
  or team collaboration.
- Provider selection now has a practical default: backend AI execution uses
  OpenRouter first. The domain and application contracts still stay provider-agnostic
  so another provider can be added behind an adapter later.
- Starting backend work too broadly would create boilerplate. Backend growth should
  follow real use cases: environment validation, AI run audit, one OpenRouter-backed
  editorial action, then document/workflow adapters.

## Open Questions

- Which author memory event types should be implemented first: raw thoughts,
  link-reactions, radar corrections, archive annotations, or release learning?
- Should topic/fabula/platform weights initially be advisory only, or should they
  produce hard validation failures in the content plan?
- How much of the context chat should be implemented before real AI provider calls?
- Which hosted deployment target should be used after local-first development?
- Should the first backend persistence slice preserve the local workspace format or
  introduce a migration layer?
