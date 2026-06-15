// Import/archive types describe material that may become memory evidence after review.
export type ExternalSourceType =
  | 'telegramChannel'
  | 'socialProfile'
  | 'blogSite'
  | 'document'
  | 'articleArchive'
  | 'manualUpload';
export type ExternalSourceStatus = 'planned' | 'connected' | 'needsReview' | 'imported' | 'paused' | 'failed';
export type ImportMode = 'manualOnly' | 'reviewedQueue' | 'archiveOnly' | 'bulkArchive';
export type EvidencePolicy = 'canSupportAssertions' | 'archiveOnly' | 'ignored';
export type ImportReviewStatus =
  | 'new'
  | 'acceptedToMemory'
  | 'acceptedToArchive'
  | 'bulkAcceptedToArchive'
  | 'rejected'
  | 'ignoredForEvidence';
export type ImportCandidateGroupType = 'source' | 'status' | 'duplicateRisk' | 'evidencePolicy' | 'tag';
export type ImportRiskLevel = 'low' | 'medium' | 'high';
export type BulkImportActionType = 'bulkAcceptToArchive' | 'bulkReject';

export interface ImportCandidateGroup {
  id: string;
  type: ImportCandidateGroupType;
  title: string;
  candidateIds: string[];
  summary: string;
  riskLevel: ImportRiskLevel;
}

export interface BulkImportAction {
  id: string;
  action: BulkImportActionType;
  candidateIds: string[];
  previousStatuses: Record<string, ImportReviewStatus>;
  createdAt: string;
  canUndo: boolean;
  createdArchiveRecordIds: string[];
}

export interface ArchiveRecord {
  id: string;
  sourceId: string;
  title: string;
  bodyExcerpt: string;
  originalUrl: string;
  publishedAt: string;
  acceptedAt: string;
  acceptanceMode: 'manual' | 'bulk';
  evidencePolicy: EvidencePolicy;
}

export interface ImportCandidateFilters {
  sourceId?: string;
  reviewStatus?: ImportReviewStatus | 'all';
  evidencePolicy?: EvidencePolicy | 'all';
  duplicateRisk?: ImportRiskLevel | 'all';
  query?: string;
}
