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

export function ArchiveView({
  records,
  sources,
  onAcceptToMemory,
  onDelete,
  onIgnoreEvidence,
  onRestoreToQueue
}: {
  records: ArchiveRecord[];
  sources: AuthorExternalSource[];
  onAcceptToMemory: (record: ArchiveRecord) => void;
  onDelete: (recordId: string) => void;
  onIgnoreEvidence: (record: ArchiveRecord) => void;
  onRestoreToQueue: (record: ArchiveRecord) => void;
}) {
  return (
    <div className="archive-list">
      <section className="card import-notice">
        <b>Архив хранит контекст, но не является active evidence.</b>
        <span>Чтобы материал влиял на позицию автора, примите конкретного кандидата во вкладке «Очередь разбора» через «В память».</span>
      </section>
      {records.map((record) => (
        <article className="card archive-card" key={record.id}>
          <div className="candidate-head">
            <span className="sig info">{sources.find((source) => source.id === record.sourceId)?.title ?? record.sourceId}</span>
            <span className="sc">{record.acceptanceMode === 'bulk' ? 'bulk accepted' : 'manual accepted'}</span>
            <span className="sc">{record.id.startsWith('archive-seeded') ? 'исторический архив' : 'из очереди'}</span>
            <span className="sc">{evidencePolicyLabel(record.evidencePolicy)}</span>
          </div>
          <h3>{record.title}</h3>
          <p>{record.bodyExcerpt}</p>
          <dl className="meta-list">
            <dt>Published</dt>
            <dd>{record.publishedAt}</dd>
            <dt>Accepted</dt>
            <dd>{formatDate(record.acceptedAt)}</dd>
            <dt>Original</dt>
            <dd>{record.originalUrl || 'local archive record'}</dd>
          </dl>
          <div className="inline-actions">
            <button className="btn btn-pri btn-sm" type="button" onClick={() => onAcceptToMemory(record)}>
              Добавить в память
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onRestoreToQueue(record)}>
              Вернуть в очередь
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onIgnoreEvidence(record)}>
              Не evidence
            </button>
            {record.originalUrl ? (
              <a className="btn btn-sec btn-sm" href={record.originalUrl} target="_blank" rel="noreferrer">
                Открыть источник
              </a>
            ) : null}
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onDelete(record.id)}>
              Удалить из архива
            </button>
          </div>
        </article>
      ))}
      {records.length === 0 ? <EmptyState text="Архив пока пуст." /> : null}
    </div>
  );
}
