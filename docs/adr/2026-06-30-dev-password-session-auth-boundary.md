# ADR: Dev Password Session Auth Boundary

- Status: Accepted
- Date: 2026-06-30

## Context

Glavred now has a SaaS-style portfolio domain: `UserAccount -> ProjectMembership ->
BlogProject -> project-scoped WorkspaceState`. The next backend boundary needs real
session semantics for local development without committing to production SSO, billing,
invites, or organization management.

The old local portfolio remains important: demos and frontend development must still
work when FastAPI is not running.

## Decision

Slice 2.17.3 uses dev-password session auth:

- seeded users log in with email/password;
- the password is read from `GLAVRED_DEV_AUTH_PASSWORD`;
- the backend stores sessions in SQLite and sets an HttpOnly cookie named by
  `GLAVRED_SESSION_COOKIE_NAME`;
- project/workspace endpoints always resolve access through active memberships;
- workspace persistence stores project-scoped JSON snapshots;
- the frontend tries backend first, shows a login panel on `401`, and falls back to
  the local demo portfolio on network/backend unavailability.

This is deliberately not production authentication.

## Consequences

- `author memory`, editorial models, drafts, final decisions, and learning notes stay
  project-scoped and must not leak between projects.
- Backend route handlers remain thin; auth, access checks, seeding, and snapshot
  persistence live in application/infrastructure modules.
- A later slice can replace dev-password auth with a production provider without
  changing the project/workspace ownership model.
- Local demo remains usable without a backend server.

## Out Of Scope

- OAuth/SSO.
- Invite flow, teams, billing, organizations, password reset, MFA.
- Fine-grained persistence for every workspace entity.
- DraftRun schema migration to project/channel/variant ownership.
