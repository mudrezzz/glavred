# Production flow

Production flow начинается после авторской памяти. В текущем demo он показывает, как
сигнал превращается в инсайт, элемент плана, редакционный пост, утвержденный текст,
визуальное решение и состояние готовности к выпуску.

Рабочая цепочка:

`Сигналы -> Кандидаты постов -> Инсайт -> Сетка вещания -> Редактура -> Фабула -> Драфт -> Визуал -> Готов к выпуску`

Note: this page documents the current local-first demo flow. `Сигналы` is implemented
as a radar, signal-review, and first post-candidate workspace. `Кандидаты постов`
creates deterministic review cards from approved signals with filtering, search,
grouping, edit/reject, and approve actions; the current grid remains a working
prototype for slot approval and downstream production.

Slice 1.8.1 note: `План` now follows the same cabinet list pattern as review queues.
Filters/search and `Список / Группы` sit above slots, expanded slots keep candidate
context visible, and `Настройка сетки` uses a clickable mini-calendar for selecting
explicit publish slots before rebuilding.

Slice 1.8.2 note: the same filter toolbar now also has `Календарь`. It reuses the
week/month/quarter period from grid settings, shows candidate counts on publish dates,
and opens the same broadcast slot rows below the clicked date.

![Утвержденная фабула](assets/screenshots/05-approved-post-brief.png)

## Сигналы

В `Сигналы` пользователь видит радары, найденные сигналы и `Кандидаты постов`. В демо
это материал из памяти автора, архива, внешних источников и ручного исследования про
AI-B2B adoption, evals, trust loop и rollout.

Сигнал можно утвердить, отредактировать, отправить в архив или отклонить. Только
утвержденный сигнал попадает в candidate assembly.

В `Кандидаты постов` Glavred показывает 2-3 deterministic сборки: сигнал, тема, фабула,
аудитория, ценность, цель, платформа, confidence и risks. Пользователь может
фильтровать, искать, группировать, редактировать или отклонять кандидатов, затем
утверждает один кандидат; он становится текущим концептом для `Собрать инсайт`.

Кнопка `Собрать инсайт` создает deterministic insight card из утвержденного кандидата:
почему это важно, для кого релевантно, где позиция автора и какие риски или фактические
gaps видны.

## План

Из инсайта создается гибридная сетка вещания: `Настройка сетки` задает период, темп,
дни/время публикаций, платформу, лимиты кандидатов и политику выбора сигналов, а
deterministic planning заполняет publish-window slots темой и фабулой. Gate 1 остается
человеческим: пользователь раскрывает конкретный слот и явно нажимает `Утвердить`.

Правая панель `Сетка вещания` показывает распределение тем/фабул и advisory warnings,
если ручная сетка выходит за declared weights или нарушает матрицу совместимости. Она
также разделяет доступных кандидатов и утвержденные концепты, чтобы показать
дефицит/профицит для выбранной сетки.

## Фабула

После утверждения слота система готовит `PostBrief`: тезис, конфликт, позицию автора,
evidence, примеры, структуру, CTA, источники и риски.

Gate 2 останавливает flow на утвержденной фабуле. Это важно: система может
предложить режиссуру поста, но автор утверждает ее сам.

Slice 1.9 note: approved plan slots now enter `Редактура` as an editorial work queue.
The selected-post workbench sits below the queue and owns production work for the
chosen post.

Slice 1.10 note: approving a plan slot now creates or updates the editorial work item
and prepares the initial post brief immediately. `Редактура` is split into `Посты`
and `Рабочий стол`: use `Посты` for queue review and `К рабочему столу`, then edit the
selected post inside the workbench.

Slice 1.10.4 note: the `Фабула` stage shows read-only candidate/slot context and lets
the author edit the `PostBrief` fields before approval. Editing an already approved
fabula invalidates stale draft, checks, final text, release, and learning artifacts,
then returns the selected post to `Фабула`.

Slice 1.10.5-1.10.7 note: `Финал` is no longer the target user-facing stage. Text is
edited and approved in `Драфт`; after text approval the post moves to `Визуал`.
Visual modes follow `Бриф -> Подготовить варианты -> Выбрать -> Утвердить визуал`;
`Мем + генерация` splits the middle step into `Подготовить мемы -> Выбрать мем ->
Сгенерировать кастом -> Выбрать`; `без визуала` remains the only direct shortcut.
The post becomes `готов к выпуску` only when text is approved and the visual is
approved or explicitly skipped.

Slice 1.11 note: `Выпуск` is a publication log, not a preparation workbench. It records
ready posts, publication attempts, statuses, external links, platform errors, and
retry notes. Until platform integrations exist, manual export remains compatibility
behavior.

Slice 2.3.2 note: draft generation is visible and auditable. After `????????? ??????`,
`?????` shows a pending state until the backend responds. Completed drafts show whether
they came from OpenRouter, backend deterministic fallback, or frontend local emergency
fallback. Backend-recorded drafts include an `AiRun ID`; use `/api/ai-runs/{id}` to
inspect sanitized prompt messages, provider metadata, generated body, and fallback/error
context.

## Ограничения текущего demo

- Инсайт, план и фабула создаются deterministic-сервисами.
- Реального мониторинга источников пока нет.
- Реальных AI-вызовов пока нет.
- Редакционная модель уже использует manual validator cards: после `Проверить`
  видны score, red/yellow/green status, evidence и suggested fixes для авторской
  позиции, anti-AI стиля, ценности аудитории, целей и матрицы тем/фабул.
