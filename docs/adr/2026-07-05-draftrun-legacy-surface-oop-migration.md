# ADR: DraftRun Legacy Surface OOP Migration

Date: 2026-07-05

Status: Accepted

## Context

The legacy DraftRun runtime still has a large flat surface under
`backend/app/application`: 110 `draft_*.py` modules and 13 `deterministic_*.py`
modules. Some files already contain cohesive service classes, but many expose
public top-level helpers for behavior, payload mapping, fallback rules, parser
logic, and trace assembly.

Moving those files into `backend/app/drafting` without changing ownership would
only rename the same procedural surface. The migration needs a decision-complete
map before slices `2.17.4.6.0.4` and `2.17.4.6.0.5` move runtime code.

## Decision

Create a `Legacy DraftRun Surface` inventory under
`backend/app/drafting/application/migration/legacy_surface_inventory.py`.

Each legacy module gets:

- `cluster`: one closed DraftRun migration cluster.
- `targetPackage`: the bounded-context package that should own the behavior.
- `moduleDisposition`: one of `service`, `policy`, `component`, `dto`,
  `privateHelper`, `compatibilityShim`, or `deleteAfterMigration`.
- `targetOwner`: the intended service, policy, component, DTO owner, or shim.
- `migrationSlice`: the slice expected to consume the migration decision.
- `publicHelpers`: every public top-level helper with `publicHelperDisposition`,
  target visibility, and rationale.

The rule is ownership clarity, not class boilerplate. Behavior with collaborators,
trace semantics, provider semantics, state, or multiple callers becomes a method on
a service, policy, or component. Pure provider-free DTO/factory helpers can remain
package-level only when they are small, documented, and explicitly listed.
Legacy `deterministic_*` modules must move under named fallback policy/service
owners inside `backend/app/drafting`; they must not become a parallel flat package.

Future migrations follow a strict `no cosmetic package moves` rule: moving a file
without reducing public helper sprawl, documenting ownership, or turning behavior
into a role-owned class/policy/component is not accepted.

## Consequences

Architecture smoke now fails when:

- a new flat `draft_*` or `deterministic_*` module appears outside the allowlist;
- an existing legacy module is missing from the inventory;
- a public top-level function is missing from the inventory;
- inventory entries contain unknown clusters, missing owners, or missing migration
  slices;
- docs stop mentioning the Legacy DraftRun Surface migration rules.

Runtime behavior is unchanged in this slice. The inventory is migration governance
for the next runtime slices.
