# Signals

`Сигналы` is the local-first workspace between author memory/archive/source material and future post candidates.

## Radars

Radars are configurable search procedures. Each radar row is a framed cabinet card: rules, sources, settings, metadata, and actions belong to the same visible entity.

![Signals radar list](assets/screenshots/12-signals-radar-list.png)

## Found Signals

Found signals are raw material. They do not own topic/fabula/audience/value matching yet; that starts in Slice 1.6 with post candidates.
Expanded signals now show deterministic editorial filter evaluations from the source
radar. These evaluations explain whether a signal passed, needs attention, was
filtered out, or intentionally creates tension with the author's position. Filtered
signals remain visible for human review.

![Found signals](assets/screenshots/13-signals-found-signals.png)

## Radar Filters

Radar setup separates:

- trigger rules;
- search sources;
- source discovery mode;
- editorial filters for author, audience, positioning, goals, forbidden topics, and topics.

Style is not a radar filter. It belongs to draft editing and editorial checks.

## UX Rule

Rows must stay framed, chips must not wrap by letters, and expanded details must remain inside the same entity card.
The workspace also keeps an explicit section header above tabs, separated action
footers, and measured visual guardrails for spacing, edit forms, and main/side column
overlap.
The section header follows the same cabinet pattern as `Редакционная модель`; tab
counters use the shared red badge style instead of being appended as plain text.

Slice 1.5.5 adds the shared action taxonomy: `+ Radar` is a normal white work button,
while red buttons are reserved for validation, approval, save/commit, and HITL
lifecycle steps. Newly added radars keep a visible last-run fallback so metadata rows
do not shift.
