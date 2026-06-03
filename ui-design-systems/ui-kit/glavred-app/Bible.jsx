// Editorial Bible — the blog's "constitution". The product's core object.
function BibleCard({ icon, title, children, tall }) {
  return (
    <div className="card" style={{ padding: '20px 22px', gridRow: tall ? 'span 2' : 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div style={{ width: 34, height: 34, borderRadius: 'var(--r-md)', background: 'var(--accent-wash)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)', flex: 'none' }}>
          <Icon name={icon} size={18} />
        </div>
        <h4 style={{ font: 'var(--ui-lg)', color: 'var(--ink-900)', margin: 0, flex: 1 }}>{title}</h4>
        <button className="btn btn-ghost btn-sm">Изменить</button>
      </div>
      {children}
    </div>
  );
}
function TagRow({ items, tone }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {items.map(t => <span key={t} className={tone === 'no' ? 'pill danger' : 'rub'} style={{ fontSize: 12 }}>{t}</span>)}
    </div>
  );
}

function BibleView() {
  return (
    <div className="page wide fade-up">
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, marginBottom: 24 }}>
        <div style={{ flex: 1 }}>
          <blockquote style={{ font: 'var(--ed-quote)', fontStyle: 'italic', color: 'var(--ink-800)', borderLeft: '3px solid var(--accent)', margin: 0, padding: '4px 0 4px 18px', maxWidth: '60ch' }}>
            «Я помогаю предпринимателям смотреть на AI не как на магию и не как на игрушку, а как на новую операционную систему бизнеса».
          </blockquote>
          <div className="gr-mark" style={{ marginTop: 12 }}>Фабула блога · ядро всех решений редакции</div>
        </div>
        <button className="btn btn-sec"><Icon name="sparkles" size={16} />Дообучить на постах</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, alignItems: 'start' }}>
        <BibleCard icon="bible" title="Автор">
          <p style={{ font: 'var(--ui-md)', color: 'var(--ink-700)', margin: 0, lineHeight: 1.6 }}>
            Анна Корн — консультант по процессам и операционной эффективности. Образ: трезвый практик без хайпа, который видел внедрения изнутри.
          </p>
        </BibleCard>

        <BibleCard icon="radar" title="Аудитория">
          <p style={{ font: 'var(--ui-md)', color: 'var(--ink-700)', margin: '0 0 12px', lineHeight: 1.6 }}>
            Основатели и операционные директора 30–45 лет, которые внедряют AI, но устали от обещаний.
          </p>
          <TagRow items={['Founders', 'COO / Ops', 'Консультанты']} />
        </BibleCard>

        <BibleCard icon="quote" title="Рубрикатор" tall>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[['Разборы', 'Объясняем сложное просто'], ['Антимнение', 'Спорим с заблуждением'], ['Кейсы', 'Применение на практике'], ['Полевые заметки', 'Личные наблюдения'], ['Методология', 'Системные фреймворки'], ['Реакции', 'Быстрый комментарий']].map(([r, d]) => (
              <div key={r} style={{ display: 'flex', alignItems: 'center', gap: 12, paddingBottom: 10, borderBottom: '1px solid var(--ink-100)' }}>
                <span className="rub">{r}</span>
                <span style={{ font: 'var(--ui-sm)', color: 'var(--ink-600)' }}>{d}</span>
              </div>
            ))}
          </div>
        </BibleCard>

        <BibleCard icon="edit" title="Стиль автора">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
            {[['Длина фраз', 'Короткие, рубленые'], ['Ирония', 'Сухая, дозированная'], ['Начало поста', 'С наблюдения из ленты'], ['Примеры', 'Только из практики']].map(([k, v]) => (
              <div key={k} className="kv" style={{ borderTop: '1px solid var(--ink-100)', padding: '7px 0' }}>
                <span className="lk">{k}</span><span className="lv">{v}</span>
              </div>
            ))}
          </div>
        </BibleCard>

        <BibleCard icon="shield" title="Запреты — чего в текстах быть не должно">
          <TagRow tone="no" items={['«важно отметить»', '«в современном мире»', 'симметричные списки', 'консалтинговый тон', 'пустые обобщения', 'политика', 'прогнозы курсов']} />
        </BibleCard>
      </div>
    </div>
  );
}
window.BibleView = BibleView;
