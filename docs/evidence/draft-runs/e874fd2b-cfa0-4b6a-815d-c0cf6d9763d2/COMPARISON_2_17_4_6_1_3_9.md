# Сравнение после review / ranking / revision / final-gate dossier migration

## Контрольные точки

- исторический baseline: `e874fd2b-cfa0-4b6a-815d-c0cf6d9763d2`;
- planning checkpoint: `c2303e05-e7d0-4cad-a3f9-6ea26fc1a3ed`;
- writer checkpoint: `72b3a2df-c8be-41a8-b2c0-e74e5e502cd0`;
- первый диагностический run 3.9: `e369175a-29a6-4e37-97cc-a4bba7e09950`;
- второй диагностический run 3.9: `37564139-55c2-4cba-beb0-b4c2aed78518`;
- третий диагностический run 3.9: `d06d8f17-36eb-46ea-8fcd-fd302905f41a`;
- финальный post-fix live proof: `7bf3a7b9-4646-4b32-8bfd-cc5b200a1b47`.

Все live-run используют один контрольный payload. Секреты и полные provider payloads
в evidence-файлы не включены.

## Что реализовано

Реальные вызовы `llmValidation`, `pairwiseRanking`, `directedRevision` и
`finalQualityGateReview` используют operation-specific dossiers. Каждая попытка
проходит `ProviderInputBudgetGate` до сборки сообщений и пишет в child `AiRun`:

- фактический `providerInput`;
- `providerDossier.runtimeMigrated=true`;
- прямой `payloadBudget`, `inputStats`, `payloadStats`;
- attempt/model metadata и resolvable handles.

Ranking получает четыре равные candidate projections: одинаковые окна начала,
середины и конца, два приоритетных finding summary на кандидата, полный
`findingCount` и семь editorial dimensions. Revision сохраняет точный candidate body,
приоритетные repair goals и anti-regression constraints. Final review получает точный
доставляемый текст и effective final-quality context.

Terminal dossier replay для последних запусков:

- verdict: `readyForMigration`;
- unresolved handles: `0`;
- forbidden field violations: `0`;
- missing required inputs: `0`;
- `DEGRADED` только `low` из-за optional evidence/rule trimming.

## Размеры provider input

| Операция | Writer checkpoint `72b3...` | Последний live `d06...` | Replay после финальной правки | Лимит |
| --- | ---: | ---: | ---: | ---: |
| `llmValidation` | 178 771-183 215 | 13 987-15 735 | 13 987-15 735 | 22 000 |
| initial `pairwiseRanking` | 436 148 | 22 738 | 20 916 | 22 000 |
| revision `pairwiseRanking` | 153 678-159 549 | 13 148-13 298 | 12 378-12 450 | 22 000 |
| `directedRevision` | 188 385-195 298 | 17 694-19 747 | 17 694-19 747 | 24 000 |
| `finalQualityGateReview` | 21 397-21 415 | 19 553-19 652 | 19 553-19 652 | 22 000 |

Последняя правка ranking compactor была сделана после live-вызова `d06...`: окна
кандидата уменьшены до трех равных 300-символьных фрагментов, а каждый кандидат
сохраняет два приоритетных finding summary и полный счетчик findings. Replay применяет
эту правку к точному сохраненному provider input `d06...` и дает `20 916/22 000`
без incident.

Финальный post-fix run `7bf3...` доказал эти лимиты в реальном provider path:

| Операция | Вызовы | Размеры, символов | Лимит | Результат |
| --- | ---: | --- | ---: | --- |
| `llmValidation` | 4 | 15 733; 15 785; 16 628; 14 808 | 22 000 | passed |
| `pairwiseRanking` | 4 | 20 534; 10 832; 10 696; 10 517 | 22 000 | passed |
| `directedRevision` | 5 | 19 197; 20 157; 18 136; 14 823; 15 616 | 24 000 | passed |
| `finalQualityGateReview` | 3 | 16 523; 17 105; 18 015 | 22 000 | passed |

Все 16 вызовов directly budgeted. Для них нет `missingDirectBudget`,
`nestedBudgetFalsePositive`, `payloadTooLarge` или `contextOverBudget`.

По сравнению с writer checkpoint `72b3...` суммарный размер фактически отправленных
messages для этих четырех семейств снизился с `2 030 528` до `272 288` символов,
то есть на `86,6%`. Суммарная зафиксированная provider cost снизилась с `$0.597017`
до `$0.302704`, то есть на `49,3%`, несмотря на 16 вызовов вместо 14. Точные token
counts в trace редактируются, поэтому economy доказывается через одинаково
посчитанные message chars и фактическую provider cost.

Полный provider-input audit также обнаружил отдельный долг предыдущего slice 3.8:
`alternativeAngleRoute=34 589/22 000`. Он не относится к четырем операциям 3.9 и
зафиксирован отдельным follow-up slice; finding не скрыт и не считается clean.

Ranking live trace содержит четыре равные candidate projections, challenger, winner и
все семь `editorialDimensionScores`. При этом три comparison rows имеют пустые
`leftCandidateId/rightCandidateId`. На качество выбора это не повлияло, но pair-level
trace нельзя считать полностью самодостаточным; ремонт зафиксирован как неблокирующий
follow-up `2.17.4.6.1.3.9.2`.

## Lifecycle замечаний

Replay `72b3...` после новой candidate scoping policy дает:

- final candidate: `revised-revised-candidate-research-brief-control-workflow-20260703211313`;
- diagnostic critical проигравших кандидатов: `3`;
- direct candidate warnings проигравших кандидатов: `20`;
- дополнительные подавленные attribution diagnostics: `4`;
- `openCriticalCount=0`;
- `openWarningCount=1`;
- единственный open warning относится к доставленному тексту:
  `finalQuality.independentReview` / paragraph fragmentation;
- editorial status: `publishableWithCaution`;
- overall verdict: `recoveredSuccess`.

Это закрывает прежний ложный blocker: findings недоставленных кандидатов остаются в
trace, но получают `resolved/candidate-not-delivered` и не считаются проблемами
финального текста. Неизвестная candidate scope в старом trace остается open
консервативно.

## Сравнение качества

| Run | Evidence | Editorial | Verdict | Open critical / warning | Символы / абзацы |
| --- | --- | --- | --- | ---: | ---: |
| `e874...` | weak | publishable with caution | degraded success | 0 / 3 после replay | 9 482 / n/a |
| `c230...` | sufficient | publishable | degraded success | 0 / 0 | 5 913 / 16 |
| `72b3...` | sufficient | publishable with caution | recovered success | 0 / 1 | 8 993 / 38 |
| `e369...` | sufficient | publishable | recovered success | 0 / 0 | 8 669 / n/a |
| `375...` | weak | publishable with caution | degraded success | 0 / 0 | 8 887 / n/a |
| `d06...` | sufficient | needs human review | needs attention | 1 / 1 | 8 660 / 46 |
| `7bf3...` | sufficient | publishable | recovered success | 0 / 0 | 8 938 / 18* |

`*` Непустые блоки, разделенные пустой строкой; у `72b3...` по той же методике их 26.

`d06...` сохраняет конкретный ТОиР-контекст, decision-workbench, гипотезу по
вибрации, историю замен, RCA, confidence boundary и человеческое решение. Однако
final gate обоснованно оставил open critical: пример является авторским сценарием,
но не source-backed implementation case, требуемым контрактом. Дополнительно текст
сильнее фрагментирован, чем `72b3...`.

Repair goal про конкретную гипотезу присутствовал в revision dossier, а final gate
проверил исправленный candidate и отклонил неулучшающий repair. Поэтому lifecycle и
safety-поведение работают честно; этот конкретный quality failure нельзя скрывать как
ложный blocker. Одновременно он не дает доказать отсутствие редакционной регрессии
относительно `72b3...`.

Финальный `7bf3...` устраняет обе прежние неопределенности. Initial ranking реально
прошел с `20 534/22 000`. Финальный текст сохранил source-backed SmartDiagnostics
пример, конкретную ночную ТОиР-ситуацию, RCA/confidence conflict, человеческую границу
решения и практический CTA. Он менее фрагментирован, чем `72b3...`, и не имеет open
critical/warning. Final repair принят, а effective review относится к реально
доставленному candidate.

С точки зрения редакционного качества `7bf3...` лучше `c230...` по конкретности и
глубине механики и не хуже `72b3...` по grounding, связности, практической ценности и
ограничениям применимости. Provider recovery `backupRecovered` вызван timeout в
evidence interpretation и schema repair в одной editorial critique; evidence fidelity
осталась `sufficient`, deterministic fallback не использовался.

## Вердикт по DoD

DoD slice 3.9 выполнен:

- runtime migration четырех operation families доказана fresh live trace;
- все их attempts directly budgeted и находятся внутри caps;
- challenger участвовал в ranking, семь dimensions переданы симметрично;
- три revision cycles и final-quality repair полностью видны;
- final review проверил repaired candidate;
- lifecycle имеет `openCriticalCount=0`, `openWarningCount=0`;
- evidence fidelity `sufficient`, editorial status `publishable`;
- quality regression относительно `c230...` и `72b3...` не обнаружена.

`2.17.4.6.1.3.9` может быть переведен в `Done`. Отдельный over-budget finding
`alternativeAngleRoute` принадлежит follow-up repair и не теряется при закрытии 3.9.
