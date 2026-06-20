import type { DraftGenerationSource, DraftGenerationUiState, EditorialWorkItem, WorkspaceState } from '../../domain/editorialWorkspace';
import { stageLabel, workStatusLabel } from './editorialWorkQueueFilters';
import { TraceRunLink } from './TraceRunLink';

export function EditorialPostsAside({ items }: { items: EditorialWorkItem[] }) {
  const todo = items.filter((item) => item.status === 'todo').length;
  const inProgress = items.filter((item) => item.status === 'inProgress').length;
  const ready = items.filter((item) => item.stage === 'readyForRelease').length;
  const nextItems = [...items]
    .sort((left, right) => `${left.date}T${left.time}`.localeCompare(`${right.date}T${right.time}`))
    .slice(0, 3);

  return (
    <aside className="memory-side editorial-side">
      <section className="panel">
        <h3>Очередь</h3>
        <div className="signal-summary-grid editorial-summary-grid">
          <Metric label="постов" value={items.length} />
          <Metric label="в очереди" value={todo} />
          <Metric label="в работе" value={inProgress} />
          <Metric label="к выпуску" value={ready} />
        </div>
      </section>
      <section className="panel">
        <h3>Ближайшие</h3>
        <div className="aside-list">
          {nextItems.length > 0 ? nextItems.map((item) => (
            <article key={item.id}>
              <b>{item.title}</b>
              <span>{formatWorkDateTime(item.date, item.time)} · {stageLabel(item.stage)}</span>
            </article>
          )) : <p>Утвержденных постов пока нет.</p>}
        </div>
      </section>
    </aside>
  );
}

export function EditorialWorkbenchAside({
  workspace,
  draftGenerationState
}: {
  workspace: WorkspaceState;
  draftGenerationState: DraftGenerationUiState;
}) {
  const selected = workspace.editorialWorkItems.find((item) => item.id === workspace.selectedEditorialWorkItemId);
  const visual = workspace.postVisual ?? selected?.visual ?? null;
  const visualWarnings = getVisualWarnings(workspace, visual);

  return (
    <aside className="memory-side editorial-side">
      <section className="panel">
        <h3>Рабочий пост</h3>
        {selected ? (
          <dl className="side-dl">
            <div><dt>Стадия</dt><dd>{stageLabel(selected.stage)}</dd></div>
            <div><dt>Статус</dt><dd>{workStatusLabel(selected.status)}</dd></div>
            <div><dt>Публикация</dt><dd>{formatWorkDateTime(selected.date, selected.time)} · {selected.platform}</dd></div>
            <div><dt>Тема</dt><dd>{selected.topicTitle ?? 'Не задана'}</dd></div>
            <div><dt>Фабула</dt><dd>{selected.fabulaTitle ?? 'Не задана'}</dd></div>
          </dl>
        ) : <p>Выберите пост на рабочем столе.</p>}
      </section>
      <section className="panel">
        <h3>Готовность</h3>
        <dl className="side-dl">
          <div><dt>Текст</dt><dd>{workspace.finalText?.approvalStatus === 'approved' ? 'Утвержден' : 'Не утвержден'}</dd></div>
          <div><dt>Визуал</dt><dd>{visual ? visualStatusLabel(visual.approvalStatus, visual.mode) : 'Не начат'}</dd></div>
          {visual?.mode === 'memeRemix' ? <div><dt>Мем</dt><dd>{visual.selectedMemeReferenceId ? 'Выбран' : 'Не выбран'}</dd></div> : null}
          {visual?.mode === 'memeRemix' ? <div><dt>Кастом</dt><dd>{visual.variants.length ? `${visual.variants.length} подготовлено` : 'Не подготовлен'}</dd></div> : null}
          <div><dt>Варианты</dt><dd>{visual?.mode === 'noVisual' ? 'Не нужны' : visual?.variants.length ? `${visual.variants.length} подготовлено` : 'Не подготовлены'}</dd></div>
          <div><dt>Выбор</dt><dd>{visual?.mode === 'noVisual' ? 'Без визуала' : visual?.selectedVariantId ? 'Вариант выбран' : 'Не выбран'}</dd></div>
          <div><dt>К выпуску</dt><dd>Нет</dd></div>
        </dl>
        {visualWarnings.length > 0 ? (
          <div className="aside-list">
            {visualWarnings.map((warning) => (
              <article key={warning}>
                <b>Предупреждение</b>
                <p>{warning}</p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
      <section className="panel">
        <h3>AI trace</h3>
        <dl className="side-dl">
          <div><dt>Статус</dt><dd>{draftGenerationState.status === 'generating' ? 'Генерация идет' : workspace.postDraft?.generation ? 'Записан' : 'Нет run'}</dd></div>
          <div><dt>Источник</dt><dd>{draftSourceLabel(workspace.postDraft?.generation?.source)}</dd></div>
          <div><dt>Provider</dt><dd>{workspace.postDraft?.generation?.provider ?? 'none'}</dd></div>
          <div><dt>Model</dt><dd>{workspace.postDraft?.generation?.model ?? 'none'}</dd></div>
          {draftGenerationState.status === 'generating' ? <div><dt>DraftRun</dt><dd>{draftGenerationState.runId ? <TraceRunLink runId={draftGenerationState.runId} label={draftGenerationState.runId} /> : 'queued'}</dd></div> : null}
          {draftGenerationState.status === 'generating' ? <div><dt>Шаг</dt><dd>{draftGenerationState.stepLabel ?? 'ожидаем worker'}</dd></div> : null}
          {workspace.postDraft?.generation?.draftRunId ? <div><dt>DraftRun</dt><dd><TraceRunLink runId={workspace.postDraft.generation.draftRunId} label={workspace.postDraft.generation.draftRunId} /></dd></div> : null}
          <div><dt>AiRun</dt><dd>{workspace.postDraft?.generation?.aiRunId ?? 'not recorded'}</dd></div>
          {draftGenerationState.status === 'failed' ? <div><dt>Ошибка</dt><dd>{draftGenerationState.error}</dd></div> : null}
        </dl>
      </section>
      <section className="panel">
        <h3>Проверки</h3>
        <div className="checks compact-checks">
          {workspace.editorialChecks.length > 0 ? workspace.editorialChecks.map((check) => (
            <article className={`check check-${check.status}`} key={check.id}>
              <b>{check.title}</b>
              <span>{check.status}</span>
              <p>{check.summary}</p>
            </article>
          )) : <p>Проверки появятся после драфта.</p>}
        </div>
      </section>
      <section className="panel">
        <h3>Заметки</h3>
        <div className="aside-list">
          {workspace.editorNotes.length > 0 ? workspace.editorNotes.map((note) => (
            <article key={note.id}>
              <b>{note.agent}</b>
              <span>{note.target}</span>
              <p>{note.text}</p>
            </article>
          )) : <p>Редакторских заметок пока нет.</p>}
        </div>
      </section>
    </aside>
  );
}

function draftSourceLabel(source: DraftGenerationSource | undefined): string {
  if (source === 'draftRun') return 'DraftRun';
  if (source === 'openrouter') return 'OpenRouter';
  if (source === 'backendFallback') return 'Backend fallback';
  if (source === 'localFallback') return 'Local fallback';
  return 'Нет';
}

function visualStatusLabel(status: string, mode: string): string {
  if (mode === 'noVisual' && status === 'approved') return 'Без визуала';
  return status === 'approved' ? 'Утвержден' : 'Черновик';
}

function getVisualWarnings(workspace: WorkspaceState, visual: WorkspaceState['postVisual']): string[] {
  if (workspace.finalText?.approvalStatus !== 'approved') return ['Сначала утвердите текст в Драфт.'];
  if (!visual) return ['Визуальное решение еще не начато.'];
  if (visual.mode !== 'noVisual' && !visual.brief) return ['Заполните бриф визуала.'];
  if (visual.mode === 'memeRemix' && visual.memeReferences.length === 0) return ['Подготовьте мемы для ремикса.'];
  if (visual.mode === 'memeRemix' && !visual.selectedMemeReferenceId) return ['Выберите мем для ремикса.'];
  if (visual.mode === 'memeRemix' && visual.variants.length === 0) return ['Сгенерируйте кастом-варианты.'];
  if (visual.mode !== 'noVisual' && visual.variants.length === 0) return ['Подготовьте варианты визуала.'];
  if (visual.mode !== 'noVisual' && !visual.selectedVariantId) return ['Выберите вариант визуала.'];
  return [];
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="summary-item">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

function formatWorkDateTime(date: string, time: string): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  const formattedDate = Number.isNaN(parsed.getTime())
    ? date
    : parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
  return time ? `${formattedDate} · ${time}` : formattedDate;
}
