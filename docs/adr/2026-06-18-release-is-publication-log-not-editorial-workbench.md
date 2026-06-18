# ADR: Release Is A Publication Log, Not An Editorial Workbench

## Status

Accepted.

## Context

The product flow has accumulated two different meanings for `Выпуск`.

The early MVP used `ReleasePackage` as a manual export workbench: final text, Markdown,
checklist, copy/download, and a release status. That was useful while the product had
only one current post and no real publication integrations.

After the editorial queue and selected-post workbench, this boundary is no longer
correct. The author expects content preparation to stay in `Редактура`: fabula, draft
text, visual decision, and the final ready state of the post. If `Выпуск` also edits or
prepares content, the workflow repeats approval steps and splits one post across two
workbenches.

## Decision

`Редактура` owns post preparation:

- fabula/brief;
- draft text and text approval;
- visual preparation and visual approval or explicit `без визуала`;
- the `readyForRelease` state.

`Выпуск` owns delivery:

- publication attempts;
- publication statuses;
- external platform links or ids;
- adapter errors and retry notes;
- delivery history.

Future model names:

- `ReadyPost`: a read/projection model produced by `Редактура` when the post is ready
  for delivery.
- `PublicationLogEntry`: a delivery log record for a ready post, publication attempt,
  or manual/exported publication state.
- `PublicationAdapter`: an infrastructure boundary for future platform delivery.

The current `ReleasePackage` remains a compatibility/manual-export surface. It is not
the future source of truth for release state and should be replaced by publication log
entries as platform integration slices arrive.

## Consequences

- The user-facing `Финал` tab should be removed. Text approval happens in `Драфт`.
- After text approval, the next production stage is `Визуал`.
- A post becomes ready for release only after text approval and a visual decision.
- `Выпуск` must not edit text, visual, candidate context, brief, or draft artifacts.
- Release-log slices should consume ready posts and create delivery records.
- Platform APIs attach behind `PublicationAdapter` and write `PublicationLogEntry`
  records.
- Analytics can later read publication log entries instead of depending on a manual
  release package.

## Alternatives Considered

### Keep `Выпуск` as a release workbench

Rejected. It keeps content preparation split across `Редактура` and `Выпуск`, repeats
approval semantics, and makes the release section responsible for editorial state.

### Rename `ReleasePackage` immediately

Rejected for the current slice. Existing runtime code and tests still use the
compatibility type. Renaming the domain artifact should be a separate implementation
slice after the UX model is corrected.
