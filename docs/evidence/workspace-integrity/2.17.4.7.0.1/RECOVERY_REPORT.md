# Workspace UTF-8 recovery report

- Slice: `2.17.4.7.0.1`
- Date: `2026-07-16`
- Affected project: `project-ai-design-patterns`
- SQLite structural integrity before recovery: `ok`
- Blocking text issues in latest affected snapshot: `1817`
- Affected project snapshots preserved in backup: `50`
- Affected history range: `2026-07-02T14:03:22.822964Z` to `2026-07-16T13:00:22.662869Z`
- Total snapshots preserved in backup: `74`
- Backup size: `82432000` bytes
- Backup SHA-256: `4aa7049af653d3c253224851c547f1de729b8974d210d3b2813ed9657570f6dd`
- Ignored backup location: `var/recovery/workspace-utf8-20260716-162604/`

## Recovery decision

No damaged string was decoded automatically. The active SQLite was rebuilt
atomically. Users, projects, memberships, and the latest clean snapshots of the
unaffected projects were preserved. `project-ai-design-patterns` received a minimal
clean seed snapshot which the frontend expands from the canonical demo workspace.

Preserved projects:

- `project-glavred-blog`
- `project-kasha-iz-topora`

Reset project:

- `project-ai-design-patterns`

## Result

- Recovered SQLite `pragma integrity_check`: `ok`
- Active workspace blocking issues: `0` for all three projects
- Ten authenticated UTF-8-safe `GET -> PUT` cycles preserved the semantic hash
  `acda48d572b32a128394fe2ffa34e3ecaf4698b22e9d74e66f4e881890d2e5a5`.
- Post-live portfolio, DraftRun, and AiRun SQLite integrity checks: `ok`.
- Damaged snapshots are absent from the active database and remain available only in
  the ignored evidence backup.
- The historical accepted RadarRun evidence remains in `docs/evidence/radar-runs/`;
  its damaged workspace payload was not copied.

## Connected acceptance

The accepted browser proof used the real Docker frontend, FastAPI backend, and
portfolio SQLite. Authentication succeeded through both `127.0.0.1:5176` and
`localhost:5176`; `/api/users/me` returned an authenticated session and no local
fallback was used.

The RadarRun started from the user-facing Signals page:

- Run: `radar-run-ai-pattern-radar-industrial-cases-1`
- Retrieval status: `succeeded`
- Signal extraction status: `succeeded`
- Found materials: `2`
- Source signals: `2`
- UI persistence: confirmed
- Technical trace: opened from the saved workspace
- Active workspace integrity issues after the run: `0`

The extraction diagnostics reported complete material-decision coverage, zero
unresolved evidence references, zero grounding violations, and no downstream
`PostCandidate`, plan-slot, or DraftRun creation. The accepted provider attempt used
`3020` input tokens and `792` output tokens; serialized messages used `12742` of the
`16000` character cap.

`RADAR_RUN_PIPELINE_AS_IS.md` is unchanged because recovery changed portfolio
persistence and rendering, not RadarRun execution semantics.
