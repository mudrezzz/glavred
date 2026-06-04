import { useEffect, useMemo, useState } from 'react';
import {
  createContentPlanItem,
  createEditorNotes,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  runEditorialChecks
} from './application/editorialServices';
import {
  approveFinalText,
  approvePlanItem,
  approvePostBrief,
  reviseDraft,
  type EditorialCheck,
  type EditorialModel,
  type FinalText,
  type PostBrief,
  type PostDraft,
  type SourceSignal,
  type WorkspaceSection,
  type WorkspaceState
} from './domain/editorialWorkspace';
import { LocalWorkspaceStore } from './infrastructure/localWorkspaceStore';

const store = new LocalWorkspaceStore();

const NAV: Array<{ id: WorkspaceSection; icon: string; label: string; count?: string; disabled?: boolean }> = [
  { id: 'editorialModel', icon: 'model', label: 'Редакционная модель' },
  { id: 'radar', icon: 'radar', label: 'Радар', count: '1' },
  { id: 'plan', icon: 'plan', label: 'План', count: '1' },
  { id: 'brief', icon: 'brief', label: 'Фабулы', count: '1' },
  { id: 'edit', icon: 'edit', label: 'Редактура' },
  { id: 'release', icon: 'release', label: 'Выпуск', disabled: true },
  { id: 'analytics', icon: 'analytics', label: 'Аналитика', disabled: true }
];

const TITLES: Record<WorkspaceSection, [string, string]> = {
  editorialModel: ['Редакционная модель', 'Правила и контекст блога'],
  radar: ['Радар', 'Источник -> инсайт'],
  plan: ['План', 'HITL · Gate 1'],
  brief: ['Фабула поста', 'HITL · Gate 2'],
  edit: ['Редактура', 'HITL · Gate 3'],
  release: ['Выпуск', 'Следующий этап'],
  analytics: ['Аналитика', 'Редакционные выводы']
};

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, string> = {
    model:
      '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    radar:
      '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
    plan:
      '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/>',
    brief:
      '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    edit:
      '<path d="M12.5 22H18a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v9.5"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M13.4 15.6a1 1 0 1 0-3-3l-5 5a2 2 0 0 0-.5.9l-.8 2.9a.5.5 0 0 0 .6.6l2.9-.8a2 2 0 0 0 .9-.5z"/>',
    release:
      '<path d="M14.5 21.7a.5.5 0 0 0 .9 0l6.5-19a.5.5 0 0 0-.6-.6l-19 6.5a.5.5 0 0 0 0 .9l7.9 3.2a2 2 0 0 1 1.1 1.1z"/><path d="m21.9 2.1-10.9 11"/>',
    analytics: '<path d="M16 7h6v6"/><path d="m22 7-8.5 8.5-5-5L2 17"/>',
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    bell:
      '<path d="M10.3 21a2 2 0 0 0 3.4 0"/><path d="M3.3 15.3A1 1 0 0 0 4 17h16a1 1 0 0 0 .7-1.7C19.4 14 18 12.5 18 8A6 6 0 0 0 6 8c0 4.5-1.4 6-2.7 7.3"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
    reset: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 3v6h6"/>',
    caret: '<path d="M4 16 L12 7 L20 16"/>'
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      dangerouslySetInnerHTML={{ __html: paths[name] ?? '' }}
    />
  );
}

export function App() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() => store.load());
  const active = workspace.activeSection;
  const [toast, setToast] = useState('Рабочее пространство сохранено локально');

  useEffect(() => {
    store.save({ ...workspace, updatedAt: new Date().toISOString() });
  }, [workspace]);

  function patchWorkspace(patch: Partial<WorkspaceState>, message?: string) {
    setWorkspace((current) => ({ ...current, ...patch, updatedAt: new Date().toISOString() }));
    if (message) {
      setToast(message);
    }
  }

  function go(section: WorkspaceSection) {
    patchWorkspace({ activeSection: section });
  }

  function resetDemo() {
    setWorkspace(store.reset());
    setToast('Демо-сценарий восстановлен');
  }

  return (
    <div className="app">
      <Sidebar active={active} onNav={go} workspace={workspace} />
      <main className="main">
        <Topbar active={active} onReset={resetDemo} />
        <div className="scroll">
          {active === 'editorialModel' && (
            <EditorialModelView
              model={workspace.editorialModel}
              onChange={(editorialModel) => patchWorkspace({ editorialModel })}
            />
          )}
          {active === 'radar' && (
            <RadarView
              workspace={workspace}
              onSignalChange={(sourceSignal) => patchWorkspace({ sourceSignal })}
              onCreateInsight={() => {
                const insightCard = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
                patchWorkspace({ insightCard }, 'Карточка инсайта собрана');
              }}
              onPlan={() => {
                const insightCard =
                  workspace.insightCard ?? createInsightCard(workspace.sourceSignal, workspace.editorialModel);
                const contentPlanItem = createContentPlanItem(insightCard);
                patchWorkspace(
                  { insightCard, contentPlanItem, activeSection: 'plan' },
                  'Инсайт добавлен в план'
                );
              }}
            />
          )}
          {active === 'plan' && (
            <PlanView
              workspace={workspace}
              onApprove={() => {
                if (!workspace.contentPlanItem) return;
                patchWorkspace(
                  { contentPlanItem: approvePlanItem(workspace.contentPlanItem) },
                  'План утвержден'
                );
              }}
              onBrief={() => {
                if (!workspace.contentPlanItem || !workspace.insightCard) return;
                const postBrief = createPostBrief(
                  workspace.contentPlanItem,
                  workspace.insightCard,
                  workspace.editorialModel
                );
                patchWorkspace({ postBrief, activeSection: 'brief' }, 'Фабула подготовлена');
              }}
            />
          )}
          {active === 'brief' && (
            <BriefView
              workspace={workspace}
              onBriefChange={(postBrief) => patchWorkspace({ postBrief })}
              onApprove={() => {
                if (!workspace.postBrief) return;
                patchWorkspace({ postBrief: approvePostBrief(workspace.postBrief) }, 'Фабула утверждена');
              }}
            />
          )}
          {active === 'edit' && (
            <EditView
              workspace={workspace}
              onGoBrief={() => go('brief')}
              onCreateDraft={() => {
                if (!workspace.postBrief || workspace.postBrief.approvalStatus !== 'approved') return;
                const postDraft = createPostDraft(workspace.postBrief, workspace.editorialModel);
                const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
                const editorNotes = createEditorNotes(editorialChecks);
                patchWorkspace(
                  { postDraft, editorialChecks, editorNotes, finalText: null },
                  'Драфт подготовлен для редакторских проверок'
                );
              }}
              onDraftChange={(body) => {
                if (!workspace.postDraft || !workspace.postBrief) return;
                const postDraft = reviseDraft(workspace.postDraft, body);
                const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
                const editorNotes = createEditorNotes(editorialChecks);
                patchWorkspace({ postDraft, editorialChecks, editorNotes, finalText: null });
              }}
              onApproveFinal={() => {
                if (!workspace.postDraft) return;
                const finalText = approveFinalText(workspace.postDraft);
                patchWorkspace({ finalText }, 'Финальный текст утвержден');
              }}
            />
          )}
          {active === 'release' && (
            <Placeholder
              icon="release"
              title="Выпуск"
              text="Публикация и адаптация под площадки остаются будущим расширением после редакторского пайплайна."
            />
          )}
          {active === 'analytics' && (
            <Placeholder
              icon="analytics"
              title="Аналитика"
              text="Здесь будут не просмотры ради просмотров, а редакционные выводы для следующего цикла."
            />
          )}
        </div>
      </main>
      {toast ? (
        <div className="toast" role="status">
          <Icon name="check" size={17} />
          {toast}
        </div>
      ) : null}
    </div>
  );
}

function Sidebar({
  active,
  onNav,
  workspace
}: {
  active: WorkspaceSection;
  onNav: (section: WorkspaceSection) => void;
  workspace: WorkspaceState;
}) {
  return (
    <aside className="side">
      <div className="brand">
        <span className="brand-mark">Г</span>
        <span className="wm">Главред</span>
      </div>
      <div className="nav-label">Редакция</div>
      {NAV.map((item) => (
        <button
          key={item.id}
          className={`nav-item${active === item.id ? ' active' : ''}${item.disabled ? ' muted' : ''}`}
          onClick={() => onNav(item.id)}
          type="button"
        >
          <Icon name={item.icon} />
          <span>{item.label}</span>
          {item.count ? <span className="count">{item.count}</span> : null}
        </button>
      ))}
      <div className="side-foot">
        <div className="author">
          <div className="ava">АК</div>
          <div>
            <b>{workspace.editorialModel.author.split(' — ')[0]}</b>
            <span>Главный редактор</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ active, onReset }: { active: WorkspaceSection; onReset: () => void }) {
  const [title, subtitle] = TITLES[active];

  return (
    <header className="topbar">
      <div className="crumb">
        {title}
        <small>{subtitle}</small>
      </div>
      <div className="spacer" />
      <div className="search">
        <Icon name="search" size={16} />
        <input aria-label="Поиск" placeholder="Поиск по темам, фабулам..." />
      </div>
      <button className="icon-btn" type="button" aria-label="Уведомления">
        <Icon name="bell" />
        <span className="dot" />
      </button>
      <button className="btn btn-sec btn-sm" type="button" onClick={onReset}>
        <Icon name="reset" size={14} />
        Сбросить демо
      </button>
    </header>
  );
}

function EditorialModelView({
  model,
  onChange
}: {
  model: EditorialModel;
  onChange: (model: EditorialModel) => void;
}) {
  return (
    <div className="page wide fade-up">
      <section className="model-hero">
        <blockquote>{model.fabula}</blockquote>
        <span className="gr-mark">Фабула блога · ядро решений редакции</span>
      </section>
      <div className="model-grid">
        <TextAreaCard title="Автор" value={model.author} onChange={(author) => onChange({ ...model, author })} />
        <TextAreaCard
          title="Аудитория"
          value={model.audience}
          onChange={(audience) => onChange({ ...model, audience })}
        />
        <TextAreaCard
          title="Позиционирование"
          value={model.positioning}
          onChange={(positioning) => onChange({ ...model, positioning })}
        />
        <TextAreaCard
          title="Фабула"
          value={model.fabula}
          onChange={(fabula) => onChange({ ...model, fabula })}
        />
        <ListCard title="Рубрики" items={model.rubrics} onChange={(rubrics) => onChange({ ...model, rubrics })} />
        <ListCard
          title="Стиль автора"
          items={model.styleRules}
          onChange={(styleRules) => onChange({ ...model, styleRules })}
        />
        <ListCard
          title="Запреты"
          items={model.forbiddenTopics}
          onChange={(forbiddenTopics) => onChange({ ...model, forbiddenTopics })}
        />
        <ListCard title="Цели блога" items={model.goals} onChange={(goals) => onChange({ ...model, goals })} />
      </div>
    </div>
  );
}

function TextAreaCard({
  title,
  value,
  onChange
}: {
  title: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="card edit-card">
      <span>{title}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function ListCard({
  title,
  items,
  onChange
}: {
  title: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  return (
    <label className="card edit-card">
      <span>{title}</span>
      <textarea value={items.join('\n')} onChange={(event) => onChange(splitLines(event.target.value))} />
    </label>
  );
}

function RadarView({
  workspace,
  onSignalChange,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  onSignalChange: (signal: SourceSignal) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const insight = workspace.insightCard;

  return (
    <div className="page fade-up">
      <div className="sec-head">
        <h2>Поводы и инсайты</h2>
        <span className="sub">Один ручной сигнал для первого рабочего периметра</span>
      </div>
      <section className="card signal-editor">
        <div className="form-row">
          <label>
            Тип сигнала
            <input
              value={workspace.sourceSignal.type}
              onChange={(event) => onSignalChange({ ...workspace.sourceSignal, type: event.target.value })}
            />
          </label>
          <label>
            Источник
            <input
              value={workspace.sourceSignal.source}
              onChange={(event) => onSignalChange({ ...workspace.sourceSignal, source: event.target.value })}
            />
          </label>
        </div>
        <label>
          Заголовок сигнала
          <input
            value={workspace.sourceSignal.title}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, title: event.target.value })}
          />
        </label>
        <label>
          Краткое содержание
          <textarea
            value={workspace.sourceSignal.summary}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, summary: event.target.value })}
          />
        </label>
        <label>
          Заметка автора
          <textarea
            value={workspace.sourceSignal.rawNote}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, rawNote: event.target.value })}
          />
        </label>
        <button className="btn btn-sec" type="button" onClick={onCreateInsight}>
          <Icon name="radar" size={16} />
          Собрать инсайт
        </button>
      </section>
      {insight ? (
        <section className="card hover insight">
          <div className="top">
            <span className="sig info">{workspace.sourceSignal.type}</span>
            <span className="rub">{insight.rubric}</span>
            <span className="urgent">Риск банальности {formatScore(insight.banalityRisk)}</span>
          </div>
          <h3>{insight.title}</h3>
          <p className="why">{insight.whyItMatters}</p>
          <div className="foot">
            <span className="sc">
              релевантность <b>{formatScore(insight.score)}</b>
            </span>
            <span className="sc">
              срочность <b>{insight.urgency}</b>
            </span>
            <div className="actions">
              <button className="btn btn-pri btn-sm" type="button" onClick={onPlan}>
                <Icon name="caret" size={14} />В план
              </button>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function PlanView({
  workspace,
  onApprove,
  onBrief
}: {
  workspace: WorkspaceState;
  onApprove: () => void;
  onBrief: () => void;
}) {
  const item = workspace.contentPlanItem;

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 1 — План"
        title="Утвердите публикацию перед фабулой"
        subtitle="План фиксирует формат, дату, площадку и ожидаемый эффект."
        action="Утвердить план"
        disabled={!item}
        onAction={onApprove}
      />
      {item ? (
        <div className="week single-week">
          <div className="day today">
            <div className="dh">
              <b>Пт</b>
              <span>5 июня</span>
            </div>
            <article className="pcard">
              <span className="rub">{item.format}</span>
              <div className="pt">{item.title}</div>
              <div className="pf">
                <span className="plat">{item.platform}</span>
                <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
                  <i />
                  {statusLabel(item.approvalStatus)}
                </span>
              </div>
            </article>
            <p className="plan-effect">{item.expectedEffect}</p>
            <button
              className="btn btn-pri"
              type="button"
              disabled={item.approvalStatus !== 'approved'}
              onClick={onBrief}
            >
              <Icon name="brief" size={16} />
              Подготовить фабулу
            </button>
          </div>
        </div>
      ) : (
        <EmptyState text="Сначала добавьте инсайт в план из раздела «Радар»." />
      )}
    </div>
  );
}

function BriefView({
  workspace,
  onBriefChange,
  onApprove
}: {
  workspace: WorkspaceState;
  onBriefChange: (brief: PostBrief) => void;
  onApprove: () => void;
}) {
  const brief = workspace.postBrief;

  if (!brief) {
    return (
      <div className="page fade-up">
        <EmptyState text="Сначала подготовьте фабулу из утвержденного элемента плана." />
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 2 — Замысел"
        title="Утвердите фабулу перед написанием"
        subtitle="Слабые тексты обычно проваливаются на замысле. Решение остается за главным редактором."
        action="Утвердить фабулу"
        onAction={onApprove}
      />
      <div className="brief-grid">
        <section className="brief-body">
          <span className="rub">{brief.rubric}</span>
          <FieldInput label="Заголовок" value={brief.title} onChange={(title) => onBriefChange({ ...brief, title })} />
          <FieldInput
            label="Главный тезис"
            value={brief.thesis}
            onChange={(thesis) => onBriefChange({ ...brief, thesis })}
            serif
          />
          <FieldInput
            label="Конфликт"
            value={brief.conflict}
            onChange={(conflict) => onBriefChange({ ...brief, conflict })}
          />
          <FieldInput
            label="Авторская позиция"
            value={brief.authorPosition}
            onChange={(authorPosition) => onBriefChange({ ...brief, authorPosition })}
          />
          <FieldList label="Доказательства" items={brief.evidence} onChange={(evidence) => onBriefChange({ ...brief, evidence })} />
          <FieldList label="Структура" items={brief.structure} onChange={(structure) => onBriefChange({ ...brief, structure })} />
          <FieldInput label="CTA" value={brief.cta} onChange={(cta) => onBriefChange({ ...brief, cta })} />
          <FieldList label="Риски" items={brief.risks} onChange={(risks) => onBriefChange({ ...brief, risks })} />
        </section>
        <aside className="aside">
          <div className="panel">
            <h4>Статус</h4>
            <span className={`pill ${brief.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
              <i />
              {statusLabel(brief.approvalStatus)}
            </span>
          </div>
          <div className="panel">
            <h4>Источники</h4>
            <ul className="bullets">
              {brief.sources.map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

function EditView({
  workspace,
  onGoBrief,
  onCreateDraft,
  onDraftChange,
  onApproveFinal
}: {
  workspace: WorkspaceState;
  onGoBrief: () => void;
  onCreateDraft: () => void;
  onDraftChange: (body: string) => void;
  onApproveFinal: () => void;
}) {
  const [tab, setTab] = useState<'brief' | 'draft' | 'final'>(() => (workspace.finalText ? 'final' : 'draft'));
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;

  if (!brief || brief.approvalStatus !== 'approved') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="brief" size={28} />
          </div>
          <h2>Сначала утвердите фабулу</h2>
          <p>Редактура открывается только после Gate 2: утвержденной фабулы поста.</p>
          <button className="btn btn-pri" type="button" onClick={onGoBrief}>
            <Icon name="brief" size={16} />
            Перейти к фабуле
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 3 — Финальный текст"
        title="Проверьте драфт и утвердите финальную версию"
        subtitle="Warnings не блокируют утверждение: человек остается главным редактором и видит риски перед решением."
        action="Утвердить текст"
        disabled={!draft}
        onAction={onApproveFinal}
      />
      <div className="tabs" role="tablist" aria-label="Редакторские вкладки">
        <button className={`tab${tab === 'brief' ? ' active' : ''}`} type="button" onClick={() => setTab('brief')}>
          Фабула
        </button>
        <button className={`tab${tab === 'draft' ? ' active' : ''}`} type="button" onClick={() => setTab('draft')}>
          Драфт
        </button>
        <button className={`tab${tab === 'final' ? ' active' : ''}`} type="button" onClick={() => setTab('final')}>
          Финал
        </button>
      </div>

      {!draft ? (
        <section className="card draft-start">
          <span className="rub">{brief.rubric}</span>
          <h2>{brief.title}</h2>
          <p>{brief.thesis}</p>
          <button className="btn btn-pri" type="button" onClick={onCreateDraft}>
            <Icon name="edit" size={16} />
            Написать драфт
          </button>
        </section>
      ) : (
        <div className="edit-grid">
          <section className="doc">
            {tab === 'brief' && <BriefSnapshot brief={brief} />}
            {tab === 'draft' && (
              <>
                <div className="doc-head">
                  <div>
                    <span className="rub">Версия {draft.version}</span>
                    <h2>{draft.title}</h2>
                  </div>
                  <span className={`pill ${draft.status === 'revised' ? 'pin' : 'ok'}`}>
                    <i />
                    {draft.status === 'revised' ? 'Отредактирован' : 'Драфт'}
                  </span>
                </div>
                <label className="draft-editor">
                  <span className="k">Текст</span>
                  <textarea
                    aria-label="Текст драфта"
                    value={draft.body}
                    onChange={(event) => onDraftChange(event.target.value)}
                  />
                </label>
              </>
            )}
            {tab === 'final' && <FinalTextView finalText={finalText} draft={draft} />}
          </section>
          <aside className="edit-side">
            <section className="panel">
              <h4>Проверки</h4>
              <div className="checks">
                {workspace.editorialChecks.map((check) => (
                  <CheckCard key={check.id} check={check} />
                ))}
              </div>
            </section>
            <section className="panel">
              <h4>Заметки редакторов</h4>
              <div className="notes">
                {workspace.editorNotes.map((note) => (
                  <article className="note" key={note.id}>
                    <div className="note-head">
                      <span className="av">{note.agent.slice(0, 2)}</span>
                      <div>
                        <b>{note.agent}</b>
                        <span>{note.tone} · {note.target}</span>
                      </div>
                    </div>
                    <p>{note.text}</p>
                  </article>
                ))}
              </div>
            </section>
          </aside>
        </div>
      )}
    </div>
  );
}

function BriefSnapshot({ brief }: { brief: PostBrief }) {
  return (
    <div className="brief-snapshot">
      <span className="rub">{brief.rubric}</span>
      <h2>{brief.title}</h2>
      <p className="lead">{brief.thesis}</p>
      <div className="snapshot-grid">
        <InfoBlock title="Конфликт" items={[brief.conflict]} />
        <InfoBlock title="Позиция" items={[brief.authorPosition]} />
        <InfoBlock title="Доказательства" items={brief.evidence} />
        <InfoBlock title="Риски" items={brief.risks} />
      </div>
    </div>
  );
}

function FinalTextView({ finalText, draft }: { finalText: FinalText | null; draft: PostDraft }) {
  if (!finalText) {
    return (
      <div className="final-empty">
        <h2>Финал еще не утвержден</h2>
        <p>Проверьте драфт, замечания редакторов и нажмите «Утвердить текст».</p>
      </div>
    );
  }

  return (
    <article className="final-doc">
      <div className="final-status">
        <span className="pill ok">
          <i />
          Финальный текст утвержден
        </span>
        <span>на основе версии {draft.version}</span>
      </div>
      <h2>{finalText.title}</h2>
      <pre>{finalText.body}</pre>
    </article>
  );
}

function InfoBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="info-block">
      <h4>{title}</h4>
      <ul className="bullets">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function CheckCard({ check }: { check: EditorialCheck }) {
  return (
    <article className={`check check-${check.status}`}>
      <div className="check-head">
        <span className="ci">{check.title.slice(0, 1)}</span>
        <div>
          <b>{check.title}</b>
          <span>{checkStatusLabel(check.status)}</span>
        </div>
      </div>
      <p>{check.summary}</p>
      <ul className="bullets">
        {check.findings.map((finding) => (
          <li key={finding}>{finding}</li>
        ))}
      </ul>
    </article>
  );
}

function HitlGate({
  tag,
  title,
  subtitle,
  action,
  disabled,
  onAction
}: {
  tag: string;
  title: string;
  subtitle: string;
  action: string;
  disabled?: boolean;
  onAction: () => void;
}) {
  return (
    <section className="gate">
      <div className="gm">
        <Icon name="caret" size={24} />
      </div>
      <div>
        <div className="gtag">{tag}</div>
        <div className="gttl">{title}</div>
        <div className="gsub">{subtitle}</div>
      </div>
      <div className="gbtns">
        <button className="btn btn-pri" type="button" disabled={disabled} onClick={onAction}>
          <Icon name="check" size={16} />
          {action}
        </button>
      </div>
    </section>
  );
}

function FieldInput({
  label,
  value,
  onChange,
  serif
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  serif?: boolean;
}) {
  return (
    <label className="field-row">
      <span className="k">{label}</span>
      <textarea className={serif ? 'serif' : ''} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function FieldList({
  label,
  items,
  onChange
}: {
  label: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  return <FieldInput label={label} value={items.join('\n')} onChange={(value) => onChange(splitLines(value))} />;
}

function Placeholder({ icon, title, text }: { icon: string; title: string; text: string }) {
  return (
    <div className="page fade-up placeholder">
      <div className="placeholder-icon">
        <Icon name={icon} size={30} />
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}

function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatScore(value: number): string {
  return value.toFixed(2);
}

function statusLabel(status: string): string {
  if (status === 'approved') return 'Утверждено';
  if (status === 'rejected') return 'Отклонено';
  return 'Черновик';
}

function checkStatusLabel(status: string): string {
  if (status === 'passed') return 'Пройдено';
  if (status === 'warning') return 'Есть warning';
  return 'Блокер';
}
