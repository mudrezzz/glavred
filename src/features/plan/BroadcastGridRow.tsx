import { useState } from 'react';
import type { ContentPlanItem, PlanWeightWarning, WorkspaceState } from '../../domain/editorialWorkspace';
import { statusLabel } from '../../shared/format/production';
import { Icon } from '../../shared/ui/Icon';
import { getPlanSlotContext } from './planSlotContext';

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
  const context = getPlanSlotContext(item, workspace);
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
    updateEditingItem({ fabulaId, fabulaTitle: fabula?.title ?? '' });
  }

  return (
    <article className={`card broadcast-row${expanded ? ' expanded' : ''}`}>
      <button className="broadcast-row-main" type="button" onClick={() => setExpanded((value) => !value)}>
        <span className="broadcast-date">{formatPlanDateTime(item.date, item.time)}</span>
        <span className="broadcast-row-copy">
          <span className="broadcast-title">{item.title}</span>
          <span className="broadcast-row-meta">
            <span>{item.platform}</span>
            <span>{context.topicTitle}</span>
            <span>{context.fabulaTitle}</span>
          </span>
        </span>
        <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
          <i />
          {statusLabel(item.approvalStatus)}
        </span>
        {itemWarnings.length > 0 ? <span className="validation-badge yellow">warning</span> : null}
      </button>
      {expanded ? (
        <div className="broadcast-details">
          {isEditing && current ? (
            <div className="broadcast-edit-stack">
              <ReadOnlyContext item={item} workspace={workspace} />
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
                  Тема слота
                  <select value={current.topicId ?? ''} onChange={(event) => updateEditingTopic(event.target.value)}>
                    {workspace.topics.map((topic) => <option value={topic.id} key={topic.id}>{topic.title}</option>)}
                  </select>
                </label>
                <label>
                  Фабула слота
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
              </div>
              <div className="inline-actions broadcast-edit-actions">
                <button className="btn btn-pri" type="button" onClick={saveEdit}>Сохранить</button>
                <button className="btn btn-sec" type="button" onClick={() => setEditingItem(null)}>Отменить</button>
              </div>
            </div>
          ) : (
            <>
              <ReadOnlyContext item={item} workspace={workspace} />
              <dl className="entity-detail-list broadcast-slot-facts">
                <div><dt>Публикация</dt><dd>{formatPlanDateTime(item.date, item.time)} · {item.platform}</dd></div>
                <div><dt>Статус</dt><dd>{statusLabel(item.approvalStatus)}</dd></div>
                <div><dt>Режим</dt><dd>{item.manualOverride ? 'Ручная правка сетки' : 'Собрано deterministic-сервисом'}</dd></div>
                {context.confidence !== null ? <div><dt>Confidence</dt><dd>{Math.round(context.confidence * 100)}%</dd></div> : null}
                <div className="broadcast-detail-wide"><dt>Тезис</dt><dd>{context.thesis}</dd></div>
                <div className="broadcast-detail-wide"><dt>Доказательство</dt><dd>{context.evidence}</dd></div>
              </dl>
              {context.risks.length > 0 ? (
                <div className="matrix-warnings broadcast-risk-block">
                  <h4>Risks</h4>
                  {context.risks.map((risk) => <p key={risk}>{risk}</p>)}
                </div>
              ) : null}
              {itemWarnings.length > 0 ? (
                <div className="matrix-warnings">
                  {itemWarnings.map((warning) => <p key={warning.id}>{warning.message}</p>)}
                </div>
              ) : null}
              <div className="inline-actions broadcast-row-actions">
                <button className="btn btn-sec" type="button" onClick={startEdit}>Редактировать</button>
                <button className="btn btn-pri" type="button" disabled={item.approvalStatus === 'approved'} onClick={() => onApprove(item.id)}>
                  Утвердить
                </button>
                <button className={`btn ${item.approvalStatus === 'approved' ? 'btn-pri' : 'btn-sec'}`} type="button" disabled={item.approvalStatus !== 'approved'} onClick={() => onBrief(item)}>
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

function ReadOnlyContext({ item, workspace }: { item: ContentPlanItem; workspace: WorkspaceState }) {
  const context = getPlanSlotContext(item, workspace);

  return (
    <dl className="broadcast-context-grid" aria-label="Контекст кандидата">
      <div><dt>Сигнал</dt><dd>{context.signal.title}</dd></div>
      <div><dt>Тема</dt><dd>{context.topicTitle}</dd></div>
      <div><dt>Фабула</dt><dd>{context.fabulaTitle}</dd></div>
      <div><dt>Аудитория</dt><dd>{context.audience}</dd></div>
      <div><dt>Ценность</dt><dd>{context.value}</dd></div>
      <div><dt>Цель</dt><dd>{context.goal}</dd></div>
    </dl>
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
