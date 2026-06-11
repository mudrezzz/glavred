# ADR: Require Reviewed Imports Before Author Position Influence

## Status

Accepted.

## Context

Glavred is being re-centered around author memory and author position. External
sources are necessary: Telegram posts, social profiles, blogs, talks, documents, and
old archives can all contain valuable evidence about how the author thinks.

The risk is that import becomes an opaque data dump. If 1,000 historical posts are
imported and immediately used to update author-position assertions, the author loses
control over the model. The product would also make it hard to explain why a position
changed.

Large archives still need bulk handling. Requiring manual review of every imported
post would make archive import unusable.

## Decision

Imported material must pass through a review layer before it can influence the author
position model.

Unreviewed import candidates cannot strengthen `AuthorPositionAssertion`.

Bulk actions are allowed, including `Добавить все`, but bulk import defaults to
archive-safe behavior:

- large historical sets should go to `ArchiveRecord` by default;
- bulk-accepted items must keep provenance and acceptance mode;
- bulk-accepted archive items should not automatically become strong evidence for
  author-position assertions;
- manually accepted memory items can become `AuthorNote` inputs;
- future evidence review can promote archive records to assertion-supporting evidence.

Every imported item must preserve provenance: source, original URL or file reference,
original date when available, import date, acceptance date, and acceptance mode.

## Consequences

- The author can import large archives without reviewing every item.
- The system remains explainable because imported evidence keeps source and acceptance
  metadata.
- The first implementation can stay local-first with mock candidates and no real
  external integrations.
- Real source APIs, backend crawling, OAuth, scheduled ingestion, and AI analysis can
  be added later without changing the review-before-influence rule.

## Alternatives Considered

- Automatic import into author position: rejected because it makes the model opaque
  and can overwrite the author's current stance with stale archive material.
- Manual-only review for every item: rejected because large archives would be
  impractical.
- Import everything as regular notes: rejected because notes and historical archive
  records need different evidence weight and provenance.
