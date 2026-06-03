// App — state, routing between editorial sections, toasts.
function App() {
  const [active, setActive] = React.useState('radar');
  const [toast, setToast] = React.useState(null);

  function flash(msg) {
    setToast(msg);
    clearTimeout(window.__grT);
    window.__grT = setTimeout(() => setToast(null), 2600);
  }
  function go(view, msg) { setActive(view); if (msg) flash(msg); document.querySelector('.scroll')?.scrollTo(0, 0); }

  let view;
  if (active === 'editorialModel') view = <EditorialModelView />;
  else if (active === 'radar') view = <RadarView onPlan={(d) => go('plan', 'Тема добавлена в план недели')} />;
  else if (active === 'plan') view = <PlanView onApprove={() => flash('План недели утверждён')} onOpenPost={() => go('brief')} />;
  else if (active === 'brief') view = <BriefView onApprove={() => go('edit', 'Замысел утверждён · редакция пишет драфт')} onReject={() => go('plan', 'Фабула возвращена на доработку')} />;
  else if (active === 'edit') view = <EditView onApprove={() => go('release', 'Текст утверждён · готов к выпуску')} />;
  else if (active === 'release') view = <Placeholder icon="release" title="Выпуск" text="Готовый текст адаптируется под Telegram, LinkedIn, Substack и рассылку. Один материал — несколько форм: пост, тред, колонка, письмо." />;
  else if (active === 'analytics') view = <Placeholder icon="analytics" title="Аналитика" text="Не просмотры, а редакционные выводы: какие тезисы работают, какие рубрики усиливают доверие, какие темы приводят качественную аудиторию." />;

  return (
    <div className="app">
      <Sidebar active={active} onNav={setActive} author={GR_DATA.author} />
      <div className="main">
        <Topbar active={active} onCreate={() => go('radar', 'Открыт Радар — выберите повод')} />
        <div className="scroll">{view}</div>
      </div>
      {toast && <div className="toast"><Icon name="check" size={17} />{toast}</div>}
    </div>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
