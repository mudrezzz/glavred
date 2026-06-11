# ADR: Avoid Anonymous Hero Text From Domain Fields

## Status

Accepted

## Context

The first topic/fabula UI rendered a large quote from a domain field as a page hero.
The text looked important but had no author-controlled project identity and no clear
editing affordance.

## Decision

Setup screens must not promote anonymous domain text into hero content. The top of
`Редакционная модель` is a `ProjectProfile`: project name, description, setup status,
and counters. Narrative fields stay inside their owning entity or rule.

## Consequences

The author understands where the page title comes from and can edit it directly. The
product avoids accidental marketing-style hero blocks inside operational cabinet UI.

## Alternatives considered

- Keep the large quote as a brand statement. Rejected because it was not a stable
  product entity.
- Remove the header entirely. Rejected because the project needs a named workspace.
