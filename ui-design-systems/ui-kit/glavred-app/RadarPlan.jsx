// Radar + Plan views.
function InsightCard({ d, onPlan }) {
  return (
    <div className="card hover insight">
      <div className="top">
        <span className={'sig ' + d.sigType}>{d.signal}</span>
        <span className="rub">{d.rubric}</span>
        {d.urgent && <span className="urgent"><Icon name="flame" size={15} />Нужна реакция сегодня</span>}
      </div>
      <h3>{d.title}</h3>
      <p className="why">{d.why}</p>
      <div className="foot">
        {d.scores.map(([k, v]) => <span key={k} className="sc">{k} <b>{v}</b></span>)}
        <div className="actions">
          <button className="btn btn-ghost btn-sm">Отложить</button>
          <button className="btn btn-pri btn-sm" onClick={() => onPlan(d)}>
            <Icon name="caret" size={14} />В план
          </button>
        </div>
      </div>
    </div>
  );
}

const GR_FILTERS = ['Все', 'Контраргумент', 'Данные', 'Вопрос', 'Кейс', 'Событие', 'Личное'];

function RadarView({ onPlan }) {
  const [f, setF] = React.useState('Все');
  return (
    <div className="page fade-up">
      <div className="sec-head">
        <h2>Поводы и инсайты</h2>
        <span className="sub">Радар слушает источники · обновлено 4 минуты назад</span>
      </div>
      <div className="filters">
        {GR_FILTERS.map(x => (
          <button key={x} className={'fchip' + (f === x ? ' on' : '')} onClick={() => setF(x)}>{x}</button>
        ))}
      </div>
      {GR_DATA.insights.map(d => <InsightCard key={d.id} d={d} onPlan={onPlan} />)}
    </div>
  );
}

// ---- Plan ---------------------------------------------------------------
const GR_WEEK = [
  { d: 'Пн', n: '2', posts: [{ t: 'Разбор: 47% внедряют AI без процессов', rub: 'Разборы', plat: 'Telegram', st: 'pin', stl: 'Драфт' }] },
  { d: 'Вт', n: '3', posts: [] },
  { d: 'Ср', n: '4', posts: [{ t: 'Полевая заметка о саботаже изменений', rub: 'Полевые', plat: 'LinkedIn', st: 'info', stl: 'Фабула' }] },
  { d: 'Чт', n: '5', today: true, posts: [{ t: 'Почему «AI заменит копирайтеров» — неправильный вопрос', rub: 'Антимнение', plat: 'TG + LinkedIn', st: 'warn', stl: 'Проверка' }] },
  { d: 'Пт', n: '6', posts: [{ t: 'Кейс: −40% к циклу найма', rub: 'Кейсы', plat: 'Telegram', st: 'pin', stl: 'Идея' }] },
  { d: 'Сб', n: '7', posts: [] },
  { d: 'Вс', n: '8', posts: [{ t: 'Длинная колонка месяца', rub: 'Колонки', plat: 'Substack', st: 'ink', stl: 'Черновик' }] },
];
const GR_ST_PILL = { pin: 'pin', info: 'info', warn: 'warn', ok: 'ok', ink: '' };

function PlanView({ onApprove, onOpenPost }) {
  return (
    <div className="page wide fade-up">
      <div className="gate">
        <div className="gm"><Icon name="caret" size={24} /></div>
        <div>
          <div className="gtag">HITL · Gate 1 — План недели</div>
          <div className="gttl">Редакция предлагает 5 публикаций на эту неделю</div>
          <div className="gsub">Баланс рубрик в норме: 2 разбора, 1 антимнение, 1 кейс, 1 личное. Реактивных постов не больше нормы.</div>
        </div>
        <div className="gbtns">
          <button className="btn btn-sec">Изменить баланс</button>
          <button className="btn btn-pri" onClick={onApprove}><Icon name="check" size={16} />Утвердить план</button>
        </div>
      </div>
      <div className="week">
        {GR_WEEK.map(day => (
          <div key={day.d} className={'day' + (day.today ? ' today' : '')}>
            <div className="dh"><b>{day.d}</b><span>{day.n} июня</span></div>
            {day.posts.map((p, i) => (
              <div key={i} className="pcard" onClick={onOpenPost}>
                <span className="rub">{p.rub}</span>
                <div className="pt">{p.t}</div>
                <div className="pf">
                  <span className="plat">{p.plat}</span>
                  <span className={'pill ' + GR_ST_PILL[p.st]} style={{ padding: '2px 8px', fontSize: 11 }}><i />{p.stl}</span>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

window.RadarView = RadarView;
window.PlanView = PlanView;
