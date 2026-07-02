# Glavred

Glavred is an AI-native editorial office for expert authors, founders, consultants,
and teams who want to run a personal media system without losing the author's own
position.

The product is not positioned as an AI copywriter. Its core job is to help the author
capture raw thoughts, reactions, corrections, and released work, turn them into a
transparent author position model, and use that model to plan, validate, draft, and
release content.

The current repository contains the first working local-first editorial cabinet. It
implements author memory, evidence-backed author-position assertions, reviewed
signals/radars, and an editable production flow from approved signal to insight card,
broadcast content grid, approved post brief, backend-assisted or deterministic-fallback
draft, editorial checks, approved text, visual decision, ready state, publication log,
and captured editorial learning note. The current `FinalText` and `ReleasePackage` artifacts remain
compatibility/manual-export surfaces until the release-log slices replace them.

`Память автора` is now the main entry point: titleless thought capture, optional local
file attachments, local link previews, targeted corrections, search/filtering, lazy
feed loading, long-note collapse, edit/delete actions, memory summary, and browser
voice-input fallback are available before any production workflow starts.

The same author-memory workspace now includes a local-first external-source shell:
`Лента`, `Источники`, `Очередь разбора`, and `Архив`. It uses deterministic mock
candidates for the active demo portfolio project, supports filtering, grouping, individual
review actions, `Добавить все`, archive-safe bulk acceptance, and undo for the latest
bulk action. Unreviewed and archive-only material does not change the author-position
assertions.

`Редакционная модель` now behaves like the workspace of a virtual publishing project:
an explicit project profile, editable atomic rules for author/audience/position/style/
goals/boundaries, compact topic and fabula lists, a topic-fabula compatibility matrix,
and a deterministic validation panel on every tab. Validation is explicit: the author
clicks `Проверить`, gets a saved snapshot, and sees `Требует повторной проверки` after
committed setup changes. Topics and fabulas can be added or deleted directly from their
lists; deletion removes compatibility matrix links but does not rewrite already-created
production artifacts. Legacy rubric/fabula fields remain available only for storage and
service compatibility. Slice 1.2 replaces the earlier ad-hoc setup check with a common
validator baseline: the manual `Проверить` action now saves a `ValidatorRun`, and each
validator returns a score, red/yellow/green status, evidence, and suggested fixes.

`План` now shows a broadcast grid rather than a single content-plan card. Slots carry
date, platform, format, topic, fabula, priority, approval status, manual override state,
and advisory weight warnings. The standalone sidebar item `Фабулы` was removed:
editorial fabulas live inside `Редакционная модель`, while approving a concrete plan
slot automatically creates the editorial work item and initial post fabula/brief.

`Сигналы` is now the material intake workspace: demo radars collect material from
author memory, archive, external sources, and manual research; found signals can be
approved, corrected, archived, or rejected before downstream production starts.
Radars are configurable search objects with atomic rules and optional sources. Found
signals are raw evidence-backed material; topic/fabula/audience/value matching belongs
to post candidates, not to the signal review UI. Radars now also separate search
surface from editorial suitability: each radar has a source discovery mode and
optional filters for author, audience, positioning, goals, forbidden topics, and
topics. Filtered-out material stays visible for human review; style is checked later
during drafting and editorial review, not during radar intake.
`Кандидаты постов` is now the first working candidate layer: approved signals become
2-3 deterministic assemblies of signal, topic, fabula, audience, value, goal, platform,
confidence, and risks. Candidate format was removed because fabula already owns the
editorial shape; platform/format settings stay in the broadcast grid layer. The
candidate list uses the same filter/search/group cabinet pattern as `Очередь разбора`;
candidates can be edited or rejected locally, and approving one candidate makes it the
current concept for `Собрать инсайт`. The current broadcast grid remains a useful
local-first prototype: it now has list/group/calendar views over the same filtered
slots, while request-more generation and a true readiness calendar remain future work.

Approved slots now enter an editorial work queue: `Редактура` has `Посты` and
`Рабочий стол` tabs, lists production work items with the shared filter/search/group
pattern, lets a post return to candidates, and owns selected-post preparation. The
target chain is `Фабула -> Драфт -> Визуал -> готов к выпуску`: text approval belongs
in `Драфт`, `Визуал` now uses `Бриф -> Подготовить варианты -> Выбрать -> Утвердить`
for `Сгенерировать` and `Найти мем`; `Мем + генерация` is two-step
`Бриф -> Подготовить мемы -> Выбрать мем -> Сгенерировать кастом -> Выбрать -> Утвердить`,
and `Без визуала` remains an explicit shortcut. The next slice turns a completed
visual decision into readiness. `Выпуск` is the future publication log for delivery
attempts, statuses, external links, and platform errors.

Attached files are stored as local demo evidence only. Real document parsing,
extraction, OCR, and AI analysis are explicitly deferred.

The current product circle re-centers the system around author memory and
validator-backed editorial entities before adding real AI provider integration.

## Source Requirements

Primary source requirements file: `glavred.md`.

Current status: `glavred.md` remains the historical product brief. The active June
2026 product revision is documented in the architecture docs and roadmap. The existing
design handoff is a secondary visual/product reference.

## Product Direction

The durable product loop is now:

`Author Memory -> Author Position Model -> Editorial System -> Content Production -> Release -> Learning`

The current product loop wraps the local workspace in a SaaS-ready portfolio shell:

`UserAccount -> BlogProject -> PublicationChannels -> Project-scoped Editorial System -> Platform Variants -> Learning`

`BlogProject` is the key boundary: one independent blog or media system with its own
author memory, editorial model, sources, plan, DraftRuns, final decisions, and learning
notes. Project switching is available locally from the lower-left sidebar identity
block through a `PortfolioState` with demo users, memberships, projects, and one
isolated workspace per selected blog.
Publication channels now live inside that project-scoped workspace. A channel is a
managed destination such as a Telegram channel, LinkedIn newsletter, Dzen project, or
site; it is not just the old freeform `platform` string. Planning keeps `platform` as a
denormalized compatibility label, but new plan slots and settings can reference a
stable `channelId`. Autoposting, OAuth credentials, and multi-target generation remain
future slices.
Slice 2.17.3 adds the first backend SaaS boundary around that same shape:
email/password dev login, HttpOnly session cookie, project memberships, and
project-scoped workspace snapshots in SQLite. The frontend tries the backend first,
shows a login panel on `401`, and falls back to the local demo portfolio when the
backend is unavailable. Production auth, multi-platform generation, and publication
adapters should grow around this boundary rather than around the old singleton
workspace. This direction is captured in ADRs
`docs/adr/2026-06-29-blog-project-portfolio-saas-boundary.md`,
`docs/adr/2026-06-30-dev-password-session-auth-boundary.md`, and detailed in
`docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md`.

After login the app opens the `Project Dashboard`, not the first blog cabinet. The
dashboard shows available blog projects as cards, supports creating a new project,
renaming a project, and soft-archiving it. Opening a card enters the existing editorial
cabinet for that project. Inside the cabinet the lower-left portfolio switcher remains
available for quick project switching and has a `Все проекты` action to return to the
dashboard. The dashboard uses the same shell language as the project cabinet: a
full-height left sidebar, topbar, centered working canvas, account placeholders in the
sidebar, and the owner profile in the sidebar footer. Project cards stay in a
constrained two-column tile grid so a single project does not stretch across the whole
screen.

The existing source-signal workflow remains useful, but it is a production layer, not
the product center. Source signals, radar findings, archive imports, analytics notes,
and manual corrections all become material for the author memory.

The revised core modules are:

- Author Memory: free internal feed of thoughts, links, reactions, corrections, and
  learning events.
- External Sources and Import Review: local source settings shell, review queue, bulk
  import, and archive-safe handling for large historical archives.
- Author Position Model: transparent, evidence-backed model of how the author thinks
  and writes.
- Topics and Fabulas: addable/removable editorial entities with weights,
  compatibility matrix, rules, and validators.
- Signals and Radars: reviewed material from author memory, archive, external sources,
  and manual input before it becomes a post candidate. Radar and signal lists use
  framed cabinet rows covered by visual and design-system guardrails. The guardrails
  now also check disclosure stability, right-aligned header metrics, inline radar
  editing, multiline rule/source fields, and radar editor form spacing.
- Post Candidates: proposed combinations of signal, topic, fabula, audience, value,
  goal, and platform, reviewed through the shared large-list pattern.
- Content Design Records: durable project-wide content decisions, similar to ADRs for
  software projects.
- Audience, goal, metrics, platforms, and formats: structured rules, not freeform
  text boxes.
- Validators: formal checks with score, status, evidence, and fix guidance.
- Context Chat: topbar-triggered assistant with `Чат` and `Подсказки` modes. It is
  synchronized with the selected product section, answers local deterministic questions,
  opens safe draft forms, and never calls AI providers or saves changes automatically.

Current working flow: the first implementation still reaches a captured editorial
learning note and uses local-first browser persistence before backend, real metrics
ingestion, autoposting, or AI provider integration.

Permanent demo portfolio: two users and three independent blog projects. Each project
has its own author memory, editorial model, topics, fabulas, signals, plan slots, and
ready benchmark scenario:

- `AI Design Patterns`: Russian Telegram-first industrial AI design patterns blog
  about ТОиР, EAM, Decision Intelligence, hybrid AI, and a future OSS pattern book.
- `Каша из топора`: Telegram-native RevOps/Product Marketing author blog with strong
  stance, irony, and field observations from complex B2B commercialization.
- `Блог Главреда`: product philosophy and practical editorial methods, with the first
  planned Telegram + Dzen multi-platform adaptation benchmark.

The demo fixtures are sanitized paraphrases of real working materials; private source
documents are not committed to the repository.

## Roadmap Workflow

The roadmap is tracker-backed. `ROADMAP.md` is a generated report and should not be
edited manually.

- Source artifact for Git review: `docs/roadmap/slices.export.jsonl`.
- Local working cache: `var/roadmap/roadmap.sqlite`.
- Human-readable report: `ROADMAP.md`.

Useful commands:

```bash
python -m backend.app.roadmap next
python -m backend.app.roadmap show 2.17.4
python -m backend.app.roadmap list --status Ready
python -m backend.app.roadmap update-status 2.17.4 Done
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
```

Before committing roadmap changes, run `check`, `render`, `export`, and
`git diff --check`. Details are in `docs/roadmap/README.md` and ADR
`docs/adr/2026-07-01-roadmap-tracker-source-of-truth.md`.

## Quick Start

Run the full local stack with Docker:

```bash
docker compose up --build
```

Then open `http://localhost:5176`. The backend is published at
`http://localhost:8000`, Redis is published at `localhost:6379`, and local AI/DraftRun
audit data is written under `var/`.
Docker Compose reads local secrets from `.env`; `.env` is ignored by Git and is not
copied into the Docker build context.

Run without Docker:

```bash
npm install
python -m pip install -e ".[dev]"
npm run dev
```

Run the backend:

```bash
npm run dev:backend
```

Run the backend worker locally when you are not using Docker:

```bash
npm run dev:worker
```

The backend currently exposes health endpoints, AI run audit endpoints, the
compatibility draft endpoint `POST /api/drafts/generate`, and the primary queued draft
runner:

- `POST /api/draft-runs`
- `GET /api/draft-runs/{id}`
- `GET /api/draft-runs/{id}/events`

The dev SaaS portfolio boundary exposes:

- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/users/me`;
- `GET /api/projects`, `GET /api/projects?includeArchived=true`,
  `POST /api/projects`, `GET/PATCH /api/projects/{projectId}`;
- `GET/PUT /api/projects/{projectId}/workspace`.

Seeded demo users are `founder@example.test` with `AI Design Patterns` and
`Каша из топора`, and `glavred-editor@example.test` with `Блог Главреда`. The
default dev password is `glavred-demo`.

When OpenRouter is configured, the compatibility endpoint can generate drafts through
the provider; missing provider config or provider errors fall back to deterministic
drafting and are recorded in local SQLite at `AI_RUN_AUDIT_DB_PATH` (default
`var/glavred-ai-runs.sqlite3`, ignored by Git).
Draft runs store a local sanitized trace with prompt messages, provider metadata,
generated draft body, fallback flag, and safe error context. The UI stores only a
summary and the `AiRun ID`; inspect the full trace through
`GET /api/ai-runs/{id}` or the separate debug page at `/ai-runs`.

The synchronous draft endpoint is a provider-integration compatibility path, not the
primary drafting model. The primary UI path starts a queued `DraftRun`, polls status,
and applies the final draft when the worker completes. The run request now includes a
`draftContext` snapshot from the selected editorial post: plan slot, candidate when
available, source signal, topic, fabula, publisher rules, and author-position
evidence. The worker writes a `SourceLedger` into
`steps[0].artifactPayload.sourceLedger`, normalizes approved brief sources into
`steps[1].artifactPayload.sourceIntent`, creates a `ResearchPlan`, executes available
public-evidence retrieval in `steps[2].artifactPayload`, runs `feasibility`
and `postContract`, then continues into `RulePack`, `MaterialPlan`, `DraftStrategy`,
`RhetoricalPlans`, and several draft candidates. Inspect `GET /api/draft-runs/{id}`:
`steps[0]` is context plus source ledger, `steps[1]` is source intent and research
plan, `steps[2]` is public evidence retrieval, `steps[3]` is feasibility, `steps[4]`
is the post contract, `steps[5]` is the rule pack plus `ruleRegistrySnapshot`, and later steps contain planning, strategy,
rhetorical plans, candidates, validation, and completion. If feasibility blocks the post, the run succeeds with `finalDraft=null`
and `complete.status=blocked`; the UI shows that the post was stopped before
generation and links to the trace. Missing candidate links are recovered from the
approved source/topic/fabula context where possible; if the source and brief evidence
are sufficient, the run proceeds with constraints instead of blocking. The rule
registry snapshot gives future validators explicit rule ids, claim provenance, and
locked editorial invariants instead of forcing them to guess from final text.
Rhetorical plans now define the routes candidates execute; candidates no longer invent
their own directions. `Фабула -> Источники` is now source intent rather than raw prompt
text: URLs, named sources, human-language research requests, proof needs, framing
hints, and exclusions become a research plan before writing. Public evidence now reads
explicit URLs; general search tasks call OpenRouter `openrouter:web_search` when
`OPENROUTER_WEB_TOOLS_ENABLED=true`, otherwise they remain explicit `notConfigured`
attempts. Search tasks are first converted into a readable `builtQuery` from the
research instruction, not from internal target ids, and returned citations pass a
conservative relevance guard before they become `PublicEvidenceItem` candidates. The
worker now synthesizes accepted public evidence into `EvidenceSynthesis` and merges
it into an enriched `SourceLedger` before feasibility, post contract, rule registry,
planning, rhetorical plans, and candidate generation. Failed, skipped, or disabled
search attempts stay as warnings and never become proof. The `MaterialPlan` step now
receives a short `usableEvidenceCandidates` projection from the enriched ledger. It
must either choose evidence or explain why projected claims were rejected; empty
evidence without accountability triggers a repair retry and then the optional
`OPENROUTER_BACKUP_MODEL` before emergency deterministic fallback is allowed.
Recommended role-model defaults for local DraftRun experiments are writer
`openai/gpt-5.1`, technical JSON backup `openai/gpt-4.1-mini`, critic/final gate
`google/gemini-2.5-pro`, and another-angle `qwen/qwen3.7-max`. Writer is
responsible for public prose, critic for strict editorial challenge, final gate for
independent acceptance of the delivered post, and another-angle for creative
divergence; backup is technical JSON recovery only and should not be treated as a
second creative opinion. Writer, revision, JSON repair, final gate, and another-angle
calls also carry role-specific generation params in child `AiRun` trace.
After validation, the worker pairwise-ranks candidates and runs a bounded
`revisionLoop` inside `validation.rankingRevision`. The loop now optimizes explicit
editorial dimensions, not only validator findings: idea strength, tension, reader
value, author stance, source integration, structure, and validator health. It builds
goals from validation, EvidenceInterpretation, EditorialCritique, the alternative-angle
tournament, material gaps, and prior rejected moves, then accepts a revision only when
it resolves targeted goals or clearly wins pairwise without deterministic/attribution
regression. The iteration count is controlled by `DRAFT_REVISION_MAX_ITERATIONS`
(default `3`). The main editor still receives one final draft; `/ai-runs?runId=...`
shows revision cycles, editorial goals, dimension scores, rejected moves, accepted or
rejected attempts, unresolved goals, and the final stop reason.
After the revision loop, `validation.rankingRevision.finalQualityGate` checks the
delivered final draft as public prose. If the text leaks internal terms like
`SourceLedger` or `publicEvidence`, reads like a source dump, or loses reader value,
the worker builds a final quality contract, asks an independent final-gate model for
public-prose review, then can run bounded targeted writer repair cycles. Repairs are
accepted only if deterministic regression checks pass and the gate findings improve.
Otherwise the previous best draft remains final and the trace shows why the repair was
rejected.

After the machine run returns `finalDraft`, the editor works with immutable draft
versions. The delivered machine draft becomes `v1`; manual edits are saved as new
versions, and the editor can send the active version plus a comment to
`POST /api/drafts/revise-with-comment` for a writer-role revision that creates
`v2`, `v3`, and so on. After a successful comment revision, Glavred runs a
review-role diagnostic quality check for comment compliance, source-marker
preservation, public-prose health, and internal jargon leaks. Failed comment
revisions do not create fake versions; failed quality checks keep the new version
with `qualityCheck.status=notRun`. Any saved version can be selected as final,
including `v1` after later revisions exist.
The approved `FinalText` stores an `EditorDecisionSnapshot` with the selected version,
human comments/manual edit counts, available machine trace summaries, and unresolved
risks. The same final-selection action now creates or updates one deterministic
`editorialLearning` author-memory note. The note is visible in `Память автора` as an
auto `Редакторское наблюдение` with status `На проверке`; it summarizes selected and
rejected versions, repeated comments, manual edits, HITL quality-check risks, and the
suggested takeaway. Pending or rejected learning notes do not affect author-position
inference. Only after the editor accepts the note does it become normal author memory.

The demo seed already includes one completed HITL learning scenario. After clearing
local storage or loading the demo workspace, open `Редактура -> Рабочий стол -> Драфт`
to see seeded versions `v1-v4`: `v2` is selected as final even though later versions
exist, and `v3/v4` show comment-quality risks. Then open
`Память автора -> Редакторские наблюдения` to review the pending auto note and accept
it into memory.

The next drafting-quality direction is an editorial lab around this spine, not a
larger "bad draft" report. DraftRun now has role-specific model policy: research,
strategy, writer, review, critic, and another-angle roles can use different OpenRouter
models, while backup remains only a technical retry/fallback model and web search uses
its own search model. Child `AiRun` traces record `modelRole`, `selectedModel`, and
`modelSelectionSource`.

DraftRun also has local article memory: `ArticleDossier` turns evidence, claims,
decisions, risks, rejected moves, and open questions from the current run into compact
cards, and `ContextPacks` select the relevant cards for each role. This is not
workspace persistence and not a vector store; it is deterministic context engineering
inside one queued run. `/ai-runs?runId=...` shows the dossier, role packs, and the
pack passed into child model calls. Evidence interpretation now turns accepted sources
into implications, examples, limits, and forbidden overclaims before material planning
and writing. The prosecutor/editor critic role now writes a report-only
`editorialCritiqueReport` inside the existing `validation` step: it attacks blandness,
weak tension, missing author stance, forced source use, generic AI prose, unsupported
leaps, and unclear reader value. It is visible in trace and feeds ArticleDossier.
The alternative-angle tournament now uses that critique to ask the `anotherAngle`
role for one deliberately different route, then asks the `writer` role to produce a
challenger candidate. Final validation, ranking, and revision run over the merged
candidate pool. If the alternative route or challenger fails, the original candidates
continue and the failure is explicit in trace.

Source strategy defaults now live in `Fabula.researchStrategy`: manual fabulas copy
configured research instructions into new work briefs, while auto fabulas create
readable prompts from the post context. `PostBrief.sources` remains the approved
per-post override and is the only source input consumed by the DraftRun `sourceIntent`
step.
`Fabula.researchDepth` now adds a separate depth policy: `light`, `standard`, `deep`,
or `marketResearch`. Backend `DRAFT_RUN_EXECUTION_MODE=smoke|standard|full` combines
with that depth into a trace-visible `DraftRunBudget` that caps research tasks, URL
reads, web-search results, accepted evidence, external ledger claims, usable material
evidence, draft candidates, and smoke revision iterations. Budget-skipped tasks and
trimmed evidence stay visible in `/ai-runs?runId=...`; they are never treated as
evaluated proof.

Run tests:

```bash
npm test
npm run test:backend
```

Run the smoke build:

```bash
npm run smoke
```

Run architecture guardrails:

```bash
npm run test:architecture
```

Run browser visual smoke checks:

```bash
npm run test:visual
```

Run structural design-system checks:

```bash
npm run test:design
```

This check covers shared cabinet primitives: section-header metric alignment,
main/right column boundaries, tab count badges, ordinary white create actions versus
red validation/commit actions, and stable radar metadata slots.

Update user wiki screenshots:

```bash
npm run docs:screenshots
```

Publish the GitHub Wiki from `docs/wiki/`:

```bash
npm run docs:wiki:publish
```

## Documentation

- [Roadmap](ROADMAP.md)
- [Author position concept](docs/architecture/AUTHOR_POSITION_CONCEPT.md)
- [External source import concept](docs/architecture/EXTERNAL_SOURCE_IMPORT_CONCEPT.md)
- [Signals and broadcast planning concept](docs/architecture/SIGNALS_AND_BROADCAST_PLANNING_CONCEPT.md)
- [System architecture overview](docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md)
- [DraftRun pipeline AS IS](docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md)
- [DraftRun pipeline AS IS PDF](docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf)
- [DraftRun pipeline TO BE 2.15.3](docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.md)
- [DraftRun pipeline TO BE 2.15.3 PDF](docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_15_3.pdf)
- [Architecture decision records](docs/adr/README.md)
- [Contributor guide](docs/contributor/CONTRIBUTING.md)
- [Developer guide](docs/developer/DEVELOPER_GUIDE.md)
- [User guide](docs/user/USER_GUIDE.md)
- [Demo](demo/README.md)
- [GitHub Wiki](https://github.com/mudrezzz/glavred/wiki)
- [Wiki source](docs/wiki/Home.md)

## Development Model

This project is developed iteratively through small slices. Each slice should leave the
product runnable, tested, documented, and demonstrable.

GitHub repository: `https://github.com/mudrezzz/glavred` (public).
