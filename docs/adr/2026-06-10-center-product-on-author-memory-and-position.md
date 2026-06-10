# ADR: Center Product on Author Memory and Position

## Status

Accepted

## Context

The first implementation circles proved the production pipeline:

`SourceSignal -> InsightCard -> ContentPlanItem -> PostBrief -> PostDraft -> EditorialChecks -> FinalText -> ReleasePackage -> EditorialLearningNote`

That pipeline is useful, but it risks making Glavred look like a structured AI content
generator. The stronger product premise is that valuable expert content depends on the
author's own position. Without that position, the system can only compile sources or
generate generic text.

The author needs a place to capture loose thoughts, reactions, corrections, links,
archive annotations, and post-release learning. Those inputs should become evidence for
a transparent model of how the author thinks and writes.

## Decision

Glavred's conceptual center is now `AuthorMemory` and `AuthorPositionModel`.

The existing production pipeline remains valid, but it becomes downstream:

`AuthorMemory -> AuthorPositionModel -> EditorialSystem -> ContentProduction`

The product should model important editorial configuration as structured entities, not
freeform text boxes:

- author persona and alter ego;
- style and anti-AI rules;
- audience and reader value;
- blog goals and metrics;
- topics;
- fabulas;
- Content Design Records;
- platforms and formats;
- validators and evidence.

Every author correction is product data. Manual changes to radar classification, topic
choice, fabula choice, draft wording, validator acceptance, or release learning should
be treated as evidence about the author's position.

AI provider integration is deferred until the author-position and validator layers are
strong enough to constrain generation.

## Consequences

- The next implementation slice should not be an AI drafting adapter. It should add
  author memory and the first author-position model baseline.
- The current `EditorialModel` should be gradually decomposed into structured
  entities.
- Validators become a shared product layer across setup, planning, drafting, release,
  and archive uniqueness, not only editorial checks on drafts.
- The UI should evolve toward an editorial operating system with a right-side
  context chat synchronized to the selected section.
- The existing local-first production demo remains useful and should not be broken.

## Alternatives considered

- Continue directly to AI drafting adapter: rejected because AI would attach to a
  model that does not yet capture the author's position deeply enough.
- Keep source signals as the product center: rejected because signals are only one
  kind of material and do not explain how the author feels or thinks about a topic.
- Store author context as one large prompt: rejected because the product needs
  inspectable entities, validator scores, evidence, and author corrections.
- Make onboarding a fixed form wizard only: rejected because the author needs a loose
  note stream and context chat, not only rigid forms.
