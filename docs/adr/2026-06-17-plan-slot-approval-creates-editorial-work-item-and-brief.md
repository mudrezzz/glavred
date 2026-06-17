# ADR: Plan Slot Approval Creates Editorial Work Item And Brief

## Status

Accepted

## Context

The production flow now has two different approval gates before editing starts:

1. `Signals -> Post Candidates -> Approve`: the author approves a post concept.
2. `Plan -> Approve`: the author approves that concept in a concrete broadcast slot.

After the second approval, there is no useful intermediate action between "approve the
slot" and "prepare the post fabula". Requiring a separate `Prepare post fabula` button
made the UX feel like a duplicated confirmation step and kept the handoff between
planning and editing ambiguous.

## Decision

Approving a plan slot creates or updates the stable `EditorialWorkItem` for that slot
and immediately prepares the initial `PostBrief` for the selected work item.

The stable work item id is derived from `contentPlanItemId`, so re-approving or
updating the same slot must not create a duplicate editorial post.

`Plan` remains responsible for broadcast demand and slot approval. `Editing` owns the
post after slot approval:

- the `Posts` tab lists approved production work items;
- the `Workbench` tab edits one selected post;
- the `Fabula -> Draft -> Final` stages are inside the selected post workbench;
- returning a work item to candidates reverses the approved slot and removes the
  work item from the editing queue.

The old singleton fields `postBrief`, `postDraft`, `finalText`, `releasePackage`, and
`editorialLearningNote` remain compatibility fields while the selected work item is
being migrated to explicit item-scoped actions.

## Consequences

- The visible `Prepare post fabula` step is no longer part of the happy path after
  plan slot approval.
- Approved plan slots can immediately appear in `Editing -> Posts`.
- Opening `Editing -> Workbench` shows a ready initial fabula/brief for the selected
  post.
- Tests must cover stable work item creation, automatic brief preparation, and return
  to candidates.
- Release queue migration remains a separate slice.

## Alternatives considered

- Keep the explicit `Prepare post fabula` button. Rejected because it duplicated the
  second approval gate and did not expose any meaningful decision between approval and
  editing.
- Move full editing into `Plan`. Rejected because planning and production editing have
  different responsibilities, and the existing `Editing` workbench already owns the
  useful fabula/draft/final experience.
