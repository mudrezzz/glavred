# Slice 2.17.4.7.1 live proof

Дата проверки: 2026-07-22.

## Свежий запуск

- Project: `project-ai-design-patterns`.
- Radar: `ai-pattern-radar-industrial-cases`.
- RadarRun: `radar-run-ai-pattern-radar-industrial-cases-9`.
- Retrieval status: `partial`; scoring status: `succeeded`.
- `partial` вызван одним malformed JSON от search provider и `403` при чтении OpenReview. Обе ошибки видимы в operation trace; extraction и scoring завершились.
- Найдено и оценено 3 русских сигнала; все получили `reviewWithCaution`, а не универсальный тематический отказ.
- У каждого сигнала тема получила `СОВПАДАЕТ` с отдельным объяснением.
- Один сигнал утвержден редактором: review revision `1`, history events `1`.
- Ручной пересчет создал scoring revision `2` без повторного search, URL read или extraction.
- Downstream artifacts не создавались: `PostCandidate=0`, `planSlot=0`, `DraftRun=0`.

## Проверяемость и бюджет

- Automatic scoring AiRun: `1f64761b-3d05-402a-947a-343183ebbc56`.
- Primary accepted с первой попытки.
- Messages: `17166/22000` chars.
- Input/output/total: `4502/1308/5810` tokens.
- Direct current-call budget proof присутствует; budget incidents отсутствуют.
- Unresolved setting refs: `0`.
- Unresolved evidence refs: `0`.
- В provider input не передаются полный workspace, публикации или старые trace envelopes.

## Replay цифрового советчика

Replay `radar-run-ai-pattern-radar-industrial-cases-7` подтвердил:

- «Цифровой советчик как модуль поддержки решений в ТОиР» имеет recommendation `reviewWithCaution`;
- промышленная тема получила `СОВПАДАЕТ`;
- результат классифицирован как `capabilityOnly`, а не как наблюдаемый эффект;
- posture источника остался `unknown`, а не был объявлен независимым;
- «Цифровой советчик» и «Автоматизированная оценка рисков в ТОиР» связаны как `relatedSameSource`;
- сырые `materialId`, `fragmentId` и `settingId` не показываются редактору.

`sameClaim` для действительно почти одинаковых сигналов покрыт golden-тестом. В replay существует один извлеченный сигнал про цифрового советчика, поэтому несуществующий дубль не синтезируется.

## UI и trace

- Авторизация подтверждена для `127.0.0.1:5176` и `localhost:5176`.
- Работают выход из dashboard, выход из меню проекта и смена аккаунта.
- Карточка показывает отдельные блоки радара, редакционной модели, качества/рисков и связей.
- Доказательства разрешаются в название источника, цитату, внешний URL и deep link в trace.
- Режим коррекции сохраняет read-only контекст, доказательства и utility report.
- Source URL, extraction trace и scoring trace открываются.
- Проверены ширины `390`, `1180`, `1440`, `1904`, `2048`; page-level overflow отсутствует.

Полные скриншоты находятся в игнорируемом каталоге `var/visual-proof/2.17.4.7.1/live/`. Полные provider inputs, workspace payload и секреты не сохраняются в документации.
