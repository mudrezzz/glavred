# Developer Guide

## Stack

- React 18
- Vite
- TypeScript
- Vitest
- Future backend: Python/FastAPI with explicit domain/application/infrastructure
  boundaries.
- Default LLM provider target for backend execution: OpenRouter.

## Product Architecture Direction

The next product boundary is a SaaS-ready blog portfolio:

`UserAccount -> BlogProject -> PublicationChannels -> Project-scoped Workspace -> PlatformVariants`

`BlogProject` is the unit of isolation. Author memory, editorial rules, topics,
fabulas, sources, plans, drafts, final decisions, DraftRun links, and editorial
learning notes are project-scoped unless a later slice explicitly marks data as
user-scoped. Do not add new singleton workspace assumptions when implementing auth,
project switching, publication channels, or benchmark fixtures.

Slice 2.17.1 implements the local shell for that boundary. Frontend runtime now loads
`PortfolioState` through `LocalPortfolioStore`, then hydrates the existing app from
the active project's `WorkspaceState`. Legacy `glavred.workspace.v1` storage is
migrated into one default project; fresh reset seeds two users and three project
containers. The visible switcher is placed in the sidebar footer identity slot, not in
an extra top strip, so global account/project context stays out of screen-level
actions. Keep future portfolio logic in role-owned modules such as
`src/domain/portfolio`, `src/application/portfolioService.ts`, and
`src/infrastructure/localPortfolioStore.ts` instead of expanding near-limit
workspace or demo fixture files.

Important architecture rules for upcoming slices:

- local multi-account/project switching comes before full backend auth and is now
  implemented as a local-first shell;
- backend auth and persistence attach to `UserAccount`, `BlogProject`, and
  `ProjectMembership`;
- publication channels are modeled before platform adapters/autoposting;
- topic/fabula concepts remain reusable, while platform/channel constraints resolve
  later through plan items, post contracts, and platform variants;
- the three-blog demo portfolio is also a benchmark surface, so seeded data must stay
  realistic, isolated, and maintainable.

See ADR `docs/adr/2026-06-29-blog-project-portfolio-saas-boundary.md`.
Use `docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md` as the implementation
contract for Slice 2.17.x. If code behavior diverges from that document, update the
document in the same slice.

## Environment

Copy `.env.example` to `.env` for local development and fill secrets locally. `.env`
is ignored by Git; `.env.example` is the committed contract.

Required variables for the backend/AI track:

- `VITE_API_BASE_URL`: frontend-to-backend URL, default `http://localhost:8000`.
- `GLAVRED_ENV`, `GLAVRED_API_HOST`, `GLAVRED_API_PORT`: local backend runtime.
- `GLAVRED_CORS_ORIGINS`: comma-separated browser origins allowed to call the
  backend, defaulting to local Vite origins.
- `DATABASE_URL`, `REDIS_URL`: future persistence and queue configuration.
- `AI_RUN_AUDIT_DB_PATH`: local SQLite audit store for backend AI run records,
  default `var/glavred-ai-runs.sqlite3`.
- `OPENROUTER_API_KEY`: local OpenRouter token. Never commit it.
- `OPENROUTER_BASE_URL`: default `https://openrouter.ai/api/v1`.
- `OPENROUTER_DEFAULT_MODEL`: default model chosen for local backend runs.
- `OPENROUTER_BACKUP_MODEL`: optional backup model used by JSON repair retries.
  ADR `2026-06-27-llm-json-steps-use-universal-retry-policy` requires every
  JSON-producing LLM step to try primary, primary-repair, optional backup, and only
  then an explicit fallback/not-run/failed outcome.
- `DRAFT_RESEARCH_MODEL`: optional model for source-intent research planning and
  external evidence synthesis.
- `DRAFT_STRATEGY_MODEL`: optional model for material plan, draft strategy, and
  rhetorical plan JSON steps.
- `DRAFT_WRITER_MODEL`: optional model for draft candidates and directed revisions.
- `DRAFT_REVIEW_MODEL`: optional model for LLM validation and pairwise ranking.
- `DRAFT_CRITIC_MODEL`: optional model for the report-only prosecutor/editor critic.
- `DRAFT_FINAL_GATE_MODEL`: optional model for the independent final public-prose
  acceptance review. If empty, the backend prefers a non-writer critic model, then
  review, then default.
- `DRAFT_ANOTHER_ANGLE_MODEL`: optional model for the alternative-angle challenger
  route.
- Recommended DraftRun role preset for local experiments:
  - writer: `openai/gpt-5.1`;
  - technical JSON backup: `openai/gpt-4.1-mini`;
  - critic/final gate: `google/gemini-2.5-pro`;
  - another-angle: `qwen/qwen3.7-max`.
  Writer and critic/final gate should not be the same family by default: writer
  creates public prose, critic attacks quality and weak reasoning, final gate accepts
  the delivered post against the explicit quality contract, and another-angle is
  creative divergence rather than a backup writer.
- `DRAFT_WRITER_TEMPERATURE`, `DRAFT_WRITER_TOP_P`: generation params for draft
  candidate prose JSON calls. Defaults: `0.65`, `0.9`.
- `DRAFT_REVISION_TEMPERATURE`, `DRAFT_REVISION_TOP_P`: generation params for
  directed revision JSON calls. Defaults: `0.35`, `0.85`.
- `DRAFT_JSON_REPAIR_TEMPERATURE`: low-temperature JSON repair/backup attempts.
  Default: `0.15`.
- `DRAFT_ANOTHER_ANGLE_TEMPERATURE`: creative route-generation temperature for the
  another-angle role. Default: `0.8`.
- `OPENROUTER_APP_NAME`, `OPENROUTER_HTTP_REFERER`: OpenRouter attribution headers.
- `DRAFT_REVISION_MAX_ITERATIONS`: maximum directed-revision improvement cycles after
  initial candidate selection. Default `3`; invalid or zero values normalize to `1`.
- `OPENROUTER_WEB_TOOLS_ENABLED`: opt-in flag for OpenRouter server-tool web search.
  Default is `false`; set `true` only when you want DraftRun public search tasks to
  call the provider.
- `OPENROUTER_WEB_SEARCH_MODEL`: optional model override for `openrouter:web_search`;
  falls back to `OPENROUTER_DEFAULT_MODEL`.
- `OPENROUTER_WEB_SEARCH_MAX_RESULTS`: maximum search results requested from the
  OpenRouter web search server tool.
- `LANGGRAPH_DOCUMENT_AI_PLATFORM_MODE`,
  `LANGGRAPH_DOCUMENT_AI_PLATFORM_CONFIG`: future document/workflow adapter settings.

OpenRouter configuration belongs to backend infrastructure adapters only. React,
domain modules, API route handlers, and tests must not hardcode provider keys or call
provider SDKs directly.

Structured JSON provider calls must not be implemented as one raw OpenRouter call plus
ad hoc `json.loads`. The owning application service defines the schema and repair
prompt, but execution must follow the universal JSON retry policy: primary role model,
repair prompt on the same model, optional `OPENROUTER_BACKUP_MODEL`, then a traceable
domain-safe fallback or explicit unavailable/failed result. Each attempt should be
visible in child `AiRun` audit payloads with model role, selected model, status, and
safe parse/validation error. JSON parse failures should also store a sanitized raw
response excerpt when available, so diagnostics can identify prose, markdown fences,
empty output, or malformed JSON without exposing headers or secrets.

Draft writer prompts must also keep public prose separate from orchestration jargon:
internal artifact names such as `SourceLedger`, `publicEvidence`, `validators`,
`RuleRegistry`, and `PostContract` are allowed only when deliberately reframed and
explained as reader-facing concepts.

`AI_RUN_AUDIT_DB_PATH` is local development state. The default `var/` directory is
ignored by Git. Audit records may contain editorial request payloads, but provider
tokens and other secrets must be redacted before persistence.
- Testing Library

## Commands

Start the full Dockerized local stack:

```bash
docker compose up --build
```

This starts:

- `backend`: FastAPI on `http://localhost:8000`, with `./var` mounted for local
  SQLite AI run audit data.
- `frontend`: Vite on `http://localhost:5176`, configured to call the backend through
  `VITE_API_BASE_URL=http://localhost:8000`.

Docker Compose reads local secrets from `.env`, but `.env` is ignored by Git and
excluded from the Docker build context by `.dockerignore`.

Install dependencies:

```bash
npm install
python -m pip install -e ".[dev]"
```

Start local development:

```bash
npm run dev
```

Start the backend:

```bash
npm run dev:backend
```

Run tests:

```bash
npm test
```

Run backend tests:

```bash
npm run test:backend
```

Run build smoke test:

```bash
npm run smoke
```

Run React architecture guardrails:

```bash
npm run test:architecture
```

Run browser visual smoke checks for operational UI guardrails:

```bash
npm run test:visual
```

Run structural design-system checks for cabinet layout contracts:

```bash
npm run test:design
```

Refresh wiki screenshots:

```bash
npm run docs:screenshots
```

Publish GitHub Wiki from `docs/wiki/`:

```bash
npm run docs:wiki:publish
```

## Product and Refactor Slice Preflight

Before implementing a product, refactor, domain, application, app, or frontend slice:

1. Read the active `ROADMAP.md` slice and confirm it has `Architecture impact`.
2. For DraftRun, drafting, LLM role, trace, validation, ranking, or revision work,
   read `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` before changing code. If the
   slice changes the pipeline, update that Markdown file and regenerate
   `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf` in the same slice.
3. Check the planned files against the current large-file limits in
   `scripts/architecture-smoke.mjs`.
4. Treat files reported as near-limit by `npm run test:architecture` as closed for new
   behavior unless the same slice includes a refactor step into a role-owned module.
5. Confirm module ownership before editing:
   - app shell and high-level wiring stay in `src/app/`;
   - feature UI stays under its own `src/features/<feature>/` folder;
   - shared visual primitives go to `src/shared/ui`;
   - shared business behavior goes to `src/application` or `src/domain`.
6. For frontend work, check existing design-system primitives before adding a new UI
   pattern.
7. Run `npm run test:architecture` before completing the slice. For visible frontend
   changes, also run `npm run test:design` and `npm run test:visual`.
8. For backend slices, confirm the slice adds only the modules required by the current
   use case. Avoid empty package scaffolding, unused base classes, and "future"
   abstractions without tests.

Architecture rules are accepted only when they are documented in ADR/SAO and backed by
an automated check or mandatory workflow checklist. Warning-level near-limit and
export-count output should be reviewed even when the command exits successfully.

## Source Layout

- `src/domain/`: framework-independent domain model.
- `src/application/`: deterministic application services for author memory inference,
  insight, planning, briefing, drafting, editorial checks, release packaging, and
  analytics prep.
- `src/infrastructure/`: browser storage adapter.
- `src/fixtures/`: demo workspace data.
- `src/App.tsx`: React composition root. It connects the app shell, workspace
  controller, context chat, and feature entrypoints, but must not own feature UI,
  persistence, autosave, reset, navigation shell, or app-level orchestration.
- `src/app/`: app shell, topbar/sidebar, navigation, context-chat overlay/scope, and
  workspace controller.
- `src/features/signals`: feature-owned `Signals` workspace. It receives workspace
  data and callbacks from the app controller and does not own persistence.
- `src/features/editorial-model`: feature-owned editorial setup workspace. It owns
  project profile UI, publisher rules, topics, fabulas, matrix, and setup validation
  rendering, but receives workspace data and callbacks from the app controller.
- `src/features/author-memory`: feature-owned author memory workspace. It owns the
  memory feed, composer, assertions/evidence correction UI, import sources, import
  queue, archive, attachments, and local import/archive UI orchestration, but receives
  workspace data and callbacks from the app controller and does not own persistence.
- `src/features/plan`: feature-owned broadcast grid and plan slot UI.
- `src/features/briefing`: feature-owned post brief / concrete post-fabula workflow.
- `src/features/editing`: feature-owned draft, editorial checks, editor notes, and
  final-text approval UI.
- `src/features/release`: feature-owned manual export package, checklist, copy, and
  Markdown export UI.
- `src/features/analytics`: feature-owned manual metrics and editorial learning note
  UI.
- Future `src/features/*`: feature-owned screens such as context chat when it is
  extracted from the app layer.
- `src/shared/ui`: shared cabinet primitives such as `Icon` and `WeightRangeEditor`.
- `src/shared/ui/WorkflowPrimitives.tsx`: shared production-flow primitives such as
  HITL gates, field rows/lists, placeholders, and empty states.
- `src/shared/format`: formatting helpers.
- `src/shared/format/production.ts`: shared production-flow labels, dates, and text
  helpers.
- `src/test/`: test setup.
- `src/test-support/`: small repeated app-flow navigation/setup helpers. Do not place
  business assertions or page-object frameworks here.
- `ui-design-systems/`: design handoff and reference UI, not production code.
- `docs/`: documentation.
- `docs/wiki/`: source files for the GitHub Wiki, including screenshot assets.
- `demo/`: demo notes and future demo assets.

Future backend layout:

- `backend/app/api/`: thin routes and HTTP shape mapping only.
- `backend/app/domain/`: provider-free entities, policies, value objects, and
  invariants.
- `backend/app/application/`: use cases, orchestration, fallback decisions, and
  provider-independent run contracts.
- `backend/app/infrastructure/`: OpenRouter, persistence, queue, file, publication,
  and `langgraph-document-ai-platform` adapters.
- `backend/app/workflows/`: real multi-step workflow composition only when a slice
  needs it.
- `backend/tests/`: backend unit, contract, adapter, and smoke tests.

Current backend files:

- `backend/app/main.py`: FastAPI app factory.
- `backend/app/__main__.py`: local server entrypoint used by `npm run dev:backend`.
- `backend/app/settings.py`: typed environment settings.
- `backend/app/api/health.py`: `/health` and `/api/health` routes.
- `backend/app/api/ai_runs.py`: `/api/ai-runs` create/read/list audit routes.
- `backend/app/api/drafts.py`: `/api/drafts/generate` compatibility draft route and
  `/api/drafts/revise-with-comment` post-run human-comment revision route.
- `backend/app/api/draft_runs.py`: queued draft-run routes.
- `backend/app/api/dependencies.py`: request-time application service wiring.
- `backend/app/application/health_service.py`: health use-case orchestration.
- `backend/app/application/ai_run_service.py`: AI run audit use case, payload
  redaction, and repository port.
- `backend/app/application/draft_generation_service.py`: OpenRouter/fallback
  orchestration for draft generation.
- `backend/app/application/draft_human_comment_revision_service.py`: post-run
  writer-role revision from active draft version plus editor comment and compact
  machine trace context.
- `backend/app/application/draft_human_comment_quality_service.py`: post-run
  review-role diagnostic check for comment compliance, source-marker preservation,
  public-prose regression, internal jargon leaks, and attempt trace.
- `backend/app/application/deterministic_draft_service.py`: deterministic backend
  fallback draft generation.
- `backend/app/application/draft_run_service.py`: durable run creation and dispatch
  orchestration.
- `backend/app/application/draft_run_pipeline.py`: deterministic worker pipeline over
  named run steps.
- `backend/app/application/draft_run_progress.py`: step start/success/failure helper
  that persists long-running step state and child `AiRun` ids incrementally.
- `backend/app/application/draft_run_step_progress.py`: operation-level progress
  sink for long-running step artifacts.
- `backend/app/application/draft_run_staleness.py`: computed stale-state inspector for
  queued/running runs with no recent timestamp progress.
- `backend/app/application/draft_run_payloads.py`: brief/model/draft payload mapping.
- `backend/app/application/draft_run_context_payloads.py`: context snapshot payload
  mapping.
- `backend/app/application/draft_run_context_builder.py`: normalized context summary
  builder for the worker `context` step.
- `backend/app/domain/health.py`: provider-free health value objects.
- `backend/app/domain/ai_run.py`: provider-agnostic AI run entity and enums.
- `backend/app/domain/draft_generation.py`: provider-free draft generation contracts.
- `backend/app/domain/draft_run.py`: provider-free queued run and step entities.
- `backend/app/domain/draft_run_context.py`: provider-free context DTOs.
- `backend/app/infrastructure/openrouter_config.py`: OpenRouter config validator with
  no provider call.
- `backend/app/infrastructure/openrouter_draft_adapter.py`: OpenRouter chat
  completions adapter for draft generation.
- `backend/app/infrastructure/sqlite_ai_run_repository.py`: stdlib SQLite audit
  repository.
- `backend/app/infrastructure/sqlite_draft_run_repository.py`: stdlib SQLite run/step
  repository.
- `backend/app/infrastructure/celery_app.py`, `celery_draft_run_dispatcher.py`, and
  `draft_run_tasks.py`: queue wiring and worker entrypoints.

AI run audit API:

- `POST /api/ai-runs`: records an audit-only run for `draftGeneration`,
  `visualGeneration`, `memeSearch`, or `documentImport`.
- `GET /api/ai-runs/{id}`: reads one audit record.
- `GET /api/ai-runs?limit=20&capability=draftGeneration`: lists recent records
  newest-first.

Slice 2.2 does not execute prompts, call OpenRouter, sync workspaces, or create
publication artifacts. The audit contract exists so provider execution can be added
behind the application/infrastructure boundary in Slice 2.3.

Draft generation API:

- `POST /api/drafts/generate`: accepts an approved `PostBrief` context and
  `EditorialModel` context, returns a frontend-compatible `PostDraft` and `AiRun`.
- `POST /api/drafts/revise-with-comment`: accepts the active draft version, an editor
  comment, optional `draftRunId`, and returns revised title/body, revision summary,
  selected writer model, attempts, and child `AiRun` id. Provider failure returns a
  safe error and must not create a local draft version.
- OpenRouter calls happen only in `backend/app/infrastructure/openrouter_draft_adapter.py`.
- Missing OpenRouter configuration, provider errors, and invalid provider JSON return a
  deterministic fallback draft and an audited `fallbackUsed: true` run.
- The frontend keeps local workspace persistence; backend sync is not part of this
  slice.

Draft generation observability:

- The maintained current-state map of the queued drafting pipeline is
  `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`; a quick-view PDF is generated at
  `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf`.
- Regenerate the PDF after updating the Markdown:
  `python scripts/generate-draft-run-pipeline-pdf.py`.
- Backend draft runs store full local sanitized trace in `AiRun.requestPayload` and
  `AiRun.resultPayload`: prompt messages, provider request summary, generated draft
  body, provider metadata, fallback flag, and safe error context.
- Frontend workspace stores only `PostDraft.generation`: source, `AiRun` id, provider,
  model, fallback flag, timestamp, and optional error.
- Never store or return API keys, `Authorization` headers, secret env values, or
  absolute local paths in AI run payloads.

Useful debug commands while the backend is running:

```powershell
Invoke-RestMethod "http://localhost:8000/api/ai-runs?capability=draftGeneration&limit=5"
Invoke-RestMethod "http://localhost:8000/api/ai-runs/<AI_RUN_ID>"
```

Frontend debug page:

- Open `http://localhost:5176/ai-runs` in Docker, or `http://localhost:5173/ai-runs`
  in local Vite.
- Get the parent `DraftRun ID` from `Редактура -> Рабочий стол -> Драфт`: the
  draft generation summary and the right `AI trace` panel show the id and include
  a direct link to `/ai-runs?runId=<DRAFT_RUN_ID>`.
- Paste a parent `DraftRun ID` to inspect the whole queued agentic pipeline.
- Or paste a child `AiRun ID` to inspect one provider call.
- Direct links work for both modes:
  `http://localhost:5176/ai-runs?runId=<DRAFT_RUN_ID>` or
  `http://localhost:5176/ai-runs?runId=<AI_RUN_ID>`.
- The page is intentionally outside the main cabinet navigation and only reads
  backend audit data.
- The trace workbench tries `GET /api/draft-runs/{id}` first. If the backend returns
  `404`, it falls back to `GET /api/ai-runs/{id}`. Other backend/network errors are
  shown as errors and are not masked as another id type.
- In parent `DraftRun` mode, the `Трейс` tab shows logical steps and all child LLM
  calls under their owning step. Click a step or child `AiRun` to inspect details.
- The `draft` step is expanded with derived read-model nodes for each candidate,
  deterministic scorecard, and selected draft. These nodes come from the existing
  `draft.artifactPayload`; they do not change backend step order or SQLite schema.
- Draft candidate scorecards render as comparison tables in the trace workbench:
  candidate title/id, total score, hard constraints, evidence, topic, fabula,
  audience value, risk penalty, publishability status, selection penalty, exclusion
  reasons, and selected/winner state. Do not fall back to generic long `Score rows`
  text for scorecard analysis.
- Emergency `deterministicFallback` candidates are diagnostic unless they pass the
  publishability guard. If a publishable provider candidate exists, fallback rows must
  be `excluded` or heavily penalized. If every candidate is invalid, the parent
  `DraftRun` completes as quality-blocked with `finalDraft=null` and
  `complete.blockedBy=draftCandidateSelection`; this is not a network/backend failure
  and must not silently invoke compatibility fallback.
- The `Смысловой результат` tab shows material plan, strategy, draft candidates,
  scorecard, selected candidate, and final draft artifacts. Raw JSON remains
  available in the detail panel, but it is not the primary analysis surface.

How to read draft generation source:

- OpenRouter success: frontend shows `source=openrouter`, an `AiRun ID`, provider,
  model, and `fallbackUsed=false`; the backend run has provider response metadata.
- Backend deterministic fallback: frontend shows `source=backendFallback`,
  `fallbackUsed=true`, and an `AiRun ID`; the backend run contains the provider/config
  error and fallback draft body.
- Frontend local emergency fallback: frontend shows `source=localFallback`,
  `aiRunId=null`; the backend was unreachable, so no backend run was recorded.

### DraftRun diagnosis workflow

Use the repo skill `$draft-run-pipeline-diagnostics` whenever a concrete run produces
a bad, generic, stuck, over-sourced, source-free, or wrongly selected post. The skill
standardizes the analysis so run reviews do not depend on ad hoc SQLite queries.
Before diagnosing expected behavior, compare the trace to
`docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` and then to the active `ROADMAP.md`
slice.

Fast local extraction:

```bash
python .agents/skills/draft-run-pipeline-diagnostics/scripts/analyze_draft_run.py <DraftRun ID>
```

The helper reads:

- `var/glavred-draft-runs.sqlite3` for the parent run, steps, artifacts, and final
  draft;
- `var/glavred-ai-runs.sqlite3` for child provider calls, fallback status, errors,
  search queries, and candidate branches.

The required diagnostic answer should cover: what happened by step, what failed, why
the current pipeline allowed it, whether the behavior is expected for the current
slice, and the smallest repair slice if the plan should be adjusted.

For a fresh end-to-end control run, use `$draft-run-pipeline-evaluation` instead of
diagnostics directly. It starts a new run through the UI or a prepared API payload,
waits for the queued backend worker, then hands the resulting `DraftRun ID` to the
diagnostic workflow.

Wait helper:

```bash
python .agents/skills/draft-run-pipeline-evaluation/scripts/wait_for_draft_run.py <DraftRun ID>
```

This helper never calls the compatibility `/api/drafts/generate` endpoint. A live
queued/running `DraftRun` must remain the source of truth until it succeeds, fails, or
becomes stale.

Backend OOP/SRP rules:

- API handlers must not contain prompt logic, persistence logic, provider calls, or
  workflow orchestration.
- Domain modules must not import OpenRouter, provider metadata, HTTP clients,
  database sessions, queues, file systems, or `langgraph-document-ai-platform`.
- Application services own use-case methods and depend on ports or adapters through
  explicit interfaces.
- Infrastructure adapters normalize provider/library errors into application-level
  results.
- Split a backend module before it becomes a catch-all. Do not allow 2-3k line files.
- Do not add boilerplate-only base classes, packages, or factories.

## Requirements Status

The primary product brief is `glavred.md`. It is filled and should drive future
architecture and implementation decisions.

Use the design handoff for visual and conceptual reference, but treat it as secondary
to the brief. Keep product logic in `src/domain/` or future domain/application modules
before wiring it into React views.

## Current Baseline

The current app implements:

- Author memory feed with titleless thought capture, link-reaction previews,
  targeted manual corrections, search/filtering, lazy display, edit/delete actions,
  memory summary, and browser speech-recognition fallback.
- Local-first external source shell inside author memory: source list, reviewed queue,
  grouping, candidate filters, archive-safe bulk actions, latest bulk undo, and archive
  records.
- Evidence-backed author-position assertions inferred from demo notes.
- Structured editorial setup inside `Редакционная модель`: project profile, atomic
  editorial rules, compact topic/fabula lists, explicit matrix save/cancel behavior,
  and a deterministic validation panel on every internal tab.
- Editable `Редакционная модель`, reviewed signals/radars, plan item, post brief, and
  post draft.
- Human approval gates for content plan, post brief, final text, and release readiness.
- Deterministic style, anti-AI, fact-check, and policy checks for the draft.
- Manual release package with Telegram/LinkedIn targets, checklist, text copy, and
  Markdown download.
- Local analytics prep with manual metrics and captured editorial learning notes.
- Local-first workspace persistence through browser `localStorage`.
- Topbar-triggered context chat overlay with deterministic section-aware chat replies
  and suggestions. The chat can open safe draft flows for rules, topics, and fabulas,
  but does not persist chat state or call AI providers.

The app does not yet include real source ingestion, AI calls, publishing integrations,
autoposting, or real metrics ingestion.

## Wiki Documentation Workflow

The GitHub Wiki is generated from `docs/wiki/`. Keep the source in the main
repository so wiki changes are reviewed, tested, and versioned with the product.

`npm run docs:screenshots` starts Vite on a dedicated local port, opens the app in
Playwright, resets browser `localStorage`, walks through the demo flow, and writes PNG
files to `docs/wiki/assets/screenshots/`.

`npm run test:visual` starts Vite on a dedicated local port and runs Playwright layout
assertions for high-risk operational screens. The current guardrail checks that
`Память автора -> Источники` rows do not overflow or collapse source titles into narrow
columns, that row actions stay inside the row, that autosave/status toast appears only
after an explicit action and disappears automatically, that the context chat overlay
opens from the topbar and keeps visible layer separation, and that `Сигналы` renders
radars and found signals as framed rows with stable chips and no horizontal overflow.
For `Сигналы`, visual smoke also verifies the section header, main/side column gap,
action-button spacing, side-panel action spacing, radar edit-form overflow, and signal
title width. These checks are intentionally stricter than ordinary smoke tests because
the screen is dense and small spacing regressions make it unreadable.

`npm run test:design` starts Vite and checks shared cabinet design-system invariants:
major section headers reuse known patterns, header metric blocks align to the right
edge, cards and panels keep internal padding, main/right columns do not overlap,
dense workspace grids keep a measurable gutter, action groups keep a measurable gap,
tab counters use the shared badge pattern, and radar edit sections align with base
form fields.
It also compares `Signals -> Radars` geometry before and after expanding/collapsing a
radar row, checks the Signals header on a wide desktop viewport, and measures vertical
form rhythm in the radar editor. A disclosure state that shifts the workspace, a
metric group drifting from the right edge, or a label/control pair with no visible gap
is a design-system failure.
The checks also require existing radar edit mode to render inside the edited
`data-testid="radar-row"` and require radar rule/source value controls to use multiline
`textarea` fields. Creating a new radar may use a temporary top-of-list draft, but
editing an existing radar must stay in-place.
For `План`, the same command checks canonical tabs, filter-card placement before the
broadcast list, row overflow, action spacing, and readable warning contrast. A
centered floating list action, a slot card in the side panel, or low-contrast warning
text is a design-system failure.
The broadcast grid filter toolbar must also expose the calendar view tab, and visual
smoke checks that the calendar opens, shows candidate counts per date, and renders the
same row cards for the selected date.
For `Редактура`, design smoke opens both `Посты` and `Рабочий стол`: the section header
must reuse project-profile padding, header metrics must align to the right edge, the
queue side panel must use shared compact `.summary-item` metric cards, and the
selected-post workbench must not reintroduce a redundant top post header.
Use it whenever a slice changes a large operational screen, not only when screenshots
change.

Cabinet action taxonomy is intentional:

- secondary white buttons are ordinary work actions, such as adding a radar/topic,
  editing, opening, cancelling or navigating;
- primary red buttons are validation, approval, save/commit and HITL lifecycle
  actions.

Entity list toolbars should use the compact count-left/action-right pattern. Entity
rows should reserve stable metadata slots and render fallbacks for optional values
instead of leaving layout holes.
Expandable rows must keep the same horizontal geometry in collapsed and expanded
states. If a row needs more detail, add vertical content inside the existing frame; do
not let disclosure change the main/side grid, toolbar width, or row width.

`npm run docs:wiki:publish` copies `docs/wiki/` into the separate GitHub Wiki
repository at `https://github.com/mudrezzz/glavred.wiki.git` and pushes it. The main
repository must be public before publishing the wiki in the current GitHub setup.

GitHub creates the backing `*.wiki.git` repository only after the first wiki page is
saved through the web UI. For the first publish, open
`https://github.com/mudrezzz/glavred/wiki`, click `Create the first page`, save a
temporary `Home` page, and then rerun `npm run docs:wiki:publish`.

When user-visible UI changes, update the matching wiki page and refresh screenshots in
the same slice.

## Revised Product Direction

The next product circle re-centers Glavred around:

`AuthorMemory -> AuthorPositionModel -> EditorialSystem -> ContentProduction`

The existing production flow remains valid, but it is downstream. Future development
should first capture the author's raw thoughts, reactions, corrections, and archive
material, then turn them into structured, evidence-backed entities that constrain the
content pipeline.

New conceptual entities:

- `AuthorNote` and `AuthorMemoryEvent` for loose thoughts, links, reactions,
  corrections, local note attachments, archive annotations, and learning events.
- `AuthorNote.targetType`, `targetId`, and `targetTitle` are optional metadata used
  only when a manual correction targets an inferred assertion or evidence item.
- `AuthorAttachment` and `AuthorNote.attachments` store small local demo files attached
  through `+ Файл`. Attachments are supporting material, not automatically analyzed
  evidence.
- `AuthorPositionAssertion` for transparent claims about how the author thinks or
  writes, with evidence.
- `AuthorExternalSource`, `ImportedMemoryCandidate`, `ImportCandidateGroup`,
  `BulkImportAction`, and `ArchiveRecord` for the local import-review shell. Only
  `acceptedToMemory` candidates become `AuthorNote`; unreviewed and archive-only
  candidates do not affect `AuthorPositionAssertion`.
- `RadarDefinition` for local-first radar settings: source type, scope, acceptance
  policy, trigger mode, status, last run, and notes.
- `RadarSearchRule` and `RadarSearchSource` for structured radar configuration.
  Rules are atomic and support `and`, `or`, and `negate`; sources are optional and can
  represent archive, URL, MCP, API, search keywords, manual source, social profile,
  document, or open web.
- `SourceSignal` now supports review metadata: `radarId`, `reviewStatus`,
  `suggestedTopicId`, `suggestedFabulaId`, `suggestedValue`, `duplicateRisk`, and
  `authorCorrection`.
  `suggestedTopicId`, `suggestedFabulaId`, and `suggestedValue` are compatibility
  fields for older signal fixtures. The `Найденные сигналы` UI treats signals as raw
  material and does not expose topic/fabula matching; `PostCandidate` is now the first
  matching layer.
  New signal-facing fields are `evidence` and `searchNote`.
- `Topic`, `Fabula`, `WeightRange`, and `TopicFabulaMatrixEntry` as implemented
  structured editorial entities. `ContentDesignRecord` and `PlatformProfile` remain
  future entities.
- `ValidatorResult` as a common score/status/evidence contract across setup,
  planning, drafting, release, and archive uniqueness.
- `ContextChatSession` for a future right-side assistant synchronized with the active
  section.

Do not model these as one large prompt or one freeform settings textarea. The product
requires small entities, explicit rules, validator scores, and evidence links.

## Architecture Boundaries

The implemented flow still contains compatibility release artifacts:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> PostCandidate -> InsightCard -> BroadcastContentPlan -> approved PostBrief -> PostDraft -> EditorialChecks -> approved FinalText -> ReleasePackage -> EditorialLearningNote`

The target production boundary is:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> PostCandidate -> InsightCard -> BroadcastContentPlan -> EditorialWorkItem -> approved PostBrief -> approved PostDraft -> Visual -> ReadyPost -> PublicationLogEntry -> EditorialLearningNote`

`FinalText` and `ReleasePackage` should be treated as compatibility/manual-export
artifacts until their cleanup slices. Do not add new user-facing preparation behavior
to `Выпуск`.

Planning architecture is being corrected after Slice 1.4. The broadcast grid is the
current compatibility layer, but the intended flow is:

`AuthorMemory/Archive/ExternalSources -> Сигналы -> Кандидаты постов -> BroadcastContentPlan -> approved PostBrief`

React UI now has an explicit architecture baseline. `App.tsx` is a composition root
and must stay small. App shell, navigation, context-chat overlay, shared icon, weight
range editor, workspace controller, signals, editorial-model, author-memory, plan,
briefing, editing, release, and analytics features have been extracted. New large
screens, editors, panels, cards, headers, overlays, and formatting helpers should be
added to `src/app/`, `src/features/<feature>/`, `src/shared/ui`, or
`src/shared/format`, not directly to `App.tsx`.

Run `npm run test:architecture` before completing any UI slice. The current guardrail
blocks `App.tsx` and `App.test.tsx` growth past the accepted baseline, checks required
app/shared extraction files, author-memory, signals, editorial-model, plan, briefing,
editing, release, and analytics feature entries, and verifies that `App.tsx` no longer
imports `LocalWorkspaceStore` or contains extracted feature internals. After Slice
1.10.6.3 the limits are `App.tsx <= 350`, `App.test.tsx <= 300`, and large App UI
declarations `<= 1`. `App.test.tsx` is shell/navigation-only; feature user flows live
beside the owning feature as `*AppFlow.test.tsx`.

After Slice 1.5.15, architecture smoke also tracks large-file baselines outside
`App.tsx`. These are temporary ceilings:

- `src/features/author-memory/AuthorMemoryView.tsx`
- `src/domain/editorialWorkspace.ts`
- `src/features/editorial-model/EditorialModelView.tsx`
- `src/fixtures/demoWorkspace.ts`
- `src/features/signals/SignalsView.tsx`
- `src/application/editorialServices.ts`
- `src/domain/editorial-model/transitions.ts`
- `src/fixtures/demoImports.ts`

Do not add product behavior to these files unless the same slice lowers the relevant
limit by extracting cohesive modules. As of the refactoring chain through Slice 1.5.23,
`editorialWorkspace.ts`, `editorialServices.ts`, and `demoWorkspace.ts` are compatibility
facades/factories rather than owners of all domain, service, or demo logic. Source comments
should explain ownership, invariants, compatibility fields, deterministic stubs, and future
provider/backend boundaries; avoid comments that only describe obvious JSX or assignments.

After Slice 1.5.24, feature entrypoints must stay thin. `AuthorMemoryView`,
`EditorialModelView`, and `SignalsView` should compose feature-local modules, not absorb
every tab, dialog, row, editor, side panel, and helper. Use the existing split as the
default destination for new code:

- Author memory import/source/archive UI belongs in `ExternalSourcesView`,
  `ImportQueueView`, `CandidateCard`, `ArchiveView`, or `BulkActionDialog`.
- Editorial model setup UI belongs in `ProjectProfileHeader`, `PublisherRulesView`,
  `TopicsTab`, `FabulasTab`, or `MatrixTab`.
- Signals setup UI belongs in `RadarEditor`; signals summary belongs in
  `SignalsSidePanel`.

After Slice 1.5.25, `AuthorMemoryView` is also only a feature composition root.
Memory feed, composer, note edit/delete, correction conflict, and filtered-note state
belong in `useMemoryFeedController`; import queue, archive restore/delete, selected
candidates, bulk confirmation, and undo state belong in `useImportReviewController`.
Rendering is split into `MemoryFeedTab`, `MemorySidePanel`, and `MemoryDialogs`.

After Slice 1.5.26, `SignalsView` is also only a feature composition root. Signals tab,
expanded row, radar draft, signal draft, filter, summary, and derived-list state belongs
in `useSignalsController`. Rendering is split into `SignalsHeader`, `SignalsTabs`,
`RadarsTab`, `RadarCard`, `FoundSignalsTab`, `SourceSignalCard`, and
`PostCandidatesPreviewTab`. `RadarEditor` remains the radar form editor, not the owner
of tab/list state.

After Slice 1.6, `PostCandidatesPreviewTab` is the real candidates tab composition root,
not a placeholder. Candidate derivation belongs in `usePostCandidatesController`,
candidate rendering belongs in `PostCandidateCard`, deterministic assembly belongs in
`src/application/postCandidateService.ts`, and candidate approval/downstream reset
belongs in `src/app/usePostCandidateWorkspaceActions.ts`.

After Slice 1.7, large operational entity lists must use the shared cabinet list
pattern: `filter card -> search -> list/group toggle -> framed rows -> bottom-left
actions`. `Кандидаты постов` follows the same UX rule as
`Память автора -> Очередь разбора`: filters and grouping live in
`PostCandidatesToolbar`, grouped rendering in `PostCandidateGroupList`, inline editing
in `PostCandidateEditForm`, and local filter/group helpers in `postCandidateFilters`.
Do not add new large-list hero/summary blocks above the filter card. Primary row
actions are red only for the main approval/save step; secondary row actions stay white.

After Slice 1.8.1, `План` follows the same cabinet-list contract. Broadcast slots must
start with a filter card, full-width search, list/group tabs, and framed rows in
`.broadcast-main`; slot cards must not render in `.broadcast-aside`. Expanded and edit
states must keep readonly candidate context visible: source signal, topic, fabula,
audience, value, and goal. Plan edit fields may change schedule/slot metadata, but
must not hide the candidate/source context that explains what is being scheduled.

After Slice 1.8.2, the broadcast grid has a third view mode: `Календарь`. It must reuse
the planning mini-calendar period model (`week | month | quarter`), count the currently
filtered plan items by date, and render date-specific candidates with the same
`BroadcastGridRow` component used by the list/group views. Do not build separate
calendar-only candidate cards unless a later slice explicitly changes the row contract.

Planning settings use the mini-calendar as the visible source of publish-slot choices.
Clicking a day selects/unselects an explicit `publishSlots` date. Period changes switch
the visible horizon: week, month, or quarter. `publishingDays` and `publishingTimes`
remain normalized fallback/default fields for older workspaces and generated slots,
but new UX should not reintroduce abstract weekday toggle bars as the primary control.

After Slice 1.7.1, `PostCandidate` does not own `format`. Fabula is the candidate's
editorial shape; broadcast grid settings and `ContentPlanItem` own plan formats.
Candidate edit context must show readonly source signal and topic, and may edit
`fabulaId` with a compatibility warning instead of silently hiding matrix risk.

After Slice 1.5.27, `ImportQueueView` is also only the author-memory import-queue
composition root. Filter controls and view-mode switching belong in
`ImportQueueToolbar`; selected-count and bulk actions belong in `ImportQueueBulkBar`;
group/list/empty rendering belongs in `ImportCandidateGroupList`, `ImportCandidateList`,
and `ImportQueueEmptyState`. Keep import transitions in the existing controller and
domain helpers; queue view modules must not own persistence.

After Slice 1.5.28, `useWorkspaceController` is also only an app-level public facade.
Do not add new persistence, context-chat, radar/signal, production-flow, or browser
export action groups directly to it. Use the role-owned app hooks instead:

- `useWorkspacePersistence` owns load/save/reset/toast and workspace patch helpers.
- `useContextChatController` owns chat open/tab/messages/suggestions/intents.
- `useSignalsWorkspaceActions` owns radar and signal workspace mutations.
- `useProductionFlowActions` owns insight, plan, brief, draft, release, and analytics
  callbacks.
- `releaseExport` owns clipboard and Markdown download browser edges.

Domain transitions follow the same rule. `src/domain/editorial-model/transitions.ts`
is a compatibility barrel. Rule transitions go to `rules.ts`, setup validators to
`validation.ts`, and topic/fabula/matrix operations to `catalog.ts`. This applies OOP/SRP
through explicit ownership and stable module boundaries rather than class-heavy React.

Use these boundaries:

- Domain objects and pure transitions live in `src/domain/`.
- Application services normalize author notes into memory events, infer
  evidence-backed author-position assertions, and turn the demo signal into an insight
  card, a broadcast content grid, a post brief, a deterministic draft, editorial
  checks, editor notes, a release package, and an editorial learning scaffold.
- Infrastructure adapters handle browser `localStorage` through a `WorkspaceStore`
  interface.
- React components render the workflow and call application services; they must not own
  domain rules.
- `WorkspaceState.contentPlanItems` is the broadcast grid. `contentPlanItem` remains a
  compatibility field for the currently selected/approved slot used by post brief,
  release, and analytics services.
- Approved posts use `EditorialWorkItem` identity rather than expanding singleton
  production state. The current `postBrief`, `postDraft`, `finalText`,
  `releasePackage`, and `editorialLearningNote` fields remain compatibility fields.
  Slice 1.10 creates or updates the selected work item and prepares its initial
  `PostBrief` when a plan slot is approved; future production actions should accept an
  explicit work-item id so editing one post does not overwrite another queued post.
- `Редактура` owns the production queue from approved slot to ready post. Its UX rule
  is `section header -> Посты / Рабочий стол tabs -> filter card -> search ->
  list/group toggle -> framed rows -> selected-post workbench`. The selected-post
  workbench owns post preparation: `Фабула`, `Драфт`, `Визуал`, and
  `readyForRelease`. Visual modes must pass through the review contract:
  brief, prepare deterministic or adapter-backed variants, select one variant,
  then approve. `memeRemix` is the exception inside that contract: it prepares and
  selects a meme reference before preparing final remix variants. `noVisual` is the
  only direct visual completion path.
- `Выпуск` owns delivery history for ready posts. It should show publication log
  records, statuses, external links, platform errors, and retry notes. It must not
  edit text, visual, brief, candidate, or slot artifacts.
- `WorkspaceState.contentPlanSettings` is normalized on load. It owns period, tempo,
  publishing days/times, candidate limits, default platform, and signal-selection
  policy. Saving settings clears generated plan slots and downstream production
  artifacts so the grid is rebuilt explicitly.
- `Сигналы` owns local-first radar settings and reviewed source material. `sourceSignals`
  is the new signal list; `sourceSignal` remains the compatibility field for the
  currently selected approved signal used by insight, plan, brief, release, and
  analytics services.
- `PostCandidate` services assemble signal/topic/fabula/audience/value/goal/platform
  combinations before insight creation. Approving a candidate sets
  `WorkspaceState.postCandidate`, switches the current `sourceSignal` to the candidate's
  source, and clears stale downstream insight, selected plan item, brief, draft,
  release, and analytics artifacts. Editing or rejecting a candidate updates only
  candidate review state and must not create or clear downstream artifacts. A rejected
  candidate cannot become the current approved concept.
- The author-memory UI may use browser-only helpers for local link previews, derived
  titles, search filters, summary counts, and voice-input capability detection. These
  helpers must not fetch external metadata or bypass local-first storage.

Do not call browser storage from domain code. Do not add backend persistence, auth,
real source ingestion, or AI provider calls until their slices are planned.

Do not deepen `План` as a standalone generator of posts. Planning settings may create
the publish-window frame, but content ideas must continue to come from approved
signals, post candidates, topics, and fabulas. Calendar binding and AI planning need
separate roadmap slices.

Signal review transitions are pure domain helpers:

- `approveSignal(signal)` marks material ready for insight generation.
- `rejectSignal(signal)` removes it from active consideration.
- `archiveSignal(signal)` keeps it as non-active context.
- `correctSignal(signal, patch)` stores author corrections. In the UI, correction also
  creates a targeted `AuthorNote` so the author-memory layer learns from review
  choices.

`LocalWorkspaceStore.normalizeWorkspace` fills missing `radars` and `sourceSignals`
from the demo workspace and maps old `activeSection: "radar"` browser state to
`activeSection: "signals"`.

Slice 1.5.8 extends `RadarDefinition` with `sourceDiscoveryMode` and `filters`.
Domain/application code owns `evaluateSignalAgainstRadarFilters(signal, radar,
workspace)`. React may render the filter editor and evaluation badges, but it must not
duplicate filter scoring rules. `notes` remains a legacy storage field for old
workspaces and must not be reintroduced as a visible radar editor field.

Radar source configuration rules:

- `specifiedOnly` requires at least one source before save.
- `specifiedAndAdditional` means explicit sources are mandatory context, but future
  search adapters may also discover additional sources.
- `autonomous` is valid without sources.
- `style` is not a radar filter dimension.
- failed filter evaluations mark a signal for review; they do not delete or hide it.

File attachments are local-first and size-limited to 1 MB per attachment in the browser
demo. They are stored as metadata plus `dataUrl`. Real PDF/DOCX parsing, OCR, image
understanding, text extraction, chunking, and AI analysis belong to a later
attachment-analysis slice after storage and provider boundaries are ready.

## External Source Import Runtime Shell

Slice 1.0.5 implements the first local-first UI shell for external source import. It
adds runtime contracts and deterministic transitions, but still does not add real
Telegram/social/blog APIs, OAuth, crawlers, backend workers, scheduled ingestion, or
AI analysis.

Runtime import entities:

- `AuthorExternalSource`: source settings for Telegram, social profiles, blogs,
  documents, article archives, and manual uploads.
- `ImportedMemoryCandidate`: imported item waiting for author review.
- `ImportCandidateGroup`: grouped candidates for large imports.
- `BulkImportAction`: reversible bulk decision such as `Добавить все` or archive
  selected items.
- `ArchiveRecord`: accepted historical material.
- `Provenance`: source, original URL/file reference, import date, acceptance date,
  acceptance mode, and author reason.
- `EvidencePolicy`: `canSupportAssertions`, `archiveOnly`, or `ignored`.

Rules:

- Unreviewed candidates must not change `AuthorPositionAssertion`.
- Large archives default to archive-safe acceptance, not active memory.
- Bulk-accepted records must remain distinguishable from manually reviewed evidence.
- `acceptCandidateToMemory` may create an `AuthorNote`; `acceptedToArchive` and
  `bulkAcceptedToArchive` create only `ArchiveRecord`.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing import fields from the demo
  workspace so old browser states continue to load.
- Real Telegram/social/blog APIs, OAuth, crawlers, backend workers, scheduled
  ingestion, and AI analysis are later slices.

## Topic And Fabula Runtime Layer

Slice 1.1 decomposes part of the old `EditorialModel` into runtime entities while
keeping legacy fields for compatibility.

Implemented entities:

- `Topic`: title, description, purpose, audience value, author stance, rules,
  forbidden angles, advisory `WeightRange`, and active/paused status.
- `Fabula`: title, description, dramaturgy, structure, proof requirements, rules,
  advisory `WeightRange`, and active/paused status.
- `TopicFabulaMatrixEntry`: `topicId`, `fabulaId`, and `enabled`.

Rules:

- `createDefaultTopicFabulaMatrix` enables all topic/fabula pairs by default.
- `completeTopicFabulaMatrix` fills missing entries during storage normalization.
- `normalizeWeightRange` clamps values to `0..100` and keeps `min <= max`.
- `getTopicFabulaWarnings` reports active topics or fabulas that have no active
  compatible pair.
- Deterministic insight/planning/briefing services use the first active compatible
  topic/fabula when the workspace passes these entities in. Calls without them keep
  the legacy rubric/fabula fallback.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing `topics`, `fabulas`, and
  `topicFabulaMatrix` from the demo workspace so old browser state continues to load.

## Editorial Model UX Rules

Slice 1.1.1 adds `ProjectProfile`, `EditorialRule`, and lightweight setup validation
contracts around the Slice 1.1 topic/fabula layer. Slice 1.1.2 adds explicit
validation-run state so the UI can show a saved validation snapshot instead of
recalculating setup feedback live. Slice 1.2 replaces the ad-hoc setup check with a
shared validator baseline.

Runtime rules:

- `WorkspaceState.projectProfile` stores the project name, description, and setup
  status. The seeded demo project is `TG-блог AI Product Manager`.
- `WorkspaceState.editorialRules` stores atomic rules grouped by author, audience,
  positioning, style voice, style language, style rhythm, anti-AI pattern, goal, and
  forbidden topic.
- `WorkspaceState.editorialSetupRevision` increments after committed editorial setup
  changes.
- `WorkspaceState.editorialValidationRun` stores the last manual validation snapshot:
  run id, revision, checked timestamp, `ValidatorRun.results`, aggregate status,
  aggregate score, and a compatibility `EditorialValidationSummary`.
- Legacy `EditorialModel.rubrics` and `EditorialModel.fabula` remain available for
  downstream service compatibility, but the UI no longer exposes them as setup fields.
- `runEditorialSetupValidators(workspace)` is the deterministic Slice 1.2 validator
  runner. It returns `ValidatorRun` with `ValidatorResult[]`.
- `createEditorialValidationRun(workspace)` wraps the runner with aggregate status,
  aggregate score, and summary compatibility for the current UI/storage boundary.
- `validateEditorialSetup(workspace)` remains as a summary helper for compatibility.
- Implemented setup validators:
  `author-position-clarity`, `anti-ai-style-coverage`, `audience-value-fit`,
  `goal-consistency`, and `topic-fabula-coverage`.
- Topic/fabula CRUD is explicit:
  - `createTopicDraft()` and `createFabulaDraft()` create local draft entities.
  - `addTopic()` and `addFabula()` commit normalized entities.
  - `deleteTopic()` and `deleteFabula()` remove entities and their matrix links.
  - `completeTopicFabulaMatrix()` fills newly missing links with `enabled: true`.
- `LocalWorkspaceStore.normalizeWorkspace` fills missing project/rule fields from the
  demo workspace so older local browser states continue to load.

Frontend rules are now ADR-backed:

- Reuse existing product interaction patterns before inventing local controls.
- Treat editorial settings as structured rules, not large textareas.
- Use read/edit/save/cancel for important entity edits.
- Use a single main column plus a right-side validation panel for editorial setup.
- Do not render anonymous domain text as a hero.
- Use compact list-first catalogs with details on demand.
- Use single-column lists for operational entity catalogs; avoid two-column card
  grids for editable/reviewable entities such as sources, topics, fabulas, future
  platforms, formats, and CDR/PDR records.
- Add real-browser visual smoke checks when changing operational catalog layout,
  because DOM tests do not catch collapsed text columns or overflowing actions.
- Render operational cabinet lists as framed rows/cards. Metadata, expanded details,
  and actions must stay inside the same entity container; status chips must not wrap by
  letters or become tall badges. See ADR `cabinet-lists-require-framed-rows-and-visual-coverage`.
- Keep autosave/status toast event-driven and temporary; do not use a permanent bottom
  overlay for local workspace status.
- Implement context chat as a topbar-triggered, tabbed overlay. Do not add a permanent
  third column or floating page button beside existing right-side panels.
- Give overlay drawers visible but restrained layer separation: subtle directional
  shadow and edge separation, not a full modal backdrop.
- Keep validation visible as a first-class UX surface.
- Run editorial setup validation only after explicit `Проверить`; show stale state
  after saved setup changes.
- Keep editorial entity layouts contained: wrap long labels, use one shared detail
  scroll area, and make matrix topic columns sticky during horizontal scroll.

## AI Provider Architecture Baseline

Slice 0.8 defines the first AI boundary without adding runtime provider calls. The
first replacement target is drafting from an approved `PostBrief`.

After the June 2026 product revision, this boundary remains valid but is no longer the
next implementation priority. AI-assisted drafting should wait until author memory,
author position, topic/fabula entities, and validator contracts are strong enough to
constrain generation.

Rules for future AI-assisted drafting:

- React components must not call AI providers, SDKs, prompt builders, or provider
  network clients directly.
- Domain modules must stay provider-free and should not import provider request,
  response, error, or metadata types.
- Application services own the orchestration decision: use a provider adapter when it
  is available and allowed, or use the deterministic `createPostDraft` fallback.
- Infrastructure adapters own provider-specific calls, authentication, SDK imports,
  response normalization, and provider error mapping.
- Local-first deterministic behavior remains the default for demo, tests, offline
  development, and provider failure.

The target drafting boundary is no longer a single request/response provider call.
The current `POST /api/drafts/generate` endpoint is a compatibility path and provider
integration proof. The primary UI path now uses a queued `DraftRun`:

`EditorialWorkItem -> DraftRunContext -> SourceIntent -> seed SourceLedger -> ResearchPlan -> PublicResearch -> EvidenceExtraction -> enriched SourceLedger -> EvidenceSynthesis -> FeasibilityGate -> PostContract -> RuleRegistrySnapshot -> RulePack -> EvidenceInterpretation -> MaterialPlan -> RhetoricalPlans -> DraftCandidates -> InitialValidation -> EditorialCritique -> AlternativeAngleTournament -> FinalValidation -> PairwiseRanking -> RevisionLoop -> FinalQualityGate -> SelectedDraft -> VersionedHumanRevisionLoop -> HumanDecisionSnapshot`

This order is a workflow rule. Do not implement the validator/revision loop before
the source ledger and post contract exist: validators need claim ids, allowed-use
policy, forbidden inferences, and locked editorial invariants to judge generated text.

After Slice 2.15 the quality direction shifts from defensive repair to an editorial
lab that creates stronger post ideas. Slice 2.15.1 introduces the first boundary:
`backend/app/domain/draft_model_roles.py` and
`backend/app/application/draft_model_role_resolver.py` make model choice a role policy.
Empty role settings fall back to `OPENROUTER_DEFAULT_MODEL`; backup retry attempts use
`OPENROUTER_BACKUP_MODEL`; public search uses `OPENROUTER_WEB_SEARCH_MODEL`.
Keep the existing spine, but use these boundaries before expanding the loop further:

- `ModelRoleConfig`: role-specific model choice for research, strategy, writer,
  critic/prosecutor, review, another-angle, and technical backup. Done for
  configuration, resolver, service wiring, and trace metadata; prompt behavior changes
  remain later slices. Backup remains a fallback, not a creative role.
- `ArticleDossier`: DraftRun-local article memory with evidence cards, claim cards,
  tensions, angle options, critique, decisions, rejected moves, voice notes, and open
  questions. Implemented in Slice 2.15.2 with
  `backend/app/domain/draft_article_memory.py` and
  `backend/app/application/draft_article_dossier_builder.py`.
- `ContextPackBuilder`: task-specific prompt context for each role. Model calls should
  receive a compact pack for the current job, not raw DraftRun JSON and not only the
  latest artifact. Implemented in Slice 2.15.2 with
  `backend/app/application/draft_context_pack_builder.py` and the thin
  `draft_article_memory_service.py` pipeline wrapper.
- `EvidenceInterpretation`: public evidence becomes implications, limits, tensions,
  usable examples, reader-value hooks, and forbidden overclaims before it is used by
  material-planning or prose prompts. Implemented in Slice 2.15.3 under the existing
  `rulePack` artifact with child `AiRun.requestPayload.draftRunStep =
  evidenceInterpretation`.
- `EditorialCritic`: the prosecutor/editor role challenges idea strength, author
  stance, reader value, forced references, and generic AI prose. This is not the same
  as deterministic validation.
- `AlternativeAngle`: intentional creative divergence through another model/role,
  distinct from retry and fallback. It consumes critique, dossier, context pack, and
  rejected/weak route signals to produce one challenger route before final
  validation/ranking.

This decision is recorded in ADR
`docs/adr/2026-06-26-drafting-needs-editorial-lab-context-memory-and-model-roles.md`.
Slice 2.16 editor-learning work is deferred until these 2.15.x drafting-intelligence
slices make the machine process worth learning from.

`ArticleDossier` and `ContextPack` are stored inside existing DraftRun step artifact
JSON and child `AiRun.requestPayload` records. They are DraftRun-local memory, not a
workspace database, not long-term RAG, and not a vector store. The trace workbench
renders them as semantic sections so developers can verify which cards a strategy,
writer, or review call received.

Conceptual interfaces for the next implementation slices:

- `DraftRun`: durable orchestration record for one post-drafting attempt.
- `DraftRunStep`: named stage with status, input summary, output artifact, error, and
  timing.
- `DraftRunContext`: selected work item plus approved brief, plan slot, post candidate,
  source signal, topic, fabula, publisher rules, and future author-memory evidence.
- `SourceIntent`: normalized approved-brief sources, URL seeds, search hints, required
  proof, optional proof, and framing-only material.
- `RuleRegistrySnapshot`: selected drafting rules with ids, scope, priority, severity,
  observable criteria, validator type, examples, and repair policy.
- `SourceLedger`: source/candidate/brief claims, provenance, confidence, allowed use,
  risks, forbidden inferences, and author corrections.
- `ResearchPlan`: explicit read/search/verify plan before prose generation.
- `PublicEvidenceItem`: external claim with source, confidence, allowed use, and
  extraction notes.
- `EvidenceSynthesis`: reconciliation of public evidence with signal, fabula, and
  author position.
- `EvidenceInterpretation`: strategy-role interpretation of accepted evidence into
  implications, examples, limits, tensions, forbidden overclaims, reader-value hooks,
  and rejected uses before material planning and writing.
- `FeasibilityReport`: pre-writing gate that may return feasible, feasible with
  constraints, needs research, needs human decision, or infeasible.
- `PostContract`: locked thesis, audience value, CTA, allowed claims, forbidden moves,
  platform constraints, and fabula obligations.
- `PublicationSizeContract`: target publication kind, character range, hard max,
  paragraph/section range, density, and fabula scale intent resolved inside
  `PostContract`.
- `RulePack`: hard constraints, soft constraints, evidence requirements, dramaturgy
  requirements, topic-fit requirements, and quality rubric.
- `MaterialPlan`: evidence inventory, missing evidence, risky claims, grounding plan,
  and retrieval/search needs.
- `DraftStrategy`: thesis, opening, argument sequence, fabula use, CTA, and forbidden
  moves.
- `RhetoricalPlan`: one editorial route for applying the same post contract.
- `DraftCandidate`: one generated draft attempt with rationale and risks.
- `DeterministicLinter`: report-only local checks over candidate prose, size
  contract, post contract, rule registry, material plan, and source ledger.
- `DraftValidationReport`: per-candidate findings with validator id, severity,
  rule ids, claim ids, evidence excerpt, repair guidance, and optional diagnostic
  metadata. Attribution findings use deterministic per-claim provenance markers such
  as source title, domain, author/person name, organization, or source label. Free-text
  material-plan attribution requirements are normalized to source-backed claim ids
  before validation. If a requirement cannot be mapped to a claim or useful expected
  markers, it is stored as diagnostic handoff metadata (`evidence.attribution.diagnostic`)
  and must not count as an actionable warning. Slice 2.13 writes this to the existing
  `validation` step but does not change `finalDraft`.
- `ValidatorResult`: future provider-backed score/findings for one rule family.
- `PairwiseRanking`: comparison and scorecard across candidates.
- `RevisionAttempt`: targeted correction input and candidate output.
- `RegressionReport`: re-check after a directed revision.
- `AiRun`: one provider call audit record inside a parent `DraftRun`.
- `AiProviderAdapter`: provider-specific adapter behind an application boundary.

Slice 2.4 runtime endpoints:

- `POST /api/draft-runs`: persists a queued run and dispatches a Celery task.
- `GET /api/draft-runs/{id}`: polling read-model with steps, artifacts, final draft,
  safe error, and computed stale fields (`isStale`, `staleReason`,
  `lastProgressAt`).
- `GET /api/draft-runs/{id}/events`: polling alias for the same read-model; not SSE
  yet.

Slice 2.5 context contract:

- Frontend builds `draftContext` in `src/application/draftRunContext.ts` from the
  selected `EditorialWorkItem` and current local `WorkspaceState`.
- The HTTP payload mapper in `src/infrastructure/draftRunRequestPayload.ts` sends
  `brief`, `editorialModel`, and optional `draftContext` to `POST /api/draft-runs`.
- Backend stores the raw snapshot in `DraftRun.requestPayload` and normalizes it in
  `backend/app/application/draft_run_context_builder.py`.
- The worker's `context` step artifact should show work item, plan slot, candidate
  if available, source signal, topic, fabula, publisher rule groups,
  author-position evidence, and `missingContext`.
- Old requests without `draftContext` still work and are marked as brief-only
  compatibility runs in the context step artifact.

Local services:

- `REDIS_URL` points to the queue broker/result backend.
- `DRAFT_RUN_DB_PATH` points to SQLite orchestration state
  (`var/glavred-draft-runs.sqlite3` by default).
- `npm run dev:backend` starts FastAPI.
- `npm run dev:worker` starts the Celery worker on Windows-friendly `solo` pool.
- `docker compose up --build` starts frontend, backend, Redis, and worker together.

`AiRun` remains provider-call audit. `DraftRun` is orchestration audit and may later
link child `AiRun` ids when individual steps call OpenRouter or other providers.
To debug Slice 2.5, open `GET /api/draft-runs/{id}` and inspect
`steps[0].artifactPayload`; it is the canonical normalized context used by later
rule-pack slices.

DraftRun fallback discipline:

- Once `POST /api/draft-runs` returns a run id, the frontend must keep that queued
  run as the primary path while it is `queued` or `running`.
- Polling timeout is not a reason to call `/api/drafts/generate`; show a long-running
  state with current step, elapsed time, DraftRun ID, and trace link instead.
- `isStale=true` means the run has had no timestamp progress for five minutes. It is
  diagnostic state for `/ai-runs` and the draft screen, not a silent fallback trigger.
- Long-running steps may write `artifactPayload.progress` while still running. Inspect
  `progress.currentOperationId` and `progress.operations[]` for URL/search tasks,
  candidate generation, deterministic lint, LLM validation, pairwise ranking,
  directed revision, and regression guard progress. These writes update
  `draft_runs.updated_at`.
- Validation progress writes must merge into the existing partial validation artifact.
  They must not replace deterministic/LLM/critic/tournament/ranking/revision payloads
  with a progress-only object. Provider-heavy validation sub-operations mark nested
  operations `failed` with safe errors and keep the best available candidate when a
  previous best exists.
- `/api/drafts/generate` and frontend local fallback are allowed only when the run was
  not created, the backend is unreachable, or the run fails explicitly according to
  the existing error path.
- If Celery hits a real task timeout, the worker records a failed `DraftRun` with a
  safe error; secrets and provider headers must not appear in the error.

To debug Slice 2.6, inspect `steps[1].artifactPayload`. It contains the compiled
`RulePack` used by later material-planning and prompt layers:

- `hardConstraints` and `softConstraints` from publisher rules and candidate intent;
- `evidenceRequirements` from brief, candidate, signal, and fabula proof needs;
- `dramaturgyRequirements` from the selected fabula;
- `topicFitRequirements` from topic purpose, audience value, stance, and rules;
- `forbiddenMoves` from topic forbidden angles, publisher bans, and candidate risks;
- `qualityRubric` as deterministic v1 evaluation criteria.

Do not add rule-pack compilation to `draft_run_context_builder.py` or
`draft_run_pipeline.py`; the compiler and section mappers own that boundary.

Slice 2.11 keeps the compatibility `RulePack` shape but adds
`ruleRegistrySnapshot` inside the same `rulePack` step artifact. This snapshot is the
machine-readable contract future validators and directed revisions must consume:

- every rule has a stable id, source, scope, category, priority, severity, condition,
  observable criteria, validator type, and repair policy;
- rule ids reference SourceLedger claim ids or PostContract obligations when
  applicable;
- `RulePack` is now derived from the registry snapshot and remains a compatibility
  payload for material planning and prompt layers;
- `/ai-runs?runId=<DraftRun ID>` shows a `Rule registry` semantic section with counts
  by severity, category, validator type, and key rules.

Rule-registry ownership is split so near-limit modules stay stable:

- `backend/app/domain/draft_rule_registry.py` defines provider-free DTOs.
- `backend/app/application/draft_rule_registry_compiler.py` orchestrates compilation.
- `backend/app/application/draft_rule_registry_contract.py` maps PostContract rules.
- `backend/app/application/draft_rule_registry_sections.py` maps brief, publisher,
  topic, fabula, source-ledger, candidate, and source-signal rules.
- `backend/app/application/draft_rule_pack_from_registry.py` maps registry rules back
  to the compatibility RulePack.

Slice 2.11.1 adds publication-size contracts:

- `ContentPlanSettings.publicationSizeProfiles` stores editable demo defaults for
  platform/kind/length profiles.
- `ContentPlanItem.publicationSizeProfileId` may lock a slot to one profile.
- `Fabula.sizeIntent` is only a dramaturgical scale (`compact`, `standard`, `deep`);
  do not create platform-specific fabula duplicates.
- Frontend sends `draftContext.publicationSize` through
  `src/application/draftRunPublicationContext.ts`.
- Backend resolves `PostContract.publicationSizeContract` in
  `backend/app/application/publication_size_contract_resolver.py`.
- `backend/app/application/draft_rule_registry_size.py` emits deterministic size rule
  ids for hard max, target range, paragraphs, sections, and density.
- Future validators must reference these rule ids; do not re-derive post size from
  free-text prompt instructions.

To debug Slice 2.7, inspect `steps[2].artifactPayload` for `MaterialPlan` and
`steps[3].artifactPayload` for `DraftStrategy`. Each artifact includes `source`,
`aiRunId`, `fallbackUsed`, optional `error`, and the full planning payload. Open the
child run through `GET /api/ai-runs/{aiRunId}` to see prompt messages, model,
provider metadata, fallback status, and sanitized result trace.

OpenRouter planning calls are wired only in the worker pipeline factory. API routes
and Celery task bodies stay thin, while `openrouter_json_adapter.py` owns the actual
provider JSON call.

To debug Slice 2.8, inspect `steps[4].artifactPayload`. It contains:

- `directions`: deterministic draft directions derived from strategy and rules;
- `candidates`: generated or fallback title/body/rationale/risk alternatives;
- `selection`: deterministic v1 scorecard and selected candidate id;
- `aiRunIds`: child provider/fallback runs for each candidate.

Open child runs through `GET /api/ai-runs/{id}` to inspect candidate prompts,
provider metadata, fallback status, and sanitized candidate results. The frontend still
receives one selected `finalDraft`; alternatives are trace/debug data until a future UI
review slice.

To debug Slice 2.12, inspect `steps[6].artifactPayload`. It contains:

- `rhetoricalPlanSet`: 2-3 routes for writing the locked `PostContract`;
- `source`, `fallbackUsed`, `aiRunId`, optional `error`, and `attempts[]`;
- each plan's moves, claims to use, claims to avoid, required rule ids, size intent,
  CTA route, risks, and rationale.

After Slice 2.13.2, malformed rhetorical-plan JSON does not immediately trigger
deterministic fallback. Inspect `attempts[]` to see primary, repair, optional backup,
and final fallback attempts with model, child `AiRun ID`, status, and validation
reason.

Draft candidates are now plan execution artifacts. In `steps[7].artifactPayload`,
each candidate must include `rhetoricalPlanId`, and child `AiRun` traces should show
which plan was sent to the model. Do not add new candidate directions that bypass the
`rhetoricalPlans` step.

Rhetorical-plan ownership is split:

- `backend/app/domain/draft_rhetorical_plan.py`: provider-free plan DTOs.
- `backend/app/application/draft_rhetorical_plan_service.py`: thin facade for the
  rhetorical-plan step.
- `backend/app/application/draft_rhetorical_plan_retry.py`: OpenRouter JSON retry and
  fallback discipline for `rhetoricalPlans`.
- `backend/app/application/json_step_retry_policy.py`: shared JSON attempt sequence
  helper.
- `backend/app/application/draft_rhetorical_plan_service.py`: step orchestration.
- `backend/app/application/draft_rhetorical_plan_prompts.py`: prompt messages.
- `backend/app/application/draft_rhetorical_plan_audit.py`: sanitized child traces.
- `backend/app/application/deterministic_rhetorical_plan_service.py`: fallback plans.
- `backend/app/application/deterministic_rhetorical_plan_step_service.py`: default
  pipeline adapter.

To debug Slice 2.9, inspect `steps[0].artifactPayload.sourceLedger`. It is written
inside the existing `context` step, not as a new `DraftRunStepKey` and not as a new
SQLite table. The v1 ledger contains:

- `claims`: brief intent, candidate claims, source claims, topic/fabula constraints,
  and author-position evidence with stable local ids;
- `risks`: candidate and brief risks that must not be turned into facts;
- `forbiddenInferences`: negative reasoning rules such as not inventing source facts
  or strengthening author correction into external proof;
- `warnings`: missing source/candidate/evidence/context signals that future gates
  should consume.

The next artifacts must make candidate validation meaningful:

- `SourceIntent` normalizes approved `PostBrief.sources` into URL seeds, source names,
  human-language research requests, required proof, exclusions, and framing-only
  material. Do not treat sources as one prompt string or pass a plain request directly
  as search keywords.
- `Fabula.researchStrategy` is the editorial-model default policy for those sources:
  `auto` creates human-readable research instructions when a work brief is created,
  while `manual` copies configured instructions into the brief. `PostBrief.sources`
  remains the runtime input; if an editor changes it in `Редактура`, that override is
  what the backend receives.
- `ResearchPlan` decides what to read, search, verify, or avoid before writing.
- `publicEvidence` executes the available research plan: exact URL tasks are read
  through infrastructure. General `findPublicSources` and `verifyClaim` tasks call
  OpenRouter `openrouter:web_search` only when `OPENROUTER_WEB_TOOLS_ENABLED=true`
  and OpenRouter is configured; otherwise they remain explicit `notConfigured`
  attempts. A planned or disabled search task is not proof.
- Search tasks must be converted into a `builtQuery` from the human research
  instruction and surrounding post context. Internal target ids such as `target-1`
  are trace links, not search queries. OpenRouter citations must pass the
  deterministic relevance guard before becoming `PublicEvidenceItem` candidates;
  rejected citations stay in trace as `search-result-drift`.
- Public evidence extraction creates `PublicEvidenceItem` records with provenance,
  confidence, allowed-use policy, and extraction notes.
- `EvidenceSynthesis` reconciles accepted public evidence before feasibility:
  only accepted `PublicEvidenceItem` records can become external ledger claims.
  Failed, skipped, disabled, rejected, or merely planned attempts stay as warnings.
- The enriched `SourceLedger` now contains internal claim ids plus external claim ids
  such as `external-evidence-<publicEvidenceItemId>`, and downstream feasibility,
  post contract, rule registry, planning, rhetorical plans, and draft candidates must
  consume that enriched ledger.
- `EvidenceInterpretation` runs after `RuleRegistrySnapshot` and before
  `MaterialPlan`. It uses the strategy role model and JSON retry discipline to convert
  accepted evidence into implications, tensions, usable examples, limits, forbidden
  overclaims, reader-value hooks, and rejected evidence uses. If provider attempts fail,
  deterministic interpretation fallback is explicit in trace. Prompt layers should use
  this artifact before raw public snippets.
- Because `EvidenceInterpretation` lives inside the `rulePack` step, the runner must
  mark `rulePack` as running before provider attempts and write nested progress
  operations for primary/repair/backup attempts. A long interpretation retry must not
  appear as stale `postContract`.
- `DraftRunBudget` is resolved from `Fabula.researchDepth` plus
  `DRAFT_RUN_EXECUTION_MODE`. It lives in the `context` artifact and is consumed by
  `sourceIntent`, `publicEvidence`, external evidence merge, `materialPlan`, `draft`,
  and smoke revision limits. Budgeted-out retrieval tasks must be stored as skipped
  attempts, and trimmed evidence or external claims must remain visible in trace
  metadata. Smoke mode lowers caps but must not skip logical DraftRun steps.
- `MaterialPlan` must not silently ignore the enriched ledger. The material planner
  receives `usableEvidenceCandidates` and must either select evidence or explain why
  candidate claims were rejected. Empty evidence without accountability triggers a
  primary repair retry, then optional `OPENROUTER_BACKUP_MODEL`, and only then an
  explicitly marked deterministic emergency fallback.
- `validation` now stores `DraftValidationReport` in the existing DraftRun step.
  The deterministic linter checks all candidates for size/shape, CTA and contract
  signals, attribution, rejected-evidence misuse, forbidden moves, raw artifact
  leakage, and publishability consistency. It is report-only in Slice 2.13: bad
  findings are visible in `/ai-runs?runId=...`, but ranking and directed revision
  consume them later.
- `llmValidationReport` is a sibling field inside the same `validation` artifact.
  It is report-only in Slice 2.13.3 and checks every candidate with one OpenRouter
  JSON validation call per candidate. The LLM validator receives the enriched
  SourceLedger, PostContract, RuleRegistry, MaterialPlan, candidate text, and
  deterministic findings. It reports source grounding, publisher/author fit,
  topic/fabula fit, coherence/compression, and audience value. If OpenRouter is not
  configured, the report is marked `not-run`; if JSON is invalid, the validator uses
  primary, repair, optional backup, then unavailable status without fake findings.
- LLM validation reports distinguish actionable `findings[]` from positive/pass
  `observations[]`. Positive notes such as `No repair needed` are visible in trace,
  but they do not count as warnings. The `/ai-runs` readable trace also reads
  enriched ledger data from `publicEvidence.enrichedSourceLedger` and selected or
  rejected evidence from nested `materialPlan` payloads.
- `editorialCritiqueReport` is another sibling field inside the same `validation`
  artifact. It uses the `critic` role and `DRAFT_CRITIC_MODEL` to challenge every
  candidate for idea strength, tension, author stance, source integration, generic AI
  prose, unsupported leaps, and reader value. It is report-only in Slice 2.15.4: the
  report is visible in `/ai-runs?runId=...` and feeds ArticleDossier, but pairwise
  ranking and revision do not yet have to consume it. If OpenRouter is not configured,
  the report is marked `not-run`; invalid JSON uses primary, repair, optional backup,
  then candidate-level unavailable status without fake critique findings.
- After `alternativeAngleTournament` creates a challenger, validation must reuse
  initial reports for original candidates and run provider-heavy LLM validation plus
  editorial critique only for the challenger. Do not rerun critic/review calls for
  already validated candidates during the merge step.
- `validation.rankingRevision` is the first actionable validation consumer. It
  pairwise-ranks candidates, then runs a bounded `revisionLoop`. Each cycle builds
  validator repair goals plus editorial goals from EvidenceInterpretation,
  EditorialCritique, alternative-angle tournament lessons, material gaps, and prior
  rejected moves. The writer receives those goals and anti-regression constraints.
  The review model then compares previous best vs revised candidate across explicit
  dimensions: idea strength, tension, reader value, author stance, source integration,
  structure, and validator health. The revision is accepted only when it resolves a
  targeted goal or clearly wins on those dimensions without deterministic or
  attribution regression. `DRAFT_REVISION_MAX_ITERATIONS` limits this loop. If provider
  calls fail or a revision does not improve the draft, the previous best remains final
  and the reason plus rejected moves are visible in `/ai-runs?runId=...`.
  Late operation failures inside the loop must finalize with that previous best rather
  than leave the DraftRun `running/stale`; the trace should show the failed nested
  operation, safe error, and final stop reason.
- `validation.rankingRevision.finalQualityGate` is the last machine acceptance layer
  before the final draft returns to the editor. It checks the delivered candidate,
  not candidate-pool noise, for public-prose quality, internal pipeline jargon,
  source-dump risk, source integration, author voice, and reader value. The gate
  builds a `FinalQualityContract` from configured editorial/fabula/post constraints
  and runs an independent `finalGate` model review before deciding repair goals. If
  the gate is `warning` or `critical`, it may run bounded writer repair cycles
  through the existing directed revision service; the count is controlled by
  `DRAFT_FINAL_REPAIR_MAX_ITERATIONS`. A repair replaces `finalDraft` only if
  deterministic regression and public-prose checks improve; otherwise the previous
  best remains final and the rejected repair stays in trace. The gate separates
  `actionableAttributionFindings` from `diagnosticAttributionNoise`: independent
  final-gate review may close only non-actionable attribution handoff noise, never a
  concrete missing source marker. Keep deterministic heuristics in
  `draft_final_quality_assessment.py`; keep contract/review/provider handoff in
  `draft_final_quality_gate.py` and final-quality review modules.
- After `finalQualityGate`, the machine pipeline is done. The frontend stores
  `DraftRun.finalDraft` as immutable `PostDraft.versions[0]` (`v1`,
  `source=machineFinal`). Human comment revisions are post-run editor actions through
  `POST /api/drafts/revise-with-comment`, not new DraftRuns and not new
  `DraftRunStepKey`s. The endpoint uses the writer role and existing JSON retry
  discipline with compact machine trace context from the parent DraftRun. After a
  successful writer revision, the endpoint runs a review-role
  `HumanCommentRevisionQualityCheck` through the same JSON retry discipline. This
  check is diagnostic: it records comment compliance, missed intents, source-marker
  regressions, public-prose status, internal jargon leaks, and attempts, but it never
  cancels a successfully created version. Manual edits and successful comment
  revisions create new immutable `DraftVersion` records; old versions must not be
  mutated. Approving final text creates
  `FinalText.editorDecisionSnapshot` with selected version, human comments/manual
  edit counts, machine trace availability, final-gate/revision/alternative-angle
  summaries, validation summary, and unresolved risks.
- Slice 2.16.1 moves post-run learning into Author Memory. Final version selection
  calls `upsertEditorialLearningAuthorNote`, creating or updating one deterministic
  `AuthorNote.type = editorialLearning` per `FinalText`. The note stores structured
  metadata from `EditorDecisionSnapshot`, version history, human comments, manual edit
  counts, rejected version ids, quality-check summaries, unresolved risks, and a
  suggested takeaway. New learning notes start as `pendingReview`; rejected or pending
  notes stay visible in the memory feed but `inferAuthorPositionAssertions` must
  ignore them. Only accepted editorial-learning notes become normal author-memory
  evidence. Do not mutate publisher rules, Topic, Fabula, validators, prompts, or
  model settings from these notes in this slice.
- `FeasibilityReport` stops unsafe drafting before prose is generated. A blocked
  DraftRun is `status=succeeded`, `finalDraft=null`, and `complete.status=blocked`;
  this is a quality decision, not an infrastructure failure.
- Candidate link recovery is part of DraftRun input hygiene. `src/application/postCandidateLinking.ts`
  is shared by plan-slot approval and `src/application/draftRunContext.ts`; missing
  `postCandidateId` must not block a run when source signal evidence, approved brief
  evidence, topic, and fabula are present.
- `PostContract` locks the thesis, audience value, CTA, allowed claims, forbidden
  moves, platform constraints, and fabula obligations for later strategy,
  validation, ranking, and revision steps.

Do not add validator prompts that judge final text without these artifacts. They would
not know what the text was allowed to claim, what public evidence was actually used,
or what invariants a revision must preserve. ADR
`2026-06-23-drafting-requires-public-evidence-research` records this rule.

Drafting steps should be narrow:

1. Build full context.
2. Normalize approved-fabula sources into source intent.
3. Build a seed source ledger with claim ids, provenance, allowed use, risks, and forbidden
   inferences.
4. Plan public research from the fabula, signal, source ledger, and author position.
5. Read exact URLs and trace unconfigured search tasks through infrastructure adapters.
6. Merge public evidence into the source ledger and synthesize what it changes.
7. Run a feasibility gate before prose generation.
8. Lock a post contract from the approved brief, candidate, slot, source ledger, and
   rules.
9. Select machine-readable rules into a rule registry snapshot.
10. Compile the compact rule pack used by planning and prompts.
11. Plan materials.
12. Choose several rhetorical plans / draft strategies.
13. Generate several candidates.
14. Run deterministic lint checks.
15. Validate candidates with report-only LLM validators.
16. Rank candidates pairwise and select the strongest initial attempt.
17. Run a bounded editorial revision loop until validator-clean, editorially-improved,
    provider failure, or `DRAFT_REVISION_MAX_ITERATIONS`.
18. Preserve rejected revision attempts as structured `rejectedMoves` and constraints
    for later loop cycles.
19. Surface the selected draft, unresolved warnings, claim provenance, and human
    decision data.

The main editor should see a compact report. The full artifact chain belongs in the
`/ai-runs` DraftRun trace workbench.

Slice 0.8 intentionally adds no provider SDKs, API keys, environment variables,
backend, streaming, billing, or real provider calls.

## Backend AI Execution Track

The backend starts as an execution layer for AI and document workflows. It does not
replace local workspace persistence until a slice explicitly moves one use case behind
the backend.

The first backend implementation order is:

1. Backend foundation and OpenRouter environment validation.
2. AI run contract and audit trail.
3. First OpenRouter-backed editorial run with deterministic fallback.
4. AI run observability and trace inspection.
5. Queued `DraftRun` contract with Redis/Celery worker foundation. Done.
6. Full draft-run context builder. Done.
7. Rule-pack compiler. Done.
8. Material plan and draft strategy steps. Done.
9. Multi-candidate draft generation. Done.
10. Source ledger foundation. Done.
11. Feasibility gate and post contract. Done.
12. Rule registry v2 and validator bindings. Done.
13. Contract-based rhetorical plans. Done.
14. Source intent and research plan. Done.
15. Public evidence retrieval foundation. Done.
16. OpenRouter web search adapter. Done.
17. Public evidence query and relevance repair. Done.
18. SourceLedger external evidence merge. Done.
19. MaterialPlan evidence accountability and retry. Done.
20. Deterministic linter and validator orchestrator. Done.
21. Attribution validator calibration. Done.
22. JSON step retry discipline. Done.
23. LLM-assisted validator reports. Done.
24. Pairwise ranking and directed revision. Done.
25. DraftRun long-running step progress budget. Done.
26. Iterative revision loop and improvement gate. Done.
27. Multi-model drafting roles. Done.
28. Article dossier and context packs. Done.
29. Evidence interpretation. Done.
30. Prosecutor critic, alternative-angle tournament, and deep revision loop v2. Done.
31. Final quality contract/gate repairs and attribution handoff calibration. Done.
32. Regression report and editor decision learning.

`langgraph-document-ai-platform` import remains important, but it should wait until
the queued-run pattern is stable enough to reuse for document workflows.

Every backend slice must update architecture smoke with the files and forbidden-import
rules it introduces. `npm run test:architecture` remains mandatory even before a
dedicated backend test command exists.

## Validation Strategy

Current tests cover:

- Author memory event creation, assertion inference, evidence links, persistence, and
  UI smoke behavior.
- Domain transitions and approval rules.
- Deterministic scoring, planning, briefing, drafting, editorial check, and release
  packaging services, plus analytics prep.
- Local workspace save/load behavior.
- Feature-owned app-flow coverage for signals, author memory, editorial model,
  context chat, plan, editing, release, and analytics.
- App shell/navigation coverage in `src/App.test.tsx`.

Run `npm test` and `npm run smoke` before completing the slice.
For new UI behavior, put tests beside the owner:

- app shell only: `src/App.test.tsx`;
- feature workflows: `src/features/<feature>/*AppFlow.test.tsx`;
- component-level feature behavior: the feature component test;
- domain/application/infrastructure behavior: the owning module test.

If `npm run test:architecture` reports a touched test file as near-limit, split that
test by feature/workflow ownership before adding more scenarios.

For backend slices, run the backend test command introduced by the slice, plus
`npm run test:architecture`. Backend tests should cover settings normalization, route
contracts, application services, provider fallback, adapter error mapping, and
dependency-boundary failures where practical.
