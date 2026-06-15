# ADR: Feature Entrypoints Stay Thin and Domain Transitions Are Role-Owned

## Status

Accepted

## Context

The project has already moved away from a single `App.tsx` god file, but several
feature entrypoints and domain transition files can still grow into the same problem
inside smaller folders. React components also do not become more maintainable just by
using classes: the useful OOP principles here are role ownership, explicit boundaries,
single responsibility, and stable public interfaces.

## Decision

- React UI uses composition and feature-local modules rather than inheritance-heavy
  class components.
- A feature entrypoint composes tabs, panels, editors, and cards; it must not own all
  internal UI details.
- Domain transitions are grouped by business role, not by a catch-all aggregate file:
  rules, validation, catalog/matrix transitions, planning, signals, imports, release,
  and analytics each own their own modules.
- Compatibility barrels may re-export existing public APIs during refactoring, but new
  logic should be added to the role-owned module first.
- Architecture smoke tests must track file-size limits and required module boundaries.
- Comments are expected where they explain non-obvious domain invariants, compatibility
  behavior, or trade-offs. Comments should not restate obvious JSX or assignments.

## Consequences

- New feature work has an obvious target file instead of defaulting to an entrypoint.
- The codebase stays closer to OOP/SRP without forcing React into class-based UI.
- Refactoring slices can remain behavior-preserving because public entrypoints and
  compatibility barrels stay stable.
- Architecture tests become part of the definition of done for future slices.

## Alternatives considered

- **Class-based React components**: rejected because React fits composition and hooks
  better here, and classes would not solve ownership by themselves.
- **One file per tiny function**: rejected because it creates boilerplate and weakens
  locality.
- **Keep large feature files until product work resumes**: rejected because adding
  post candidates on top of existing large files would recreate the maintainability
  problem we just fixed at the app-shell level.
