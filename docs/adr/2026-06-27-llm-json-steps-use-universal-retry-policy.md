# ADR: LLM JSON steps use a universal retry policy

## Status

Accepted

## Context

Glavred increasingly uses LLM calls that must return structured JSON: research
planning, evidence synthesis, evidence interpretation, material planning, rhetorical
plans, candidate generation, validation, editorial critique, alternative-angle routing,
pairwise ranking, and directed revision.

Several slices already implemented local retry behavior for selected steps, but live
DraftRun diagnostics showed that the rule is not universal yet. A malformed provider
response can still disable important work, for example critic or alternative-angle
candidate generation, after a single JSON parse error.

That is not acceptable as the project grows. The issue is not specific to one
DraftRun pipeline. Any future workflow that asks an LLM for JSON needs the same
discipline:

1. try the selected role model;
2. retry with a stricter repair prompt that includes the parse/shape error;
3. try the configured backup model when available and distinct;
4. only then use a domain-safe deterministic fallback, or mark the step `not-run` /
   `failed` if no honest fallback exists.

## Decision

Every LLM call in Glavred that requires JSON output must use a shared
application-level JSON retry policy.

The required attempt sequence is:

`primary -> primary-repair -> optional backup -> fallback | not-run | failed`

Where:

- `primary` uses the role-selected model for that step;
- `primary-repair` uses the same role-selected model with a stricter repair prompt;
- `backup` uses `OPENROUTER_BACKUP_MODEL` only when it is configured and not the same
  effective model;
- `fallback` is allowed only when the owning domain has a deterministic, honest,
  traceable result;
- `not-run` or `failed` must be used instead of fake findings or fake evidence when
  deterministic fallback would misrepresent the result.

Each attempt must create or update sanitized audit trace:

- child `AiRun` id when a provider call was attempted;
- attempt label;
- model role;
- selected model;
- model selection source;
- backup marker;
- status;
- parse/validation error;
- safe provider metadata.

The retry engine can be shared, but each application service owns its required JSON
schema, parser/normalizer, validation criteria, and repair prompt details.

## Consequences

- Direct single-call-then-fallback JSON parsing is not allowed for new LLM JSON steps.
- Existing partial retry implementations converged on the shared policy in the
  dedicated repair slice `2.15.6.3: Model Stabilization and Universal JSON Retry
  Repair`; new structured-provider steps must not reintroduce one-call JSON parsing.
- Architecture smoke should check for bypasses where practical. When static detection
  is brittle, the developer checklist must explicitly require the retry policy for new
  JSON-producing LLM services.
- Trace analysis becomes more reliable: a failed JSON step can show whether primary,
  repair, and backup attempts were actually exhausted.
- This rule applies beyond DraftRun. Future import, document-analysis, release,
  analytics, or author-memory workflows must follow the same JSON attempt discipline
  when they request structured provider output.

## Alternatives considered

- Keep retry policy per service. Rejected: this already led to uneven behavior and
  hard-to-diagnose single-step failures.
- Always fallback deterministically after one malformed response. Rejected:
  deterministic fallbacks can hide provider/prompt defects and are not honest for
  critic, review, evidence, or alternative-angle work.
- Retry indefinitely until valid JSON appears. Rejected: retries need bounded cost,
  visible trace, and clear fallback/failure semantics.
- Make all JSON repair use the backup model immediately. Rejected: the role model
  should first get one repair attempt because many failures are formatting errors, not
  model incapability.
