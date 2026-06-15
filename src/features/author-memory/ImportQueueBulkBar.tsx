import type { ImportedMemoryCandidate } from '../../domain/editorialWorkspace';
import type { PendingBulkAction } from './types';

export function ImportQueueBulkBar({
  candidates,
  filteredCandidates,
  selectedCandidateIds,
  onClearSelection,
  onOpenBulk,
  onSelectAllFiltered,
  onSelectPage,
  onUnselectAllFiltered,
  onUnselectPage
}: {
  candidates: ImportedMemoryCandidate[];
  filteredCandidates: ImportedMemoryCandidate[];
  selectedCandidateIds: string[];
  onClearSelection: () => void;
  onOpenBulk: (action: PendingBulkAction) => void;
  onSelectAllFiltered: () => void;
  onSelectPage: () => void;
  onUnselectAllFiltered: () => void;
  onUnselectPage: () => void;
}) {
  const actionableSelected = selectedCandidateIds.filter((id) =>
    candidates.some((candidate) => candidate.id === id && candidate.reviewStatus === 'new')
  );
  const pageCandidateIds = filteredCandidates.slice(0, 10).map((candidate) => candidate.id);
  const filteredCandidateIds = filteredCandidates.map((candidate) => candidate.id);
  const allPageSelected =
    pageCandidateIds.length > 0 && pageCandidateIds.every((candidateId) => selectedCandidateIds.includes(candidateId));
  const allFilteredSelected =
    filteredCandidateIds.length > 0 &&
    filteredCandidateIds.every((candidateId) => selectedCandidateIds.includes(candidateId));

  return (
    <div className="bulk-bar">
      <span>
        Показано {filteredCandidates.length} из {candidates.length}; выбрано {selectedCandidateIds.length}
      </span>
      <button className="btn btn-sec btn-sm" type="button" onClick={allPageSelected ? onUnselectPage : onSelectPage}>
        {allPageSelected ? 'Снять выделение со страницы' : 'Выбрать все на странице'}
      </button>
      <button
        className="btn btn-sec btn-sm"
        type="button"
        onClick={allFilteredSelected ? onUnselectAllFiltered : onSelectAllFiltered}
      >
        {allFilteredSelected ? 'Снять выделение по фильтру' : 'Выбрать все по фильтру'}
      </button>
      {selectedCandidateIds.length > 0 ? (
        <button className="btn btn-sec btn-sm" type="button" onClick={onClearSelection}>
          Сбросить выделение
        </button>
      ) : null}
      <button
        className="btn btn-pri btn-sm"
        type="button"
        disabled={filteredCandidates.length === 0}
        onClick={() =>
          onOpenBulk({
            action: 'archive',
            candidateIds: selectedCandidateIds.length > 0 ? selectedCandidateIds : filteredCandidates.map((candidate) => candidate.id),
            destination: 'Архив'
          })
        }
      >
        Добавить все
      </button>
      <button
        className="btn btn-sec btn-sm"
        type="button"
        disabled={actionableSelected.length === 0}
        onClick={() =>
          onOpenBulk({
            action: 'archive',
            candidateIds: actionableSelected,
            destination: 'Архив'
          })
        }
      >
        Принять выбранные в архив
      </button>
      <button
        className="btn btn-sec btn-sm"
        type="button"
        disabled={actionableSelected.length === 0}
        onClick={() =>
          onOpenBulk({
            action: 'reject',
            candidateIds: actionableSelected,
            destination: 'Отклонено'
          })
        }
      >
        Отклонить выбранные
      </button>
    </div>
  );
}
