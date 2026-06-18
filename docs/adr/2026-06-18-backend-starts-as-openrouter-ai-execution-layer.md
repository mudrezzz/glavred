# ADR: Backend starts as an OpenRouter AI execution layer

## Status

Accepted

## Context

Glavred has enough local-first product surface to start proving real AI-assisted
execution. The risk is adding a backend as a broad boilerplate shell or wiring LLM
calls directly into React. The project also needs to use `langgraph-document-ai-platform`
without letting that library shape the frontend, domain model, or storage contract.

The backend must follow the same architecture discipline already applied to the
frontend: explicit ownership, small modules, OOP/SRP boundaries, file-size guardrails,
and architecture smoke coverage.

## Decision

The backend will start as an AI execution layer, not as a full replacement for the
local workspace.

The default LLM provider is OpenRouter. Provider keys and runtime settings live in
local `.env` files and are documented in `.env.example`. Tokens are never committed.

The backend architecture will use a thin HTTP API over explicit application services:

- domain objects and policies stay provider-free;
- application services orchestrate use cases and own request/result contracts;
- infrastructure adapters own OpenRouter, database, queue, file, and
  `langgraph-document-ai-platform` calls;
- API handlers stay thin and do not contain prompt, persistence, or workflow logic;
- frontend code never calls OpenRouter, LLM SDKs, prompt builders, or
  `langgraph-document-ai-platform` directly.

Backend slices must avoid boilerplate. A module, class, or adapter is added only when
it has an immediate role in a closed slice. Large files and god services are not
acceptable; backend file-size and dependency rules must be added to architecture smoke
as soon as the backend folder appears.

The first backend implementation track is:

1. FastAPI backend foundation and OpenRouter environment validation.
2. AI run contract and persistence for auditable calls.
3. First real OpenRouter run behind one selected editorial use case.
4. `langgraph-document-ai-platform` import through a dedicated adapter/facade.

## Consequences

Glavred can introduce real LLM behavior without breaking the local-first demo or
turning provider calls into UI code. OpenRouter becomes the practical default provider,
while the domain and application contracts remain provider-agnostic.

The backend will have its own architecture tests and smoke rules. Every backend slice
must update SAO/ADR/workflow docs when it adds a new architecture rule.

The local `.env` file can exist for developer setup, but only `.env.example` is part
of the repository contract.

## Alternatives considered

- Add LLM calls directly to the React/Vite app. Rejected because it exposes keys,
  bypasses orchestration, and weakens HITL/audit boundaries.
- Build a broad backend platform first. Rejected because it creates boilerplate before
  the first real AI use case proves the abstractions.
- Start with a provider-specific OpenRouter domain model. Rejected because provider
  metadata belongs at the infrastructure/application boundary, not in domain objects.
