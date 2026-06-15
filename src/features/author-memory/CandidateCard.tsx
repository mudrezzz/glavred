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

export function CandidateCard({
  candidate,
  selected,
  source,
  onAcceptToArchive,
  onAcceptToMemory,
  onIgnoreEvidence,
  onReject,
  onSelect
}: {
  candidate: ImportedMemoryCandidate;
  selected: boolean;
  source?: AuthorExternalSource;
  onAcceptToArchive: (candidate: ImportedMemoryCandidate) => void;
  onAcceptToMemory: (candidate: ImportedMemoryCandidate) => void;
  onIgnoreEvidence: (candidate: ImportedMemoryCandidate) => void;
  onReject: (candidate: ImportedMemoryCandidate) => void;
  onSelect: (candidateId: string) => void;
}) {
  const disabled = candidate.reviewStatus !== 'new';

  return (
    <article className={`card candidate-card ${disabled ? 'muted' : ''}`}>
      <label className="candidate-check">
        <input
          type="checkbox"
          checked={selected}
          disabled={disabled}
          onChange={() => onSelect(candidate.id)}
          aria-label={`Выбрать ${candidate.title}`}
        />
      </label>
      <div className="candidate-body">
        <div className="candidate-head">
          <span className="sig info">{source?.title ?? candidate.sourceId}</span>
          <span className={`sc risk-${candidate.duplicateRisk}`}>duplicate {duplicateRiskLabel(candidate.duplicateRisk)}</span>
          <span className="sc">{reviewStatusLabel(candidate.reviewStatus)}</span>
        </div>
        <h3>{candidate.title}</h3>
        <p>{candidate.excerpt}</p>
        <dl className="meta-list">
          <dt>Captured</dt>
          <dd>{candidate.capturedAt}</dd>
          <dt>Target</dt>
          <dd>{candidate.suggestedTarget}</dd>
          <dt>Policy</dt>
          <dd>{evidencePolicyLabel(candidate.evidencePolicy)}</dd>
          <dt>Provenance</dt>
          <dd>{candidate.originalUrl || source?.fileReference || source?.url || 'local mock candidate'}</dd>
        </dl>
        <div className="tag-row">
          {candidate.detectedTags.map((tag) => (
            <span className="rub" key={tag}>
              {tag}
            </span>
          ))}
        </div>
        <div className="inline-actions">
          <button className="btn btn-pri btn-sm" type="button" disabled={disabled} onClick={() => onAcceptToMemory(candidate)}>
            В память
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onAcceptToArchive(candidate)}>
            В архив
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onReject(candidate)}>
            Отклонить
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onIgnoreEvidence(candidate)}>
            Не evidence
          </button>
        </div>
      </div>
    </article>
  );
}
