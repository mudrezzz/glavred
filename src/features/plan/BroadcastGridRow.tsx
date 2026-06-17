import { useState } from 'react';
import type { ContentPlanItem, PlanWeightWarning, WorkspaceState } from '../../domain/editorialWorkspace';
import { statusLabel } from '../../shared/format/production';
import { Icon } from '../../shared/ui/Icon';

export function BroadcastGridRow({
  defaultExpanded,
  item,
  itemWarnings,
  workspace,
  onApprove,
  onBrief,
  onItemChange
}: {
  defaultExpanded: boolean;
  item: ContentPlanItem;
  itemWarnings: PlanWeightWarning[];
  workspace: WorkspaceState;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
  onItemChange: (item: ContentPlanItem) => void;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [editingItem, setEditingItem] = useState<ContentPlanItem | null>(null);
  const isEditing = editingItem?.id === item.id;
  const current = isEditing ? editingItem : item;

  function startEdit() {
    setExpanded(true);
    setEditingItem({ ...item });
  }

  function saveEdit() {
    if (!editingItem) return;
    onItemChange({ ...editingItem, manualOverride: true });
    setEditingItem(null);
  }

  function updateEditingItem(patch: Partial<ContentPlanItem>) {
    setEditingItem((currentItem) => (currentItem ? { ...currentItem, ...patch } : currentItem));
  }

  function updateEditingTopic(topicId: string) {
    const topic = workspace.topics.find((candidate) => candidate.id === topicId);
    updateEditingItem({ topicId, topicTitle: topic?.title ?? '' });
  }

  function updateEditingFabula(fabulaId: string) {
    const fabula = workspace.fabulas.find((candidate) => candidate.id === fabulaId);
    updateEditingItem({ fabulaId, fabulaTitle: fabula?.title ?? '', format: fabula?.title ?? '' });
  }

  return (
    <article className={`card broadcast-row${expanded ? ' expanded' : ''}`}>
      <button className="broadcast-row-main" type="button" onClick={() => setExpanded((value) => !value)}>
        <span className="broadcast-date">{formatPlanDateTime(item.date, item.time)}</span>
        <span className="broadcast-title">{item.title}</span>
        <span className="broadcast-meta">{item.platform}</span>
        <span className="broadcast-meta">{item.topicTitle}</span>
        <span className="broadcast-meta">{item.fabulaTitle}</span>
        <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
          <i />
          {statusLabel(item.approvalStatus)}
        </span>
        {itemWarnings.length > 0 ? <span className="validation-badge yellow">warning</span> : null}
      </button>
      {expanded ? (
        <div className="broadcast-details">
          {isEditing && current ? (
            <div className="broadcast-edit-grid">
              <label>
                Заголовок
                <input value={current.title} onChange={(event) => updateEditingItem({ title: event.target.value })} />
              </label>
              <label>
                Дата
                <input type="date" value={current.date} onChange={(event) => updateEditingItem({ date: event.target.value })} />
              </label>
              <label>
                Время
                <input type="time" value={current.time} onChange={(event) => updateEditingItem({ time: event.target.value })} />
              </label>
              <label>
                Площадка
                <input value={current.platform} onChange={(event) => updateEditingItem({ platform: event.target.value })} />
              </label>
              <label>
                Тема
                <select value={current.topicId ?? ''} onChange={(event) => updateEditingTopic(event.target.value)}>
                  {workspace.topics.map((topic) => <option value={topic.id} key={topic.id}>{topic.title}</option>)}
                </select>
              </label>
              <label>
                Фабула
                <select value={current.fabulaId ?? ''} onChange={(event) => updateEditingFabula(event.target.value)}>
                  {workspace.fabulas.map((fabula) => <option value={fabula.id} key={fabula.id}>{fabula.title}</option>)}
                </select>
              </label>
              <label>
                Приоритет
                <input value={current.priority} onChange={(event) => updateEditingItem({ priority: event.target.value })} />
              </label>
              <label className="broadcast-edit-wide">
                Ожидаемый эффект
                <textarea value={current.expectedEffect} onChange={(event) => updateEditingItem({ expectedEffect: event.target.value })} />
              </label>
              <div className="entity-actions broadcast-edit-actions">
                <button className="btn btn-pri" type="button" onClick={saveEdit}>Сохранить</button>
                <button className="btn btn-sec" type="button" onClick={() => setEditingItem(null)}>Отменить</button>
              </div>
            </div>
          ) : (
            <>
              <dl className="entity-detail-list">
                <div><dt>Ожидаемый эффект</dt><dd>{item.expectedEffect}</dd></div>
                <div><dt>Связка</dt><dd>{item.topicTitle} · {item.fabulaTitle}</dd></div>
                <div><dt>Публикация</dt><dd>{formatPlanDateTime(item.date, item.time)} · {item.platform}</dd></div>
                <div><dt>Режим</dt><dd>{item.manualOverride ? 'Ручная правка сетки' : 'Собрано deterministic-сервисом'}</dd></div>
              </dl>
              {itemWarnings.length > 0 ? (
                <div className="matrix-warnings">
                  {itemWarnings.map((warning) => <p key={warning.id}>{warning.message}</p>)}
                </div>
              ) : null}
              <div className="entity-actions">
                <button className="btn btn-sec" type="button" onClick={startEdit}>Редактировать</button>
                <button className="btn btn-sec" type="button" disabled={item.approvalStatus === 'approved'} onClick={() => onApprove(item.id)}>
                  Утвердить
                </button>
                <button className="btn btn-pri" type="button" disabled={item.approvalStatus !== 'approved'} onClick={() => onBrief(item)}>
                  <Icon name="brief" size={16} />
                  Подготовить фабулу поста
                </button>
              </div>
            </>
          )}
        </div>
      ) : null}
    </article>
  );
}

function formatPlanDateTime(date: string, time: string): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  const formattedDate = Number.isNaN(parsed.getTime())
    ? date
    : parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
  return time ? `${formattedDate} · ${time}` : formattedDate;
}
