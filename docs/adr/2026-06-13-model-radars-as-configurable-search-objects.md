# ADR: Model Radars as Configurable Search Objects

## Status

Accepted

## Context

`Сигналы` must not treat a radar as a passive source card. In the product model, a
radar is a configurable search procedure that finds fuel for future posts.

The author needs to define what the radar searches for and where it searches. Those
settings must be structured because they will later become prompt context, validator
inputs, and provider/integration configuration.

## Decision

A radar is modeled as a configurable object with:

- user-defined name;
- status: active, paused, needs review;
- acceptance policy: manual, automatic, automatic with review;
- trigger mode: scheduled, manual, deficit-driven;
- `RadarSearchRule[]` for trigger/search logic;
- `RadarSearchSource[]` for explicit search surfaces.

Each search rule is an atomic rule, not a textarea paragraph. Rules support:

- operator: `and` or `or`;
- `negate` flag for NOT rules;
- statement;
- active/paused status.

Sources are optional and can be mixed. A radar may search:

- author archive;
- external URL;
- MCP server;
- API;
- search keywords;
- manual source;
- social profile;
- document;
- open web.

If sources are empty, the radar still remains valid: the future AI/search layer may
choose where to search based on the rules.

## Consequences

- The UI must provide add/edit/delete flows for radars, rules, and sources.
- Radar rows should show signal count and last run date without becoming dense cards.
- Future AI/provider adapters can consume structured rules and sources.
- Future validators can check rule conflicts, missing sources, risky automatic policy,
  and stale radar runs.

## Alternatives considered

- Keep radar as one textarea. Rejected because the product requires explicit,
  validator-ready rules.
- Treat every radar as one source URL. Rejected because radars may combine archive,
  API, MCP, web search, manual sources, and no explicit source at all.
