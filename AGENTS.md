# AGENTS.md

## Project operating model

This project is developed iteratively.

Work is organized as:

1. Iterations
2. Slices
3. Small, reviewable increments

A slice is the smallest meaningful unit of product progress. Each slice must leave the project in a working, demonstrable, documented, and tested state.

Do not work in a waterfall style where one large module is fully built before the rest of the product becomes usable. Prefer concentric product growth: first create a limited but complete working product perimeter, then expand it in controlled circles.

## Source of truth

The project backlog is maintained through the roadmap tracker.

- `docs/roadmap/slices.export.jsonl` is the committed source artifact for review.
- `var/roadmap/roadmap.sqlite` is the local generated working database and is not committed.
- `ROADMAP.md` is a generated human-readable report. Do not edit it manually.

Use the tracker CLI for roadmap work:

```bash
python -m backend.app.roadmap next
python -m backend.app.roadmap show <slice-id>
python -m backend.app.roadmap add-slice ...
python -m backend.app.roadmap update-status <slice-id> Done
python -m backend.app.roadmap check
python -m backend.app.roadmap render
python -m backend.app.roadmap export
```

Always keep the tracker artifacts current:

- Add new tasks through the CLI or JSONL export, then render.
- Take work from `python -m backend.app.roadmap next`.
- Update task status during and after work through the tracker.
- Record completed slices, blocked items, and assumptions in tracker records.
- Keep the next actionable task easy to identify.

Before starting implementation, inspect the tracker first and use `ROADMAP.md` as the generated report fallback.

If the user asks to “take the next task”, “continue the project”, “work on the next slice”, or gives a vague continuation request, use `$project-onboarding` first.

## Product requirements source

The project must be driven by the user's source requirements document.

When starting architecture, bootstrapping, or planning work:

1. Ask the user to identify the source requirements file if it is not known.
2. If the user did not specify a file, search the repository root for likely requirements documents, including:
   - `SPEC.md`
   - `SPECIFICATION.md`
   - `REQUIREMENTS.md`
   - `PRD.md`
   - `TASK.md`
   - `TZ.md`
   - `ТЗ.md`
   - files containing "requirements", "spec", "prd", "task", "тз", or "задание" in the name.
3. If several candidates exist, inspect them and choose the most likely primary requirements source. State the choice and uncertainty.
4. Do not invent requirements when the source document is missing or ambiguous. Record assumptions explicitly in `ROADMAP.md` or the relevant architecture document.

## Documentation standards

Keep documentation current together with code.

The repository should maintain:

- `README.md` as the main entry point.
- `ROADMAP.md` as the generated backlog and delivery report.
- `docs/roadmap/slices.export.jsonl` as the roadmap source artifact.
- `docs/roadmap/README.md` as the roadmap workflow guide.
- `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`.
- ADRs in `docs/adr/`.
- Contributor documentation in `docs/contributor/CONTRIBUTING.md`.
- Developer documentation in `docs/developer/DEVELOPER_GUIDE.md`.
- User documentation in `docs/user/USER_GUIDE.md`.
- Demo documentation in `demo/README.md`.

Documentation must be suitable for publishing on GitHub.

When behavior, architecture, setup, commands, public APIs, or user-facing flows change, update the relevant documentation in the same slice.

Use `$docs-sync` when a task changes architecture, setup, public behavior, demo behavior, or user-facing functionality.

## Architecture principles

Use object-oriented design where appropriate.

Follow these principles:

- Single Responsibility Principle: one component should own one clear role.
- Keep domain logic separated from infrastructure, UI, persistence, transport, and integration code.
- Prefer explicit boundaries between modules.
- Prefer small cohesive classes, services, functions, and modules.
- Avoid god objects, hidden coupling, and cross-layer shortcuts.
- Avoid premature abstractions, but extract abstractions when repetition or role confusion appears.
- Keep public interfaces intentional and documented.

Use `$architecture-design` for new architectural decisions, major feature design, or module boundary changes.

## Backend architecture recovery

Before adding or changing backend runtime code, read:

- `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`
- `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`
- `docs/developer/BACKEND_MODULE_TEMPLATE.md`
- `docs/adr/2026-07-03-backend-bounded-contexts-and-operation-contracts.md`

New DraftRun backend modules must live under `backend/app/drafting`, not the flat
legacy `backend/app/application/draft_*.py` or `backend/app/domain/draft_*.py`
namespaces. New upstream radar/search/signal modules must live under
`backend/app/upstream`, not `backend/app/application/upstream_radar_*.py`.

The flat legacy files are an explicit migration allowlist. Treat each one as exactly
one of three statuses: active compatibility facade, migrated thin shim, or remaining explicit debt.
Do not add new files there unless the roadmap slice explicitly records a temporary
debt exception and architecture smoke is updated intentionally.

New bounded-context backend modules must declare ownership in the module docstring:
`Owner`, `Used by`, `Does not own`, and `Architecture doc`. Provider-heavy operations
must expose typed results, attempts, safe errors, and trace-safe payloads instead of
leaking raw provider exceptions across layers. Use the Provider-Heavy Review Checklist
in `docs/developer/BACKEND_MODULE_TEMPLATE.md`; shared operation governance,
payload/runtime budgets, migrated-shim rules, and `npm run test:architecture` are
mandatory backend guardrails.

When backend package quality is questioned, when a backend slice may add structural
debt, or before a broad backend refactor, use `$backend-architecture-audit`. The audit
must distinguish known ledgered debt from new unclassified smells such as public
helper sprawl, procedural bounded packages, raw dict contracts, provider boundary
leaks, dependency-direction risks, and behavior inside migrated thin shims. The
blocking command is `python scripts/backend-architecture-audit.py --format json
--ledger docs/architecture/backend-architecture-debt-ledger.json
--fail-on-unledgered high`.

## Testing standards

Maximize useful test coverage.

Expected test layers:

- Unit tests for isolated logic.
- Integration tests for component collaboration.
- Smoke tests for critical startup and happy-path behavior.
- End-to-end tests for important user-facing flows when applicable.

Every slice must include or update tests for the behavior it introduces or changes.

After each slice:

1. Run targeted tests relevant to the changed area.
2. Run smoke tests if the project has them.
3. Run broader regression tests when there is meaningful risk to existing behavior.
4. Report which tests were run and which were not run.

Use `$regression-and-test-strategy` when choosing the right validation scope or when a change may affect existing functionality.

## Demo standards

Maintain a realistic demo example.

The demo must:

- Evolve with the project.
- Show available working functionality clearly.
- Be realistic, live, and market-relevant.
- Allow a user to see, touch, and understand the product value.
- Cover the most important supported flows.
- Avoid toy examples when a realistic example is possible.

Use `$demo-maintenance` when adding or changing user-visible functionality.

## Code and test comments

Comment code and tests where comments increase maintainability.

Comments should explain:

- non-obvious intent
- domain rules
- trade-offs
- assumptions
- edge cases
- test purpose

Do not add comments that merely restate obvious code.

## Git and GitHub

The project should be connected to Git.

When bootstrapping a new project:

- Initialize a Git repository if one does not exist.
- Create a useful initial commit.
- Propose a concise, marketable project name.
- Create a GitHub repository under the account `mudrezzz` when GitHub CLI authentication is available.
- Prefer a repository name that is lowercase, hyphenated, and easy to remember.
- Do not overwrite existing remotes without asking.
- Do not publish secrets, local environment files, or generated private artifacts.

Use `$project-bootstrap` for initial repository creation, structure setup, README creation, Git initialization, and GitHub setup.

## Workflow expectations

Before making changes:

1. Inspect the roadmap tracker (`python -m backend.app.roadmap next/show`) and generated `ROADMAP.md`.
2. Inspect relevant documentation.
3. Inspect the source requirements file if the task depends on product requirements.
4. Identify the current iteration and slice.
5. Propose or infer the smallest useful next increment.

During changes:

- Keep the slice small.
- Keep the product runnable.
- Keep docs and tests synchronized.
- Prefer minimal, localized changes.
- Preserve existing behavior unless the task explicitly changes it.

## Remote Docker test runtime

All Glavred tests, Docker operations, authenticated browser acceptance, and live
provider proof run on `flowise` through
`.agents/skills/remote-docker-testing/SKILL.md`. Local execution is allowed for source
inspection, editing, Git, roadmap render/export, and document generation, but local
tests are not acceptance evidence. Do not start local Glavred Docker unless the user
explicitly requests it.

Run `python scripts/remote_docker_runtime.py doctor` before remote work. Use compose
project `glavred`, preserve Power Web resources, transfer secrets only through the
repository CLI, and never print tokens, passwords, interpolated Compose config, or
container environment values.

## Execution transparency

Make the applied workflow visible to the user instead of leaving skills and commands
implicit.

- In the first substantive progress update, state which repo-local or plugin skills
  will be used and why. If no skill applies, say `Skills: none`.
- When the selected skill set changes during the task, announce the newly used skill
  in the next progress update.
- In the final response, include a `Skills used` section listing only skills whose
  instructions were actually opened or applied. Do not list skills merely because
  they were available.
- In the final response, include a `Commands run` section with the executed
  user-relevant shell/application commands and their outcome. This includes tests,
  builds, architecture checks, Docker operations, migrations, roadmap commands, and
  Git operations.
- Keep the command ledger exact enough to reproduce the work. Identical retries or
  polling commands may be grouped with a count, and routine read-only exploration
  may be summarized when listing every file-read command would obscure the result.
- Never expose secrets, access tokens, passwords, full sensitive payloads, or command
  arguments containing them. Replace sensitive values with `<redacted>` while still
  naming the command and its purpose.
- A task is not considered fully reported until the skills and command ledger are
  present, even when all tests pass.

## Workspace text integrity

Never perform a full workspace `GET -> PUT` roundtrip with PowerShell
`Invoke-RestMethod`. On Windows that path can silently reinterpret UTF-8 response
text before saving it again. Use `python scripts/workspace_utf8_client.py` or an
application-owned seed/recovery command and verify the semantic hash after the
roundtrip. Do not print complete workspace payloads or damaged text in diagnostics.

Changes to portfolio persistence or a persisted user-facing workspace require at
least one browser acceptance scenario against real FastAPI, authenticated session,
and temporary SQLite. A visual test that received `401`, CORS failure, unavailable
backend, or `localFallback` is not proof of backend workspace behavior.

## Complex pipeline slice guardrails

Complex DraftRun, RadarRun, upstream search, provider-input, trace, quality/fidelity,
budget, diagnostics, async/staleness, validation, ranking, revision, or hard-to-verify
backend pipeline slices must follow this lifecycle:

`AS IS -> Change Intent -> TO BE -> DoD -> Implementation -> AS IS Update`

Use these sources:

- `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md` for DraftRun pipeline work.
- `docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md` for RadarRun runtime/search/coverage
  and trace work.
- `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md` for broader upstream
  source registry, found material, signal extraction, scoring, candidate assembly,
  plan, and DraftRun handoff work.

A complex pipeline slice is not ready for implementation unless its tracker record
states AS IS sources, TO BE necessity, preserved AS IS invariants, changed AS IS
invariants, proof evidence, and Definition of Done. If the slice changes runtime
order, trace shape, provider input, retry/backup/fallback, quality/fidelity, budgets,
diagnostics, async/staleness, or search coverage, it needs an approved TO BE document
or an explicit documented exception.

At completion, the implementer must state either `AS IS unchanged` with a reason or
`AS IS updated` with regenerated PDF where applicable. Every `CHANGED vs AS IS`,
`NEW`, or `REMOVED` TO BE item needs proof in the DoD. Every safety/quality
`NOT THIS SLICE` item must become known debt or a follow-up roadmap slice.

Before finishing:

1. Update the roadmap tracker, then run `python -m backend.app.roadmap render` and `python -m backend.app.roadmap export`.
2. Update relevant docs.
3. Add or update tests.
4. Run the relevant validation commands.
5. Summarize:
   - what changed
   - which slice was completed or advanced
   - which tests were run
   - which docs were updated
   - which skills were used
   - which commands were executed and their outcomes
   - remaining risks or next tasks

## Skills routing

Use these skills when available:

- `$architecture-design` for architecture design based on user input and root project files.
- `$draft-run-pipeline-diagnostics` for diagnosing a concrete DraftRun/AiRun result,
  explaining why a post was bad, generic, stuck, over-sourced, source-free, or
  selected incorrectly, and deciding whether to add a repair slice.
- `$draft-run-pipeline-evaluation` for launching a fresh DraftRun, waiting for queued
  execution, and then running the standard pipeline diagnosis.
- `$draft-run-pipeline-autofix` for launching a fresh DraftRun, diagnosing it against
  `ROADMAP.md`, applying bounded small non-architectural repairs, and repeating the
  run/fix loop up to 5 cycles.
- `$draft-run-to-be-planning` for preparing a detailed DraftRun pipeline TO BE
  Markdown + PDF before implementing a new drafting slice, so the target design can
  be discussed and approved first.
- `$project-bootstrap` for initial project creation, repository structure, Git, GitHub, README, and baseline docs.
- `$project-blueprint-creation` for turning an approved Glavred blog-project blueprint
  into project fixtures, docs, backend-visible demo snapshots, and validation checks.
- `$project-onboarding` when entering an existing project, starting a new chat, or continuing from `ROADMAP.md`.
- `$glavred-project-immersion` when the user asks to get immersed in Glavred, start a
  new chat with a concise project briefing, explain what the product is, where to
  look, which roadmap slice is current, which checks to run, and which architecture
  guardrails matter before doing implementation.
- `$backend-architecture-audit` when reviewing backend package quality, checking
  whether new backend work introduced structural debt, or planning cleanup for public
  helper sprawl, procedural bounded packages, raw dict contracts, provider boundary
  leaks, dependency-direction risks, or migrated-shim behavior.
- `$roadmap-slice-planning` for turning requirements into iterations, slices, and actionable backlog items.
- `$slice-implementation` for implementing the next small product increment.
- `$docs-sync` for keeping README, architecture docs, ADRs, contributor docs, developer docs, user docs, and demo docs current.
- `$regression-and-test-strategy` for deciding and running the correct test scope.
- `$demo-maintenance` for creating or updating the realistic demo example.
- `$remote-docker-testing` for every Glavred test, Docker operation, authenticated
  browser acceptance, remote diagnostics, or live provider proof.

Do not duplicate full skill workflows here. The `SKILL.md` files are the source of truth for task-specific procedures.
