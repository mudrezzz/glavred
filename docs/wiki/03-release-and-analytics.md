# Выпуск и аналитика

После утвержденной фабулы пользователь может создать deterministic-драфт, пройти
редакторские проверки, утвердить финальный текст, подготовить ручной выпуск и
зафиксировать learning note.

## Редактура

В `Редактуре` есть стадии `Фабула`, `Драфт`, `Финал` внутри выбранного рабочего
поста. После `Утвердить фабулу` Glavred автоматически готовит deterministic-драфт
из утвержденной фабулы и редакционной модели.

The `Фабула` stage also displays read-only candidate and slot context. The author edits
only the `PostBrief` production artifact there. If an approved fabula is edited,
Glavred clears stale draft, checks, final text, release, and learning artifacts before
the updated fabula is approved again.

Редакторский pipeline показывает четыре проверки:

- стиль;
- anti-AI;
- fact-check;
- policy.

Автор может вручную изменить драфт и только потом нажать `Утвердить текст`.

![Редактура и финальный текст](assets/screenshots/06-editorial-review-final-text.png)

## Выпуск

`Выпуск` не публикует пост автоматически. Он готовит release package для ручного
экспорта: финальный текст, Markdown preview, площадки и checklist.

После checklist можно отметить выпуск как готовый, скопировать текст или скачать
Markdown. После copy/download статус становится `Экспортировано вручную`.

![Manual export](assets/screenshots/07-release-manual-export.png)

## Аналитика

`Аналитика` открывается после ручного экспорта. Здесь нет real-time dashboard и
автоматического сбора метрик: пользователь вводит показатели вручную и фиксирует
редакционные выводы.

Learning note нужен не для красивой отчетности, а для следующего редакционного цикла:
что сработало, какие тезисы цепляют аудиторию, где автор звучит сильнее, что развить
в серию.

![Learning note](assets/screenshots/08-analytics-learning-note.png)
