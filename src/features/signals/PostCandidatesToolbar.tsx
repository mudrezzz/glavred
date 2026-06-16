import type { SourceSignal, Topic } from '../../domain/editorialWorkspace';
import type { CandidateGroupMode, CandidateViewMode, PostCandidateFilters } from './postCandidateTypes';

export function PostCandidatesToolbar({
  filters,
  groupMode,
  signals,
  topics,
  viewMode,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode
}: {
  filters: PostCandidateFilters;
  groupMode: CandidateGroupMode;
  signals: SourceSignal[];
  topics: Topic[];
  viewMode: CandidateViewMode;
  onChangeFilters: (filters: PostCandidateFilters) => void;
  onChangeGroupMode: (mode: CandidateGroupMode) => void;
  onChangeViewMode: (mode: CandidateViewMode) => void;
}) {
  function patchFilters(patch: Partial<PostCandidateFilters>) {
    onChangeFilters({ ...filters, ...patch });
  }

  return (
    <section className="card import-toolbar-panel post-candidate-toolbar">
      <div className="import-filter-grid">
        <label>
          Сигнал
          <select value={filters.signalId} onChange={(event) => patchFilters({ signalId: event.target.value })}>
            <option value="all">Все сигналы</option>
            {signals.map((signal) => (
              <option key={signal.id} value={signal.id}>
                {signal.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Статус
          <select value={filters.status} onChange={(event) => patchFilters({ status: event.target.value as PostCandidateFilters['status'] })}>
            <option value="all">Все</option>
            <option value="draft">Новые</option>
            <option value="approved">Утвержденные</option>
            <option value="rejected">Отклоненные</option>
          </select>
        </label>
        <label>
          Тема
          <select value={filters.topicId} onChange={(event) => patchFilters({ topicId: event.target.value })}>
            <option value="all">Все темы</option>
            {topics.map((topic) => (
              <option key={topic.id} value={topic.id}>
                {topic.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Risk
          <select value={filters.risk} onChange={(event) => patchFilters({ risk: event.target.value as PostCandidateFilters['risk'] })}>
            <option value="all">Любой</option>
            <option value="withRisks">Есть риски</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>
      </div>
      <label className="import-search">
        Поиск
        <input
          value={filters.query}
          onChange={(event) => patchFilters({ query: event.target.value })}
          placeholder="title, thesis, value, evidence..."
        />
      </label>
      <div className="view-toggle">
        <button className={`tab${viewMode === 'list' ? ' active' : ''}`} type="button" onClick={() => onChangeViewMode('list')}>
          Список
        </button>
        <button className={`tab${viewMode === 'groups' ? ' active' : ''}`} type="button" onClick={() => onChangeViewMode('groups')}>
          Группы
        </button>
        {viewMode === 'groups' ? (
          <select value={groupMode} onChange={(event) => onChangeGroupMode(event.target.value as CandidateGroupMode)}>
            <option value="signal">По сигналу</option>
            <option value="topic">По теме</option>
            <option value="status">По статусу</option>
            <option value="risk">По risk</option>
          </select>
        ) : null}
      </div>
    </section>
  );
}
