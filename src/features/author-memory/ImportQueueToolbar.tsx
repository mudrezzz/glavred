import type {
  AuthorExternalSource,
  EvidencePolicy,
  ImportCandidateFilters,
  ImportCandidateGroupType,
  ImportReviewStatus,
  ImportRiskLevel
} from '../../domain/editorialWorkspace';
import type { ImportViewMode } from './types';

export function ImportQueueToolbar({
  filters,
  groupMode,
  sources,
  viewMode,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode
}: {
  filters: ImportCandidateFilters;
  groupMode: ImportCandidateGroupType;
  sources: AuthorExternalSource[];
  viewMode: ImportViewMode;
  onChangeFilters: (filters: ImportCandidateFilters) => void;
  onChangeGroupMode: (mode: ImportCandidateGroupType) => void;
  onChangeViewMode: (mode: ImportViewMode) => void;
}) {
  function patchFilters(patch: ImportCandidateFilters) {
    onChangeFilters({ ...filters, ...patch });
  }

  return (
    <section className="card import-toolbar-panel">
      <div className="import-filter-grid">
        <label>
          Источник
          <select value={filters.sourceId ?? 'all'} onChange={(event) => patchFilters({ sourceId: event.target.value })}>
            <option value="all">Все источники</option>
            {sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Статус
          <select
            value={filters.reviewStatus ?? 'all'}
            onChange={(event) => patchFilters({ reviewStatus: event.target.value as ImportReviewStatus | 'all' })}
          >
            <option value="all">Все</option>
            <option value="new">Новые</option>
            <option value="acceptedToMemory">В памяти</option>
            <option value="acceptedToArchive">Принятые из очереди</option>
            <option value="bulkAcceptedToArchive">Bulk archive из очереди</option>
            <option value="rejected">Отклонены</option>
            <option value="ignoredForEvidence">Не evidence</option>
          </select>
        </label>
        <label>
          Evidence policy
          <select
            value={filters.evidencePolicy ?? 'all'}
            onChange={(event) => patchFilters({ evidencePolicy: event.target.value as EvidencePolicy | 'all' })}
          >
            <option value="all">Любая</option>
            <option value="canSupportAssertions">Может поддержать выводы</option>
            <option value="archiveOnly">Только архив</option>
            <option value="ignored">Игнорировать</option>
          </select>
        </label>
        <label>
          Duplicate risk
          <select
            value={filters.duplicateRisk ?? 'all'}
            onChange={(event) => patchFilters({ duplicateRisk: event.target.value as ImportRiskLevel | 'all' })}
          >
            <option value="all">Любой</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
      </div>
      <label className="import-search">
        Поиск
        <input
          value={filters.query ?? ''}
          onChange={(event) => patchFilters({ query: event.target.value })}
          placeholder="tag, title, excerpt..."
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
          <select value={groupMode} onChange={(event) => onChangeGroupMode(event.target.value as ImportCandidateGroupType)}>
            <option value="source">По источнику</option>
            <option value="status">По статусу</option>
            <option value="duplicateRisk">По дублям</option>
            <option value="evidencePolicy">По evidence</option>
            <option value="tag">По тегу</option>
          </select>
        ) : null}
      </div>
    </section>
  );
}
