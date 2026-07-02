# AI Design Patterns Project Blueprint

This document defines the current demo/benchmark contract for the `AI Design Patterns`
blog project. It is intentionally written in Glavred product entities, so the concept
can be loaded into project fixtures and later into real project tables.

## 1. Project Concept

`AI Design Patterns` is no longer a generic AI engineering publication. It is a
Russian, Telegram-first industrial AI blog whose product goal is client attraction
through visible expertise.

The editorial promise:

> We collect an open pattern book about how to build reliable AI applications for
> industry: not around the model, but around decisions, data, checks, constraints,
> and the human in the loop.

The project narrows the AI topic to industrial contexts: maintenance, EAM, equipment
diagnostics, production data quality, industrial decision support, and applied AI
architecture.

## 2. Project Profile

- Name: `AI Design Patterns`
- Language: `ru`
- Primary channel: Telegram
- Business role: expertise-led client attraction
- Benchmark role: industrial AI pattern-quality benchmark
- Future asset: OSS/community `industrial-ai-patterns` pattern book

## 3. Editorial Model

### Author

The author is an industrial AI / AI Product Management practitioner who curates
repeatable design patterns from field knowledge, source material, OSS, papers, and
public cases.

### Audience

- industrial digital transformation leaders;
- CDO/CIO;
- product leaders in B2B industrial software;
- maintenance / EAM / ТОиР practitioners;
- AI architects and engineering teams building reliable applied AI systems.

### Positioning

The blog is not an AI news channel. It turns noisy practice into named industrial AI
patterns with evidence, limits, implementation hints, and community discussion.

### Editorial Rules

- Stay inside industrial AI unless a general AI pattern is explicitly translated to
  industrial use.
- Every post should produce a reusable pattern, anti-pattern, criterion, architecture
  boundary, or RFC question.
- Strong claims require a source, case, benchmark, OSS example, or explicit
  author-hypothesis marker.
- Tone is confident but not dogmatic: criticism and co-authorship are part of the
  format.

## 4. Author Memory

Seeded memory should include these durable positions:

- Industrial AI is designed around a decision, not a model.
- The system should augment engineers, not replace them.
- Reliable industrial AI is hybrid: GenAI, diagnostics, rules, regulations,
  optimization, knowledge graph, and HITL.
- The project should grow into an OSS/community pattern book inspired by GoF, POSA,
  and Fowler, but adapted for industrial AI.
- The existing `https://t.me/ai_product_mgmt` channel is author-validated material,
  not a template to copy.

Private user documents must be paraphrased into public-safe notes. The repository must
not contain the original PDF text or full private materials.

## 5. Topics

### Decision Intelligence for ТОиР

AI helps maintenance engineers assemble data, understand events, find similar cases,
build RCA, and choose the next action. The key claim: industrial AI starts with
decision support, source visibility, and human responsibility.

### Hybrid AI Architecture

Industrial AI is not one LLM. It is a controlled contour combining GenAI,
ML/diagnostics, rules, regulations, knowledge graph, optimization, and human review.

### Live Industrial AI Cases

Case selection should prefer non-obvious, mechanism-rich examples: equipment
passporting, classification of defects and work types, data quality control, similar
failure search, diagnostics event interpretation, AI planning, RCA assistants, EAM
survey agents, call/request analysis, and training simulators.

### OSS Pattern Book

The blog gradually becomes an invitation to build a community pattern book: pattern
cards, critique, examples, disputed sections, and future pull requests.

## 6. Fabulas

### Pattern Card

Structure:

1. Situation
2. Pattern
3. Mechanism
4. Example or source
5. Where it works
6. Where it breaks
7. What we take into practice

### Industrial Case Breakdown

Structure:

1. Case
2. Data and roles
3. AI mechanism
4. What changed
5. Limits
6. Pattern for the book

### Paper / Benchmark Review

Must not become a model leaderboard. The review should answer: which pattern becomes
more useful for industrial AI practice because of this paper/report/benchmark?

### Monthly Pattern Book Digest

Separates:

- confirmed patterns;
- candidate patterns;
- disputed patterns;
- anti-patterns;
- questions for the community.

### OSS / Framework Teardown

Looks at a repository or framework as an embodied pattern, not as a tool announcement.

## 7. Publication Channels

### Telegram

- Role: primary
- Language: Russian
- Size profile: `telegram-post`
- Content expectation: energetic, concrete, practical, with enough detail to show
  expertise.

### GitHub Pattern Book

- Role: experiment
- Status: paused in v1
- Purpose: future community pattern book, not active publishing in this slice.

## 8. Source Signals and Radars

Radars should seek:

- industrial AI cases with data, roles, limits, and results;
- papers and reports about patterns/frameworks, not model leaderboards;
- OSS/frameworks that embody a reusable architecture pattern;
- sanitized author materials about applied AI for ТОиР and AI Product Management.

The first seeded signal is `Maintenance Decision Intelligence Workbench`: a pattern
where the system collects ТОиР data, explains confidence, surfaces sources, and leaves
the final decision to an engineer.

## 9. Benchmark Expectations

A good generated post for this project should:

- stay in industrial AI;
- name a reusable pattern;
- use source/evidence material without dumping it;
- distinguish proven practice from author hypothesis;
- show client-attracting expertise;
- invite expert discussion instead of closing the topic with dogma.

A bad generated post:

- is generic AI news;
- centers model comparison without industrial context;
- promises autonomous AI without HITL and controls;
- lists tools without an implementation pattern;
- sounds like vendor marketing.

## 10. Slice 2.17.4.1 Fixture Mapping

The slice maps this blueprint to:

- `ProjectProfile`;
- `EditorialModel`;
- `AuthorNote[]`;
- `EditorialRule[]`;
- `Topic[]`;
- `Fabula[]`;
- `RadarDefinition[]`;
- `SourceSignal[]`;
- `PublicationChannel[]`;
- one ready-to-run `ContentPlanItem`.

`PublicationChannel[]` stores destination, handle, language, role, publishing mode,
status, and default size/profile only. Project audience stays in the `Audience`
editorial rules above; channels must not duplicate it.

Future project rework slices should follow the same document-first pattern for
`Северная стена` and `Блог Главреда`.
