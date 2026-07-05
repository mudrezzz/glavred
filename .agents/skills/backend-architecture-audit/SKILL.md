---
name: backend-architecture-audit
description: Use before backend architecture/refactor slices, when backend package quality is questioned, or when a backend change may introduce new public helper sprawl, procedural bounded packages, raw dict contracts, provider-heavy drift, or legacy-shim behavior. Produces a repo-grounded audit, separates known debt from new debt, and proposes tracker-backed repair slices.
---

# Backend Architecture Audit Skill

## Goal

Run a repeatable backend architecture audit so structural debt is found by process,
not by manual frustration after a slice is implemented.

This skill is diagnostic and planning-first. Do not refactor code during the audit
unless the user explicitly asks to implement a selected repair slice.

## Required Reads

1. `AGENTS.md`.
2. Roadmap tracker:
   - `python -m backend.app.roadmap next`
   - `python -m backend.app.roadmap list --status Ready`
   - `python -m backend.app.roadmap show <active-or-next-slice-id>`
3. Backend architecture docs:
   - `docs/architecture/BACKEND_ARCHITECTURE_AS_IS.md`
   - `docs/architecture/BACKEND_ARCHITECTURE_TARGET.md`
   - `docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md`
   - `docs/developer/BACKEND_MODULE_TEMPLATE.md`
   - `backend/app/drafting/README.md`
   - `backend/app/drafting/DRAFTING_BACKEND_COMPONENT_MAP.md`
4. Relevant ADRs:
   - `docs/adr/2026-07-03-backend-bounded-contexts-and-operation-contracts.md`
   - `docs/adr/2026-07-05-draftrun-legacy-surface-oop-migration.md`
   - backend architecture audit ADR when present.
5. Debt ledger when present:
   - `docs/architecture/backend-architecture-debt-ledger.json`

## Audit Workflow

1. Run the automated audit command:
   - `python scripts/backend-architecture-audit.py --format json`
   - `python scripts/backend-architecture-audit.py --format markdown`
   - `python scripts/backend-architecture-audit.py --format json --ledger docs/architecture/backend-architecture-debt-ledger.json --fail-on-unledgered high`
2. If the command is not available yet, run a temporary AST scan for:
   - public top-level functions;
   - large modules;
   - bounded modules with many public helpers;
   - modules with repeated `*_prompts`, `*_parser`, `*_audit`, `*_payloads`, or
     `deterministic_*` procedural surfaces;
   - raw `.complete_json(` usage outside bounded adapters;
   - raw `dict[str, Any]` result contracts crossing service boundaries;
   - behavior inside migrated thin shims;
   - API/application/domain/infrastructure dependency direction risks.
3. Compare findings with `docs/architecture/backend-architecture-debt-ledger.json`:
   - known debt: already listed with owner, severity, repair slice, and guardrail;
   - changed debt: listed but severity/count/surface changed;
   - new debt: not listed and must become a ledger entry or immediate fix;
   - unledgered `critical` / `high` findings fail the `fail-on-unledgered high`
     command and therefore fail `npm run test:architecture`.
4. For each high-severity finding, identify the target owner shape:
   - service;
   - policy;
   - component;
   - DTO/value contract;
   - private helper;
   - compatibility shim;
   - delete-after-migration.
5. Propose the smallest tracker-backed repair slice or confirm the existing slice
   that owns the debt.

## Smell Classes

- `publicHelperSprawl`: public top-level functions in bounded application packages.
- `proceduralBoundedPackage`: a migrated package still mirrors old flat file naming
  and helper style.
- `godService`: one class owns orchestration, provider calls, parsing, trace mapping,
  and fallback decisions.
- `rawDictContract`: raw dict result/request surfaces where a typed DTO or envelope
  is expected.
- `providerBoundaryLeak`: raw provider calls, raw provider errors, or provider SDK
  objects outside infrastructure/bounded adapters.
- `shimBehavior`: migrated thin shim contains behavior, class definitions, provider
  calls, fallback logic, or trace mutation.
- `dependencyDirectionRisk`: API/domain/application/infrastructure imports violate
  the documented direction.
- `testMirrorsBadArchitecture`: tests import legacy/procedural owners instead of
  canonical package owners.

## Output

Answer in Russian unless asked otherwise.

Include:

- short verdict;
- new vs known debt counts;
- top findings by severity with file paths;
- affected packages and target owners;
- exact tracker slice that should repair each cluster;
- whether current `npm run test:architecture` covers the issue;
- recommended next slice.

## Guardrails

- A migrated thin shim is never a behavior owner.
- New DraftRun code belongs under `backend/app/drafting`; new upstream/radar/search
  code belongs under `backend/app/upstream`.
- Provider-heavy code must follow the Provider-Heavy Review Checklist in
  `docs/developer/BACKEND_MODULE_TEMPLATE.md`.
- If a smell is not covered by current smoke rules, propose a smoke or ledger check.
- Do not dismiss public helper sprawl as acceptable just because tests pass.
