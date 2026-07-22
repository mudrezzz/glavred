# ADR: Signal criteria and relationships are separate explainable contracts

Date: 2026-07-21
Status: Accepted

## Context

The first signal utility implementation stored traceable dimensions, but the user
interface flattened extraction fields, radar filters, project settings, and system
quality checks into one list. It exposed material and fragment IDs as evidence,
treated non-empty mechanism/outcome strings as proof, and defaulted missing duplicate
analysis to low risk. This made a technically traceable report editorially opaque.

## Decision

Signal evaluation uses four explicit contracts:

1. type-owned signal semantics describe what the source claims and which fields are
   applicable;
2. radar and project criteria snapshot the setting, mode, verdict, explanation, and
   evidence used by the decision;
3. system quality checks report grounding, result support, source posture, freshness,
   and relationship integrity without pretending to be user-configured filters;
4. signal relationships classify duplicate, same-claim, related, corroborating,
   contradictory, distinct, or inconclusive pairs independently from project utility.

Internal handles stay canonical for integrity and replay. User-facing evidence is
resolved to source titles, domains, exact quotations, URLs, and trace links. Missing
proof remains unknown or inconclusive rather than receiving an optimistic default.

Exact duplicate and same-claim records are grouped non-destructively under one
canonical presentation. Related claims remain separate. Relationship classification
reuses the bounded utility provider operation and does not add an unbounded call.

Provider responses use dossier-owned short aliases for signals, criteria, and evidence.
The payload mapper resolves those aliases to persisted handles and rejects unknown,
duplicate, or missing identities. This bounds response size without inferring identity
from order or exposing trace IDs as editorial evidence.

## Consequences

- A criterion can be traced back to the radar or project setting that created it.
- Filter modes have different user verdicts and deterministic effects.
- Capability descriptions cannot masquerade as observed outcomes.
- Source independence must be demonstrated, not inferred from the absence of a known
  vendor name.
- Legacy utility reports and duplicate-risk fields remain readable but are not
  canonical until explicitly recalculated.
- Human review remains separate and source evidence remains immutable.

## Alternatives considered

- Keep the flat dimensions list and improve labels: rejected because origin, mode,
  applicability, and relationship semantics would remain ambiguous.
- Add a separate provider call for semantic deduplication: rejected because it adds
  latency and context growth where the bounded scoring dossier already has the needed
  signal projections.
- Destructively delete duplicate signals: rejected because provenance, replay, and
  human auditability would be lost.
