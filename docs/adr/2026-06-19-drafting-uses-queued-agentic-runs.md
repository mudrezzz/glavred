# ADR: Drafting Uses Queued Agentic Runs

## Status

Accepted

## Context

Slice 2.3 added the first OpenRouter-backed draft generation path. That path is useful
as an end-to-end provider integration, but it is not the target drafting model.

Real Glavred drafting must account for many independent inputs:

- the approved `PostBrief`;
- the approved plan slot and post candidate;
- the source signal, provenance, evidence, and author correction;
- publisher rules for author, audience, position, style, goals, and forbidden topics;
- topic attributes: purpose, audience value, author stance, rules, forbidden angles,
  weight range, and status;
- fabula attributes: dramaturgy, structure, proof requirements, rules, weight range,
  and status;
- future author memory, author-position evidence, archive retrieval, and document
  analysis.

Putting all of this into one prompt creates a brittle black box. The model can ignore
rules, lose topic/fabula constraints, overfit to the brief, or produce an acceptable
draft without any traceable reason why it is acceptable.

Draft generation also becomes long-running once it includes material planning,
retrieval, multiple candidates, validator scoring, revision loops, and self-review.
A synchronous request/response endpoint is the wrong execution model for that work.

## Decision

Glavred will model real drafting as a queued `DraftRun`, not as a larger synchronous
draft-generation prompt.

`DraftRun` is the parent orchestration record. It owns:

- status and lifecycle;
- named steps;
- context summary;
- rule-pack artifacts;
- material plan;
- draft strategy;
- candidate drafts;
- validator results;
- revision attempts;
- selected result and unresolved warnings.

`AiRun` remains the audit record for one provider call. A single `DraftRun` may create
zero, one, or many child `AiRun` records as planning, drafting, validation, and
revision steps call OpenRouter or another provider.

The drafting runner should follow this staged pipeline:

1. Build full context from the selected editorial work item.
2. Compile rule packs from publisher, topic, fabula, signal, candidate, and brief
   constraints.
3. Create a material plan that identifies available evidence, missing evidence, risky
   claims, and grounding strategy.
4. Create a draft strategy that defines thesis, opening, argument sequence,
   dramaturgy, CTA, and forbidden moves.
5. Generate several draft candidates.
6. Validate candidates using narrow validators.
7. Revise failed candidates with targeted correction instructions.
8. Stop by target score, hard-constraint failures, maximum iterations, or no-improvement
   rule.
9. Select the best attempt and return traceable scorecard/warnings.

Celery and Redis are the preferred local worker/queue direction for this class of
long-running backend work. The queue is infrastructure. Domain objects must not import
Celery, Redis, OpenRouter, HTTP clients, or persistence libraries.

Slice 2.4 implements the first baseline of this decision:

- durable `DraftRun`/`DraftRunStep` storage in SQLite at `DRAFT_RUN_DB_PATH`;
- `POST /api/draft-runs` for run creation;
- `GET /api/draft-runs/{id}` and `/events` as polling read-models;
- Redis/Celery services in Docker Compose;
- a deterministic placeholder worker pipeline with named steps;
- frontend polling after `Утвердить фабулу`;
- `/api/drafts/generate` retained as compatibility fallback.

Slice 2.5 adds the first real context boundary:

- frontend sends a read-only `draftContext` snapshot with `POST /api/draft-runs`;
- backend stores the raw snapshot in `DraftRun.requestPayload`;
- worker `context` step writes a normalized summary for trace/debug and future
  rule-pack compilation;
- missing linked entities are recorded as `missingContext`, not treated as a hard
  run failure;
- `PostBrief` remains the approved fabula artifact and must not absorb slot,
  candidate, signal, topic, fabula, or publisher-rule fields.

## Consequences

- Slice 2.4 implements `Draft Run Contract and Queue Foundation`.
- The existing `/api/drafts/generate` endpoint remains a compatibility path during
  transition, not the long-term drafting interface.
- Future prompt work must be split by step: context/rule pack, material plan, draft
  strategy, candidate generation, validation, and revision.
- Context building is a separate application boundary. Backend provider steps must use
  the normalized `DraftRunContext`/context step artifact rather than re-reading
  frontend workspace state.
- Validators become first-class application/domain concepts, not hidden prompt text.
- Frontend drafting UX should track queued/running/completed states and show named
  steps rather than a single loading state.
- Backend architecture smoke must evolve with queue modules and continue to enforce
  provider-free domain boundaries.

## Alternatives considered

- **Make the current prompt larger.** Rejected because the rule set is too large and
  internally diverse. Larger prompts would reduce debuggability and make failures
  harder to attribute.
- **Use one synchronous OpenRouter call with a self-review instruction.** Rejected
  because self-review inside one call cannot provide durable step trace, retry control,
  validator ownership, or cancellation/status semantics.
- **Start with `langgraph-document-ai-platform` import integration first.** Deferred
  because the immediate product risk is draft orchestration. Document workflows can
  reuse the same queued-run pattern later.
- **Use FastAPI background tasks only.** Rejected for real drafting because process-local
  background execution is not durable enough for long AI workflows, retries, or status
  recovery.
