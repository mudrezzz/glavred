import type { EditorialWorkItem, Fabula, Topic } from '../../domain/editorialWorkspace';
import type {
  EditorialWorkGroupMode,
  EditorialWorkQueueFilters,
  EditorialWorkQueueViewMode
} from './editorialWorkQueueFilters';

export function EditorialWorkQueueToolbar({
  fabulas,
  filters,
  groupMode,
  items,
  topics,
  viewMode,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode
}: {
  fabulas: Fabula[];
  filters: EditorialWorkQueueFilters;
  groupMode: EditorialWorkGroupMode;
  items: EditorialWorkItem[];
  topics: Topic[];
  viewMode: EditorialWorkQueueViewMode;
  onChangeFilters: (filters: EditorialWorkQueueFilters) => void;
  onChangeGroupMode: (mode: EditorialWorkGroupMode) => void;
  onChangeViewMode: (mode: EditorialWorkQueueViewMode) => void;
}) {
  const platforms = Array.from(new Set(items.map((item) => item.platform).filter(Boolean)));

  function patch(patchValue: Partial<EditorialWorkQueueFilters>) {
    onChangeFilters({ ...filters, ...patchValue });
  }

  return (
    <section className="card import-toolbar-panel editorial-work-toolbar" data-testid="editorial-work-toolbar">
      <div className="import-filter-grid">
        <label>
          Стадия
          <select value={filters.stage} onChange={(event) => patch({ stage: event.target.value as EditorialWorkQueueFilters['stage'] })}>
            <option value="all">Все стадии</option>
            <option value="brief">Фабула</option>
            <option value="draft">Драфт</option>
            <option value="final">Финал</option>
            <option value="readyForRelease">Готов к выпуску</option>
          </select>
        </label>
        <label>
          Статус
          <select value={filters.status} onChange={(event) => patch({ status: event.target.value as EditorialWorkQueueFilters['status'] })}>
            <option value="all">Все</option>
            <option value="todo">В очереди</option>
            <option value="inProgress">В работе</option>
            <option value="approved">Утвержден</option>
            <option value="blocked">Блокер</option>
          </select>
        </label>
        <label>
          Площадка
          <select value={filters.platform} onChange={(event) => patch({ platform: event.target.value })}>
            <option value="all">Все площадки</option>
            {platforms.map((platform) => <option value={platform} key={platform}>{platform}</option>)}
          </select>
        </label>
        <label>
          Тема
          <select value={filters.topicId} onChange={(event) => patch({ topicId: event.target.value })}>
            <option value="all">Все темы</option>
            {topics.map((topic) => <option value={topic.id} key={topic.id}>{topic.title}</option>)}
          </select>
        </label>
        <label>
          Фабула
          <select value={filters.fabulaId} onChange={(event) => patch({ fabulaId: event.target.value })}>
            <option value="all">Все фабулы</option>
            {fabulas.map((fabula) => <option value={fabula.id} key={fabula.id}>{fabula.title}</option>)}
          </select>
        </label>
      </div>
      <label className="import-search">
        Поиск
        <input
          value={filters.query}
          placeholder="title, topic, fabula, platform..."
          onChange={(event) => patch({ query: event.target.value })}
        />
      </label>
      <div className="view-toggle">
        <button className={`tab${viewMode === 'list' ? ' active' : ''}`} type="button" role="tab" aria-selected={viewMode === 'list'} onClick={() => onChangeViewMode('list')}>
          Список
        </button>
        <button className={`tab${viewMode === 'groups' ? ' active' : ''}`} type="button" role="tab" aria-selected={viewMode === 'groups'} onClick={() => onChangeViewMode('groups')}>
          Группы
        </button>
        {viewMode === 'groups' ? (
          <select value={groupMode} onChange={(event) => onChangeGroupMode(event.target.value as EditorialWorkGroupMode)}>
            <option value="stage">По стадии</option>
            <option value="date">По дате</option>
            <option value="platform">По площадке</option>
            <option value="status">По статусу</option>
          </select>
        ) : null}
      </div>
    </section>
  );
}
