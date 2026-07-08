---
name: docs-sync
description: Use when code, architecture, setup, public behavior, demo behavior, or user-facing functionality changes and documentation must be synchronized. Updates README, architecture overview, ADRs, contributor docs, developer docs, user docs, demo docs, and tracker-rendered roadmap artifacts.
---

# Docs Sync Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Keep documentation accurate, useful, and GitHub-ready.

## Process

1. Inspect changed files.
2. Identify documentation affected by the change.
3. Update the minimum necessary docs.
   - On Windows/PowerShell, treat Cyrillic mojibake in command output as an encoding
     display issue, not source corruption. Verify docs through UTF-8-aware reads
     before changing Russian text.
4. Add ADRs for meaningful architectural decisions.
5. Ensure `README.md` remains the project entry point.
6. Ensure tracker state reflects completed or new work, then regenerate `ROADMAP.md` and `docs/roadmap/slices.export.jsonl`.

## Documentation responsibilities

- `README.md`: product overview, quick start, links to docs.
- `docs/roadmap/slices.export.jsonl`: tracker source artifact for backlog, iterations, slices, statuses.
- `ROADMAP.md`: generated readable roadmap report.
- `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`: architecture and component responsibilities.
- `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`: current DraftRun pipeline map.
  If DraftRun steps, artifacts, role model usage, retry/fallback behavior, validation,
  ranking, revision, trace semantics, or context flow change, update this file and
  regenerate `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.pdf` with
  `python scripts/generate-draft-run-pipeline-pdf.py`.
- `docs/adr/`: architectural decisions.
- `docs/contributor/CONTRIBUTING.md`: contribution workflow.
- `docs/developer/DEVELOPER_GUIDE.md`: local development, commands, internals.
- `docs/user/USER_GUIDE.md`: user-facing usage.
- `demo/README.md`: how to run and understand the demo.

## Completion checklist

Before finishing:

- Docs match current behavior.
- Links from `README.md` work.
- New public behavior is documented.
- Setup commands are current.
- Architecture changes are reflected.
- `ROADMAP.md` is consistent with the work done.
