import type { ImportRiskLevel } from '../imports/types';
import type { EditorialEntityStatus } from '../shared/types';

// Signals are raw reviewed material from radars; topic/fabula matching happens later.
export type RadarSourceType = 'authorMemory' | 'archive' | 'externalSource' | 'manualResearch';
export type RadarAcceptancePolicy = 'manual' | 'automatic' | 'automaticWithReview';
export type RadarTriggerMode = 'scheduled' | 'manual' | 'deficitDriven';
export type RadarStatus = 'active' | 'paused' | 'needsReview';
export type RadarRuleOperator = 'and' | 'or';
export type RadarSourceDiscoveryMode = 'specifiedOnly' | 'specifiedAndAdditional' | 'autonomous';
export type RadarSourceLanguagePolicy = 'editorialOnly' | 'editorialAndEnglish' | 'any';
export type RadarEditorialFilterDimension =
  | 'author'
  | 'audience'
  | 'positioning'
  | 'goals'
  | 'forbiddenTopics'
  | 'topics';
export type RadarEditorialFilterMode = 'mustMatch' | 'shouldMatch' | 'mustNotMatch' | 'seekTension';
export type SignalFilterEvaluationStatus = 'passed' | 'warning' | 'failed' | 'tension';
export type SignalFilterStatus = 'passed' | 'warning' | 'rejected';
export type RadarSearchSourceType =
  | 'authorArchive'
  | 'externalUrl'
  | 'mcpServer'
  | 'api'
  | 'searchKeywords'
  | 'manualSource'
  | 'socialProfile'
  | 'document'
  | 'openWeb';
export type SignalReviewStatus = 'candidate' | 'new' | 'approved' | 'rejected' | 'archived' | 'corrected';

export interface RadarDefinition {
  id: string;
  title: string;
  sourceType: RadarSourceType;
  scope: string;
  rules: RadarSearchRule[];
  sources: RadarSearchSource[];
  sourceHandleIds?: string[];
  sourceDiscoveryMode?: RadarSourceDiscoveryMode;
  sourceLanguagePolicy?: RadarSourceLanguagePolicy;
  filters?: RadarEditorialFilterRule[];
  acceptancePolicy: RadarAcceptancePolicy;
  triggerMode: RadarTriggerMode;
  status: RadarStatus;
  lastRunAt: string;
  notes: string;
}

export interface RadarSearchRule {
  id: string;
  operator: RadarRuleOperator;
  negate: boolean;
  statement: string;
  status: EditorialEntityStatus;
}

export interface RadarSearchSource {
  id: string;
  type: RadarSearchSourceType;
  title: string;
  value: string;
  notes: string;
  status: EditorialEntityStatus;
}

export interface RadarEditorialFilterRule {
  id: string;
  dimension: RadarEditorialFilterDimension;
  enabled: boolean;
  mode: RadarEditorialFilterMode;
  instruction: string;
}

export interface SignalFilterEvaluation {
  filterId: string;
  dimension: RadarEditorialFilterDimension;
  status: SignalFilterEvaluationStatus;
  score: number;
  summary: string;
  evidence: string;
}

export interface SignalEvidence {
  id: string;
  sourceTitle: string;
  sourceUrl: string;
  quote: string;
  summary: string;
  materialId?: string;
  fragmentId?: string;
}

export interface SignalEvidenceRef {
  materialId: string;
  fragmentId: string;
  quote: string;
}

export interface SourceSignal {
  id: string;
  type: string;
  title: string;
  source: string;
  capturedAt: string;
  summary: string;
  rawNote: string;
  evidence?: SignalEvidence[];
  searchNote?: string;
  radarId?: string;
  reviewStatus?: SignalReviewStatus;
  suggestedTopicId?: string;
  suggestedFabulaId?: string;
  suggestedValue?: string;
  duplicateRisk?: ImportRiskLevel;
  authorCorrection?: string;
  filterEvaluations?: SignalFilterEvaluation[];
  filterStatus?: SignalFilterStatus;
  radarRunId?: string;
  evidenceRefs?: SignalEvidenceRef[];
  confidence?: 'low' | 'medium' | 'high';
  uncertainty?: string;
  mechanism?: string;
  actors?: string[];
  outcome?: string;
  limitations?: string[];
  provenance?: { materialIds: string[] };
  reasonCodes?: string[];
  editorialLanguage?: string;
  sourceLanguage?: string;
  localizationStatus?: 'original' | 'localized' | 'failed' | 'unverified';
  localizationReasonCodes?: string[];
}
