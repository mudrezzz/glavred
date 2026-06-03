# UI Kit — Главред app (редакционный кабинет)

A high-fidelity, click-through recreation of the Главред editorial cabinet — the
"editorial OS" where the author works as Editor-in-Chief over a newsroom of AI agents.
This is a **cosmetic recreation** for prototyping, not production logic.

## Run
Open `index.html`. React + Babel are loaded from CDN; components are plain JSX files
sharing scope via `window`. Tokens come from `../../colors_and_type.css`; component
styling from `app.css`.

## Core screens (click the sidebar + the primary buttons to move through the flow)
1. **Редакционная библия** (`Bible.jsx`) — the blog's constitution: fabula, author,
   audience, rubricator, style model, forbidden list.
2. **Радар** (`RadarPlan.jsx`) — feed of scored **insight cards**; "В план" → Plan.
3. **План** (`RadarPlan.jsx`) — weekly calendar + **HITL Gate 1** banner. Click a post
   card → Brief.
4. **Фабула** (`BriefEdit.jsx`) — the post brief; **HITL Gate 2**. "Утвердить замысел" → Editing.
5. **Редактура** (`BriefEdit.jsx`) — draft workspace with version tabs, editor checks,
   agent notes, alt headlines; **HITL Gate 3**. "Утвердить текст" → Release.

`Выпуск` and `Аналитика` are light placeholders (no shipped design to recreate).

## Files
| File | Contents |
|---|---|
| `index.html` | Mounts the app, loads React + all JSX. |
| `app.css` | All component styles (shell, buttons, chips, cards, calendar, gates, editing). |
| `Icons.jsx` | `<Icon name>` — Lucide glyph data + the custom brand caret. |
| `Data.jsx` | `GR_DATA` — all seed editorial content. |
| `Shell.jsx` | `Sidebar`, `Topbar`, nav config + per-view titles. |
| `RadarPlan.jsx` | `RadarView`, `PlanView`, `InsightCard`. |
| `BriefEdit.jsx` | `BriefView`, `EditView`, `Placeholder`. |
| `Bible.jsx` | `BibleView`, `BibleCard`. |
| `App.jsx` | State, routing between sections, toasts. |

## Reuse notes
- Components export to `window`; import order in `index.html` matters (Icons & Data first).
- Style object collisions are avoided — styles live in `app.css` as classes; inline
  styles are scoped per element.
- The three **HITL gates** (`.gate`) are the product's signature pattern — reuse them
  anywhere the human must approve before the machine proceeds.
