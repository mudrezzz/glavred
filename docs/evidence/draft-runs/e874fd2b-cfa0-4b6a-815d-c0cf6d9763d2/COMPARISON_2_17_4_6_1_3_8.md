# Сравнение после writer / alternative-angle dossier migration

## Контрольные запуски

- исторический baseline: `e874fd2b-cfa0-4b6a-815d-c0cf6d9763d2`;
- checkpoint после planning migration: `c2303e05-e7d0-4cad-a3f9-6ea26fc1a3ed`;
- промежуточный quality proof: `aefc9064-582d-48e0-9595-901f7b602168`;
- финальный runtime/budget proof: `72b3a2df-c8be-41a8-b2c0-e74e5e502cd0`;
- slice: `2.17.4.6.1.3.8`.

Все запуски используют один и тот же контрольный DraftRun payload. Известный входной
дефект CTA с символами `?` присутствовал уже в baseline и не считается регрессией
dossier-миграции.

## Что доказано

`draftCandidate`, `alternativeAngleRoute` и `alternativeAngleCandidate` больше не
получают полный planning stack, полный `rulePack`, `SourceLedger`, `ArticleDossier`,
`ContextPack`, старые operation envelopes или вложенные budgets. Их provider input
строится из role-owned dossier, сохраняет handles и проходит прямой current-call
`payloadBudget`.

| Операция | Baseline | Checkpoint 3.7 | Proof 3.8 | Снижение к baseline | Budget verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `draftCandidate` | 323 888-323 946 | 268 026-268 091 | 16 256-16 533 | примерно 94,9% | `directlyBudgeted` |
| `alternativeAngleRoute` | 262 166 | 228 651 | 18 386 | примерно 93,0% | `directlyBudgeted` |
| `alternativeAngleCandidate` | 323 757 | 268 126 | 16 534 | примерно 94,9% | `directlyBudgeted` |

Direct budget proof по финальному proof-run:

- `draftCandidate`: `527b9110-778c-4132-b363-50d367ae0b2d`, `45585b88-4bd2-4a54-bda9-034383d129d3`, `e41ca74c-e06d-4c5f-8a85-f98333ff0261`;
- `alternativeAngleRoute`: `d03ae334-59ee-47f2-8400-de1cc7f6eb67`;
- `alternativeAngleCandidate`: `c8792432-851a-4329-a623-bca0ab3f9a01`.

Для всех трех семейств:

- `runtimeMigrated=true`;
- unresolved handles: `0`;
- forbidden field violations: `0`;
- `missingDirectBudget`, `nestedBudgetFalsePositive`, `payloadTooLarge`,
  `contextOverBudget`: `0`;
- `DEGRADED` связан только с optional trimming, missing required inputs: `0`.

## Качество результата

| Показатель | Baseline `e874...` | Checkpoint `c230...` | Quality proof `aefc...` | Final proof `72b3...` |
| --- | --- | --- | --- | --- |
| Pipeline | `succeeded` | `succeeded` | `succeeded` | `succeeded` |
| Evidence coverage | `weak` | `sufficient` | `sufficient` | `sufficient` |
| Fallback-interpreted evidence | `1` | `0` | `0` | `0` |
| Editorial status | `needsHumanReview` | `publishable` | `publishable` | `needsHumanReview` |
| Overall verdict | `needsAttention` | `degradedSuccess` | `degradedSuccess` | `needsAttention` |
| Open critical / warning | `1 / 19` | `0 / 0` | `0 / 0` | `3 / 22` |
| Final draft chars | `9 482` | `5 913` | `9 028` | `9 323` |

Редакционно `72b3...` не хуже baseline как текст: есть конкретная сцена инженера
ТОиР, рабочие источники, decision surface, ограничения применимости и
человеческий контур принятия решения. Он ближе к `aefc...` по плотности и
практической конкретности, чем к baseline.

Но `72b3...` не считается clean quality proof: `qualityFidelity.issueLifecycle`
сохраняет open critical из validation reports для промежуточных и проигравших
кандидатов, включая `candidate-contrast` с `Draft is 10939 chars, above hard max
10240`. Финальный текст `72b3...` имеет `9 323` символа и сам не превышает
`hardMaxChars=10240`; final gate выдал только `warning` по числу абзацев.

Вывод: это не потеря writer dossier context и не regression от compact input. Это
оставшийся долг следующего slice `2.17.4.6.1.3.9`: review/ranking/final-gate
dossier migration и lifecycle должны отделить финально выбранный/отремонтированный
текст от промежуточных и проигравших candidate reports.

## Storage incident

Во время первого финального proof-run `1bc2dbe7-5d78-41d4-9c69-91105302c0e9`
прямое чтение `var/glavred-ai-runs.sqlite3` с Windows-хоста во время Docker-записи
завершилось `database disk image is malformed`. Поврежденная ignored runtime DB
сохранена как `var/glavred-ai-runs.sqlite3.corrupt-20260710-221934`.

Повторный proof-run `72b3...` выполнялся с чистой `ai-runs` DB, одним worker и без
host-side SQLite чтения во время активной записи. После завершения:

- `draftRuns` integrity: `ok`;
- `aiRuns` integrity: `ok`.

Это фиксирует дополнительное operational правило: во время live Docker DraftRun на
Windows bind mount нужно смотреть прогресс через API/логи, а прямые host-side
SQLite audits запускать после terminal status.

## Вердикт по slice 3.8

Writer / alternative-angle dossier migration работает в реальном runtime:
provider-входы стали меньше примерно на 93-95%, все три целевые операции имеют
direct budget proof, handles разрешаются, запрещенные полные артефакты не уходят
провайдеру, pipeline дошел до `complete`.

Полная редакционная приемка результата остается заблокирована не этим slice, а
следующим review/ranking/final-gate слоем `2.17.4.6.1.3.9`. Поэтому 3.8 закрывает
provider-input migration proof, но не объявляет `72b3...` чистым публикационным
результатом.
