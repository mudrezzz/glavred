---
name: draft-run-to-be-planning
description: Use before implementing a Glavred DraftRun or drafting-pipeline slice when the user asks to prepare, discuss, approve, or refine a detailed TO BE technical document with diagrams and PDF. Creates or updates a docs/architecture DraftRun Pipeline TO BE Markdown and PDF pair for the slice, links it from ROADMAP.md, and keeps it aligned with the maintained AS IS pipeline map.
---

# DraftRun TO BE Planning Skill

## Goal

Prepare an implementation-ready TO BE document before a DraftRun pipeline slice is
implemented.

This skill is for design approval, not code implementation. It turns a roadmap slice
and discussion context into a concrete target pipeline map with step order, role/model
handoff, artifacts, trace contract, boundaries, tests, and a generated PDF.

## Required inputs

1. The user's current request and discussion context.
2. `ROADMAP.md`.
3. `docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md`.
4. The active slice entry and nearby follow-up slices.
5. Existing ADRs/docs only when the slice changes architecture rules.

## Output files

Create or update:

- `docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_<slice>.md`
- `docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_<slice>.pdf`

Use a filesystem-safe slice suffix:

- `2.15.3` -> `2_15_3`
- `2.15.3.1` -> `2_15_3_1`

Generate PDF with:

```powershell
python scripts/generate-draft-run-pipeline-pdf.py `
  --source docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_<slice>.md `
  --output docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_<slice>.pdf
```

## Process

1. Read the AS IS pipeline document first.
2. Read the active roadmap slice and nearby follow-up slices.
3. Identify exactly what changes in the target slice and what must remain out of scope.
4. Create the TO BE document before implementation.
5. Mark every important change with one of:
   - `NEW in <slice>`
   - `CHANGED vs AS IS`
   - `UNCHANGED`
   - `NOT <slice>`
6. Include rendered-diagram-friendly Mermaid blocks in Markdown. The PDF generator must
   render them as diagrams, not code.
7. Link the TO BE Markdown and PDF from the active `ROADMAP.md` slice.
8. Link durable TO BE docs from `README.md` or SAO when they define a meaningful
   architecture target, not just a temporary note.
9. Generate the PDF and visually inspect key pages.
10. Do not implement the slice unless the user explicitly asks for implementation after
    approving the TO BE.

## Document structure

Use this baseline structure and adapt only when the slice needs a different shape:

```markdown
# DraftRun Pipeline TO BE <slice>

## 1. Target change summary
## 2. Why this slice exists
## 3. Target step order
## 4. Target role-aware execution map
## 5. Controlled algorithm / policy
## 6. Target artifact flow
## 7. Step-by-step TO BE flow
## 8. Trace contract
## 9. Acceptance criteria
## 10. Implementation boundaries
## 11. Explicit non-goals
## 12. Maintenance rule
```

## Required content

Every TO BE document must answer:

- Which DraftRun step or operation changes?
- Is this a new persisted step or an operation inside an existing step?
- Which role is active?
- Which model setting is used?
- What `ContextPack` is passed?
- Which artifacts are consumed?
- Which artifacts are produced?
- What moves from raw data into interpreted/controlled data?
- What appears in `/ai-runs?runId=...` trace?
- What remains explicitly out of scope?
- What tests should implementation later add?

## DraftRun-specific rules

- Do not silently change step order. If the slice does not need a new step, say so.
- Do not add a new SQLite schema in a TO BE unless the roadmap slice explicitly requires
  it.
- Preserve separation of `SourceLedger`, `PostContract`, `RuleRegistrySnapshot`,
  `MaterialPlan`, `ArticleDossier`, `ContextPack`, candidates, validators, ranking,
  and revision.
- Role interaction is artifact-mediated: roles do not share hidden conversation state.
- Raw evidence must not be treated as interpreted editorial meaning.
- Future roles such as `critic` and `anotherAngle` may be shown as future consumers, but
  do not make them active unless the slice scope says so.

## PDF checks

After generating PDF:

- Verify text extraction contains the document title and key `NEW/CHANGED` markers.
- Verify text extraction does not contain Mermaid syntax such as `flowchart TD`,
  `flowchart LR`, or `sequenceDiagram`.
- Render representative pages with `pypdfium2` or Poppler and visually inspect spacing,
  tables, and diagrams.
- Remove temporary render files under `tmp/pdfs/` before finishing.

## Completion checklist

- TO BE Markdown exists and is linked from the active roadmap slice.
- TO BE PDF exists and has rendered diagrams.
- AS IS document remains unchanged unless the current actual pipeline changed.
- `ROADMAP.md` points from the slice to the TO BE document.
- `git diff --check` passes.
- `npm run test:architecture` passes when docs/skills/roadmap changed.
