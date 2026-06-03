// Главред marketing landing — sections.
function Nav() {
  return (
    <nav className="nav"><div className="wrap"><div className="row">
      <a className="logo" href="#"><img src="../../assets/logo-mark.svg" width="36" height="36" alt="" /><b>Главред</b></a>
      <div className="links">
        <a href="#how">Как это работает</a>
        <a href="#newsroom">Редакция</a>
        <a href="#rubrics">Рубрики</a>
        <a href="#pricing">Цены</a>
      </div>
      <div className="right">
        <a className="btn btn-ghost" href="#">Войти</a>
        <a className="btn btn-pri" href="#">Собрать редакцию<Icon name="arrow" size={16} /></a>
      </div>
    </div></div></nav>
  );
}

function Hero() {
  return (
    <header className="hero"><div className="wrap"><div className="hero-grid">
      <div>
        <span className="eyebrow">AI-издательство</span>
        <h1>Не AI-копирайтер.<br/><em>AI-редакция</em> для вашего личного медиа.</h1>
        <p className="lead">Главред находит поводы, превращает их в темы и фабулы, пишет драфты в вашем стиле и проверяет факты. Вы утверждаете ключевые решения как главный редактор.</p>
        <div className="cta">
          <a className="btn btn-pri btn-lg" href="#">Собрать редакцию<Icon name="arrow" size={17} /></a>
          <a className="btn btn-sec btn-lg" href="#how">Как это работает</a>
        </div>
        <div className="note">Редакционная модель · радар источников · 3 точки вашего контроля</div>
      </div>
      <div className="stack">
        <div className="float-card">
          <div className="top"><span className="sig">Контраргумент</span><span className="rub">Антимнение</span></div>
          <h4>«AI заменит копирайтеров» — снова в топе. Пора возразить.</h4>
          <p>Три канала за сутки повторяют тезис. У вас есть сильная контрпозиция и кейс.</p>
          <div className="scores">
            <span className="sc">релевантность <b>0.88</b></span>
            <span className="sc">новизна <b>0.64</b></span>
            <span className="sc">риск ↓ <b>0.18</b></span>
          </div>
        </div>
        <div className="mini-news">
          <div className="mh">Редакция за работой</div>
          <div className="agrow"><div className="av" style={{ background: 'var(--info-tint)', color: 'var(--info-ink)' }}>СК</div><span>Скаут</span><small>6 сигналов</small></div>
          <div className="agrow"><div className="av" style={{ background: 'var(--warn-tint)', color: 'var(--warn-ink)' }}>ФЧ</div><span>Фактчекер</span><small>2 проверки</small></div>
          <div className="agrow"><div className="av" style={{ background: 'var(--ok-tint)', color: 'var(--ok-ink)' }}>АА</div><span>Анти-AI</span><small>чистит</small></div>
        </div>
      </div>
    </div></div></header>
  );
}

function Contrast() {
  return (
    <section className="band" id="how"><div className="wrap">
      <span className="eyebrow sec-eyebrow" style={{ display: 'flex', justifyContent: 'center' }}>Главное отличие</span>
      <h2 className="sec-title">Промпт даёт текст. Редакция даёт систему.</h2>
      <div className="contrast">
        <div className="cbox old">
          <div className="lab">Обычный AI-копирайтер</div>
          <div className="flow"><span className="node">Промпт</span><span className="arrow">→</span><span className="node">Текст</span></div>
          <p className="cap">Каждый раз с чистого листа. Ничего не помнит: ни вашу позицию, ни что вы уже говорили, ни чего избегаете.</p>
        </div>
        <div className="cbox new">
          <div className="lab">Главред</div>
          <div className="flow">
            <span className="node">Источники</span><span className="arrow">→</span>
            <span className="node">Инсайты</span><span className="arrow">→</span>
            <span className="node gate">План ✓</span><span className="arrow">→</span>
            <span className="node gate">Фабула ✓</span><span className="arrow">→</span>
            <span className="node">Драфт</span><span className="arrow">→</span>
            <span className="node">Проверка</span><span className="arrow">→</span>
            <span className="node gate">Выпуск ✓</span><span className="arrow">→</span>
            <span className="node">Аналитика</span>
          </div>
          <p className="cap">Система помнит, кто вы и зачем пишете — и с каждым циклом становится точнее. Красным отмечены точки вашего контроля.</p>
        </div>
      </div>
    </div></section>
  );
}

const GR_AGENTS = [
  ['ГР', 'accent', 'Главный редактор', 'Оркестратор. Следит за фабулой и приоритетами.'],
  ['СК', 'info', 'Скаут', 'Ищет поводы в источниках и превращает в инсайты.'],
  ['АН', 'ink', 'Аналитик', 'Проверяет, есть ли под темой фактура и данные.'],
  ['БР', 'accent2', 'Брифинг-редактор', 'Собирает фабулу поста до написания.'],
  ['СТ', 'ink', 'Стиль-редактор', 'Переписывает драфт в ваш авторский голос.'],
  ['АА', 'ok', 'Анти-AI-редактор', 'Убирает шаблонность, штампы и стерильность.'],
  ['ФЧ', 'warn', 'Фактчекер', 'Сверяет цифры, имена, даты и источники.'],
  ['РС', 'info', 'Дистрибуция', 'Адаптирует материал под Telegram, LinkedIn, Substack.'],
];
const GR_AG_TINT = {
  accent: ['var(--accent-tint)', 'var(--accent-ink)'], accent2: ['var(--accent-wash)', 'var(--accent)'],
  info: ['var(--info-tint)', 'var(--info-ink)'], ink: ['var(--ink-100)', 'var(--ink-700)'],
  ok: ['var(--ok-tint)', 'var(--ok-ink)'], warn: ['var(--warn-tint)', 'var(--warn-ink)'],
};

function Newsroom() {
  return (
    <section className="band alt" id="newsroom"><div className="wrap">
      <span className="eyebrow sec-eyebrow" style={{ display: 'flex', justifyContent: 'center' }}>Ваша редакция</span>
      <h2 className="sec-title">Не один промпт, а команда ролей</h2>
      <p className="sec-sub">Пятнадцать редакционных агентов с разной зоной ответственности. Вы — главный редактор над ними.</p>
      <div className="agrid">
        {GR_AGENTS.map(([ini, t, name, desc]) => {
          const [bg, fg] = GR_AG_TINT[t];
          return (
            <div className="acard" key={ini}>
              <div className="av" style={{ background: bg, color: fg }}>{ini}</div>
              <b>{name}</b><span>{desc}</span>
            </div>
          );
        })}
      </div>
    </div></section>
  );
}

const GR_PIPE = [
  ['radar', 'Источники', 'поток', false],
  ['sparkles', 'Инсайты', 'карточки', false],
  ['plan', 'План', 'Gate 1', true],
  ['brief', 'Фабула', 'Gate 2', true],
  ['edit', 'Драфт', 'автор. стиль', false],
  ['shield', 'Проверка', 'факты · политика', false],
  ['release', 'Выпуск', 'Gate 3', true],
  ['analytics', 'Аналитика', 'обучение', false],
];

function Workflow() {
  return (
    <section className="band"><div className="wrap">
      <span className="eyebrow sec-eyebrow" style={{ display: 'flex', justifyContent: 'center' }}>Редакционный конвейер</span>
      <h2 className="sec-title">AI готовит. Редакция проверяет. Вы утверждаете.</h2>
      <p className="sec-sub">Три обязательные точки человеческого контроля — план, замысел, финальный текст. Никакого слепого автопилота.</p>
      <div className="pipe">
        {GR_PIPE.map(([ic, t, s, gate]) => (
          <div className={'step' + (gate ? ' gate' : '')} key={t}>
            <div className="si"><Icon name={ic} size={20} /></div>
            <b>{t}</b><small>{s}</small>
          </div>
        ))}
      </div>
    </div></section>
  );
}

const GR_RUBS = [
  ['Разборы', 'Объясняем сложное простым языком.'],
  ['Антимнение', 'Спорим с популярным заблуждением.'],
  ['Кейсы', 'Показываем применение на практике.'],
  ['Полевые заметки', 'Личные наблюдения автора.'],
  ['Методология', 'Системные фреймворки и модели.'],
  ['Реакции', 'Быстрые комментарии к событиям.'],
];

function Rubrics() {
  return (
    <section className="band alt" id="rubrics"><div className="wrap">
      <span className="eyebrow sec-eyebrow" style={{ display: 'flex', justifyContent: 'center' }}>Рубрикатор</span>
      <h2 className="sec-title">Блог — это сетка, а не «всё обо всём»</h2>
      <p className="sec-sub">У каждой рубрики свои правила: длина, структура, частота, степень личного и допустимый CTA.</p>
      <div className="rgrid">
        {GR_RUBS.map(([t, d]) => (
          <div className="rcard" key={t}>
            <span className="rub">{t}</span>
            <div className="rd" style={{ marginTop: 12 }}>{d}</div>
          </div>
        ))}
      </div>
    </div></section>
  );
}

function FinalCTA() {
  return (
    <section className="band" id="pricing"><div className="wrap">
      <div className="cta-band">
        <h2>Превратите блог в редакцию</h2>
        <p>От поиска тем до публикации — в одной AI-системе с вашей памятью и вашим голосом.</p>
        <div className="cta">
          <a className="btn btn-pri btn-lg" href="#">Собрать редакцию<Icon name="arrow" size={17} /></a>
          <a className="btn btn-light btn-lg" href="#">Посмотреть демо</a>
        </div>
      </div>
    </div></section>
  );
}

function Footer() {
  return (
    <footer><div className="wrap">
      <div className="row">
        <div className="logo"><img src="../../assets/logo-mark.svg" width="32" height="32" alt="" />Главред</div>
        <div className="fl">
          <a href="#">Возможности</a><a href="#">Редакция</a><a href="#">Цены</a><a href="#">Блог</a><a href="#">Контакты</a>
        </div>
      </div>
      <div className="cr">© 2026 Главред · AI-издательство для авторского медиа</div>
    </div></footer>
  );
}

function Site() {
  return (<>
    <Nav /><Hero /><Contrast /><Newsroom /><Workflow /><Rubrics /><FinalCTA /><Footer />
  </>);
}
ReactDOM.createRoot(document.getElementById('root')).render(<Site />);
