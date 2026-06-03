# Главред — Design System

> **«Главред» (Glavred / "Editor-in-Chief")** — an AI-native *editorial newsroom* for
> expert bloggers, founders, consultants and companies who want to run a blog as a
> *system*, not grind out posts by hand.
>
> The product's promise is **not** "write me a post." It is the shift **from chaos to
> an editorial machine**: the blogger acts as Editor-in-Chief; a team of AI agents
> acts as the newsroom — scouts, researchers, fact-checkers, a managing editor, an
> illustrator, a content director. The system finds occasions, turns them into
> topics, topics into briefs, briefs into drafts, drafts into publications, and
> publications into data for the next cycle.

This repository is the design system that lets design agents produce on-brand
interfaces, slides and assets for Главред.

---

## Positioning

The chosen line (variant 3 from the brief):

> **Не AI-копирайтер. AI-редакция для вашего личного медиа.**
> *(Not an AI copywriter. An AI newsroom for your personal media.)*

Everything in this system reinforces one distinction: the value is not "the AI writes
better," it is **"the product gives the author editorial discipline"** — answering not
just *what to write* but *why this, why now, for whom, in which rubric, advancing which
thesis, building which reputation.*

---

## The product (entities & surfaces)

Главред is organised around durable editorial objects, surfaced as app sections:

| Section | RU | What it is |
|---|---|---|
| **Editorial Model** | Редакционная модель | The blog's durable editorial context: author, audience, fabula, style model, rubricator, forbidden topics, goals. |
| **Radar** | Радар | Stream of incoming signals → **insight cards** (event / insight / question / counter-argument / case / data / personal / pattern), each scored. |
| **Plan** | План | Content calendar with rubrics, statuses, priorities. **HITL Gate 1.** |
| **Briefs** | Фабулы | Where the *intent* of a post is approved before any draft exists. **HITL Gate 2.** |
| **Editing** | Редактура | Workspace: author version, AI version, editor notes, style / fact / anti-AI checks, alternative leads & headlines. **HITL Gate 3.** |
| **Release** | Выпуск | Publish & adapt per platform (Telegram, LinkedIn, Medium, Substack, X, newsletter). |
| **Analytics** | Аналитика | Editorial conclusions, not just views — which theses work, which rubrics build trust. |

**The newsroom (agents):** Publisher · Главный редактор · Scout · Analyst · Rubric Editor ·
Content Planner · Briefing Editor · Writer · Style Editor · **Anti-AI Editor** ·
Fact-checker · Policy Editor · Visual Editor · Distribution Agent · Growth Analyst.

**Central workflow:**
`Источники → Инсайты → Темы → Контент-план → Фабула → Драфт → Редактура → Проверка → Визуал → Публикация → Аналитика → Обучение системы`
— with three mandatory human-in-the-loop gates (plan, brief, final text).

**Surfaces represented in this system:**
1. **Главред app** — the editorial cabinet (`ui_kits/glavred-app/`)
2. **Marketing site** — the landing page (`ui_kits/marketing-site/`)

---

## Sources for this system

There was **no existing codebase, Figma file, or brand kit.** This design system was
authored from scratch from the product concept brief ("AI-издательство «Главред»").
All visual decisions — palette, type pairing, logo, motifs — are original to this
system and documented below so they can be evolved.

---

## CONTENT FUNDAMENTALS — how Главред writes

The product is in **Russian** and its voice is **editorial, warm, and quietly
confident** — a seasoned editor-in-chief talking to a peer, never a SaaS growth-hacker
and never a sterile consultant.

- **Address:** «вы» (lowercase, respectful but not stiff). The product speaks *to* the
  author as a partner. Agents speak in first person of their role («Я нашёл 6 сигналов»,
  «Предлагаю перенести на вторник»).
- **Casing:** Sentence case everywhere — UI labels, buttons, headings. **No ALL-CAPS**
  except small mono system marks/labels (e.g. `РУБРИКА`, `СКОРИНГ`, `HITL`).
- **Tone:** Editorial, decisive, specific. Verbs of editorial craft: *найти, отобрать,
  утвердить, отклонить, заострить, проверить, выпустить.* Avoids hype, avoids
  «революционный / инновационный / магия».
- **The product mocks its own category.** Anti-AI-slop is a *brand value*. Copy
  explicitly rejects: «важно отметить», «в современном мире», symmetric lists for the
  sake of lists, sterile consultant tone. This attitude should show up in microcopy.
- **Editorial framing of everything.** Buttons say «Утвердить фабулу», not «Submit».
  Empty states talk like an editor: «Пока нет поводов. Радар слушает источники.»
- **Numbers earn their place.** Scores (релевантность, новизна, срочность, риск
  банальности) are shown as compact mono chips — they are editorial judgements, not
  vanity metrics.
- **Emoji:** **No.** The brand voice is editorial print, not chat. Status is carried by
  color + the proofreader's-mark iconography, never by emoji.

**Sample microcopy**
- Onboarding step: «Сначала — кто автор и для кого он пишет. Остальное достроим по ходу.»
- Radar card CTA: «Может стать постом» / «Нужна реакция сегодня» / «Вечнозелёная тема»
- Gate-2 approve: «Утвердить замысел» · reject: «Вернуть на доработку»
- Anti-AI Editor note: «Убрал три пустых обобщения и один симметричный список.»
- Empty plan: «План пуст. Откройте Радар — там 12 поводов ждут отбора.»

---

## VISUAL FOUNDATIONS — "The Quiet Newsroom"

The aesthetic is **editorial gravitas wearing soft, airy SaaS clothing.** White/paper
backgrounds, generous air, rounded forms — explicitly *not* the square-cut consulting
look. Print-shop discipline (a real type hierarchy, a single decisive accent) keeps it
from feeling like a generic startup.

### Signature motif — the editor's red pen
The whole identity hangs on **the proofreader's mark**. The logo is a geometric serif
«Г» with a vermilion **insertion caret** beneath it. That caret/mark language recurs:
section accents, the "approve" gesture, the active-nav indicator, callout rules. One
red, used sparingly, like an editor's pen on a manuscript.

### Color
- **Surfaces:** warm paper `--paper #FBF9F5` for the app field; pure `--surface #FFFFFF`
  for cards; `--surface-sunk #F6F2EB` for wells, inputs at rest, code.
- **Ink:** a *warm* near-black scale (`--ink-900 #211D19` → `--ink-50`), slightly taupe.
  Never cold/blue-gray. Text is `ink-900`; secondary `ink-600`; borders `ink-200`.
- **Accent:** one signature vermilion `--accent #DD4F2E` (the red pen). Hover/press
  darken (`#C5401F`/`#AE3517`). Tints `--accent-tint`/`--accent-wash` for fills.
- **Semantic:** warm & restrained — `--ok #1F8A5B` (published), `--warn #C2890F`
  (needs fact-check / risk), `--danger #C8392B` (policy violation), `--info #2D6BC4`
  (scout signal). Each has a `-tint` fill and `-ink` on-tint text.
- **Imagery vibe:** warm, natural-light editorial photography; never cold or neon.
  Restrained use; the type and white space do the work.

### Type
A deliberate **duality that mirrors the product**: software chrome is sans, the content
the newsroom *produces* is serif.
- **Golos Text** (Cyrillic-native humanist sans) — all UI: nav, labels, buttons, body.
- **Lora** (serif) — editorial content: article previews, big quotes, landing display.
- **JetBrains Mono** — system marks, agent labels, scores, `HITL` gates. Uppercase,
  tracked, small.
- Headlines set tight (`letter-spacing -0.01…-0.02em`); editorial body airy
  (`line-height 1.7`, `max-width ~64ch`, `text-wrap: pretty/balance`).
- Full ramp + tokens in `colors_and_type.css`.

### Spacing, radii, elevation
- **Spacing:** 4px base (`--sp-1…--sp-20`). Layouts breathe — section padding 32–64px.
- **Radii:** soft and consistent — inputs/buttons `--r-md 12px`, cards `--r-lg 16px` /
  `--r-xl 22px`, pills `--r-pill`. Nothing sharp.
- **Elevation:** soft, **warm-tinted** shadows (the tint is ink, not gray): `--shadow-sm`
  for resting cards, `--shadow-md` on hover/popovers, `--shadow-lg`/`xl` for modals &
  dropdowns. A dedicated `--shadow-accent` glow for primary CTAs.
- **Borders:** hairline `1px var(--ink-200)`; cards often use *border + soft shadow*
  together (the border defines the edge on white-on-white, the shadow lifts it).

### Backgrounds
Predominantly flat warm paper. **No heavy gradients**, no bluish-purple AI clichés.
Allowed: a barely-there paper texture / faint dot-grid in hero zones, and gentle
top-down `--accent-wash` washes behind editorial hero blocks. Section dividers can use a
thin rule with a small red caret tick (the mark motif).

### Motion
Calm and editorial. Entrances **fade + 6–10px rise**, `--dur 200ms` with `--ease`
(ease-out). **No bounce** on UI; no infinite decorative loops. The "approve" action may
draw a quick red caret/check stroke (180ms). Reduced-motion shows end-state.

### Interaction states
- **Hover:** subtle — surfaces go to `--ink-50/100` well; accent buttons darken to
  `--accent-hover`; cards gain `--shadow-md` and lift `-1px`.
- **Press:** darken one more step (`--accent-active`) + `scale(0.985)`; no big squish.
- **Focus:** `--ring-focus` (info-blue ring) for inputs; `--ring-accent` for primary.
- **Selected/active nav:** `--accent-wash` pill + a vertical red caret/mark indicator;
  label goes `ink-900` + weight 600.

### Cards
The workhorse. White surface, `--r-lg/xl` corners, `1px var(--ink-200)` border,
`--shadow-sm` at rest → `--shadow-md` on hover. Insight/Post cards carry: a mono rubric
tag, a serif title, a one-line rationale, scoring chips, and a status dot. Generous
internal padding (20–24px).

---

## ICONOGRAPHY

- **Primary set: [Lucide](https://lucide.dev)** (CDN). Chosen for its rounded,
  open, even **1.75–2px stroke** geometry — it matches the soft, airy brand far better
  than filled or sharp icon sets. **This is a substitution** (there was no existing icon
  asset to import); flagged for the user below. Load:
  `<script src="https://unpkg.com/lucide@latest"></script>` then `lucide.createIcons()`,
  or import individual SVGs.
- **Default stroke:** `2px`, `currentColor`, `round` caps/joins, 20–24px box in UI.
- **The proofreader's caret** (insertion mark) is a **custom brand glyph**, not from
  Lucide — used for the logo, the "approve/mark" gesture, active-nav indicator and
  section ticks. Defined as inline SVG (`assets/logo-mark.svg` and reused inline).
- **No emoji. No unicode glyphs as icons.** Agent avatars are mono-initials in tinted
  chips (e.g. `СК` Scout, `ФЧ` Fact-checker), not emoji or clip-art.
- Icons are functional and quiet — they support labels, rarely stand alone, and never
  carry color except to inherit a semantic state.

---

## INDEX — what's in this system

| Path | What |
|---|---|
| `README.md` | This file — context, content & visual fundamentals, iconography, index. |
| `SKILL.md` | Agent-Skills-compatible entry point. |
| `colors_and_type.css` | All design tokens: color, type ramps, spacing, radii, elevation, motion. |
| `assets/` | Logo mark, outline mark, wordmark (SVG). Brand glyphs. |
| `preview/` | Small spec cards rendered in the Design System tab (type, color, spacing, components). |
| `ui_kits/glavred-app/` | UI kit — the editorial cabinet app. `index.html` + JSX components. |
| `ui_kits/marketing-site/` | UI kit — the landing page. `index.html` + JSX components. |

**Fonts** are loaded from Google Fonts (Golos Text, Lora, JetBrains Mono) via `@import`
in `colors_and_type.css` — all three have full Cyrillic coverage. If you need them
self-hosted/offline, download the families and drop them in `fonts/`.

---

## CAVEATS / open questions for the user
- **Fonts & icons are tasteful substitutions** (Golos Text + Lora + JetBrains Mono;
  Lucide icons). If Главред has, or wants, a specific brand typeface or icon set, send
  it and I'll swap.
- The **vermilion accent** and the red-pen motif are a strong creative bet. If you'd
  prefer a calmer / different signature color, that's a one-token change — say the word.
- No real product screenshots existed, so the UI kit screens are an **original
  interpretation** of the concept, not a recreation of shipped UI.
