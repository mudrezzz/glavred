# Radar signal extraction live proof

Дата проверки: 2026-07-14.

## Контрольные запуски

- `radar-run-ai-pattern-radar-industrial-cases-7` не принят как доказательство:
  Docker DNS временно перестал разрешать внешние домены, два поисковых запроса и оба
  чтения завершились сетевой ошибкой. Retrieval получил `partial`, читаемых материалов
  не было, extraction честно получил `notRun`.
- `radar-run-ai-pattern-radar-industrial-cases-8` выполнен на финальном runtime-коде и
  принят как live proof.

## Retrieval

Финальный запуск завершился со статусом `succeeded`:

- 3 из 3 `openWebQuery` завершились успешно;
- получено 60 raw results против 52 в baseline;
- выбрано и успешно прочитано 2 материала из 2 разных доменов;
- `metadataOnly=0`, accepted noise `=0`;
- benchmark сохранил `warning` только потому, что обязательное направление
  `limitationCritique` было запланировано, но пропущено прежним лимитом
  `maxExternalQueries=3`.

Таким образом, retrieval не ухудшился относительно
`radar-run-industrial-ai-triage-v2-live-20260713`.

## Первичное извлечение

Revision 1 завершилась с первой попытки:

- обработано 2 материала и записано 2 терминальных решения;
- один материал дал 3 доказательных сигнала, второй честно получил `insufficient`;
- все 3 сигнала разрешаются в сохраненные material/fragment handles;
- unresolved evidence refs `=0`, grounding violations принятого payload `=0`;
- создано `PostCandidate=0`, plan slots `=0`, DraftRun `=0`.

Provider input занимал 12 496 символов при лимите сообщений 16 000. OpenRouter
вернул 2 848 input tokens, 895 output tokens и 3 743 total tokens. Бюджетных
инцидентов не было.

## Качество сигналов

Принятые сигналы описывают один промышленный кейс с разными полезными аспектами:

- измеримый результат пилота predictive maintenance;
- механизм через vibration/ultrasound sensors и predictive ML diagnostics;
- операционное принятие через долю обработанных alerts;
- расширение пилота на дополнительные площадки;
- ограничения явно отмечают отсутствие независимой проверки, методики baseline и
  данных о false positives.

Сигналы остаются в `reviewStatus=candidate`. Они не получают topic, fabula, audience,
value, goal, platform или channel: оценка пользы для проекта относится к
`2.17.4.7.1`.

## Повтор без поиска

Forced retry создал revision 2 и не повторял retrieval:

- число search operations осталось 3;
- число URL reads осталось 2;
- в workspace осталось ровно 3 сигнала без дублированных ID;
- первая попытка была отклонена из-за неподтвержденного числа `40`;
- repair той же моделью получил только структурированную ошибку, исправил grounding
  и был принят;
- rejected grounding incident остался в trace, но не попал в принятые сигналы.

Первичная попытка retry использовала 4 106 total tokens, repair - 4 078. Сообщения
занимали 12 496 и 12 647 символов соответственно, оба значения ниже лимита 16 000.

## Где смотреть

- Техническая трасса:
  `http://localhost:5176/radar-runs?runId=radar-run-ai-pattern-radar-industrial-cases-8&projectId=project-ai-design-patterns`.
- Пользовательский UI: проект `Опытный цех «Сборочная»` -> `Сигналы` ->
  `Найденные сигналы`.
- Диагностика:

```bash
python scripts/analyze_radar_signal_extraction.py \
  --project-id project-ai-design-patterns \
  --run-id radar-run-ai-pattern-radar-industrial-cases-8 \
  --format markdown
```
