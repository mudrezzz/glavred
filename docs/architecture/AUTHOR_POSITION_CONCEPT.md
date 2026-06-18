# Author Position Concept

## Core Shift

Glavred is no longer centered on the idea that a source signal becomes content. That
pipeline remains important, but it is downstream.

The product center is:

`Author Memory -> Author Position Model -> Editorial System -> Content Production`

The main product risk is generic AI compilation. Glavred avoids it by making the
author's own position explicit, editable, evidence-backed, and continuously validated.

## Author Memory

Author Memory is the central local-first knowledge stream. It should feel lightweight:
an internal feed of notes that do not force the author into a rigid form.

Inputs include:

- raw thoughts and stream-of-consciousness notes;
- links with the author's reaction;
- manual source material dropped into the system;
- corrections to radar classification, topic choice, fabula choice, or priority;
- editorial learning notes after release;
- imported archive posts and annotations;
- rejected or revised drafts when they reveal author preference.

Every author intervention is product data. If the author moves a radar item from one
topic to another, rejects a banal angle, changes tone, or rewrites a thesis, the system
should treat that as evidence about the author's position.

## Author Position Model

The Author Position Model is the transparent digest of Author Memory. It is not a
single prompt. It is a set of editable, evidence-backed entities and rules:

- author persona and alter ego;
- style and anti-AI constraints;
- audience and reader value;
- blog goal and decomposed metrics;
- topics and directions;
- post fabulas;
- Content Design Records;
- platforms and formats;
- validators and scoring rules.

The model must always be inspectable. When the system claims "the author avoids
tool-hype framing", it should show the notes, corrections, archive posts, or CDRs that
support that conclusion.

## Editorial Entities

Everything important should be modeled as an entity, not as an undifferentiated text
box.

### Topics

A topic is an editable card with:

- name and purpose;
- audience value;
- author position;
- content rules;
- evidence requirements;
- forbidden angles;
- tone and length guidance;
- validator set;
- weight range in the content plan.

Topic weights should be ranges, not exact percentages, to avoid brittle scheduling and
edge effects.

### Fabulas

A fabula is the post's dramaturgy or narrative pattern. It describes how the post works,
not what it is about.

A fabula has:

- scenario and structure;
- conflict requirements;
- proof requirements;
- expected reader movement;
- validator set;
- weight range;
- compatibility with topics.

The system should maintain a `Topic x Fabula` compatibility matrix. Defaults can be
enabled, but the author must be able to disable incompatible combinations.

### Content Design Records

Content Design Records are durable content decisions, analogous to ADRs in software.

Examples:

- no alarmist AI adoption headlines;
- every process-adoption post must show an operational mechanism;
- product bridges must not dominate trust-building posts;
- no post may be published without a clear author conflict or position.

Each CDR should include a statement, rationale, status, scope, evidence, and validator
impact.

### Persona, Style, Audience, Goal, Metrics

Persona, style, audience, goal, and metrics are also structured entities.

The goal should be cross-validated against the persona, audience, topics, fabulas, and
platforms. For example, if the goal is to sell courses to IT professionals, but the
persona model does not build expert trust, validation should raise a red flag.

Metrics should include:

- platform metrics: views, reactions, comments, shares, saves;
- business metrics: leads, consultations, subscriptions, qualified requests;
- editorial metrics: trust signals, quality of audience response, repeated questions,
  strong theses, and topics that attract the right readers.

## Radars and Material Mill

Radars collect material, but they do not own the author's position.

Radar modes:

- continuous radar;
- manually triggered deep radar;
- manual note/link input;
- archive import;
- post-release analytics input.

The author should be able to inspect how a radar selected, rejected, or classified
material. Corrections to radar decisions become Author Memory events.

## Content Plan

The content plan is the broadcast grid where weights meet reality.

It is influenced by:

- topic weight ranges;
- fabula weight ranges;
- platform and format weights;
- publishing tempo;
- manual priorities and constraints.

Manual edits to the grid are stronger than abstract weights. The system should either
adjust the underlying weights or show conflicts when the plan no longer satisfies the
declared model.

## Validators

Validators are a common layer across the product.

They should evaluate:

- author position;
- persona;
- style and anti-AI quality;
- audience value;
- goal fit;
- topic rules;
- fabula rules;
- platform/format rules;
- CDR compliance;
- uniqueness against archive;
- evidence quality and fact gaps.

Each validator result should include status, score, summary, evidence, and suggested
fixes. The UI should show compact colored indicators, with drill-down evidence when
the author opens a check.

## Context Chat and Wizard

Each product section should have a context chat synchronized with the active section.
The implementation uses a topbar-triggered, tabbed overlay instead of a permanent third
right-side column, because many sections already reserve the right side for validation,
evidence, summary, or release metadata. The overlay opens from the right edge of the app
on desktop/laptop screens and becomes a bottom sheet on mobile.

The chat is not a generic assistant. It has separate `Чат` and `Подсказки` modes and
helps the author complete the current section:

- goal formulation;
- persona extraction;
- audience rules;
- topic design;
- fabula design;
- CDR creation;
- platform and format setup;
- radar review;
- validator failure correction.

The onboarding wizard should happen through this chat, but the output must be
structured entities and rules, not a freeform document. Accepted suggestions should open
draft/edit flows and still require explicit author save/approval.

## Relationship to Current Implementation

The current flow remains a valid production compatibility layer:

`SourceSignal -> InsightCard -> ContentPlanItem -> PostBrief -> PostDraft -> EditorialChecks -> FinalText -> ReleasePackage -> EditorialLearningNote`

The target production boundary now routes preparation through:

`SourceSignal -> InsightCard -> ContentPlanItem -> EditorialWorkItem -> PostBrief -> PostDraft -> Visual -> ReadyPost -> PublicationLogEntry -> EditorialLearningNote`

`FinalText` and `ReleasePackage` remain compatibility/manual-export artifacts. Future
slices should keep author memory and author position above this layer, route production
through those entities and validators, and treat `Выпуск` as delivery log rather than
an editorial workbench.
