# ADR: Editorial Settings Are Structured Rules

## Status

Accepted

## Context

The product premise requires validator-backed author position, topics, style, goals,
and constraints. Large freeform textareas hide the individual units that need to be
checked, scored, edited, paused, or linked to evidence.

## Decision

Important editorial settings are modeled as structured rules. Each rule has an id,
group, title, statement, status, and optional evidence link. UI blocks such as author,
audience, position, style, goals, and forbidden topics render lists of rules, not one
large text field.

## Consequences

Validators can evaluate specific rules. Authors can add, pause, edit, and delete one
constraint without rewriting a whole blob. The legacy `EditorialModel` fields remain
only for compatibility until downstream services move fully to structured entities.

## Alternatives considered

- Keep one textarea per settings block. Rejected because it blocks validation and
  evidence-level editing.
- Generate rules only at AI runtime. Rejected because the author must see and own the
  rules before AI acts on them.
