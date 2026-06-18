# ADR: AI run observability stores local trace

- Status: Accepted
- Date: 2026-06-18

## Context

Glavred now has the first backend provider path for draft generation. During local
debugging the team must be able to answer three questions without guessing:

- what prompt/messages were sent;
- what provider or fallback returned;
- why the user sees the current draft in the UI.

The workspace remains local-first and should not become a full prompt/debug log.

## Decision

Every backend provider execution slice must include AI run observability.

For draft generation, backend `AiRun` records store a full local sanitized trace:

- request capability input;
- prompt messages;
- provider request metadata such as model, temperature, and response format;
- generated draft title/body/version/status;
- provider response id/model/usage when available;
- fallback metadata and safe error context.

The frontend stores only lightweight generation metadata on the produced artifact:
source, `AiRun` id, provider, model, fallback flag, timestamp, and optional error.

Secrets are forbidden in audit records and API responses. This includes API keys,
authorization headers, secret environment values, and absolute local paths.

## Consequences

- `GET /api/ai-runs/{id}` is the primary local debugging surface for provider runs.
- Provider adapters must expose enough metadata to build a useful audit trace.
- Prompt construction stays in application code; API handlers stay thin and
  infrastructure adapters only execute provider calls.
- Before public or hosted production use, Glavred needs retention and redaction policy
  for AI run traces.
