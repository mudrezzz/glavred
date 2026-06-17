import { useState } from 'react';
import type { EditorialWorkItem } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import {
  getEditorialWorkWarnings,
  stageLabel,
  workStatusLabel,
  type EditorialWorkGroup
} from './editorialWorkQueueFilters';

export function EditorialWorkQueueList({
  items,
  selectedId,
  onReturn,
  onSelect
}: {
  items: EditorialWorkItem[];
  selectedId: string | null;
  onReturn: (itemId: string) => void;
  onSelect: (itemId: string) => void;
}) {
  if (items.length === 0) {
    return <div className="card empty-state">В очереди нет постов по выбранным фильтрам.</div>;
  }

  return (
    <div className="editorial-work-list" data-testid="editorial-work-list">
      {items.map((item) => (
        <EditorialWorkRow
          item={item}
          key={item.id}
          selected={item.id === selectedId}
          onReturn={onReturn}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

export function EditorialWorkGroupList({
  groups,
  selectedId,
  onReturn,
  onSelect
}: {
  groups: EditorialWorkGroup[];
  selectedId: string | null;
  onReturn: (itemId: string) => void;
  onSelect: (itemId: string) => void;
}) {
  if (groups.length === 0) {
    return <div className="card empty-state">В очереди нет постов по выбранным фильтрам.</div>;
  }

  return (
    <div className="editorial-work-list" data-testid="editorial-work-list">
      {groups.map((group) => (
        <section className="broadcast-group" key={group.id}>
          <div className="group-head">
            <h3>{group.title}</h3>
            <span>{group.items.length}</span>
          </div>
          {group.items.map((item) => (
            <EditorialWorkRow
              item={item}
              key={item.id}
              selected={item.id === selectedId}
              onReturn={onReturn}
              onSelect={onSelect}
            />
          ))}
        </section>
      ))}
    </div>
  );
}

function EditorialWorkRow({
  item,
  selected,
  onReturn,
  onSelect
}: {
  item: EditorialWorkItem;
  selected: boolean;
  onReturn: (itemId: string) => void;
  onSelect: (itemId: string) => void;
}) {
  const [expanded, setExpanded] = useState(selected);
  const warnings = getEditorialWorkWarnings(item);

  return (
    <article className={`card editorial-work-row${selected ? ' selected' : ''}${expanded ? ' expanded' : ''}`} data-testid="editorial-work-row">
      <button className="editorial-work-row-main" type="button" onClick={() => setExpanded((value) => !value)}>
        <span className="broadcast-date">{formatWorkDateTime(item.date, item.time)}</span>
        <span className="broadcast-row-copy">
          <span className="broadcast-title">{item.title}</span>
          <span className="broadcast-row-meta">
            <span>{item.platform}</span>
            <span>{item.topicTitle ?? 'Тема не задана'}</span>
            <span>{item.fabulaTitle ?? 'Фабула не задана'}</span>
          </span>
        </span>
        <span className={`pill ${item.status === 'approved' ? 'ok' : 'pin'}`}>
          <i />
          {stageLabel(item.stage)}
        </span>
        <span className={`pill ${item.status === 'approved' ? 'ok' : 'pin'}`}>
          <i />
          {workStatusLabel(item.status)}
        </span>
        </button>
      {expanded ? (
        <>
          <dl className="broadcast-context-grid editorial-work-context">
            <div><dt>Публикация</dt><dd>{formatWorkDateTime(item.date, item.time)} · {item.platform}</dd></div>
            <div><dt>Тема</dt><dd>{item.topicTitle ?? 'Не задана'}</dd></div>
            <div><dt>Фабула</dt><dd>{item.fabulaTitle ?? 'Не задана'}</dd></div>
            <div><dt>Источник</dt><dd>{item.sourceSignalId ?? 'Не задан'}</dd></div>
          </dl>
          {warnings.length > 0 ? (
            <div className="matrix-warnings editorial-work-warnings">
              {warnings.map((warning) => <p key={warning}>{warning}</p>)}
            </div>
          ) : null}
          <div className="inline-actions editorial-work-actions">
            <button className="btn btn-pri" type="button" onClick={() => onSelect(item.id)}>
              <Icon name="edit" size={16} />
              {selected ? 'На рабочем столе' : 'К рабочему столу'}
            </button>
            <button className="btn btn-sec" type="button" onClick={() => onReturn(item.id)}>
              Вернуть в кандидаты
            </button>
          </div>
        </>
      ) : null}
    </article>
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
