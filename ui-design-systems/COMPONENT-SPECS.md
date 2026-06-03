# COMPONENT-SPECS — точные спецификации компонентов «Главред»

Справочник с конкретными значениями для сборки. Все величины записаны через токены из
`colors_and_type.css` (а где для контекста полезно — продублирован реальный hex/px).
Каждому компоненту соответствует живой образец в `spec-previews/` — открывайте рядом.

**Общие константы**
- Базовый шрифт UI: `var(--ui-md)` → Golos Text 500 / 15px / 1.5
- Цвет текста по умолчанию: `var(--ink-900)` `#211D19`; вторичный `--ink-700`/`--ink-600`
- Бордеры по умолчанию: `1px solid var(--ink-200)` `#E8E2D8`
- Переход по умолчанию: `all var(--dur) var(--ease)` → 200ms, ease-out
- Скругления: input/button `--r-md 12px`, карточки `--r-lg 16px` / `--r-xl 22px`, pill `--r-pill`

---

## Кнопки → `spec-previews/comp-buttons.html`

Общее: `font: var(--ui-md); font-weight: 600; border-radius: var(--r-md); padding: 10px 18px;
border: 1px solid transparent; display: inline-flex; align-items: center; gap: 8px;
transition: all var(--dur) var(--ease);`

| Вариант | Фон | Текст | Бордер | Тень | Hover |
|---|---|---|---|---|---|
| **Primary** (`.pri`) | `var(--accent)` | `#fff` | — | `var(--shadow-accent)` | фон → `var(--accent-hover)` |
| **Secondary** (`.sec`) | `var(--surface)` | `var(--ink-800)` | `var(--ink-300)` | `var(--shadow-xs)` | фон → `var(--ink-50)` |
| **Ghost** (`.ghost`) | прозрачный | `var(--ink-700)` | — | — | фон → `var(--ink-100)` |
| **Danger** (`.danger`) | `var(--surface)` | `var(--danger-ink)` | `var(--danger-tint)` | — | фон → `var(--danger-tint)` |

- **Small** (`.sm`): `font: var(--ui-sm); font-weight: 600; padding: 6px 12px; border-radius: var(--r-sm);`
- **Press:** темнее на ступень (`--accent-active`) + `scale(0.985)`.
- **Disabled:** `opacity: .45; box-shadow: none; cursor: not-allowed;`
- **Иконка-каретка** внутри primary («Утвердить»): inline-SVG 14×14, штрих `#fff` 2.5px,
  `round` стыки. Путь: `M5 14 L12 7 L19 14` (знак вставки корректора).
- Тексты — редакторские: «Утвердить фабулу», «Вернуть на доработку», «Отложить», «Отклонить»,
  «Выпустить», «Ещё варианты заголовка».

---

## Чипы и статусы → `spec-previews/comp-chips.html`

**Рубрика** (`.rub`): `font: var(--mono-sm); text-transform: uppercase; letter-spacing: .1em;
padding: 5px 10px; border-radius: var(--r-pill); background: var(--ink-100); color: var(--ink-700);`

**Статус-чип** (`.status`): `display: inline-flex; align-items: center; gap: 7px;
font: var(--ui-sm); font-weight: 600; padding: 5px 11px; border-radius: var(--r-pill);`
с точкой `i` 8×8, `border-radius: 50%`.

| Статус | Фон | Текст | Точка | Смысл |
|---|---|---|---|---|
| Новый сигнал | `--info-tint` | `--info-ink` | `--info` | скаут нашёл повод |
| В плане | `--accent-tint` | `--accent-ink` | `--accent` | отобрано в план |
| Нужен фактчек | `--warn-tint` | `--warn-ink` | `--warn` | риск / проверка |
| Опубликовано | `--ok-tint` | `--ok-ink` | `--ok` | выпущено |
| Риск политики | `--danger-tint` | `--danger-ink` | `--danger` | нарушение политики |

---

## Поля ввода → `spec-previews/comp-inputs.html`

- **Label** (`label`): `font: var(--ui-xs); color: var(--ink-600);`
- **Поле** (`.field`): `font: var(--ui-md); color: var(--ink-900); background: var(--surface-sunk);
  border: 1px solid var(--ink-200); border-radius: var(--r-md); padding: 10px 13px;`
- **Focus** (`.focus`): фон → `var(--surface)`, бордер → `var(--info)`, `box-shadow: var(--ring-focus)`.
- **Placeholder:** цвет `var(--ink-500)`.
- **Select:** то же поле + шеврон-SVG 16×16, цвет `var(--ink-500)`, путь `M6 9l6 6 6-6`.
- **Тоггл** (`.sw`): трек `38×22`, `border-radius: var(--r-pill)`, фон `var(--accent)` (вкл);
  ручка `18×18` круглая `#fff` с `var(--shadow-xs)`, отступ 2px.
- Колонки полей раскладываются `display: flex; gap: 16px;` (по `flex: 1`), внутри колонки
  `flex-direction: column; gap: 7px;`.

---

## Навигация (сайдбар) → `spec-previews/comp-nav.html`

- **Контейнер** (`.nav`): `display: flex; flex-direction: column; gap: 4px; width: 230px;
  background: var(--surface); border: 1px solid var(--ink-200); border-radius: var(--r-lg);
  padding: 10px; box-shadow: var(--shadow-sm);`
- **Пункт** (`.item`): `display: flex; align-items: center; gap: 11px; padding: 9px 12px;
  border-radius: var(--r-md); font: var(--ui-md); font-weight: 500; color: var(--ink-700);
  position: relative;` — иконка 18×18 цвета `var(--ink-500)`.
- **Hover:** `background: var(--ink-100);`
- **Active** (`.active`): фон `var(--accent-wash)`, текст `var(--ink-900)`, `font-weight: 600`,
  иконка → `var(--accent)`. **Индикатор-каретка:** `::before` слева (`left: -10px`),
  `width: 3px; height: 20px; border-radius: 2px; background: var(--accent);` по центру по вертикали.
- **Бейдж** (`.badge`): `font: var(--mono-sm); background: var(--accent); color: #fff;
  border-radius: var(--r-pill); padding: 1px 7px;` — прижат вправо (`margin-left: auto`).

---

## Карточка инсайта → `spec-previews/comp-insight-card.html`

Рабочая лошадка Радара. **Карточка** (`.card`): `background: var(--surface);
border: 1px solid var(--ink-200); border-radius: var(--r-xl); box-shadow: var(--shadow-sm);
padding: 18px 20px; max-width: 560px;` (hover → `--shadow-md`, подъём `-1px`).

Структура сверху вниз:
1. **Верхняя строка** (`display: flex; gap: 8px; align-items: center; margin-bottom: 11px;`):
   - сигнал-тип (`.sig`): mono-sm, uppercase, `letter-spacing: .1em`, `color: var(--info-ink)`,
     фон `var(--info-tint)`, `padding: 4px 9px`, `border-radius: var(--r-pill)`;
   - рубрика (`.rub`): как чип рубрики выше;
   - срочность (`.urgent`, прижата вправо): `font: var(--ui-sm); font-weight: 600;
     color: var(--accent-ink);` — текст вида «Нужна реакция сегодня».
2. **Заголовок** (`h3`): `font: var(--ed-h2); font-size: 23px; color: var(--ink-900);
   margin: 0 0 6px;` — **serif (Lora)**, это контент.
3. **Обоснование** (`.why`): `font: var(--ui-md); color: var(--ink-600); margin: 0 0 14px;`
4. **Скоринги** (`.scores`, `display: flex; gap: 8px; align-items: center;`):
   чип `.sc` — `font: var(--mono-sm); background: var(--surface-sunk);
   border: 1px solid var(--ink-200); color: var(--ink-700); padding: 4px 8px;
   border-radius: var(--r-sm);`, значение в `<b>` цвета `var(--ink-900)`.
   Метрики: «релевантность 0.88», «новизна 0.64», «риск банальности 0.18».
   CTA-ссылка (`.cta`, `margin-left: auto`): `font: var(--ui-sm); font-weight: 600;
   color: var(--accent);` + стрелка-SVG 14×14 (`M5 12h14M13 6l6 6-6 6`).

---

## HITL-гейт (фирменный паттерн) → `spec-previews/comp-hitl-gate.html`

Точка, где человек подтверждает перед продолжением машины. Их три: План, Фабула, Финальный текст.

**Контейнер** (`.gate`): `display: flex; align-items: center; gap: 16px;
background: var(--surface); border: 1px solid var(--accent-tint); border-radius: var(--r-xl);
padding: 16px 20px; box-shadow: var(--shadow-sm); border-left: 3px solid var(--accent);`
(левая красная линия — обязательна, это «перо редактора»).

- **Знак** (`.mark`): квадрат `42×42`, `border-radius: var(--r-md)`, фон `var(--accent-wash)`,
  по центру каретка-SVG 22×22, штрих `var(--accent)` 2.5px, путь `M4 16 L12 7 L20 16`.
- **Текст** (`.txt`, `flex: 1`):
  - тег (`.tag`): `font: var(--mono-sm); text-transform: uppercase; letter-spacing: .12em;
    color: var(--accent-ink);` — например «HITL · Gate 2 — Замысел».
  - заголовок (`.ttl`): `font: var(--ui-lg); color: var(--ink-900);` — «Утвердите фабулу перед написанием».
  - подзаголовок (`.sub`): `font: var(--ui-sm); color: var(--ink-600);`.
- **Кнопки** (`.btns`, `display: flex; gap: 10px;`): secondary «Вернуть» + primary «Утвердить замысел».

---

## Аватары агентов → `spec-previews/comp-agents.html`

Mono-инициалы в тонированных чипах — **не картинки, не эмодзи**.

- **Аватар** (`.av`): `width: 38px; height: 38px; border-radius: var(--r-md);
  display: flex; align-items: center; justify-content: center; font: var(--mono-md);
  font-weight: 600;` — цвета по роли (фон `*-tint`, текст `*-ink`).
- **Подпись** (`.nm`): имя `font: var(--ui-sm); font-weight: 600; color: var(--ink-900)`;
  роль-тег `font: var(--mono-sm); color: var(--ink-500)`.

| Агент | Инициалы | Палитра |
|---|---|---|
| Скаут | `СК` | `--info-tint` / `--info-ink` |
| Главред | `ГР` | `--accent-tint` / `--accent-ink` |
| Фактчекер | `ФЧ` | `--warn-tint` / `--warn-ink` |
| Стиль-редактор | `СТ` | `--ink-100` / `--ink-700` |
| Анти-AI | `АА` | `--ok-tint` / `--ok-ink` |

---

## Карточка (общий паттерн)

Базовый блок системы. `background: var(--surface); border-radius: var(--r-lg)` (или `--r-xl`
для крупных); `border: 1px solid var(--ink-200); box-shadow: var(--shadow-sm)` в покое →
`var(--shadow-md)` на hover; внутренние отступы 20–24px. Бордер + мягкая тень работают
вместе: бордер задаёт край на «белом по белому», тень приподнимает.

> Для остальных токенов (полная палитра, type-рампы, шкала отступов, радиусы, тени)
> смотрите `spec-previews/color-*.html`, `type-*.html`, `spacing-*.html` и
> сам `colors_and_type.css`.
