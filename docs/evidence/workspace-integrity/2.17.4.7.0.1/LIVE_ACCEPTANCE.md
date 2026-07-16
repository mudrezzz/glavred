# Connected Signals UI acceptance

- Slice: `2.17.4.7.0.1`
- Date: `2026-07-16`
- Project: `project-ai-design-patterns`
- Run: `radar-run-ai-pattern-radar-industrial-cases-1`

## User path

The acceptance scenario used the real Docker frontend and FastAPI backend. It logged
in through the user interface, asserted an authenticated `/api/users/me` response,
opened the project Signals page, started the industrial AI radar, waited for the live
provider-backed result, confirmed persistence in the backend workspace, and opened
the technical trace.

Authentication and backend-session checks passed for both supported development
hosts:

- `http://127.0.0.1:5176/`
- `http://localhost:5176/`

No `localFallback` path was accepted.

## Runtime result

| Check | Result |
| --- | --- |
| RadarRun status | `succeeded` |
| Signal extraction | `succeeded` |
| Found materials | `2` |
| Source signals | `2` |
| Material decision coverage | complete |
| Unresolved evidence references | `0` |
| Grounding violations | `0` |
| Downstream artifacts | none |
| Provider input tokens | `3020` |
| Provider output tokens | `792` |
| Serialized message size | `12742 / 16000` chars |
| Workspace integrity after run | `0` issues |
| Portfolio/DraftRun/AiRun SQLite | `ok / ok / ok` |

The benchmark verdict is `warning` because the live search budget did not execute
all required search families. This is an existing Radar coverage limitation and not
a UTF-8, persistence, layout, or signal-extraction regression.

## Visual proof

Automated screenshots are written to the ignored directory
`var/visual-proof/2.17.4.7.0.1/live/`. The desktop Signals screenshot confirms clean
Cyrillic text, bounded two-column geometry, readable radar rules, and bounded insight
preview. The trace screenshot confirms that the saved run is available from the
workspace and that its materials and signals are visible.

The connected visual suite also checks page-level horizontal overflow at widths
`390`, `1180`, `1440`, `1904`, and `2048` pixels and fails on authentication errors,
CORS failures, backend unavailability, or local fallback.
