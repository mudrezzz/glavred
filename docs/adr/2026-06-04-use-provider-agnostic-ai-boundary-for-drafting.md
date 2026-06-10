# ADR: Use Provider-Agnostic AI Boundary for Drafting

## Status

Accepted

## Context

Glavred now has a complete local-first editorial loop from source signal to captured
editorial learning note. The next product circle should allow deterministic services
to be replaced by AI-assisted services without breaking the current workflow, tests,
or demo.

The first AI-assisted scenario is drafting from an approved `PostBrief`. This is the
most visible replacement target because the existing flow already has human approval
before drafting and after final text review.

## Decision

AI provider integration is an application and infrastructure concern.

React components must not call provider APIs. Domain objects must not import provider
SDKs, browser APIs, secrets, or network clients. Application services will own the
choice between deterministic fallback and an AI drafting adapter. Infrastructure
adapters will own provider-specific API calls when a real provider is introduced.

The first provider boundary is drafting:

- input: approved `PostBrief`, `EditorialModel`, and optional previous
  `EditorialLearningNote`;
- output: a `PostDraft`-compatible result;
- default fallback: deterministic `createPostDraft`;
- provider strategy: provider-agnostic until the first implementation slice chooses a
  concrete provider.

## Consequences

- The current local-first demo remains deterministic and offline-capable.
- Future AI-assisted drafting can be tested with mock adapters before real provider
  calls.
- Provider failures can fall back to deterministic drafting without blocking the
  editorial workflow.
- Prompt templates and provider run metadata become application-level contracts, not
  UI concerns.
- Provider choice remains deferred, so the first implementation may need a small
  follow-up decision once API access is selected.

## Alternatives considered

- Call the provider directly from React: rejected because it couples UI, secrets,
  network behavior, and prompt construction.
- Add provider types to the domain model: rejected because domain objects should stay
  provider-free and durable.
- Choose a concrete provider now: deferred because Slice 0.8 is an architecture
  baseline and must not add API keys, SDKs, or real calls.
- Replace all deterministic services at once: rejected because drafting is the smallest
  useful AI replacement target with clear HITL boundaries.
