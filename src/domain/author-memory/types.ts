import type {
  EvidencePolicy,
  ExternalSourceStatus,
  ExternalSourceType,
  ImportMode,
  ImportReviewStatus,
} from '../imports/types';
import type { ImportRiskLevel } from '../imports/types';

// Author memory is the source of evidence about the author's position.
export type AuthorNoteType = 'thought' | 'linkReaction' | 'manualCorrection';
export type AuthorPositionAssertionType = 'persona' | 'style' | 'audience' | 'topic' | 'principle';
export type AuthorPositionAssertionStatus = 'inferred' | 'confirmed';

export interface AuthorNote {
  id: string;
  type: AuthorNoteType;
  title: string;
  body: string;
  sourceUrl: string;
  tags: string[];
  attachments: AuthorAttachment[];
  capturedAt: string;
  targetType?: 'assertion' | 'evidence';
  targetId?: string;
  targetTitle?: string;
}

export interface AuthorAttachment {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  dataUrl: string;
  createdAt: string;
  localOnly: boolean;
}

export interface AuthorMemoryEvent {
  id: string;
  noteId: string;
  type: AuthorNoteType;
  summary: string;
  detectedSignals: string[];
  createdAt: string;
}

export interface EvidenceLink {
  noteId: string;
  quote: string;
  reason: string;
}

export interface AuthorPositionAssertion {
  id: string;
  type: AuthorPositionAssertionType;
  title: string;
  statement: string;
  confidence: number;
  evidence: EvidenceLink[];
  status: AuthorPositionAssertionStatus;
}

export interface AuthorExternalSource {
  id: string;
  type: ExternalSourceType;
  title: string;
  url: string;
  fileReference: string;
  status: ExternalSourceStatus;
  importMode: ImportMode;
  lastCheckedAt: string;
  lastImportedAt: string;
  notes: string;
}

export interface ImportedMemoryCandidate {
  id: string;
  sourceId: string;
  title: string;
  excerpt: string;
  originalUrl: string;
  capturedAt: string;
  detectedTags: string[];
  duplicateRisk: ImportRiskLevel;
  suggestedTarget: string;
  reviewStatus: ImportReviewStatus;
  evidencePolicy: EvidencePolicy;
}
