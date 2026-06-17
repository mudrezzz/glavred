# ADR: Approved Posts Use an Editorial Work Queue

## Status

Accepted

## Context

The current production flow was originally built for one post at a time:

`contentPlanItem -> postBrief -> postDraft -> finalText -> releasePackage`

This made the first end-to-end demo possible, and the existing `Редактура` and
`Выпуск` screens already contain useful single-post workbench behavior. After signals,
post candidates, and broadcast grid settings, the product now needs to handle many
approved posts in a feed. Keeping singleton production state would make the author
jump between plan slots and overwrite the current brief, draft, final text, and
release package.

## Decision

Approved plan slots should enter an `EditorialWorkQueue`.

The queue owns production work items for approved posts. Each work item keeps the
source slot/candidate context and its own production artifacts:

- post brief;
- draft;
- editorial checks and editor notes;
- final text.

Slice 1.9 implements the queue through final text and keeps `postBrief`,
`postDraft`, `editorialChecks`, `editorNotes`, and `finalText` synchronized with
the selected work item through compatibility fields. `releasePackage` and
`editorialLearningNote` remain singleton compatibility state until the release queue
slice.

`Редактура` becomes the queue and selected-post workbench:

- the screen starts with the shared large-list pattern: filter card, search, view
  toggle, framed rows, bottom-left actions;
- selecting a row opens the existing `Фабула -> Драфт -> Финал` workbench for that
  post;
- `Фабула` is the first editing tab, not a separate top-level workflow destination.

`Выпуск` becomes a release queue for work items whose final text is approved:

- the screen starts with the same list pattern;
- selecting a row opens the existing release package/checklist/copy/Markdown workbench;
- release actions operate on the selected work item, not global singleton state.

The current singleton fields may remain temporarily as compatibility fields during
migration, but new production work should be modeled around work-item identity.

## Consequences

- `План` remains responsible for broadcast demand and approved slots.
- `Редактура` owns post production from approved slot to approved final text.
- `Выпуск` owns manual packaging/export for finalized posts.
- Existing `BriefView`, `EditView`, and `ReleaseView` behavior should be reused by
  extracting selected-post workbench components instead of rewriting the editing
  experience.
- Future production actions should accept a work-item id, update one work item, and
  avoid clearing unrelated posts.
- Tests must cover that preparing, editing, finalizing, and releasing one post does
  not overwrite another queued post.

## Alternatives considered

- Keep the singleton production state and add more navigation from `План`. Rejected:
  it does not scale to a feed of approved posts and hides which post is being edited.
- Move all editing controls into `План`. Rejected: planning and editing have different
  responsibilities, and the current `Редактура` workbench is already the better place
  for draft/final work.
- Create separate top-level sections for brief, draft, final, and release. Rejected:
  this would fragment one post's lifecycle and duplicate existing workbench behavior.
