# Северная стена Project Blueprint

This document defines the current demo/benchmark contract for the `Северная стена`
blog project. It is written in Glavred product entities so the concept can be loaded
into project fixtures and later into real project tables.

The technical project id remains `project-kasha-iz-topora` for compatibility with
existing portfolio memberships and snapshots. The user-facing project name is
`Северная стена`.

## 1. Project Concept

`Северная стена` is a Russian, Telegram-first blog about engineering complex B2B
sales systems.

The business goal is client attraction through visible expertise: the reader should
recognize their own commercial chaos, see that the author can turn it into a route,
and want to stand next to this team on a difficult climb.

The editorial promise:

> Как проводить сложные B2B-сделки через туман, закупки, ЛПР, CRM-хаос и внутреннюю
> политику клиента.

The blog is not about seller motivation, sales charisma, or generic RevOps theory.
It is about route design for complex B2B deals: client relief, value, decision roles,
sales materials, CRM discipline, forecast, ABM, product marketing, and the rope team
between sales, marketing, product, and implementation.

AI is allowed only as light gear: useful acceleration for account research, CRM
hygiene, call review, materials, and analytics. It must not become the main topic or
a magic replacement for commercial judgment.

## 2. Project Profile

- Name: `Северная стена`
- Language: `ru`
- Primary channel: Telegram
- Business role: consulting client attraction
- Benchmark role: complex B2B / RevOps voice benchmark
- Core metaphor: alpine climb
- Technical id: `project-kasha-iz-topora`

## 3. Goals

The project goals are explicit business and editorial goals, not generic content
production goals:

- attract consulting/project clients who need a manageable system for complex B2B
  sales, not another sales training;
- explain why the market has matured for RevOps and when a company has already
  outgrown heroic seller-driven sales;
- show that strong complex sales are engineered through process, evidence, CRM,
  sales materials, ABM, product marketing, and product/sales/marketing alignment;
- demonstrate practical expertise without sounding like a large expensive consulting
  firm;
- show AI as acceleration for commercial operations, but never as the main story or
  a substitute for experience;
- make the reader think: "these people have already climbed my wall."

## 4. Audience

Primary readers:

- B2B founders whose enterprise deals stall after a demo or proposal;
- commercial directors and heads of sales who see CRM stages but not real deal
  movement;
- RevOps, product marketing, and product leaders who need sales, marketing, and
  product to work as one rope team;
- teams selling complex industrial, enterprise, or technical products where the
  client buys process change, not a boxed feature.

This section owns reader segment and buying context only. It must not contain style
rules such as "start with recognizable pain". Such rules belong to `Voice`, `Fabula`
or `EditorialRule`, depending on whether they apply to every post or only to a
specific dramaturgy.

Why they read:

- the posts name the pain they live with every week;
- the tone is field-level and alive, not a consulting textbook;
- the blog turns vague RevOps into visible mechanisms: route, gear, belay, roles,
  proof, next step;
- the reader gets language for explaining why "we sent a proposal" is not a deal
  strategy.

Why they contact the team:

- they see that the team can enter commercial fog quickly;
- they see concrete route-building competence, not abstract advice;
- they see a pragmatic, fast, reasonably priced alternative to heavy consulting;
- they see AI used as acceleration, but filtered through field expertise.

## 5. Editorial Model

### Author

The author is a practitioner of commercializing complex technical B2B products. He
has worked at the junction of product, sales, product marketing, presale,
implementation, CRM discipline, and industrial / enterprise client contexts.

He writes from field experience: how a product becomes value, how a deal passes
through LPRs, procurement, economics, materials, internal client politics and
implementation risk. The author is not a sales coach and not a detached big-consulting
methodologist. The author is a member of a small fast team that can enter commercial
fog, map the relief, assemble the route, and build the belay system.

The public persona: a calm but sharp route leader. He has enough altitude experience
to joke, argue, and simplify, but he does not romanticize chaos or seller heroics.

### Positioning

`Северная стена` shows how to run complex B2B deals through fog, procurement,
decision makers, CRM chaos, and client politics without McKinsey tone and without
faith in lone seller heroics.

### Voice

- energetic field notes;
- one alpine metaphor, never mixed with pilot or military jargon;
- humorous and sharp, but not cynical;
- expert without becoming expensive-consultant theater;
- practical: every post should leave the reader with a route checkpoint, gear item,
  belay rule, or decision criterion.
- when the fabula is a field note or practical breakdown, start with a recognizable
  deal situation: a stalled deal, dead proposal, CRM forecast fiction, procurement
  fork, tired internal champion, or missing decision owner.

### Forbidden Moves

- student handbook explanations of RevOps, ABM, CRM, BANT, or product marketing;
- seller motivation, charisma coaching, or "hire better salespeople";
- mixed metaphors such as cockpit, fighter pilot, battle, and summit in one frame;
- AI hype as a replacement for commercial discipline;
- generic consulting memo tone.

## 6. Author Memory

Seeded memory should include these durable positions:

- A deal usually does not "stall"; it loses the route.
- Complex B2B is a rope team: sales, marketing, product, and implementation must
  move together.
- Sales materials are gear, not decoration: proposal, one-pager, battlecard,
  account brief, and demo must help the client pass the next section of the route.
- CRM should work as belay: stage criteria, owner, risk, evidence, next step,
  forecast discipline.
- AI is light gear: it reduces weight and speeds preparation, but it does not choose
  the route.

Private user-provided documents are paraphrased into public-safe notes. The repository
must not contain the original PDF text or full private materials.

The public Telegram channel `https://t.me/minqly` may be used as author-validated
tone inspiration, not as copied post source.

## 7. Topics

### Маршрут сложной сделки

How deals move through market, account, decision roles, value, economics,
procurement, implementation, and feedback. The point is to replace CRM-stage theater
with a route map.

### Рельеф клиента

Client decision terrain: LPR, influencers, procurement, finance, engineering risks,
internal politics, and the internal champion who has to climb with your material.

### Снаряжение продаж

Sales enablement as route gear: proposal, one-pager, demo, battlecard, account brief,
role-specific proof, and next-step material.

### Страховка RevOps

CRM discipline, BANT+, stage criteria, forecast, pipeline hygiene, ABM, and
sales-marketing-product alignment as belay for complex deals.

## 8. Fabulas

### Полевая записка с маршрута

One recognizable scene from a complex deal: where the team lost the route, which
client relief was ignored, and what belay should be added.

This fabula should normally start with recognizable pain. That opening rule belongs
here because it is dramaturgical, not an audience definition.

### Проверка снаряжения

One sales enablement artifact under load: proposal, battlecard, account brief, demo,
or CRM field. The question is whether it helps the deal move.

### RevOps без тумана

Explain one RevOps mechanism through a deal route, not through a textbook definition.

### Разбор вершины

Longer case-style breakdown from market to implementation, used when the post needs
deep research and several source signals.

## 9. Publication Channels

### Telegram

- Role: primary
- Language: Russian
- Size profile: `telegram-post`
- Content expectation: alive, concrete, witty, field-tested.

Publication channels do not own the project audience. The audience is centralized in
`EditorialModel.audience` / project editorial settings. Channel settings own
destination, language, role, publishing mode, and default size/profile choices.

No multi-platform generation or publishing adapter is introduced in this project
rework slice.

## 10. Source Signals and Radars

Radars should seek:

- complex B2B sales failures with visible route loss;
- RevOps, ABM, CRM, forecast, and sales enablement practices that can be translated
  into route/gear/belay language;
- public cases and best practices from enterprise sales and product marketing;
- author memory from validated posts and sanitized team materials.

The first seeded signal is `Сделка не зависла. Она потеряла маршрут`: a post about
why the CRM stage "proposal sent" often hides procurement, economics, decision-maker,
and internal champion risks.

## 11. Benchmark Expectations

A good generated post for this project should:

- start from pain a founder/commercial leader recognizes;
- use only alpine metaphor language;
- show route, gear, or belay as a practical mechanism;
- connect sales, marketing, product, and implementation;
- sound expert, fast, and human;
- create consulting demand without direct hard selling.

A bad generated post:

- reads like a student RevOps summary;
- mixes cockpit, battle, and climb metaphors;
- gives generic sales motivation;
- makes AI the main hero;
- sounds like a big consulting slide deck.

## 12. Slice 2.17.4.2 Fixture Mapping

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
