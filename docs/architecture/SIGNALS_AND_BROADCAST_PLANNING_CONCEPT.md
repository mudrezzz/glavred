# Signals and Broadcast Planning Concept

## Context

Slice 1.4 introduced a broadcast grid in `План`, but the product model is not
complete if the grid directly generates post slots from topics and fabulas. A real
editorial plan needs two separate layers:

1. Editorial demand in time: how often the author wants to publish and when.
2. Editorial material: signals, approved inputs, and post candidates that can fill
   those publishing slots.

Without the signal layer, `План` becomes a formal schedule with weak material behind
it. The next product circle should therefore pause deeper calendar implementation and
build `Сигналы` first.

## Product Model

The revised planning flow is:

`Редакционная модель -> Сигналы -> Кандидаты постов -> Сетка вещания -> Фабула поста -> Редактура -> Выпуск -> Аналитика`

Responsibilities:

- `Редакционная модель`: defines author, audience, goals, topics, fabulas, rules,
  weights, compatibility, and validators.
- `Сигналы`: finds and reviews raw material from radars, author memory, archives,
  external sources, and manual input.
- `Кандидаты постов`: assembles potential post concepts from a signal, topic, fabula,
  audience, value, goal, platform, and format.
- `План`: describes publishing demand and calendar status. It should not invent
  material without signals and candidates.
- `Фабула поста`: the approved concept/brief for one selected slot and candidate.

## Signals

Signals are not just imported links. A signal is any piece of material that may become
fuel for a post:

- an external news/event/source;
- a note from `Память автора`;
- a record from the archive;
- a manual research item;
- a correction the author made to a radar or candidate;
- a learning note after release.

The `Сигналы` section should have three internal tabs:

1. `Радары`
   - radar name and source;
   - monitored scope;
   - acceptance policy: manual, automatic, or automatic with review;
   - trigger mode: scheduled, manual, or deficit-driven;
   - token/budget behavior for future AI-backed radars;
   - current status and last run.
2. `Найденные сигналы`
   - filter by radar/source/status/topic/fabula/freshness/duplicate risk;
   - approve, reject, archive, or correct;
   - corrections become author-memory evidence.
3. `Кандидаты постов`
   - combinations of `Signal + Topic + Fabula + Audience + Value + Goal`;
   - candidate count follows broadcast grid settings;
   - author can approve one candidate, reject it, request more variants, or edit the
     combination.

Unapproved signals do not become active post concepts. Archive-only signals do not
change author-position assertions unless explicitly accepted into memory.

## Broadcast Grid Settings

`План` should start from publishing settings, not per-post details:

- article/post tempo;
- planning period: week, month, quarter, year;
- publishing days and times;
- candidate count per slot: minimum and maximum;
- platform and format defaults until dedicated platform entities exist;
- whether signals can be selected automatically or require HITL approval.

When the author saves these settings, the system generates calendar slots for the
selected horizon. Each slot then asks the signal/candidate layer for enough viable
concepts.

## Calendar View

The second `План` tab should be `Календарь выпуска`.

Calendar zoom levels:

- week;
- month;
- quarter;
- year.

Slot statuses:

- `empty`: slot exists but no suitable material is attached;
- `waitingForSignals`: matching signals exist but need human approval;
- `hasCandidates`: candidates are ready for review;
- `conceptApproved`: a post concept is approved and can move into briefing/editing;
- `inProduction`: draft or editorial work exists;
- `ready`: final text/release package is ready;
- `published`: manual export/release is complete;
- `atRisk`: deadline is near and the slot is not ready.

Clicking a calendar day or slot should open a detail panel below the calendar:

- if no signals exist, show radar actions;
- if signals exist, show signal approval actions;
- if candidates exist, show candidate comparison;
- if a concept is approved, link to `Фабула поста` or `Редактура`;
- if published, link to release/analytics and future platform URL.

## Radar Demand Loop

Radars should react to plan deficit:

- if the calendar has enough approved candidates, radars can stay idle;
- if candidate count falls below the configured minimum, radars should suggest or run
  additional searches;
- if signals exist but require HITL, the plan should show a waiting state instead of
  silently filling slots;
- if the author overrides radar decisions, those corrections become author-memory
  evidence.

This loop prevents unnecessary future AI/provider usage while keeping the calendar
operational.

## Near-Term Slice Order

1. `Slice 1.4.1: Broadcast Planning Concept Correction`
   - document this revised model;
   - mark current broadcast grid as a temporary local-first prototype;
   - update navigation and roadmap assumptions.
2. `Slice 1.5: Signals and Radar Workspace`
   - implement `Сигналы` as the next product layer;
   - add radar settings, found signals, and HITL signal review.
3. `Slice 1.6: Post Candidate Assemblies`
   - implement candidate concepts as combinations of signal/topic/fabula/audience/value.
4. `Slice 1.7: Broadcast Grid Settings`
   - implement tempo, period, days/times, and min/max candidate settings.
5. `Slice 1.8: Calendar View for Broadcast Plan`
   - implement calendar zoom levels, slot statuses, and slot detail panel.

Archive uniqueness remains important, but it should follow the signal/candidate
planning correction because archive material is one of the signal sources.
