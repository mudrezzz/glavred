# ADR: Use Collapsible Overlay for Context Chat

- Status: Superseded by `2026-06-13-context-chat-is-topbar-triggered-tabbed-overlay.md`
- Date: 2026-06-12

## Context

Glavred already uses right-side panels for author memory summaries, import summaries,
author-position assertions, release metadata, analytics context, and editorial validation.
Adding context chat as another right column would compress operational workspaces and
repeat the layout failures already seen in entity catalogs.

The chat is important as a wizard surface, but it must not permanently displace the
current right panel. Authors need to keep validation and evidence visible, then open the
chat only when they want help.

## Decision

Context chat is implemented as a collapsible overlay, not as a third layout column.

- Default state is collapsed.
- Collapsed state is a fixed `Помощник` control under the topbar.
- Expanded state is a fixed right drawer with `width: clamp(360px, 34vw, 460px)`.
- On wide screens the drawer can partially cover the existing right panel.
- On laptop-width screens it may cover the right panel completely.
- On mobile it becomes a bottom sheet.
- Chat suggestions can open existing draft/edit flows, but they do not save workspace
  changes automatically.
- Visual smoke tests must cover collapsed and expanded states.

## Consequences

- Existing right panels remain the primary persistent context surfaces.
- The assistant is available everywhere without forcing every screen into a three-column
  layout.
- Any future chat feature must preserve collapse/expand behavior and avoid bypassing
  read/edit/save/cancel workflows.

## Alternatives Considered

- Permanent third column. Rejected because current product screens already use their
  horizontal space for main work plus right panel.
- Replacing validation/evidence panels with chat. Rejected because validation and
  evidence must remain visible even without opening chat.
- Inline chat per section. Rejected for Slice 1.3 because it would duplicate chat chrome
  across screens and make later AI integration harder to reason about.
