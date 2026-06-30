# Demo

## Current Demo

The current demo is the local Vite app:

```bash
docker compose up --build
```

Open `http://localhost:5176`. The Dockerized demo starts the Vite frontend and FastAPI
backend together; backend AI run audit data is stored under local `var/`.

The non-Docker development path is:

```bash
npm install
npm run dev
```

It shows the first working Glavred editorial cabinet:

`AuthorNote -> AuthorMemoryEvent -> AuthorPositionAssertion -> SourceSignal -> InsightCard -> BroadcastContentPlan -> approved PostBrief -> PostDraft -> EditorialChecks -> approved text -> Visual -> ReadyPost -> PublicationLogEntry -> EditorialLearningNote`

`FinalText` and `ReleasePackage` still exist as compatibility/manual-export artifacts
in the current runtime, but the demo path now includes `Редактура -> Визуал` as a
local visual/no-visual decision. `Выпуск` records delivery state and must not edit the
prepared content.

The app uses the `ui-design-systems/ui-kit/glavred-app` reference shape: sidebar,
topbar, cards, HITL gates, plan area, brief area, editorial review area, future release
log area, analytics prep area, and the new author memory workspace.

## Permanent Demo Scenario

- Format: Telegram blog.
- Author: AI Product Manager.
- Subject: research experience building AI-B2B products in the current market.
- Audience: AI PM, founders, CPO/product leaders, and B2B SaaS teams.
- Position: AI-B2B product value comes from workflow, evals, trust loop, adoption, and
  deployment economics, not from demo magic.
- Source signal: AI-B2B pilots often fail between impressive demo and regular user
  adoption.
- Expected output: an approved Telegram research note with a completed visual decision,
  ready for release logging and followed by captured editorial learning.

## Backend/Local Portfolio Shell and Benchmark Demo

The demo now includes a SaaS-style portfolio shell with two users and three
independent blog project containers. With FastAPI running, the frontend uses
dev-password backend login and project-scoped SQLite workspace snapshots. Without
FastAPI, the same shell falls back to local browser storage.

The default post-login entry point is the `Project Dashboard`: choose a blog card,
click `Открыть кабинет`, or create/rename/archive a project. The lower-left sidebar
identity block remains inside an opened project for quick switching and has `Все
проекты` to return to the dashboard. The architecture contract for the portfolio is
`docs/architecture/SAAS_BLOG_PORTFOLIO_ARCHITECTURE.md`.

Slice 2.17.1 proves local switching and project isolation. Slice 2.17.2 fills those
project containers with realistic benchmark memories, editorial models, source
examples, plan slots, and production scenarios. Slice 2.17.3 adds backend login,
sessions, memberships, and workspace snapshots. Slice 2.17.3.1 adds dashboard-first
navigation and owner-local project lifecycle actions. Slice 2.17.3.2 polishes the
dashboard with an account sidebar and a bounded two-column project tile grid.

Backend demo login:

- `founder@example.test` / `glavred-demo`
- `glavred-editor@example.test` / `glavred-demo`

Target portfolio:

- User A:
  - `AI Design Patterns`: technical/research blog about durable AI design patterns,
    best practices, engineering/product lessons, and anti-hype synthesis. It should
    be English-capable and likely LinkedIn-first, with possible Telegram companion
    notes.
  - `Каша из топора`: Telegram-native RevOps/Product Marketing author blog with
    strong stance, irony, and practical field observations.
- User B:
  - `Блог Главреда`: product philosophy, build-in-public notes, practical editorial
    methods, and explanations of the product's AI-native editorial approach. This is
    the planned first Telegram + Dzen multi-platform benchmark.

The portfolio should become both visible demo data and a quality benchmark:

- project isolation: one blog's author memory and learning notes must not affect
  another blog;
- channel adaptation: one editorial idea can produce different Telegram, LinkedIn,
  or Dzen variants;
- voice preservation: the RevOps blog should not sound like the technical AI patterns
  blog;
- research depth: the technical blog can require more public evidence than a quick
  Telegram opinion post;
- product narrative: the Glavred blog should explain product philosophy without
  sounding like a generic marketing brochure.

The seeded fixtures are intentionally sanitized. They are derived from real working
materials supplied by the product owner, but the source PDFs/resume and private
details are not committed. The public demo keeps only reusable editorial signals,
source descriptions, author-memory notes, and benchmark expectations.

## Seeded Author Memory

Each blog now has its own memory feed:

- `AI Design Patterns`: execution layer, evidence-first generation, context packs,
  and reliability layers.
- `Каша из топора`: complex B2B sales, five RevOps questions, BANT+, Loss-to-Action,
  and sales enablement materials.
- `Блог Главреда`: product philosophy, SourceLedger/evidence discipline, HITL,
  editor decision learning, and future Telegram/Dzen adaptation.

The app shows inferred author-position assertions with evidence links back to the
active project's notes only.

The author memory workspace also demonstrates the hardened UX: titleless capture,
optional title reveal, local file attachments, local link preview, targeted correction
from assertions and evidence, search/filtering, lazy loading, long-note collapse,
edit/delete actions, summary counters, and a browser voice-input fallback.

The demo also includes a topbar `Помощник` overlay with `Чат` and `Подсказки` modes. It
is synchronized with the current section, answers deterministic local questions,
suggests next steps for the active portfolio project, and can open draft forms for
rules, topics, and fabulas. It does not call AI providers and does not save changes
without the normal `Сохранить` action.

## Structured Editorial Model

`Редакционная модель` opens inside the selected portfolio project. The dashboard shows
`AI Design Patterns`, `Каша из топора`, and `Блог Главреда` as separate projects; each
has its own profile, memory, topics, fabulas, signals, and ready benchmark scenario.

The `Издательство` tab contains atomic demo rules for author, audience, position, style, goals, and forbidden topics. The right-side validation panel starts as `Еще не проверено`; click `Проверить` to create the deterministic `ValidatorRun`. The panel then shows validator cards with score, red/yellow/green status, evidence, and suggested fixes. After saving setup changes, the panel marks that snapshot as `Требует повторной проверки` until the next manual run.

Demo topics:

- AI product discovery;
- Evals & quality loop;
- Enterprise trust & rollout;
- GTM/adoption economics;
- Workflow automation architecture.

Demo fabulas:

- Исследовательская заметка;
- Разбор мифа;
- Практический фреймворк;
- Postmortem пилота;
- Позиционный манифест.

The compatibility matrix starts with every pair enabled. The author can turn off
specific topic/fabula combinations and see warnings when a topic or fabula can no
longer participate in planning.

The demo also supports creating a custom topic or fabula from the list toolbar. New
entities stay as local drafts until `Сохранить`, then appear in the compatibility
matrix with enabled links by default. Deleting an entity removes its matrix links; use
`Пауза` instead when an entity should remain available for later.

## Broadcast Content Plan

`План` now opens as a broadcast grid for the AI Product Manager Telegram blog. The demo
seed contains a monthly settings profile: three posts per week, Monday/Wednesday/Friday
publishing at 10:00, Telegram as the local-first platform, HITL signal selection, and
candidate limits per slot. The generated grid shows dates, times, topics, fabulas,
approval status, manual override state, and advisory weight/matrix warnings.

This is a useful compatibility prototype, but it is not the final planning model. The
demo now includes `Сигналы`: radar settings, found signals, explicit signal review, and
the first `Кандидаты постов` review layer with filters, search, grouping, edit, reject,
and approve actions. `Настройка сетки` creates the publish-window frame and shows
available candidates versus approved concepts. Slice 1.8.2 makes the demo plan screen
match the same cabinet UX as the review queues: filters/search and
`Список / Группы / Календарь` sit above broadcast slots, slot rows stay in the main
content column, expanded slots show the candidate/source context, and `Настройка
сетки` uses a clickable mini-calendar for week/month/quarter publish-slot selection.
The calendar view marks publish dates, shows filtered candidate counts per date, and
opens the same slot cards under the selected date. Future slices can add candidate
variant requests and then turn `План` into a real calendar with readiness statuses.

The standalone sidebar item `Фабулы` is removed. Editorial fabulas are edited inside
`Редакционная модель -> Фабулы`. A concrete `Фабула поста` is still part of production:
approve a plan slot and Glavred automatically creates the editorial work item plus
its initial post brief for `Редактура`.

Approved plan slots now appear as an editorial work queue in `Редактура`. `Посты`
lists queued work items with filters and row actions; `Рабочий стол` edits one
selected post through `Фабула -> Драфт -> Визуал -> готов к выпуску`. `Финал` is no
longer a user-facing tab; text approval belongs in `Драфт`. Approving `Фабула`
starts a backend `DraftRun`, shows queued/running step progress, and applies the
completed draft when the worker finishes. `Выпуск` is the future publication log for
ready posts, publication attempts, external links, platform errors, and retry notes.
The existing manual package/checklist/copy/Markdown surface is only a compatibility
bridge until release-log slices replace it.

The current drafting-quality demo trace now includes role-specific model choices,
`ArticleDossier`, `ContextPacks`, `EvidenceInterpretation`, validation, ranking, and
the final revision-loop decision. The dossier shows the run-local cards Glavred kept
in memory: evidence, claims, decisions, risks, rejected moves, and open questions.
Context packs show which cards were sent to strategy, writer, review, and critic calls.
The recommended local role preset uses writer `openai/gpt-5.1`,
technical JSON backup `openai/gpt-4.1-mini`, critic/final gate
`google/gemini-2.5-pro`, and another-angle `qwen/qwen3.7-max`; another-angle is
creative divergence, not a writer duplicate or technical backup. Writer/revision/
repair/final-gate/another-angle calls also record their effective temperature/top-p
profile in trace.
Demo fabulas now use mixed research depths (`light`, `standard`, `deep`,
`marketResearch`). A DraftRun trace shows the resolved `DraftRunBudget`, including
execution mode, caps, skipped retrieval tasks, and trimmed evidence/claims.
Evidence interpretation shows how accepted sources became implications, limits,
usable examples, reader-value hooks, and forbidden overclaims before the writer saw
them. The prosecutor/editor critique now appears inside the `validation` trace as a
quality challenge: it explains whether candidates are boring, generic, under-argued,
missing author stance, or using sources mechanically. The alternative-angle
tournament then asks another model role for one different route, asks the writer to
draft the challenger, and lets final validation/ranking decide whether it beats the
original pool.
JSON-producing provider calls in the trace should show primary, repair, optional
backup, and final fallback/not-run/failed decisions. A single malformed JSON response
is no longer expected to silently disable draft candidates, critique, alternative
angle, ranking, or revision.

The post-run demo also shows the Author Memory learning handoff. After the editor
selects a draft version as final, Glavred creates an auto `Редакторское наблюдение`
note in `Память автора`. It summarizes selected and rejected versions, human
comments, manual edits, HITL quality-check risks, and a suggested takeaway. The note
starts as `На проверке`: it is visible in the `Редакторские наблюдения` filter but it
does not strengthen author-position inference until the user clicks
`Принять в память`.

The seeded demo workspace includes this flow out of the box. In
`Редактура -> Рабочий стол -> Драфт`, the selected demo post has versions `v1-v4`:
`v1` is the machine final, `v2` responds to "усиль авторскую позицию" and is selected
as final, `v3` responds to "добавь 3 критерия" with a warning, and `v4` is a manual
tone cleanup that remains rejected. In `Память автора -> Редакторские наблюдения`,
the linked pending auto note summarizes those comments, rejected versions, quality
checks, and the suggested takeaway. This is seeded fixture data, not a live OpenRouter
HITL run.

## External Sources Scenario

The import layer is implemented as a local-first UI shell around the same AI Product
Manager demo. It uses mock candidates and a source list only; no real API, backend,
crawler, OAuth, or AI analysis is connected.

Demo source examples:

- Telegram channel archive with about 1,000 historical posts about AI-B2B product
  work.
- Customer interview notes about pilot-to-adoption friction.
- Blog/site essays about evals, trust loops, and enterprise rollout.
- A talk document about AI product discovery and confidence boundaries.
- Manual upload of research notes and screenshots.

The UX does not require reviewing every archived Telegram post. The import queue can
filter and group candidates, then allow `Выбрать все по фильтру` and `Добавить все`.
For large archives, the safe default is accepting material into archive, not
immediately strengthening the live author-position model.

## Visual Walkthrough

The visual user walkthrough is published in the GitHub Wiki:

- `https://github.com/mudrezzz/glavred/wiki`

The source pages live in `docs/wiki/`, and screenshots are generated from the real
local app:

```bash
npm run docs:screenshots
```

The wiki covers the same local portfolio demo: author memory, production flow,
future release log, manual export compatibility, and analytics learning note.

If the GitHub Wiki has not been initialized yet, GitHub redirects the URL back to the
repository. Create the first temporary Wiki page in the web UI once, then run
`npm run docs:wiki:publish`.

## Main User Flow

1. Open `Память автора`.
2. Review seeded notes and `Как система поняла автора`.
3. Add a quick thought without a title, or reveal `+ Заголовок` when needed.
4. Use `+ Файл` to attach a small research note or screenshot as supporting material.
5. Switch to `Реакция на ссылку`, paste a URL, and confirm the local link preview.
6. Use `Корректировать` from an assertion or evidence item to create a targeted manual
   correction.
7. Try search, type filters, `Показать еще`, long-note expansion, edit, and delete.
8. Open `Источники`, inspect demo source rows, then open `Очередь разбора`.
9. Filter candidates, use `Выбрать все по фильтру`, confirm `Добавить все`, inspect
   `Архив`, and try `Отменить последнее групповое действие`.
10. Accept one candidate through `В память` to see it become an active memory note.
11. Open `Редакционная модель`, inspect `Издательство`, project profile, structured rules, and the right-side validation panel.
12. Open `Темы`, add a custom topic, save it, expand a row, edit or delete one entity.
13. In `Редакционная модель`, open `Фабулы`, add a custom fabula, save it, then inspect its compatible topics.
14. Open `Матрица`, toggle one compatibility pair, then use `Сохранить матрицу` or `Отменить`.
15. Open `Сигналы`.
16. Inspect `Радары`.
17. Open `Найденные сигналы`.
18. Approve, archive, reject, or edit one signal.
    Slice 1.5.1 note: expand a radar to inspect atomic search rules and optional
    sources; expand a found signal to inspect raw evidence, duplicate risk, and search
    notes. Topic/fabula matching happens later in post candidates.
    Slice 1.5.2 note: radar and signal rows are framed cabinet cards; metadata,
    evidence, and actions must stay inside the same visible entity card.
    Slice 1.5.3 note: the `Сигналы` section has its own header, stable row layout,
    separated action footers, and visual checks for spacing and column overlap.
    Slice 1.5.4 note: the header now follows the same cabinet pattern as
    `Редакционная модель`, tab counters use the shared red badge, and
    `npm run test:design` checks the layout contract.
    Slice 1.5.5 note: `+ Radar` is an ordinary white work action, not a red validation
    gate. The radar toolbar follows the same count-left/action-right pattern as topics
    and fabulas, and newly added radars keep a visible last-run fallback.
    Slice 1.5.6 note: expanding/collapsing a radar must not shift the workspace.
    `npm run test:design` checks this disclosure stability, wide-screen header metric
    alignment, and radar editor field spacing.
    Slice 1.5.7 note: editing an existing radar opens the editor inside that radar
    card. Radar rules and source values are multiline fields, so demo instructions,
    URLs, API/MCP notes, and keyword sets are not cramped into one-line inputs.
    Slice 1.5.8 note: radar setup now also includes source discovery mode and
    `Фильтры отбора`. Expand a found signal to see deterministic filter evaluations
    for author, audience, positioning, goals, forbidden topics, and topics.
19. Open `Кандидаты постов`, use the filter/search/group controls, optionally
    `Редактировать` a concept while checking its readonly signal/topic context and
    editable fabula, or `Отклонить` a weak concept, then click `Утвердить` on one card.
20. Click `Собрать инсайт`; the insight should use the approved candidate's title,
    topic, fabula, value, and risks.
21. Click `В план`.
22. In `План`, open `Настройка сетки` if you want to change period, tempo, days/times,
    candidate limits, platform, signal policy, or publication size profile; save settings before rebuilding.
    Slice 1.8.1 note: select dates directly in the mini-calendar; the counter shows
    target, selected, remaining, or extra slots while you click.
    Slice 2.11.1 note: `Размер публикации` edits demo profiles such as Telegram post,
    LinkedIn post, or LinkedIn article. Fabulas keep only compact/standard/deep scale,
    so the same `Signal X Topic X Fabula` can still be reused across platforms.
23. Switch the broadcast grid to `Календарь` to see candidate counts by publish date,
    then click a date to inspect that day's same slot cards.
24. Review the broadcast grid, expand a slot, optionally edit it with `Сохранить` or
    `Отменить`, and approve one slot.
25. Open `Редактура`; the approved slot is already in `Посты`.
26. Click `К рабочему столу`, or open `Рабочий стол` and choose the post from the picker.
27. Review the prepared `Фабула`, edit the brief if needed, then click `Утвердить фабулу`.
    Slice 1.10.4 note: the `Фабула` screen also shows read-only
    signal/topic/fabula/audience/value/goal, platform/date, confidence, evidence, and
    risks from the approved candidate and slot. Editing an approved fabula clears stale
    draft/final/release artifacts until the updated brief is approved again.
28. Review the automatically prepared draft checks and editor notes. During generation
    the `Драфт` stage shows a queued/running `DraftRun`. Inspect
    `/api/draft-runs/{id}` to see the selected-post context snapshot, context step
    summary, `sourceLedger` in step 0, source intent and `ResearchPlan` in step 1,
    public evidence URL reads plus optional OpenRouter web-search attempts in step 2.
    Public-search trace shows the built query, accepted evidence, and rejected
    citations before feasibility in
    step 3, post contract in step 4, compiled rule pack plus
    `ruleRegistrySnapshot` and `EvidenceInterpretation` in step 5, material plan in step 6, draft strategy in step 7,
    rhetorical plans in step 8, draft candidates and selection in step 9, final draft,
    final quality gate, and errors. The final quality gate shows the explicit final
    quality contract, independent review model attempts, whether the delivered draft
    was accepted as public prose, repaired through bounded final repair cycles, or
    kept unchanged because the repair regressed. If feasibility
    blocks the post, the demo shows a readable stopped-before-generation state and no
    local fallback draft is created. If candidate selection blocks the post, the trace
    scorecard shows `eligible / penalized / excluded`, penalty, and reasons, and no
    local fallback draft is created. A missing candidate link alone no longer blocks
    the demo when the source signal, brief evidence, topic, and fabula are present.
    Planning and candidate child `AiRun` ids can be inspected through
    `/api/ai-runs/{id}`. If the
    backend is unreachable, the UI marks the draft as local fallback with no recorded
    backend run.
    The source ledger now shows which claims are allowed, risky, or forbidden, while
    feasibility, post contract, and rule registry lock whether and how the post may
    be written before validators/revision. `PostContract.publicationSizeContract`
    shows the resolved size profile, target range, hard max, paragraph/section range,
    density, and fabula scale.
    Demo fabulas include a research strategy default: manual strategies copy their
    instructions into a new work brief, while auto strategies create readable research
    prompts from topic, fabula, candidate, signal, and proof needs. The workbench
    `Фабула -> Источники и исследовательские поручения` field remains the final
    per-post override.
    `Фабула -> Источники` is now shown as source intent: URLs, source names, proof
    requests, exclusions, and human-language instructions become a local research plan.
    The public-evidence step now reads exact URLs and can execute general search tasks
    through OpenRouter when backend web tools are enabled. Accepted evidence
    candidates are synthesized and merged into the DraftRun `SourceLedger`; skipped,
    failed, or rejected attempts remain warnings in the same trace before validators
    or directed revision. The `EvidenceInterpretation` trace shows implications,
    tensions, usable examples, limits, forbidden overclaims, rejected evidence uses,
    and the provider/fallback attempts that produced them. The `MaterialPlan` trace now
    shows selected evidence, rejected evidence with reasons, repair attempts,
    backup-model use, and emergency fallback if all LLM attempts ignore the enriched
    ledger.
    The `validation` trace step now contains deterministic per-candidate findings for
    size/shape, contract/CTA, attribution, rejected evidence, forbidden moves,
    publishability, and raw artifact leakage.
    The same step can also contain `LLM validation` findings for source grounding,
    publisher/author fit, topic/fabula fit, coherence/compression, and audience
    value. Positive/pass model observations are displayed separately from actionable
    findings. `Editorial critique` is shown separately from validation and attacks
    idea strength, tension, author stance, source integration, generic AI prose, and
    reader value. The same `validation` artifact also stores pairwise ranking and a
    bounded editorial revision loop: each cycle records validator repair goals,
    editorial goals, constraints, revised candidate, regression checks, old-vs-new
    comparison, dimension scores, accepted/rejected decision, rejected moves, and
    final stop reason. Long-running `publicEvidence`, `draft`, and `validation` steps also
    write nested operation progress, so the `Драфт` waiting state and
    `/ai-runs?runId=...` show the current URL/search/candidate/validator/ranking/
    revision operation instead of only a broad step name. If a late validation/revision
    provider operation fails after a usable best draft exists, the trace shows the
    failed nested operation and the demo keeps the previous best instead of staying
    stale forever. The main demo still opens one editable draft; `/ai-runs?runId=...`
    shows whether that draft came from the original winner or accepted revision-loop
    candidate. Child AI calls also show
    `modelRole`, `selectedModel`, and `modelSelectionSource`, so the trace distinguishes
    researcher, strategist, writer, review, critic, active alternative-angle policy,
    and technical backup retries.
29. In `Драфт`, inspect the version list. The machine draft is `v1`. To test the
    human loop, add a comment such as `Сделай вывод жестче и убери лишнюю
    канцелярщину`, then click `Улучшить по комментарию`; a successful writer-role
    revision creates `v2` without mutating `v1`. The version card shows the diagnostic
    quality-check status for the comment revision; open the active version summary to
    inspect matched or missed comment intent, source-marker regression, public-prose
    risks, and any internal jargon leaks. Manual textarea edits must be saved
    with `Сохранить как новую версию`, which creates a separate `manualEdit` version.
30. Select the version you want to approve, including `v1` if it is still better than
    later revisions, then click `Сделать финальной` in `Драфт`. The final text stores
    an `EditorDecisionSnapshot` with the selected version, human comments, manual edit
    count, machine trace availability, and unresolved risks.
31. Open `Визуал`, choose one visual mode (`Сгенерировать`, `Найти мем`,
    `Мем + генерация`, or `Без визуала`). For `Сгенерировать` and `Найти мем`,
    fill one local `Бриф`, click `Подготовить варианты`, select one placeholder
    variant, and approve it. For `Мем + генерация`, fill the same `Бриф`, click
    `Подготовить мемы`, choose a meme reference, click `Сгенерировать кастом`,
    select a final remix variant, and approve it. `Без визуала` remains a direct
    explicit decision.
32. Open `Выпуск` to inspect the publication log or, until integrations exist, the
    compatibility manual export surface.
33. Open `Аналитика`.
34. Click `Подготовить аналитику`.
35. Enter manual metrics and editorial conclusions.
36. Click `Зафиксировать выводы`.
37. Reload the page to confirm state persists.
39. Use `Сбросить демо` to restore the seeded AI Product Manager scenario.

## Reference Materials

The supplied design handoff is available in `ui-design-systems/`.

Useful reference entry points:

- `ui-design-systems/spec-previews/index.html`
- `ui-design-systems/ui-kit/glavred-app/index.html`
- `ui-design-systems/ui-kit/marketing-site/index.html`

These are reference prototypes and design materials, not production code.

## Next Demo Step

The SaaS-style blog portfolio benchmark is now seeded:

1. Add a local user/project switcher. Done.
2. Seed two users and three independent blogs. Done.
3. Give each blog its own author memory, editorial model, source examples, plan slots,
   and benchmark scenarios. Done.
4. Use the portfolio to test project isolation, author voice preservation, research
   depth, and multi-platform adaptation. In progress through future benchmark runner
   and multi-platform slices.

Real provider-backed drafts already exist through the local backend/OpenRouter path.
Backend auth, publication automation, platform metrics, real attachment parsing, and
broader AI analysis remain later steps.
