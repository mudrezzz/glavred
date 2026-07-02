# Опытный цех «Сборочная» Project Blueprint

This document defines the current demo/benchmark contract for the former
`AI Design Patterns` blog project. The technical project id stays
`project-ai-design-patterns`, but the user-facing project is now:

`Опытный цех «Сборочная»`

The document is written in Glavred product entities so the project can be loaded into
fixtures and, later, into real project tables without losing ownership boundaries.

## 1. Project Concept

`Опытный цех «Сборочная»` is a Russian, Telegram-first industrial AI publication for
client attraction through visible expertise.

The blog is not about AI in general. It is about applied AI for industry: maintenance,
EAM, diagnostics, production data, regulations, reliability contours, and real
decision support.

The core metaphor is not magic, hype, or a generic software catalog. It is an
experimental workshop:

- industrial AI ideas enter the workshop as raw artifacts;
- cases, papers, OSS projects, and internal field notes go onto the test stand;
- the output is a usable pattern, anti-pattern, protocol, boundary, or RFC question;
- the community is invited to critique and improve the pattern book.

Editorial promise:

> We assemble industrial AI practice into tested patterns: with evidence, limits,
> implementation criteria, and enough skepticism to be useful outside a demo.

The long-term asset is an OSS/community pattern book inspired by GoF, POSA, and
Fowler, but adapted for industrial AI and written as a living workshop journal.

## 2. Project Profile

- Technical id: `project-ai-design-patterns`
- User-facing name: `Опытный цех «Сборочная»`
- Compatibility name: former `AI Design Patterns`
- Language: `ru`
- Primary channel: Telegram
- Business role: expertise-led client attraction
- Benchmark role: industrial AI pattern-quality benchmark
- Future asset: OSS/community industrial AI pattern book

## 3. Author Image

The author is a practitioner of industrial AI product design and applied AI
architecture.

He writes as a workshop lead, not as a trend commentator:

- has field context in AI for ТОиР/EAM, diagnostics, production data, and industrial
  decision support;
- understands that a model is only one part of a controlled contour;
- treats claims as artifacts that need sources, tests, limits, and operating criteria;
- is curious and open to dispute, but allergic to empty AI news and vendor gloss;
- wants clients to see engineering judgment, not just content production.

The author should sound like a person who has opened the hood, inspected the parts,
found the weak assembly, and can explain what should be rebuilt.

## 4. Goals

The blog exists to:

- attract clients who need practical industrial AI expertise, not AI theater;
- show that reliable industrial AI requires product, data, process, and reliability
  engineering;
- build a public pattern language for industrial AI applications;
- invite expert discussion and community co-authorship around the pattern book;
- make the author's expertise visible through concrete analysis, not self-promotion.

Every issue should support at least one of these goals.

## 5. Audience

The primary audience:

- leaders of industrial digital transformation;
- CDO/CIO/CTO roles in industrial and B2B technology companies;
- product leaders building AI-enabled industrial products;
- ТОиР/EAM practitioners and maintenance transformation teams;
- AI architects and engineering teams building reliable applied AI systems;
- clients who suspect they need AI, but want a grounded industrial implementation
  path instead of a model demo.

The reader comes for:

- non-obvious industrial AI cases;
- architecture patterns that survive real constraints;
- evidence and limits;
- implementation criteria;
- a language for discussing AI with engineers, operations, product, and management.

## 6. Positioning

`Опытный цех «Сборочная»` is not:

- AI news;
- a model leaderboard;
- a list of tools;
- vendor marketing;
- a mystical story about AI;
- an academic paper review for its own sake.

It is a workshop for turning scattered industrial AI practice into named and reusable
patterns.

Positioning principles:

- Industrial AI starts with a decision, role, process, data, and responsibility.
- The model is one part of the assembly, not the hero.
- Hybrid contours matter: GenAI, diagnostics, rules, regulations, optimization,
  knowledge graphs, and HITL.
- Strong claims need evidence or an explicit hypothesis marker.
- Good industrial AI patterns include failure modes and conditions of use.

## 7. Style

Voice:

- energetic, precise, workshop-like;
- confident but not dogmatic;
- alive enough for Telegram, specific enough for technical readers;
- inviting criticism and co-authorship.

Language:

- use the workshop metaphor consistently: цех, сборка, стенд, протокол испытаний,
  допуск, дефект, партия паттернов, контрольный образец;
- do not force the metaphor into every sentence;
- avoid mystical vocabulary as the public frame;
- explain English technical terms when they carry the idea better than a weak
  translation.

Public post shape should normally produce one clear artifact:

- pattern;
- anti-pattern;
- test protocol;
- implementation criterion;
- architecture boundary;
- RFC/community question.

This is a style and output-quality rule, not the author image.

## 8. Forbidden Moves

- Publish a tool or model announcement without extracting an industrial AI pattern.
- Promise autonomous AI without HITL, validation, and responsibility boundaries.
- Turn a post into a generic AI productivity thread.
- Retell a vendor case without mechanism, data, role, limitation, or result.
- Use internal Glavred pipeline jargon as public prose.
- Present unverified hypotheses as proven practice.
- Collapse every topic into the same `pattern card` structure when a failure story,
  protocol, field note, or digest would be stronger.

## 9. Author Memory

Seeded memory should include these durable positions:

- Industrial AI is designed around a decision, not around a model.
- The system should augment engineers, not replace them.
- Reliable industrial AI is hybrid: GenAI, diagnostics, rules, regulations,
  optimization, knowledge graph, and HITL.
- A useful AI pattern is a tested assembly: mechanism, context, limits, and criteria.
- The future pattern book should be a community artifact, not a one-author dogma.
- The existing `https://t.me/ai_product_mgmt` channel is author-validated material,
  not a template to copy.

Private user documents must be paraphrased into public-safe notes. The repository must
not contain the original PDF text or full private materials.

## 10. Editorial Rules

Canonical UI-visible Publisher blocks are `editorialRules`, not only free-text
`EditorialModel` summaries.

Required active groups:

- `author`: workshop lead / industrial AI practitioner.
- `audience`: industrial and B2B teams who need reliable AI systems.
- `goal`: client attraction, pattern book, and mature industrial AI framing.
- `positioning`: industrial AI workshop, not AI news or model-first hype.
- `styleVoice` / `styleLanguage`: reusable output, evidence plus limits, and a
  practical workshop voice.

## 11. Topics

Topics are territories. They define what the blog studies, not the story form.

### Промышленные артефакты

Cases and objects from the industrial floor: ТОиР, EAM, diagnostics, equipment
passports, work orders, defects, spare parts, RCA, and maintenance events.

### Контуры надежности

How industrial AI remains controlled: validation, fallback, traceability, evidence,
HITL, safety boundaries, and responsibility.

### Гибридная сборка

How different components assemble into a working AI contour: LLM, ML diagnostics,
rules, regulations, knowledge graph, optimization, tools, workflow.

### Данные как сырье

The raw material of industrial AI: classifications, event logs, documents,
regulations, defect codes, equipment hierarchy, data quality, and provenance.

### Полигон внедрения

Where patterns meet reality: pilots, economics, adoption, roles, operational change,
integration with EAM/ERP/CRM, and measurable success criteria.

### Открытый каталог паттернов

The community pattern book itself: naming, dispute, RFCs, examples, anti-patterns,
digest updates, and future OSS collaboration.

## 12. Fabulas

Fabulas are reusable narrative mechanics. They must be able to work across several
topics.

### Карточка паттерна

Situation -> recurring problem -> named pattern -> mechanism -> source/example ->
where it works -> where it breaks -> what we take into practice.

### Протокол испытаний

Claim or tool -> test stand -> input data/conditions -> observed behavior -> failure
modes -> admissible use -> decision.

### Разбор артефакта

Case, paper, OSS repository, or product artifact -> what it is -> embodied pattern ->
useful parts -> limits -> industrial application.

### Полевой отчет из цеха

Concrete scene -> observation -> why it matters -> principle -> practical move.

### Анти-паттерн

Common seductive move -> why it looks reasonable -> how it fails in industry -> safer
assembly -> check before use.

### Журнал испытаний

Periodic digest: confirmed patterns, candidate patterns, disputed patterns,
anti-patterns, source queue, and community questions.

## 13. Topic x Fabula Matrix

The matrix is curated, not all-to-all and not one-to-one.

- `Промышленные артефакты`: `Карточка паттерна`, `Протокол испытаний`,
  `Полевой отчет из цеха`.
- `Контуры надежности`: `Карточка паттерна`, `Протокол испытаний`, `Анти-паттерн`.
- `Гибридная сборка`: `Карточка паттерна`, `Разбор артефакта`, `Анти-паттерн`.
- `Данные как сырье`: `Карточка паттерна`, `Полевой отчет из цеха`,
  `Анти-паттерн`.
- `Полигон внедрения`: `Протокол испытаний`, `Полевой отчет из цеха`,
  `Анти-паттерн`.
- `Открытый каталог паттернов`: `Карточка паттерна`, `Разбор артефакта`,
  `Журнал испытаний`.

## 14. Publication Channels

### Telegram

- Role: primary
- Language: Russian
- Size profile: `telegram-post`
- Content expectation: energetic, concrete, practical, and distinct enough to show
  expertise.

### GitHub Pattern Book

- Role: experiment
- Status: paused in v1
- Purpose: future community pattern book, not active publishing in this slice.

Channels store destination mechanics only. Project audience stays in Publisher /
editorial rules.

## 15. Source Signals and Radars

Radars should seek:

- industrial AI cases with data, roles, limits, and results;
- papers and reports about patterns/frameworks, not model leaderboards;
- OSS/frameworks that embody reusable architecture patterns;
- sanitized author materials about applied AI for ТОиР and AI Product Management.

The first seeded signal is `Maintenance Decision Intelligence Workbench`: a pattern
where the system collects ТОиР data, explains confidence, surfaces sources, and leaves
the final decision to an engineer.

## 16. Ready Scenario

Ready benchmark scenario:

- Topic: `Промышленные артефакты`
- Fabula: `Карточка паттерна`
- Signal: `Maintenance Decision Intelligence Workbench`
- Channel: Telegram
- Expected output: a Russian Telegram post that presents a concrete industrial AI
  pattern, not a generic AI promise.

## 17. Benchmark Expectations

A good generated post:

- stays in industrial AI;
- names a reusable pattern or anti-pattern;
- uses source/evidence material without dumping it;
- distinguishes proven practice from author hypothesis;
- shows client-attracting expertise;
- invites expert discussion instead of closing the topic with dogma.

A bad generated post:

- is generic AI news;
- centers model comparison without industrial context;
- promises autonomous AI without HITL and controls;
- lists tools without an implementation pattern;
- sounds like vendor marketing;
- loses the workshop identity.

## 18. Fixture Mapping

The fixture maps this blueprint to:

- `ProjectProfile`;
- `EditorialModel`;
- `AuthorNote[]`;
- `EditorialRule[]`;
- `Topic[]`;
- `Fabula[]`;
- `TopicFabulaMatrixEntry[]`;
- `RadarDefinition[]`;
- `SourceSignal[]`;
- `PublicationChannel[]`;
- one ready-to-run `ContentPlanItem`.

`PublicationChannel[]` stores destination, handle, language, role, publishing mode,
status, and default size/profile only. Project audience stays in the `Audience`
editorial rules above; channels must not duplicate it.
