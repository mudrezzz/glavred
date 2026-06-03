// Brief (Gate 2) + Editing (Gate 3) + light model/release/analytics views.
function Field({ k, children, serif }) {
  return (
    <div className="field-row">
      <div className="k">{k}</div>
      <div className={'v' + (serif ? ' serif' : '')}>{children}</div>
    </div>
  );
}

function BriefView({ onApprove, onReject }) {
  const b = GR_DATA.brief;
  return (
    <div className="page wide fade-up">
      <div className="gate">
        <div className="gm"><Icon name="brief" size={24} /></div>
        <div>
          <div className="gtag">HITL · Gate 2 — Замысел</div>
          <div className="gttl">Утвердите фабулу перед написанием</div>
          <div className="gsub">Большинство слабых текстов проваливаются на замысле, а не на исполнении. Решение — за вами.</div>
        </div>
      </div>
      <div className="brief-grid">
        <div className="brief-body">
          <span className="rub">{b.rubric}</span>
          <h1>{b.title}</h1>
          <Field k="Главный тезис" serif>{b.thesis}</Field>
          <Field k="Конфликт">{b.conflict}</Field>
          <Field k="Авторская позиция">{b.position}</Field>
          <Field k="Структура">
            <ol className="bullets">{b.structure.map((s, i) => <li key={i}>{s}</li>)}</ol>
          </Field>
          <Field k="Доказательства">
            <ul className="bullets">{b.evidence.map((s, i) => <li key={i}>{s}</li>)}</ul>
          </Field>
          <Field k="Ожидаемая эмоция">{b.emotion}</Field>
          <Field k="CTA">{b.cta}</Field>
          <Field k="Риски">
            <ul className="bullets">{b.risks.map((s, i) => <li key={i}>{s}</li>)}</ul>
          </Field>
        </div>
        <div className="aside">
          <div className="panel">
            <h4>Параметры</h4>
            {b.meta.map(([k, v]) => <div key={k} className="kv"><span className="lk">{k}</span><span className="lv">{v}</span></div>)}
          </div>
          <div className="panel">
            <h4>Решение редактора</h4>
            <div className="stack-btns">
              <button className="btn btn-pri" onClick={onApprove}><Icon name="check" size={16} />Утвердить замысел</button>
              <button className="btn btn-sec">Заострить угол</button>
              <button className="btn btn-sec">Больше фактуры</button>
              <button className="btn btn-ghost" onClick={onReject}>Вернуть на доработку</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---- Editing ------------------------------------------------------------
const GR_NOTE_TINT = { ink: ['var(--ink-100)', 'var(--ink-700)'], ok: ['var(--ok-tint)', 'var(--ok-ink)'], warn: ['var(--warn-tint)', 'var(--warn-ink)'], info: ['var(--info-tint)', 'var(--info-ink)'] };
const GR_CHK = {
  ok: ['var(--ok-tint)', 'var(--ok)', 'check'],
  warn: ['var(--warn-tint)', 'var(--warn)', 'flame'],
};

function EditView({ onApprove }) {
  const dr = GR_DATA.draft;
  const [tab, setTab] = React.useState('ai');
  return (
    <div className="page wide fade-up">
      <div className="tabs">
        <button className={'tab' + (tab === 'author' ? ' on' : '')} onClick={() => setTab('author')}>Версия автора</button>
        <button className={'tab' + (tab === 'ai' ? ' on' : '')} onClick={() => setTab('ai')}>Версия AI</button>
        <button className={'tab' + (tab === 'final' ? ' on' : '')} onClick={() => setTab('final')}>Финал</button>
      </div>
      <div className="edit-grid">
        <div className="doc">
          <span className="rub">{GR_DATA.brief.rubric}</span>
          <h1 style={{ marginTop: 12 }}>{dr.title}</h1>
          {dr.paras.map((p, i) => (
            <p key={i}>
              {i === 2 && tab === 'ai'
                ? <>AI отлично закрывает механику. Он не закрывает позицию. <span className="mark-del">Важно отметить, что в современном мире</span> <span className="mark-add">Заменяет он не автора</span>, а того, кто и раньше писал без неё — гладко, корректно и ни о чём.</>
                : p}
            </p>
          ))}
        </div>
        <div className="aside">
          <div className="panel">
            <h4>Проверки редакции</h4>
            {GR_DATA.checks.map((c, i) => {
              const [bg, fg, ic] = GR_CHK[c.state];
              return (
                <div key={i} className="check">
                  <div className="ci" style={{ background: bg, color: fg }}><Icon name={ic} size={16} /></div>
                  <div className="cb"><b>{c.title}</b><span>{c.text}</span></div>
                </div>
              );
            })}
          </div>
          <div className="panel">
            <h4>Альтернативные заголовки</h4>
            <div className="alt">
              {dr.headlines.map((h, i) => (
                <div key={i} className="alt-item">{h}{i === 0 && <span className="pick">выбран</span>}</div>
              ))}
            </div>
          </div>
          <div className="panel">
            <h4>Замечания редакторов</h4>
            {GR_DATA.notes.map((n, i) => {
              const [bg, fg] = GR_NOTE_TINT[n.tint];
              return (
                <div key={i} className="note">
                  <div className="av" style={{ background: bg, color: fg }}>{n.ag}</div>
                  <div className="nt"><b>{n.name}</b><p>{n.text}</p></div>
                </div>
              );
            })}
          </div>
          <button className="btn btn-pri" style={{ width: '100%', justifyContent: 'center' }} onClick={onApprove}>
            <Icon name="check" size={16} />Утвердить текст
          </button>
        </div>
      </div>
    </div>
  );
}

// ---- Light views --------------------------------------------------------
function Placeholder({ icon, title, text }) {
  return (
    <div className="page fade-up" style={{ textAlign: 'center', paddingTop: 90 }}>
      <div style={{ width: 64, height: 64, borderRadius: 'var(--r-xl)', background: 'var(--accent-wash)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)', marginBottom: 18 }}>
        <Icon name={icon} size={30} />
      </div>
      <h2 style={{ font: 'var(--ed-h1)', fontSize: 30, color: 'var(--ink-900)', margin: '0 0 10px' }}>{title}</h2>
      <p style={{ font: 'var(--ui-md)', color: 'var(--ink-600)', maxWidth: 460, margin: '0 auto' }}>{text}</p>
    </div>
  );
}

window.BriefView = BriefView;
window.EditView = EditView;
window.Placeholder = Placeholder;
