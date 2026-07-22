# Use Isolated Remote Docker for the Test Runtime

Date: 2026-07-22

## Status

Accepted

## Context

The Glavred test and live-proof workload no longer fits reliably on the developer
workstation. The available `flowise` host has enough CPU, memory, and disk capacity,
but it also hosts Power Web. A global Docker context, shared ports, shared volumes, or
an unrestricted cleanup command could therefore disrupt an unrelated project.

Glavred also needs provider-backed checks. Copying `.env`, interpolating secrets into
Compose output, or placing an API token in container environment variables would make
the remote runtime an unacceptable secret boundary.

## Decision

Repository editing, Git, roadmap rendering, and document generation remain local.
Docker builds, automated tests, browser acceptance, and provider-backed live proofs run
on the Docker daemon reachable as `ssh://flowise`.

The checked-in owner is `scripts/remote_docker_runtime.py`. It always supplies the
explicit Docker host, Compose project `glavred`, base Compose file, and remote override.
It validates SSH resolution, port ownership, runtime inputs, and a remote operation
lock before stateful work. It never changes the global Docker context, prunes globally,
or addresses resources belonging to another Compose project.

The remote override binds the UI and API to server loopback ports `5176` and `8000`,
does not publish Redis, and uses Glavred-owned named volumes. Browser access from the
workstation uses an SSH tunnel. The ephemeral QA container uses host networking only
so its browser can exercise those loopback bindings; product services remain on the
project network and QA does not address reserved Power Web ports.

Deterministic tests use a clean `qa` service with no live env or secret mounts.
Authenticated, persisted-state, and provider-backed checks use `qa-live`; its runtime
volume is read-only and its secret mounts remain file-backed and read-only. A saved
fresh live run may be reused only to repeat post-run browser and trace acceptance.

The local `.env` is reduced to a generated ignored runtime env. Allowlisted secret
values are transferred over SSH stdin into `/opt/glavred-secrets` by atomic replacement,
with directory mode `0700` and file mode `0600`. Containers receive read-only files and
load them through `OPENROUTER_API_KEY_FILE` and
`GLAVRED_DEV_AUTH_PASSWORD_FILE`; values are not placed in container environment.

## Consequences

- A local test run is useful for diagnosis but is not acceptance evidence.
- Local Docker is used only when the user explicitly requests it.
- Current uncommitted source is included in the remote Docker build context, so a
  commit is not required before testing.
- Stateful remote commands serialize through a Glavred-specific lock.
- Power Web ports, containers, networks, volumes, and source directory are outside the
  Glavred runtime owner's authority.
- Rootless Docker and a dedicated non-root remote user remain future hardening work.

## Pipeline Impact

DraftRun and RadarRun AS IS are unchanged. This decision changes only the execution
environment used to build, test, inspect, and prove those pipelines; runtime order,
provider contracts, trace semantics, HTTP API, and SQLite schema are unchanged.
