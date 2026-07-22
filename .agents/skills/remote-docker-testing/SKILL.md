---
name: remote-docker-testing
description: Use for every Glavred test, Docker stack operation, authenticated browser acceptance, or live provider proof. Runs the current local source tree on the isolated flowise remote Docker host, protects Power Web resources, and transfers runtime secrets without printing them.
---

# Remote Docker Testing

## Goal

Run all Glavred validation on `flowise` through the repository-owned remote runtime.
Do not start local Glavred Docker containers unless the user explicitly requests it.

## Required workflow

1. Run `python scripts/remote_docker_runtime.py doctor`.
2. Run `python scripts/remote_docker_runtime.py sync-secrets` before the first build
   or after `.env` changes.
3. Use `build` and `up` through the same CLI.
4. Run tests with `python scripts/remote_docker_runtime.py test --suite <suite>`.
5. Use CLI `exec`, `logs`, and `ps` for diagnostics.
6. Print the SSH tunnel with `tunnel-command`, start it, then open local ports
   `5176` and `8000`.
7. Retrieve proof with `collect-artifacts`.

## Isolation rules

- Always use Docker host `ssh://flowise` and compose project `glavred`.
- Never switch the global Docker context.
- Never run a global prune or an unscoped `docker compose down` on the shared server.
- Do not stop, recreate, or modify the `power-web-os` project.
- Treat ports `5173`, `8001`, and `6380` as reserved for Power Web.
- Glavred uses loopback ports `5176` and `8000`; Redis remains internal.
- Respect the remote runtime lock and never bypass another task.

## Secret rules

- Keep `.env` local and excluded from Docker build context.
- Use `sync-secrets`; never copy `.env` or put secret values in commands.
- Never print interpolated Compose config, container `.Config.Env`, tokens,
  passwords, or secret files.
- Report only secret presence, permissions, and functional provider proof.

## Test ownership

- `backend`: backend pytest.
- `frontend`: Vitest.
- `architecture`: architecture guardrails.
- `design`: design-system checks.
- `visual`: Playwright and connected FastAPI acceptance.
- `smoke`: production TypeScript/Vite build.
- `auth`: authenticated browser flow through the running remote frontend and FastAPI.
- `live-radar`: provider-backed RadarRun and signal utility browser proof.
- `workspace-integrity`: read-only integrity check against the persisted runtime volume.
- `full`: all suites, workspace integrity, and backend architecture audit.

Deterministic suites run in the clean `qa` service without runtime configuration or
secrets. `auth`, `workspace-integrity`, and `live-radar` run in `qa-live`, which gets
only the sanitized runtime env, read-only secret files, and read-only access to the
runtime volume where needed. After a fresh provider-backed run has been persisted,
`test --suite live-radar --reuse-live-run` may repeat a failed browser/trace
acceptance without launching search again. Do not use reuse as a substitute for the
fresh live run required by a slice.

Targeted tests may run through CLI `exec`. A local test result can diagnose a
bootstrap failure but is not acceptance evidence.

## Completion report

Report remote host/project, suites, live run ids, tunnel/browser proof, Power Web
before/after state, secret redaction proof, and every command executed.
