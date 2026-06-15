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

export function BulkActionDialog({
  action,
  candidates,
  filters,
  onCancel,
  onConfirm
}: {
  action: PendingBulkAction;
  candidates: ImportedMemoryCandidate[];
  filters: ImportCandidateFilters;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const highDuplicateCount = candidates.filter((candidate) => candidate.duplicateRisk === 'high').length;
  const activeEvidenceCount = candidates.filter((candidate) => candidate.evidencePolicy === 'canSupportAssertions').length;

  return (
    <div className="confirm-popover" role="dialog" aria-label="Подтверждение группового действия">
      <div className="card bulk-confirm">
        <h3>{action.action === 'archive' ? 'Добавить все в архив?' : 'Отклонить выбранные?'}</h3>
        <p>
          Будет обработано {candidates.length} кандидатов. Назначение: {action.destination}. Активные фильтры: {formatImportFilters(filters)}.
        </p>
        <dl className="meta-list">
          <dt>High duplicate</dt>
          <dd>{highDuplicateCount}</dd>
          <dt>Can support assertions</dt>
          <dd>{activeEvidenceCount}</dd>
          <dt>Evidence impact</dt>
          <dd>Архив и отклонение не меняют блок «Как система поняла автора».</dd>
        </dl>
        <div className="inline-actions">
          <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
            Отмена
          </button>
          <button className="btn btn-pri btn-sm" type="button" onClick={onConfirm}>
            Подтвердить
          </button>
        </div>
      </div>
    </div>
  );
}
