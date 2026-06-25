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
candidates for the AI Product Manager demo, supports filtering, grouping, individual
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

Permanent demo example: a Telegram blog by an AI Product Manager who shares research
experience building AI-B2B products. The demo starts with author notes about workflow
risk, evals, trust, adoption, and confidence boundaries, then routes the same example
through the existing production flow.

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
After validation, the worker pairwise-ranks candidates and runs a bounded
`revisionLoop` inside `validation.rankingRevision`. The loop tries directed repairs,
revalidates the revised candidate, compares it against the previous best, and accepts
only measurable improvement without deterministic regression. The iteration count is
controlled by `DRAFT_REVISION_MAX_ITERATIONS` (default `3`). The main editor still
receives one final draft; `/ai-runs?runId=...` shows revision cycles, accepted or
rejected attempts, unresolved goals, and the final stop reason.

The next drafting-quality direction is an editorial lab around this spine, not a
larger "bad draft" report. DraftRun now has role-specific model policy: research,
strategy, writer, review, critic, and another-angle roles can use different OpenRouter
models, while backup remains only a technical retry/fallback model and web search uses
its own search model. Child `AiRun` traces record `modelRole`, `selectedModel`, and
`modelSelectionSource`. Future slices add a DraftRun-local `ArticleDossier`,
task-specific `ContextPacks`, evidence interpretation, a prosecutor/editor critic
role, and an alternative-angle route. The goal is to create better post ideas before
and during writing: accumulated research, rejected moves, critique, and source
implications should be curated into compact role-specific context instead of either
being discarded or dumped into one huge prompt.

Source strategy defaults now live in `Fabula.researchStrategy`: manual fabulas copy
configured research instructions into new work briefs, while auto fabulas create
readable prompts from the post context. `PostBrief.sources` remains the approved
per-post override and is the only source input consumed by the DraftRun `sourceIntent`
step.

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
