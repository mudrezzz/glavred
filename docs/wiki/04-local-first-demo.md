# Local-first demo

Glavred пока работает как local-first demo. Все состояние хранится в browser
`localStorage`; backend, auth, team work, реальные AI-вызовы, автопостинг и ingestion
метрик пока не подключены.

## Запуск

```bash
npm install
npm run dev
```

Откройте локальный URL, который напечатает Vite.

## Сброс демо

Кнопка `Сбросить демо` в topbar возвращает постоянный сценарий:

- Telegram-блог AI Product Manager;
- аудитория AI PM, founders, CPO/product leaders и B2B SaaS команды;
- позиция: AI-B2B-продукт выигрывает не демо-магией, а workflow, evals, trust loop,
  adoption и экономикой внедрения.

## Переснять скриншоты

```bash
npm run docs:screenshots
```

Команда запускает Vite на отдельном локальном порту, очищает `localStorage` в
Playwright-браузере, проходит основные состояния интерфейса и обновляет PNG в
`docs/wiki/assets/screenshots/`.

## Опубликовать Wiki

```bash
npm run docs:wiki:publish
```

Команда публикует содержимое `docs/wiki/` в GitHub Wiki repository:

`https://github.com/mudrezzz/glavred.wiki.git`

Перед публикацией основной репозиторий должен быть public, иначе GitHub Wiki может
быть недоступна в выбранном режиме проекта.

Для самой первой публикации GitHub требует один ручной web UI шаг: откройте
`https://github.com/mudrezzz/glavred/wiki`, нажмите `Create the first page`, сохраните
временную страницу `Home`, затем снова запустите `npm run docs:wiki:publish`.
