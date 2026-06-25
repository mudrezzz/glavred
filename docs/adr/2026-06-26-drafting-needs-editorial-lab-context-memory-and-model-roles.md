# ADR: Drafting needs editorial lab, context memory, and model roles

## Status

Accepted

## Context

Slice 2.15 added a bounded revision loop, but control DraftRuns showed a deeper
quality problem: the system can now trace, validate, and repair drafts, yet it can
still produce dry or weak prose. A post can satisfy formal checks while lacking a
strong editorial idea, tension, author stance, or live use of sources.

The current pipeline often treats quality improvement as:

1. generate candidates;
2. validate;
3. repair findings;
4. report unresolved issues.

That is not enough for Glavred. The product goal is not to produce a defensive report
that the draft is bad. The goal is to create the conditions for a strong post to
emerge.

The user identified three core gaps:

- one model may be stuck in one writing mode, so the system needs role-specific and
  provider-diverse models rather than only default/backup fallback;
- the run accumulates a large amount of research, validation, critique, and revision
  context, but the pipeline either drops too much or passes oversized blobs;
- there is not enough editorial debate: no durable prosecutor/critic role, no
  productive argument, and no explicit search for alternative angles.

## Decision

Glavred drafting will evolve from a generator-validator-repair workflow into an
editorial lab.

The next drafting-quality slices must introduce:

- a role-specific model portfolio: research, strategy, writer, critic/prosecutor,
  review, another-angle, and technical backup models;
- an `ArticleDossier` / article memory artifact inside `DraftRun`, distinct from raw
  trace JSON and final workspace state;
- task-specific `ContextPack` builders so each LLM receives the right subset of
  evidence, decisions, critique, rejected moves, and author-position constraints;
- source interpretation before citation injection: public evidence must become
  editorial implications, tensions, and usable angles before prose generation;
- explicit editorial roles, especially a prosecutor/critic that attacks blandness,
  weak sourcing, generic AI prose, missing author stance, and forced references;
- an alternative-angle mechanism that asks a different model/provider to propose a
  genuinely different route instead of another retry of the same prompt;
- a deeper revision loop that optimizes for editorial improvement, not only fewer
  validation warnings.

This decision does not remove the quality spine already built:

`SourceLedger -> FeasibilityGate -> PostContract -> RuleRegistry -> MaterialPlan ->
RhetoricalPlans -> DraftCandidates -> Validators -> Ranking -> RevisionLoop`

Instead, it adds a new layer around it:

`ArticleDossier + ContextPacks + Editorial Roles + Model Portfolio`.

## Consequences

- `DRAFT_REVISION_MAX_ITERATIONS` remains useful, but iteration count alone is not the
  core quality mechanism.
- Future slices should avoid simply adding more validators before adding better
  context and editorial debate.
- The main trace surface must show not just failures, but the thinking artifacts that
  explain how the post idea evolved.
- Provider configuration must support role-based model selection, not only
  default/backup failover.
- The pipeline must distinguish raw evidence, interpreted implications, critic notes,
  rejected moves, and final prose decisions.
- `PostContract`, `SourceLedger`, and `RuleRegistry` remain mandatory boundaries; the
  editorial lab must consume them instead of bypassing them with a generic prompt.

## Alternatives considered

- Keep 2.16 as a regression report and human decision learning slice. Rejected for now:
  it would document weak output instead of improving the machine drafting process.
- Add more deterministic validators. Rejected as the next move: validators can detect
  issues but do not create a stronger editorial idea.
- Increase revision loop iterations. Rejected as insufficient: repeating the same
  writer/reviewer pattern can converge on a formally cleaner but still dull draft.
- Add a generic RAG store immediately. Deferred: first we need article-specific memory
  semantics and context-pack ownership, then persistence/retrieval can be added behind
  that contract.
