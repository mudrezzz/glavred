# ADR: Radars Separate Trigger Rules, Sources, and Editorial Filters

## Status

Accepted.

## Context

The Signals workspace originally treated a radar as a simple combination of search
instructions and optional sources. That is not enough for the product model. A radar
needs to answer three different questions:

- What should count as a found signal?
- Where should the system search?
- Which editorial constraints should explain whether the found material is useful?

These responsibilities must remain separate because they will later map to different
AI/provider operations, validation prompts, and human review steps.

## Decision

Radar configuration is split into:

- trigger rules: atomic instructions for what to find;
- search sources: optional explicit source surfaces such as archive, URL, API, MCP,
  search keywords, documents, or open web;
- source discovery mode: specified sources only, specified sources plus additional
  discovery, or autonomous discovery;
- editorial filters: author, audience, positioning, goals, forbidden topics, and topics.

Style is intentionally not a radar filter. Style belongs to drafting and editorial
checks after a post concept exists.

Filter evaluation is deterministic in the current local-first product. A failed filter
does not delete or hide a signal. It marks the signal as material that needs human
review, because rejected or tense material may still teach the system something about
the author's position.

## Consequences

- React renders radar filters but does not own filter logic.
- Domain/application code returns explicit filter evaluations with status, score,
  summary, and evidence.
- Found signals can be filtered by aggregate filter status.
- Post candidate assembly remains a later step: topic/fabula/audience/value matching
  must not be moved back into the raw signal review UI.
- Future AI adapters can replace deterministic evaluation behind the same boundary.
