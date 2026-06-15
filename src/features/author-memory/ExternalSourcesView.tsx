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

export function ExternalSourcesView({
  candidates,
  sources,
  onOpenQueue,
  onPatchSource
}: {
  candidates: ImportedMemoryCandidate[];
  sources: AuthorExternalSource[];
  onOpenQueue: (sourceId?: string) => void;
  onPatchSource: (source: AuthorExternalSource) => void;
}) {
  const [expandedSourceId, setExpandedSourceId] = useState(sources[0]?.id ?? '');

  return (
    <div className="import-workspace">
      <section className="card import-intro">
        <span className="rub">Local-first shell</span>
        <h3>Демо-источники без API</h3>
        <p>
          Здесь показана будущая карта источников автора: архив TG-канала, интервью, блог, доклад и ручные uploads.
          Кандидаты mock/deterministic; Telegram, OAuth, crawlers и AI-анализ не подключены.
        </p>
      </section>
      <div className="source-list" data-testid="external-source-list">
        {sources.map((source) => {
          const sourceCandidates = candidates.filter((candidate) => candidate.sourceId === source.id);
          const needsReview = sourceCandidates.filter((candidate) => candidate.reviewStatus === 'new').length;
          const isExpanded = expandedSourceId === source.id;

          return (
            <article className={`card source-row${isExpanded ? ' expanded' : ''}`} data-testid="source-row" key={source.id}>
              <div className="source-row-main">
                <div className="source-row-title">
                  <span className="sig info">{sourceTypeLabel(source.type)}</span>
                  <button
                    className="entity-title-button source-title-button"
                    type="button"
                    aria-expanded={isExpanded}
                    onClick={() => setExpandedSourceId(isExpanded ? '' : source.id)}
                  >
                    {source.title}
                  </button>
                </div>
                <span className={`pill ${source.status === 'paused' ? 'pin' : 'ok'}`}>
                  <i />
                  {sourceStatusLabel(source.status)}
                </span>
              </div>
              <div className="source-row-meta-bar">
                <span className="entity-row-meta">{importModeLabel(source.importMode)}</span>
                <span className="entity-row-meta">
                  {sourceCandidates.length} total · {needsReview} review
                </span>
                <span className="entity-row-meta">checked {source.lastCheckedAt || 'нет'}</span>
              </div>
              {isExpanded ? (
                <div className="source-row-details">
                  <p>{source.notes}</p>
                  <dl className="entity-detail-list">
                <dt>Mode</dt>
                <dd>{importModeLabel(source.importMode)}</dd>
                <dt>Candidates</dt>
                <dd>
                  {sourceCandidates.length} total · {needsReview} review
                </dd>
                <dt>Checked</dt>
                <dd>{source.lastCheckedAt || 'не проверялся'}</dd>
                <dt>Imported</dt>
                <dd>{source.lastImportedAt || 'нет импорта'}</dd>
                  </dl>
                </div>
              ) : null}
              <div className="source-row-actions">
                <button className="btn btn-pri btn-sm" type="button" onClick={() => onOpenQueue(source.id)}>
                  Открыть очередь
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() =>
                    onPatchSource({
                      ...source,
                      status: source.status === 'paused' ? 'needsReview' : 'paused'
                    })
                  }
                >
                  {source.status === 'paused' ? 'Возобновить' : 'Пауза'}
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() => onPatchSource({ ...source, lastCheckedAt: new Date().toISOString().slice(0, 10) })}
                >
                  Проверить вручную
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
