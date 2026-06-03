# UI Kit — Marketing site (landing)

The Главред landing page. Sells the positioning **«Не AI-копирайтер. AI-редакция для
вашего личного медиа.»** — drawing the line between a prompt-and-text copywriter and a
remembering editorial system.

## Run
Open `index.html`. React + Babel from CDN. Tokens from `../../colors_and_type.css`;
layout from `site.css`. Icons reused from `Icons.jsx`.

## Sections (`Sections.jsx`)
| Component | What it shows |
|---|---|
| `Nav` | Sticky blurred header, logo lockup, links, primary CTA. |
| `Hero` | Editorial display headline (serif, italic vermilion accent), lead, CTAs, and a floated insight card + dark "newsroom at work" panel. |
| `Contrast` | The core argument — dashed "Промпт → Текст" box vs a dark panel with the full pipeline, the 3 HITL gates marked red. |
| `Newsroom` | Grid of the editorial agents with mono-initial avatars. |
| `Workflow` | Horizontal conveyor of 8 stages; Plan / Фабула / Выпуск highlighted as human gates. |
| `Rubrics` | Rubricator cards. |
| `FinalCTA` | Dark ink band with accent glow + dual CTA. |
| `Footer` | Logo, links, copyright. |

## Reuse notes
- Components export via the module render at the bottom (`Site`); to reuse individual
  sections, lift them and assign to `window`.
- Same token + type system as the app kit — the serif/sans duality and the red-pen
  accent carry across both surfaces.
- `site.css` is responsive (single-column < 900px).
