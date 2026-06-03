# ADR: Stop First Product Flow at Approved Post Brief

## Status

Accepted

## Context

The source brief describes a full editorial loop from sources to insights, planning,
post intention, draft, checks, publication, analytics, and learning. Building the whole
loop in the first implementation slice would make the product broad before its core
editorial control is proven.

The brief also emphasizes that weak AI content usually starts from a weak intention.
The product should therefore make the author approve the post intention before any
draft is written.

## Decision

The first working product flow stops at an approved `PostBrief`:

`SourceSignal -> InsightCard -> ContentPlanItem -> approved PostBrief`

Draft generation, editorial checks, manual export, publication, analytics, and learning
are deferred to later slices.

## Consequences

- The first implementation slice can deliver a small, complete, demonstrable workflow.
- The first demo proves the product's editorial-control thesis before adding writing.
- Slice 0.4 does not need a writing model, fact-checking pipeline, or final review UI.
- The demo is less visually complete than a draft workflow, so docs and UI copy must
  clearly present the approved brief as a meaningful product output.

## Alternatives considered

- Continue through draft and editorial review: more impressive, but too much scope for
  the first working perimeter.
- Build the full loop through release and analytics: closest to the long-term concept,
  but too large and likely to force premature backend, AI, and integration decisions.
