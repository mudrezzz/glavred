# Remote Docker Runtime Proof

Date: 2026-07-22

Slice: `2.17.4.7.1.0.1`

## Runtime

- SSH target: `flowise` resolved to `root@213.148.13.45:22`.
- Docker host: `ssh://flowise`.
- Compose project: `glavred`.
- Host capacity at acceptance: 4 CPU, 16,770,080,768 bytes RAM, more than 10 GiB
  free under `/var/lib/docker`.
- Frontend: `127.0.0.1:5176` only.
- API: `127.0.0.1:8000` only.
- Redis: internal port `6379`; no host publication.
- Named volumes: `glavred_runtime`, `glavred_artifacts`.
- Celery proof: one worker node returned `pong` before and after the restart cycle.

The workstation reached HTTP `200` from the frontend and a healthy API only while
the documented SSH tunnel was active. Direct TCP connections to public ports `5176`
and `8000` failed.

## Source And Secrets

- A temporary untracked probe was present in the QA image, proving that the current
  local tree, not only committed Git state, was sent as build context. The probe was
  removed locally after verification.
- `/app/.env` was absent from the runtime image.
- `OPENROUTER_API_KEY` was absent from the container environment.
- `/run/secrets/openrouter_api_key` existed as a read-only mount; the host source had
  mode `0600` and `/opt/glavred-secrets` had mode `0700`.
- Secret values were transferred through SSH stdin and were not printed by the CLI,
  test output, logs, or this evidence file.
- Unknown secret-like settings and credential-bearing URLs are rejected by the env
  sanitizer before containers are started.

## Isolation

Power Web was captured before and after the complete Glavred build, test, live,
`down`, and `up` cycle.

- Container IDs and stopped statuses remained unchanged.
- Network remained `739953be226b|power-web-os_default`.
- `/opt/power-web-os/docker-compose.yml` SHA-256 remained
  `9ff1fd7800579fe170ae5ae1bdb5effad4766657757d7cc53271014845d4dc14`.
- Reserved bindings `5173`, `8001`, and `127.0.0.1:6380` were not changed.

`down` removed only Glavred containers and `glavred_default`. Both Glavred volumes
remained. The portfolio SQLite SHA-256 before and after `down/up` was identical:
`c0b43168719aa4787b11645921b9a99fbb8231a0289f001cabe0c37debee070f`.

## Automated Proof

- Remote runtime and file-secret tests: 25 passed.
- Backend regression: 497 passed, one dependency deprecation warning.
- Frontend regression: 330 passed.
- Architecture smoke: passed.
- Design-system smoke: passed.
- Connected Signals browser smoke: passed at 390, 1180, 1440, 1904, and 2048 px.
- Production TypeScript/Vite build: passed.
- Workspace integrity: three active project snapshots, zero blocking issues.
- Backend architecture audit: no new unledgered high-severity finding.
- Auth session smoke: logout, account switching, and dashboard logout passed against
  the real remote FastAPI session.

## Provider-Backed Proof

Accepted RadarRun: `radar-run-ai-pattern-radar-industrial-cases-1`.

- Run status: `succeeded`.
- Source signals: 3.
- Signal scoring: `succeeded`, one accepted scoring attempt.
- Recommendations: three `reviewWithCaution`.
- OpenRouter usage: 4,579 input tokens, 2,004 output tokens, 6,583 total tokens.
- Scoring budget respected: yes.
- Unresolved setting refs: 0.
- Unresolved evidence refs: 0.
- Human review: one signal approved, revision 1, one immutable review event.
- Manual rescore: revision 2.
- Source URL, extraction trace, scoring trace, relationship report, and hidden raw
  evidence handles were verified in the browser.
- Page-level overflow was absent at all five acceptance widths.

A later fresh provider attempt returned zero signals and was classified as
inconclusive rather than used to hide the accepted run. The browser/trace assertions
were repeated against the already persisted accepted run with `--reuse-live-run`.
Ignored screenshots and raw QA artifacts are stored under
`var/remote-proof/2.17.4.7.1.0.1` and are not committed.

## Pipeline Impact

DraftRun and RadarRun AS IS are unchanged. The slice changes test execution,
isolation, secret transport, and acceptance workflow, not pipeline order, provider
contracts, trace semantics, HTTP API, or SQLite schema.
