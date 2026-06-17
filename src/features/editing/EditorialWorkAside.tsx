import type { EditorialWorkItem, WorkspaceState } from '../../domain/editorialWorkspace';
import { stageLabel, workStatusLabel } from './editorialWorkQueueFilters';

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

export function EditorialWorkbenchAside({ workspace }: { workspace: WorkspaceState }) {
  const selected = workspace.editorialWorkItems.find((item) => item.id === workspace.selectedEditorialWorkItemId);

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
