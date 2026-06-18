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

Roadmap correction after Slice 1.10.4: `Редактура` owns the full post-preparation
chain `Фабула -> Драфт -> Визуал -> готов к выпуску`. `Выпуск` is not a preparation
workbench; it is the future publication log for ready posts, delivery attempts,
statuses, external links, and platform errors.

Responsibilities:

- `Редакционная модель`: defines author, audience, goals, topics, fabulas, rules,
  weights, compatibility, and validators.
- `Сигналы`: finds and reviews raw material from radars, author memory, archives,
  external sources, and manual input.
- `Кандидаты постов`: assembles potential post concepts from a signal, topic, fabula,
  audience, value, goal, and platform. Candidate format is intentionally absent
  because fabula owns the editorial shape; broadcast settings still own plan item
  formats.
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
   - filter by radar/source/status/search text/freshness/duplicate risk;
   - approve, reject, archive, or correct;
   - corrections become author-memory evidence.
3. `Кандидаты постов`
   - combinations of `Signal + Topic + Fabula + Audience + Value + Goal + Platform`;
   - the first implementation generates 2-3 deterministic candidates from approved
     signals and active topic/fabula pairs;
   - author can filter, group, edit, reject, and approve candidates;
   - request-more variants and slot binding are later controls.

Unapproved signals do not become active post concepts. Archive-only signals do not
change author-position assertions unless explicitly accepted into memory.

## Broadcast Grid Settings

`План` should start from publishing settings, not per-post details:

- article/post tempo;
- planning period: week, month, quarter;
- publishing days and times;
- candidate count per slot: minimum and maximum;
- platform default until dedicated platform entities exist;
- whether signals can be selected automatically or require HITL approval.

When the author saves these settings, the current grid is marked stale by clearing
generated plan slots and downstream production artifacts. Slice 1.8 uses a hybrid
model: settings create publish-window slots from the current date, while deterministic
planning can still fill those slots with topic/fabula ideas. The UI also shows slot
demand, available post candidates, approved concepts, and deficit/proficit. Full
calendar binding remains a later slice.

Slice 1.8.2 adds a lightweight calendar representation inside the current broadcast
grid, not the final readiness calendar. The filter card remains first; `Список`,
`Группы`, and `Календарь` are view modes over the same filtered plan items. The
calendar reuses the settings week/month/quarter model, marks publish dates, shows the
number of filtered candidates on each date, and renders the same broadcast rows below a
clicked date. It does not yet assign candidates to new slots or show production
readiness statuses.

Before the full readiness calendar, approved slots enter an editorial work queue.
Approving a slot creates or updates the stable `EditorialWorkItem` and prepares its
initial post brief automatically. `Редактура` owns `Посты` for queue review and
`Рабочий стол` for the selected-post preparation workbench. `Выпуск` owns publication
logging for ready posts, not release preparation. Calendar readiness should be derived
from work items, ready-post state, and publication log entries instead of singleton
post artifacts.

The target readiness model replaces the old `Финал -> release queue` language with:
draft text is approved inside `Драфт`, the selected post then passes through `Визуал`,
and only a text-approved plus visual-approved or `без визуала` post becomes
`ReadyPost`. Release/calendar readiness should read that state and future
`PublicationLogEntry` records, not a release package checklist.

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

## Slice 1.5.1 Correction: Radars and Raw Signals

After the first `Сигналы` implementation, the product model was corrected:

- a radar is a configurable search object, not a passive source card;
- radar configuration consists of atomic trigger/search rules and optional search
  sources;
- rules support `AND`, `OR`, and `NOT`;
- sources can be author archive, URL, MCP server, API, search keywords, manual source,
  social profile, document, or open web;
- a radar may intentionally have no explicit sources, letting a future AI/search layer
  decide where to search from the rules;
- a found signal is raw material and must not own topic/fabula/audience/value matching;
- `Найденные сигналы` shows radar provenance, date, finding, evidence, search note,
  duplicate risk, and review status;
- topic/fabula/audience/value matching starts only in `Кандидаты постов`.
- `Радары` and `Найденные сигналы` must use framed rows/cards so the author can see
  which rules, evidence, metadata, and actions belong to one entity.
- `Сигналы` must reuse the cabinet header rhythm from `Редакционная модель`; tab
  counters are separate red badges, and normal right panels must never overlap main
  content. `npm run test:design` enforces these structural UI rules.

This keeps the flow clean:

`Radar rules/sources -> raw SourceSignal -> reviewed SourceSignal -> PostCandidate`.

## Slice 1.5.8 Correction: Radar Discovery Mode and Editorial Filters

A radar is now modeled as four separate configuration layers:

1. Trigger rules: atomic instructions that say what should count as a signal.
2. Search sources: optional explicit places to search, such as archive, URL, API, MCP,
   keywords, documents, or open web.
3. Source discovery mode: `specifiedOnly`, `specifiedAndAdditional`, or `autonomous`.
4. Editorial filters: author, audience, positioning, goals, forbidden topics, and
   topics.

The distinction matters because a future adapter may search broad surfaces while the
editorial filters explain whether the found material fits the author and publishing
project. Style is intentionally excluded from radar filtering; it belongs to post
drafting and editorial checks.

Filtered-out signals remain visible. The system should show why they failed, warn, or
create useful tension, then let the author approve, archive, reject, or correct them.
No signal should disappear automatically before human review.

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
3. `Slice 1.6: First Real Post Candidate Assemblies`
   - implement deterministic compare-and-approve candidate concepts.
4. `Slice 1.7: Candidate Editing and Variant Control`
   - add request-more controls for candidate generation.
5. `Slice 1.8: Broadcast Grid Settings`
   - implement tempo, period, days/times, explicit publish slots, and min/max
     candidate settings.
6. `Slice 1.8.2: Broadcast Grid Candidate Calendar View`
   - implement calendar view over the same filtered grid rows.
7. `Slice 1.9: Editorial Work Queue Foundation`
   - turn approved slots into `Редактура` work items and reuse the selected-post
     selected-post workbench.
8. `Slice 1.10: Редактура как очередь постов и рабочий стол`
   - create the work item and initial brief on slot approval;
   - split `Редактура` into `Посты` and `Рабочий стол`.

Archive uniqueness remains important, but it should follow the signal/candidate
planning correction because archive material is one of the signal sources.
