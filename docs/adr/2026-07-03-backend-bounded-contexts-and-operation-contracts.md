# ADR: Backend bounded contexts and operation contracts

## Status

Accepted

## Context

The backend grew through many useful DraftRun and upstream search slices. The result
is functionally valuable but structurally weak: more than one hundred DraftRun
application modules and dozens of DraftRun domain modules live in flat namespaces,
and the newer upstream radar runner has started to repeat the same pattern.

The next search and drafting features would add even more provider-heavy operations.
Without a package boundary and mechanical guardrails, each new step would invent its
own payload, retry, trace, and failure shape.

## Decision

New backend DraftRun code belongs under `backend/app/drafting`. New upstream
radar/search/signal code belongs under `backend/app/upstream`. Cross-context helpers
belong under `backend/app/shared` only when they are genuinely shared.

Existing flat `draft_*` and `upstream_radar_*` modules are legacy debt. They are
allowlisted temporarily so the product keeps working, but new modules in those flat
locations fail architecture smoke.

Provider-heavy operations must expose application-level operation contracts: typed
input, typed result, attempt trace, safe error, and secret-safe audit payloads. Raw
provider exceptions, headers, tokens, and provider-specific response objects must not
cross the infrastructure boundary.

## Consequences

- Backend package placement becomes an architecture decision, not a naming accident.
- Future DraftRun and radar slices start from a bounded context instead of extending
  flat `application` and `domain` namespaces.
- Architecture smoke can block drift before code review.
- Existing legacy files remain editable during migration, but every new exception
  must be explicit.

## Alternatives considered

- Move all DraftRun modules immediately. Rejected because it would be too risky and
  would mix behavior-preserving migration with provider-heavy product work.
- Keep only line-count limits. Rejected because line limits do not prevent namespace
  sprawl or one-off operation contracts.
- Create broad empty packages first. Rejected unless each package has a documented
  owner and a concrete migration slice.
