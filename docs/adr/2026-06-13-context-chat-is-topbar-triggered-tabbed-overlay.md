# ADR: Context Chat Is a Topbar-Triggered Tabbed Overlay

- Status: Accepted
- Date: 2026-06-13

## Context

Slice 1.3 added a collapsible context chat, but the first implementation still had
three UX problems:

- the collapsed floating button could overlap working content;
- the expanded drawer used an abstract viewport width instead of the existing right
  panel geometry;
- suggestions and chat messages shared one surface, so suggestions consumed the space
  needed for conversation.

The product already has dense operational screens with a main work area and a right
panel for validation, memory, source summaries, or release context. Context chat must
help with the current section without becoming another permanent column or damaging the
main work area.

## Decision

Context chat is opened from the topbar, not from a floating page button.

- The topbar contains the `Помощник` trigger and a compact suggestion count.
- `Сбросить демо` is demoted to an icon action.
- When closed, chat has no floating page control.
- When opened on desktop/laptop, the drawer aligns to the right panel: its left edge
  must match the left edge of the persistent right panel for the current workspace.
- The drawer must not overlap the main work column on laptop-sized screens.
- On mobile, the drawer becomes a full-width bottom sheet.
- The drawer has one close control: `x`.
- The drawer contains two tabs:
  - `Чат` for freeform local conversation;
  - `Подсказки` for section-aware deterministic recommendations.
- Read-only suggestions are dismissed with `x`; they do not use ambiguous accept
  buttons.
- Actionable suggestions and chat-generated actions open existing draft/edit flows and
  never save automatically.

## Consequences

- Context chat is visually part of the app shell instead of an extra floating artifact.
- The right panel remains the geometric anchor for assistant overlay behavior.
- Visual smoke tests must verify topbar trigger, right-panel alignment, no main-content
  overlap, and mobile bottom-sheet behavior.
- Future AI provider work must keep the same HITL contract: chat may propose or prefill,
  but persistence goes through existing explicit save/approve actions.

## Alternatives Considered

- Keep the floating button. Rejected because it repeatedly conflicts with dense working
  screens.
- Keep suggestions and chat in one scroll area. Rejected because suggestions can grow
  and make the chat unusable.
- Let the drawer cover main content on laptop screens. Rejected because authors must be
  able to keep the active form/list stable while consulting the assistant.
