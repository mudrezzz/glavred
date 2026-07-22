# ADR: Workspace text integrity and connected UI acceptance

- Status: Accepted
- Date: 2026-07-16
- Slice: `2.17.4.7.0.1`

## Context

The saved workspace for `project-ai-design-patterns` was structurally valid JSON in
a structurally valid SQLite database, but many strings had been repeatedly decoded
and encoded through an unsafe PowerShell full-workspace roundtrip. The application
then saved the damaged JSON again. Fixture-only visual checks opened the local demo
after failed backend authentication, so they did not exercise the persisted data and
did not expose the page-width failure caused by the expanded text.

## Decision

1. The portfolio application owns `WorkspaceTextIntegrityInspector` and
   `WorkspaceIntegrityPolicy` as read-before-render and write-before-persist gates.
2. The policy reports paths, reason codes, sizes, and hashes only. It never attempts
   semantic text repair and never returns the damaged values in diagnostics.
3. Corrupt writes return `422 workspace-text-integrity-failed`; corrupt stored
   snapshots return controlled `409` and are not rendered as ordinary workspaces.
4. The browser keeps integrity failure separate from backend unavailability. It
   stops autosave and does not silently replace corrupt backend data with local demo.
5. Full workspace roundtrips use the UTF-8-safe Python client and semantic hashes.
   PowerShell `Invoke-RestMethod` is not an approved read-modify-write path.
6. Persisted workspace UI changes require a browser check with real FastAPI,
   authenticated session, and temporary SQLite. `401`, CORS failure, unavailable
   backend, or `localFallback` invalidates the check.
7. Long valid content is constrained by layout ownership: zero-minimum grid tracks,
   wrapping, bounded previews, and local scrolling. Page-level overflow is not hidden.

## Consequences

- Successful workspace contracts and the SQLite schema remain unchanged.
- Recovery preserves the corrupt database as evidence and atomically builds a clean
  working database rather than guessing the original text.
- Visual gates take longer because one scenario starts a connected backend, but they
  now prove the actual persistence boundary.
- `RADAR_RUN_PIPELINE_AS_IS.md` is unchanged: RadarRun semantics did not change.
