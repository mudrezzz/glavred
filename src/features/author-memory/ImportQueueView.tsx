import {
  type AuthorExternalSource,
  type ImportedMemoryCandidate,
  type ImportCandidateFilters,
  type ImportCandidateGroup,
  type ImportCandidateGroupType
} from '../../domain/editorialWorkspace';
import { ImportCandidateGroupList } from './ImportCandidateGroupList';
import { ImportCandidateList } from './ImportCandidateList';
import { ImportQueueBulkBar } from './ImportQueueBulkBar';
import { ImportQueueToolbar } from './ImportQueueToolbar';
import type { ImportViewMode, PendingBulkAction } from './types';

export function ImportQueueView({
  candidates,
  filteredCandidates,
  filters,
  groups,
  groupMode,
  selectedCandidateIds,
  sources,
  viewMode,
  onAcceptToArchive,
  onAcceptToMemory,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode,
  onIgnoreEvidence,
  onOpenBulk,
  onReject,
  onClearSelection,
  onSelect,
  onSelectAllFiltered,
  onSelectPage,
  onUnselectAllFiltered,
  onUnselectPage
}: {
  candidates: ImportedMemoryCandidate[];
  filteredCandidates: ImportedMemoryCandidate[];
  filters: ImportCandidateFilters;
  groups: ImportCandidateGroup[];
  groupMode: ImportCandidateGroupType;
  selectedCandidateIds: string[];
  sources: AuthorExternalSource[];
  viewMode: ImportViewMode;
  onAcceptToArchive: (candidate: ImportedMemoryCandidate) => void;
  onAcceptToMemory: (candidate: ImportedMemoryCandidate) => void;
  onChangeFilters: (filters: ImportCandidateFilters) => void;
  onChangeGroupMode: (mode: ImportCandidateGroupType) => void;
  onChangeViewMode: (mode: ImportViewMode) => void;
  onIgnoreEvidence: (candidate: ImportedMemoryCandidate) => void;
  onOpenBulk: (action: PendingBulkAction) => void;
  onReject: (candidate: ImportedMemoryCandidate) => void;
  onClearSelection: () => void;
  onSelect: (candidateId: string) => void;
  onSelectAllFiltered: () => void;
  onSelectPage: () => void;
  onUnselectAllFiltered: () => void;
  onUnselectPage: () => void;
}) {
  return (
    <div className="import-workspace">
      <section className="card import-notice">
        <b>Архивные и неразобранные материалы не меняют выводы о позиции автора.</b>
        <span>Очередь показывает mock candidates без API и без AI-анализа. Evidence включается только после действия «В память».</span>
      </section>
      <ImportQueueToolbar
        filters={filters}
        groupMode={groupMode}
        sources={sources}
        viewMode={viewMode}
        onChangeFilters={onChangeFilters}
        onChangeGroupMode={onChangeGroupMode}
        onChangeViewMode={onChangeViewMode}
      />
      <ImportQueueBulkBar
        candidates={candidates}
        filteredCandidates={filteredCandidates}
        selectedCandidateIds={selectedCandidateIds}
        onClearSelection={onClearSelection}
        onOpenBulk={onOpenBulk}
        onSelectAllFiltered={onSelectAllFiltered}
        onSelectPage={onSelectPage}
        onUnselectAllFiltered={onUnselectAllFiltered}
        onUnselectPage={onUnselectPage}
      />
      {viewMode === 'groups' ? (
        <ImportCandidateGroupList groups={groups} />
      ) : (
        <ImportCandidateList
          filteredCandidates={filteredCandidates}
          selectedCandidateIds={selectedCandidateIds}
          sources={sources}
          onAcceptToArchive={onAcceptToArchive}
          onAcceptToMemory={onAcceptToMemory}
          onIgnoreEvidence={onIgnoreEvidence}
          onReject={onReject}
          onSelect={onSelect}
        />
      )}
    </div>
  );
}
