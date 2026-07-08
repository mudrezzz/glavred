---
name: project-blueprint-creation
description: Use when creating or reworking a Glavred blog project from an approved blueprint into demo fixtures, backend-visible snapshots, docs, and validation checks. Trigger when asked to create/rework a blog project, convert a project blueprint into Glavred data, refresh demo portfolio project data, or prevent empty Publisher blocks, channel-audience duplication, mojibake, or one-to-one topic/fabula coupling.
---

# Project Blueprint Creation

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Overview

Turn an approved blog-project blueprint into consistent Glavred project data. Keep the blueprint as the planning source, write UTF-8 fixtures/docs first, then refresh backend-visible snapshots through safe application paths.

## Required Context

Before editing, read:

- `python -m backend.app.roadmap next` and `python -m backend.app.roadmap show <slice-id>`;
- `ui-design-systems/START-HERE.md` if any visible UI changes are involved;
- `docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md`;
- existing project blueprints in `docs/architecture/*PROJECT_BLUEPRINT.md`;
- demo fixture builders under `src/fixtures/`;
- backend seed/snapshot behavior before changing backend-visible data.

For the blueprint checklist, read `references/blueprint-checklist.md`.

## Workflow

1. Confirm the active slice and whether the blueprint is already approved.
2. Normalize the blueprint into the checklist sections: profile, author, goals, audience, positioning, style, forbidden moves, memory, rules, topics, fabulas, matrix, channels, signals, scenarios, benchmark criteria.
3. Map concept ownership:
   - Publisher/editorial contract owns author, audience, goals, positioning, style, and forbidden moves.
   - Publication channels own destination mechanics only.
   - Topics own territories.
   - Fabulas own reusable story mechanics.
4. Update source artifacts first: blueprint Markdown, fixture builders, and docs.
5. Run fixture validation and targeted tests.
6. Refresh backend snapshots only through safe seed/reset/migration scripts or application APIs.
7. Verify backend mode or local UI shows the refreshed project.
8. Update docs and roadmap tracker, then render/export/check.

## Non-Negotiable Guards

- Never patch Cyrillic demo content directly into SQLite through inline shell commands.
- Never trust mojibake terminal output as proof of corrupted data; verify with UTF-8-aware reads.
- Do not set canonical audience on `PublicationChannel`.
- Do not rely only on `EditorialModel.author/audience/goals`; UI-visible Publisher blocks and DraftRun context must be backed by `editorialRules`.
- Do not create topic/fabula pairs that are effectively one-to-one unless the blueprint explicitly records a narrow project exception.
- Do not leave backend snapshots stale after changing seeded fixtures.

## Validation

Run the relevant fixture validation tests. At minimum, project fixtures must fail if they contain:

- empty active Publisher groups for `author`, `audience`, or `goal`;
- `PublicationChannel.audience` in new seed data;
- mojibake patterns such as `Рџ...`, `СЃ...`, `вЂ`, or four-or-more question marks;
- a topic/fabula matrix that degenerates into one-to-one pairs;
- a ready scenario without source signal, topic, fabula, and channel.

## Completion

Before finishing:

- run targeted fixture tests;
- run `npm run test:architecture`;
- run `npm run smoke` when demo/runtime behavior changed;
- run `python -m backend.app.roadmap check`, `render`, and `export` if roadmap status changes;
- report how backend-visible snapshots were refreshed or why no refresh was needed.
