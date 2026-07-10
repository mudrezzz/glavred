# Сравнение после planning dossier migration

## Контрольные запуски

- baseline: `e874fd2b-cfa0-4b6a-815d-c0cf6d9763d2`;
- принятый live proof: `c2303e05-e7d0-4cad-a3f9-6ea26fc1a3ed`;
- slice: `2.17.4.6.1.3.7`.

Оба запуска используют один и тот же сохраненный request payload. Известный дефект
CTA с символами `?` присутствовал уже во входе baseline и исключен из оценки
регрессии dossier-архитектуры.

## Размер provider-контекста

| Операция | Baseline | После миграции | Снижение | Budget verdict |
| --- | ---: | ---: | ---: | --- |
| `materialPlan` | 207 065 | 14 900 | 92,8% | `directlyBudgeted` |
| `strategy` | 210 584 | 15 017 | 92,9% | `directlyBudgeted` |
| `rhetoricalPlans` | 45 249 | 13 601 | 69,9% | `directlyBudgeted` |

Все фактические primary/retry-вызовы трех planning-операций имеют direct
current-call budget proof. Нет `overBudget`, `payloadTooLarge`,
`contextOverBudget`, `missingDirectBudget` или `nestedBudgetFalsePositive`.

## Dossier contract

- runtime migration: `partiallyMigrated`, потому что этот slice мигрирует только
  planning-семейство;
- `materialPlan`, `strategy`, `rhetoricalPlans`: `runtimeMigrated=true`;
- unresolved handles: `0`;
- forbidden field violations: `0`;
- readiness всех трех dossier: `degraded` только из-за optional-контекста;
- missing required inputs: `0`.

Полные `rulePack`, `SourceLedger`, `ArticleDossier`, `ContextPack`, старые
operation envelopes и budgets не попали в provider input. Полные родительские
артефакты остались в DraftRun для replay, fallback и диагностики.

## Runtime и качество

| Показатель | Baseline | После миграции |
| --- | --- | --- |
| Pipeline | `succeeded` | `succeeded` |
| Child AiRun | 34 | 32 |
| Evidence coverage | `weak` | `sufficient` |
| Интерпретировано evidence | 25 | 36 |
| Fallback-interpreted evidence | 1 | 0 |
| Editorial status | `needsHumanReview` | `publishable` |
| Editorial trust | ограничен | `trusted` |
| Open critical | 1 | 0 |
| Open warning | 19 | 0 |
| Overall verdict | `needsAttention` | `degradedSuccess` |
| Final draft chars | 9 482 | 5 913 |

`materialPlan` принят провайдером с первой попытки и сохранил evidence
accountability: 18 доступных кандидатов, 3 выбранных, 3 отклоненных, 3 требующих
атрибуции; accountability valid.

`strategy` использовал существующий deterministic fallback из-за malformed JSON
ответа OpenRouter (`Expecting value`). Dossier был `degraded` без missing required
inputs, budget incident отсутствовал. Это provider reliability signal, а не потеря
контекста при миграции.

`rhetoricalPlans` восстановился второй попыткой той же модели. Итоговый artifact
получен от OpenRouter без fallback.

## Вердикт

Planning dossier migration работает в реальном runtime. Она резко сократила
provider-входы, сохранила доказательную подотчетность, не сломала downstream pipeline
и не ухудшила итоговое качество. Напротив, принятый live run имеет достаточное
evidence coverage и не содержит открытых редакционных замечаний.

Оставшиеся provider fallback/retry относятся к надежности конкретных моделей и к
еще не мигрированным операциям. Они видимы в trace и остаются задачей следующих
slices `3.8-3.9`, но не блокируют закрытие `3.7`.
