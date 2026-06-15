import { useEffect, useMemo, useState } from 'react';
import { type ContextChatIntent } from '../../application/contextChat';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../../application/editorialServices';
import {
  acceptCandidateToArchive,
  acceptCandidateToMemory,
  bulkAcceptCandidatesToArchive,
  bulkRejectCandidates,
  filterImportCandidates,
  groupImportCandidates,
  ignoreCandidateForEvidence,
  markCandidateAcceptedToArchive,
  markCandidateAcceptedToMemory,
  rejectCandidate,
  undoLastBulkImportAction,
  type ArchiveRecord,
  type AuthorAttachment,
  type AuthorExternalSource,
  type AuthorNote,
  type AuthorNoteType,
  type AuthorPositionAssertion,
  type BulkImportAction,
  type EvidencePolicy,
  type ImportedMemoryCandidate,
  type ImportCandidateFilters,
  type ImportCandidateGroupType,
  type ImportReviewStatus,
  type ImportRiskLevel,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import type { CorrectionTarget, ImportViewMode, LinkPreview, MemoryInternalTab, MemoryTypeFilter, PendingBulkAction, PendingCorrectionConflict } from './types';
import { CandidateCard } from './CandidateCard';
import {
  AssertionCard,
  AttachmentList,
  EmptyState,
  FileAttachmentPicker,
  LinkPreviewCard,
  MemoryTabNav,
  SummaryItem,
  AuthorNoteCard
} from './components';
import {
  attachmentTypeLabel,
  authorNoteTypeLabel,
  assertionTypeLabel,
  buildCorrectionTargets,
  buildEvidenceCorrectionTarget,
  buildLinkPreview,
  createAuthorAttachment,
  correctionTargetKey,
  deriveNoteTitle,
  duplicateRiskLabel,
  evidencePolicyLabel,
  filterAuthorNotes,
  formatBytes,
  formatDate,
  formatDateTime,
  formatImportFilters,
  formatScore,
  getImportSummary,
  getMemorySummary,
  getSpeechRecognitionConstructor,
  hasCorrectionConflict,
  importModeLabel,
  isEvidenceNote,
  MAX_AUTHOR_ATTACHMENT_BYTES,
  readFileAsDataUrl,
  reviewStatusLabel,
  sourceStatusLabel,
  sourceTypeLabel,
  splitLines,
  splitTags
} from './helpers';

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
  groups: ReturnType<typeof groupImportCandidates>;
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

  function patchFilters(patch: ImportCandidateFilters) {
    onChangeFilters({ ...filters, ...patch });
  }

  return (
    <div className="import-workspace">
      <section className="card import-notice">
        <b>Архивные и неразобранные материалы не меняют выводы о позиции автора.</b>
        <span>Очередь показывает mock candidates без API и без AI-анализа. Evidence включается только после действия «В память».</span>
      </section>
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
      {viewMode === 'groups' ? (
        <div className="import-groups">
          {groups.map((group) => (
            <article className="card import-group" key={group.id}>
              <div>
                <span className={`risk-dot ${group.riskLevel}`} />
                <b>{group.title}</b>
              </div>
              <span>{group.summary}</span>
              <small>{group.candidateIds.join(', ')}</small>
            </article>
          ))}
        </div>
      ) : (
        <div className="candidate-list">
          {filteredCandidates.map((candidate) => (
            <CandidateCard
              candidate={candidate}
              key={candidate.id}
              selected={selectedCandidateIds.includes(candidate.id)}
              source={sources.find((item) => item.id === candidate.sourceId)}
              onAcceptToArchive={onAcceptToArchive}
              onAcceptToMemory={onAcceptToMemory}
              onIgnoreEvidence={onIgnoreEvidence}
              onReject={onReject}
              onSelect={onSelect}
            />
          ))}
          {filteredCandidates.length === 0 ? <EmptyState text="В очереди нет кандидатов под выбранные фильтры." /> : null}
        </div>
      )}
    </div>
  );
}
