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
- `$project-onboarding` when entering an existing project, starting a new chat, or continuing from `ROADMAP.md`.
- `$roadmap-slice-planning` for turning requirements into iterations, slices, and actionable backlog items.
- `$slice-implementation` for implementing the next small product increment.
- `$docs-sync` for keeping README, architecture docs, ADRs, contributor docs, developer docs, user docs, and demo docs current.
- `$regression-and-test-strategy` for deciding and running the correct test scope.
- `$demo-maintenance` for creating or updating the realistic demo example.

Do not duplicate full skill workflows here. The `SKILL.md` files are the source of truth for task-specific procedures.
