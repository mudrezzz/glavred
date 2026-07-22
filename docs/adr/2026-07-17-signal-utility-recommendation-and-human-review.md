# ADR: Signal Utility Recommendation and Human Review Are Separate Contracts

Date: 2026-07-17
Status: Accepted

## Context

The old Signals UI used a TypeScript keyword heuristic as if it were a project-level
editorial verdict. Missing phrase overlap could reject a strong industrial case, the
same generic explanation appeared for different filters, and automated evaluation was
mixed with the editor's decision.

## Decision

Project utility is evaluated in `backend.app.upstream` through this chain:

`ProjectEditorialOpportunityProfile -> SignalUtilityDossier -> provider evaluation -> deterministic decision policy -> SignalUtilityReport`.

The provider supplies semantic dimension evidence. Backend policy validates signal,
setting, material, and fragment identities and owns the terminal categorical
recommendation. It cannot change the human review status.

Human review is a separate authenticated, reversible, optimistic-concurrency
lifecycle. Correction may change only editorial title, summary, and author comment.
Evidence, quotations, mechanism, outcome, limitations, and provenance are immutable.

All provider attempts use operation-owned dossiers, direct current-call budgets, and
post-construction message guards. Manual rescore reuses stored signals/materials and
does not repeat search, URL reading, or extraction.

## Consequences

- `notRecommended` requires a proven conflict with an active blocking criterion;
  `notProven` is not a rejection.
- Utility recommendations use categories instead of a pseudo-precise percentage.
- Legacy client heuristic results remain visible only as non-canonical history and
  legacy signals require explicit re-extraction.
- A positive recommendation does not create `PostCandidate`, plan, or DraftRun.
- Search-to-filter alignment and useful-yield diagnostics remain Slice
  `2.17.4.7.1.1`.
