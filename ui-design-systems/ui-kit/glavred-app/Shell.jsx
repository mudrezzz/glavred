// App shell — sidebar nav + topbar.
const GR_NAV = [
  { id: 'bible', icon: 'bible', label: 'Редакционная библия' },
  { id: 'radar', icon: 'radar', label: 'Радар', count: 12 },
  { id: 'plan', icon: 'plan', label: 'План', count: 5, muted: true },
  { id: 'brief', icon: 'brief', label: 'Фабулы', count: 2, muted: true },
  { id: 'edit', icon: 'edit', label: 'Редактура' },
  { id: 'release', icon: 'release', label: 'Выпуск' },
  { id: 'analytics', icon: 'analytics', label: 'Аналитика' },
];

function Sidebar({ active, onNav, author }) {
  return (
    <aside className="side">
      <div className="brand">
        <img src="../../assets/logo-mark.svg" width="40" height="40" alt="" />
        <span className="wm">Главред</span>
      </div>
      <div className="nav-label">Редакция</div>
      {GR_NAV.map(n => (
        <button key={n.id} className={'nav-item' + (active === n.id ? ' active' : '')} onClick={() => onNav(n.id)}>
          <Icon name={n.icon} />
          <span>{n.label}</span>
          {n.count != null && <span className={'count' + (n.muted ? ' muted' : '')}>{n.count}</span>}
        </button>
      ))}
      <div className="side-foot">
        <div className="author">
          <div className="ava">{author.initials}</div>
          <div>
            <b>{author.name}</b>
            <span>{author.role}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

const GR_TITLES = {
  bible: ['Редакционная библия', 'Конституция блога'],
  radar: ['Радар', '12 поводов за сегодня'],
  plan: ['План', 'Неделя 2–8 июня'],
  brief: ['Фабула поста', 'HITL · Gate 2 — замысел'],
  edit: ['Редактура', 'Драфт · пайплайн редакторов'],
  release: ['Выпуск', 'Адаптация под площадки'],
  analytics: ['Аналитика', 'Редакционные выводы'],
};

function Topbar({ active, onCreate }) {
  const [t, sub] = GR_TITLES[active] || ['', ''];
  return (
    <header className="topbar">
      <div className="crumb">{t}<small>{sub}</small></div>
      <div className="spacer" />
      <div className="search">
        <Icon name="search" size={16} />
        <input placeholder="Поиск по темам, фабулам…" />
      </div>
      <button className="icon-btn"><Icon name="bell" /><span className="dot" /></button>
      <button className="btn btn-pri" onClick={onCreate}><Icon name="plus" size={16} />Создать</button>
    </header>
  );
}

window.Sidebar = Sidebar;
window.Topbar = Topbar;
