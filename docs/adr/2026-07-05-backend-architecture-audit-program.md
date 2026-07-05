# ADR: Backend Architecture Audit Program

## Status

Accepted

## Context

The backend recovery track moved DraftRun code from the flat
`backend/app/application` namespace into bounded packages under
`backend/app/drafting`. That migration stopped new flat legacy growth, but it did
not automatically make every migrated package internally cohesive. Some packages
still expose procedural helper surfaces, repeated `*_prompts` / `*_parser` /
`*_audit` files, raw `dict[str, Any]` seams, and public top-level functions that
are hard to reason about.

Existing architecture smoke catches important hard failures, but it is mostly a
set of explicit rules. It can miss new structural smells that are not yet encoded
as guardrails.

## Decision

We will add a recurring backend architecture audit program before continuing broad
backend feature work.

The program has three parts:

1. An automated backend architecture audit command that scans backend modules for
   ownership, public surface, dependency direction, provider boundaries, raw dict
   seams, migrated-shim behavior, and procedural bounded-package drift.
2. A machine-readable backend architecture debt ledger that records known debt with
   `debtId`, package, module, smell type, severity, owner, target shape,
   allowed-until slice, repair slice, guardrail, and notes.
3. A repo-local `backend-architecture-audit` skill that future agents use to run
   the audit, compare findings with the ledger, distinguish known debt from new
   debt, and propose tracker-backed repair slices.

The audit program is introduced as roadmap Slice `2.17.4.6.0.7`. Cleanup is then
split into focused slices for validation, revision/final-quality, HITL/provider
operations, and the remaining API/application/infrastructure surface.

The implemented command surface is:

```bash
python scripts/backend-architecture-audit.py --format json
python scripts/backend-architecture-audit.py --format markdown
python scripts/backend-architecture-audit.py --format json --ledger docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high
```

The committed artifacts are:

- `scripts/backend-architecture-audit.py`;
- `docs/architecture/backend-architecture-debt-ledger.json`;
- `docs/architecture/BACKEND_ARCHITECTURE_AUDIT.md`.

`npm run test:architecture` executes the ledger-gated command and fails on
unledgered `critical` / `high` findings.

## Consequences

- Passing tests is no longer treated as proof of acceptable backend architecture.
- Known debt can remain temporarily only when it has owner, severity, repair slice,
  and guardrail classification.
- New unclassified backend smells should fail architecture smoke once the audit
  command and ledger are in place.
- Product slices can still proceed, but backend cleanup is now visible and can be
  interleaved deliberately instead of rediscovered manually.

## Alternatives considered

- Refactor only the currently visible `validation` package. Rejected because the
  same smell exists in multiple backend packages and would continue to reappear.
- Add more one-off architecture-smoke regexes. Rejected as insufficient because the
  missing piece is a recurring audit plus known-debt ledger, not only more hardcoded
  fragments.
- Stop all product work until every backend smell is repaired. Rejected because the
  project still needs iterative product progress; the audit ledger lets cleanup and
  feature development be interleaved consciously.
