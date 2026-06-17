import type { ContentPlanItem, Fabula, Topic } from '../../domain/editorialWorkspace';
import type { BroadcastGridFilters, BroadcastGridGroupMode, BroadcastGridViewMode } from './broadcastGridFilters';

export function BroadcastGridToolbar({
  filters,
  groupMode,
  items,
  viewMode,
  fabulas,
  topics,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode
}: {
  filters: BroadcastGridFilters;
  groupMode: BroadcastGridGroupMode;
  items: ContentPlanItem[];
  viewMode: BroadcastGridViewMode;
  fabulas: Fabula[];
  topics: Topic[];
  onChangeFilters: (filters: BroadcastGridFilters) => void;
  onChangeGroupMode: (mode: BroadcastGridGroupMode) => void;
  onChangeViewMode: (mode: BroadcastGridViewMode) => void;
}) {
  const platforms = Array.from(new Set(items.map((item) => item.platform).filter(Boolean)));

  function patch(patchValue: Partial<BroadcastGridFilters>) {
    onChangeFilters({ ...filters, ...patchValue });
  }

  return (
    <section className="card import-toolbar-panel broadcast-filter-toolbar" data-testid="broadcast-filter-toolbar">
      <div className="import-filter-grid">
        <label>
          Статус
          <select value={filters.status} onChange={(event) => patch({ status: event.target.value as BroadcastGridFilters['status'] })}>
            <option value="all">Все</option>
            <option value="draft">Черновики</option>
            <option value="approved">Утвержденные</option>
            <option value="rejected">Отклоненные</option>
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
        <label>
          Risk
          <select value={filters.risk} onChange={(event) => patch({ risk: event.target.value as BroadcastGridFilters['risk'] })}>
            <option value="all">Любой</option>
            <option value="warning">С предупреждениями</option>
            <option value="clear">Без предупреждений</option>
          </select>
        </label>
      </div>
      <label>
        Поиск
        <input
          value={filters.query}
          placeholder="title, effect, topic, fabula..."
          onChange={(event) => patch({ query: event.target.value })}
        />
      </label>
      <div className="toolbar-bottom-row">
        <div className="tabs compact-tabs" role="tablist" aria-label="Вид сетки">
          <button className={`tab${viewMode === 'list' ? ' active' : ''}`} type="button" role="tab" aria-selected={viewMode === 'list'} onClick={() => onChangeViewMode('list')}>
            Список
          </button>
          <button className={`tab${viewMode === 'groups' ? ' active' : ''}`} type="button" role="tab" aria-selected={viewMode === 'groups'} onClick={() => onChangeViewMode('groups')}>
            Группы
          </button>
        </div>
        {viewMode === 'groups' ? (
          <select value={groupMode} onChange={(event) => onChangeGroupMode(event.target.value as BroadcastGridGroupMode)}>
            <option value="date">По дате</option>
            <option value="topic">По теме</option>
            <option value="fabula">По фабуле</option>
            <option value="status">По статусу</option>
            <option value="risk">По risk</option>
          </select>
        ) : null}
      </div>
    </section>
  );
}
