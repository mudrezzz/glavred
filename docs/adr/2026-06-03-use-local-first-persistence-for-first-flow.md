# ADR: Use Local-First Persistence for First Flow

## Status

Accepted

## Context

The first implementation slice needs a workspace that can preserve the author's
editorial model, source signal, insight card, plan item, and approved post brief. A
backend would add decisions about hosting, auth, accounts, sync, migrations, and data
ownership before the first product flow exists.

## Decision

Slice 0.4 will use a local-first workspace store backed by browser `localStorage`, with
fixtures as the initial demo state. The architecture will define a `WorkspaceStore`
interface so backend persistence can replace the adapter later.

## Consequences

- The first product flow can work without backend, auth, or network dependencies.
- The approved brief can survive page reloads.
- Domain and application code must not call browser storage directly; storage remains
  an infrastructure adapter.
- Multi-device sync, collaboration, account isolation, and durable production storage
  are deferred.

## Alternatives considered

- Mock-only fixtures: fastest, but the product would not preserve user work.
- Backend now: more production-like, but too much infrastructure before the product
  flow is validated.
