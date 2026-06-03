# ADR 0001: Use React, Vite, and TypeScript for the Foundation

## Status

Accepted

## Context

The repository contains a frontend design handoff with React-style reference screens for
the Glavred app and marketing site. The primary product brief, `glavred.md`, exists but
is currently empty, so the first slice should avoid irreversible product architecture.

## Decision

Use React + Vite + TypeScript for the initial runnable application baseline.

## Consequences

- The project can run locally with a standard frontend toolchain.
- Future UI work can port the reference screens with minimal conceptual friction.
- TypeScript allows the domain baseline to be tested independently from React.
- Backend, persistence, AI provider, and deployment decisions remain deferred until the
  source brief is available.
