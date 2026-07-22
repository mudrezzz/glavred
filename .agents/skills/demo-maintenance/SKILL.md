---
name: demo-maintenance
description: Use when creating, updating, or validating the project demo. Ensures the demo is realistic, market-relevant, complete enough to show current functionality, and evolves with each user-visible slice.
---

# Demo Maintenance Skill

## Language Rule

When communicating with the user, write in clear Russian. Do not mix English and
Russian in explanatory prose. Keep English only for literal code, commands, file
paths, API fields, identifiers, commit messages, and exact status values.

## Goal

Keep a realistic demo that shows the current working product clearly and convincingly.

Run demo tests and browser acceptance through
`.agents/skills/remote-docker-testing/SKILL.md`; local Docker is not acceptance proof.

## Demo principles

The demo must be:

- realistic
- market-relevant
- runnable
- understandable
- broad enough to show current functionality
- updated as the product grows

Avoid toy scenarios when a real-world scenario is possible.

## Process

1. Inspect current product functionality.
2. Inspect `demo/`.
3. Inspect `ROADMAP.md` for the current slice.
4. Identify whether the slice changes user-visible behavior.
5. Update demo data, scripts, documentation, or flows.
6. Ensure demo instructions are clear.
7. Validate the demo if possible.
   - If the demo uses backend workspace snapshots, validate one authenticated flow
     against real FastAPI. Fixture-only or local-fallback rendering is insufficient.
   - Refresh complete workspaces only through UTF-8-safe Python/application clients,
     never through a PowerShell `Invoke-RestMethod` `GET -> PUT` cycle.

## Demo README should include

- What the demo shows
- How to run it
- Expected result
- Main user flows
- Demo data explanation
- Known limitations

## Completion checklist

Before finishing:

- Demo reflects current functionality.
- Demo remains realistic.
- Demo can be run using documented commands.
- `demo/README.md` is current.
- Any demo gaps are recorded in `ROADMAP.md`.
