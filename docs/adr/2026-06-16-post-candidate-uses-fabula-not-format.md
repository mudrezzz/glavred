# ADR: Post candidate uses fabula, not format

## Status

Accepted

## Context

`PostCandidate` initially stored both `fabulaId` and `format`. In the current product
model the candidate's structural shape is the fabula. Keeping a separate candidate
format duplicated the same concept, made candidate cards harder to scan, and exposed a
misleading editable field. Format still belongs to broadcast grid settings and
`ContentPlanItem`, but not to the candidate concept.

Candidate editing also needs immutable context. The author must see which source
signal and proposed topic produced the candidate before changing editable fields.

## Decision

`PostCandidate` no longer stores `format`.

- Candidate generation produces signal, topic, fabula, audience, value, goal, platform,
  title, thesis, evidence summary, confidence, risks, and approval status.
- Candidate edit supports changing `fabulaId`, but keeps `topicId` and
  `sourceSignalId` readonly in this slice.
- Candidate edit UI shows readonly source signal and topic context.
- Legacy persisted `format` values are dropped during workspace normalization.
- Incompatible topic/fabula choices show a warning but do not block saving.

## Consequences

Candidate concepts are cleaner and do not duplicate fabula as format. Broadcast plan
items may still carry `format` because the calendar/planning layer can later apply
platform-specific format settings independently from candidate assembly.

Architecture smoke tracks the candidate edit context and card helper modules. Domain,
UI, and storage tests enforce the removed candidate `format` field and legacy
normalization behavior.

## Alternatives considered

- Keep `format` but hide it from UI. Rejected because it would keep a misleading
  domain field and persistence contract.
- Replace fabula with format. Rejected because fabula is the richer editorial
  dramaturgy concept and already owns proof/structure rules.
- Make topic editable in the same slice. Rejected to keep this correction small; topic
  editing changes matrix and candidate generation semantics more broadly.
