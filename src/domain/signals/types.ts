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
  | 'topics'
  | 'evidenceStrength'
  | 'factualSpecificity'
  | 'sourceCredibility'
  | 'mechanism'
  | 'observableOutcome'
  | 'actionability'
  | 'novelty'
  | 'productiveTension'
  | 'freshness'
  | 'duplicationRisk'
  | 'promotionalNoise';
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

export type SignalUtilityDimensionStatus = 'matched' | 'partial' | 'notProven' | 'conflict';
export type SignalUtilityImportance = 'blocking' | 'weighted' | 'diagnostic';
export type SignalUtilityRecommendation = 'recommended' | 'reviewWithCaution' | 'notRecommended' | 'inconclusive';
export type SignalCriterionOrigin = 'radar' | 'project' | 'system';
export type SignalCriterionEffect = 'pass' | 'caution' | 'block' | 'diagnostic';
export type SignalRelationshipKind =
  | 'exactDuplicate'
  | 'sameClaim'
  | 'relatedSameSource'
  | 'corroborates'
  | 'contradicts'
  | 'distinct'
  | 'inconclusive';

export interface SignalUtilityDimensionResult {
  dimension: string;
  status: SignalUtilityDimensionStatus;
  importance: SignalUtilityImportance;
  summary: string;
  reasonCodes: string[];
  settingRefs: string[];
  evidenceRefs: Array<{ materialId: string; fragmentId: string }>;
  uncertainty?: string;
}

export interface SignalUtilityCriterionResult {
  criterionId: string;
  origin: SignalCriterionOrigin;
  dimension: string;
  title: string;
  statement: string;
  mode: RadarEditorialFilterMode;
  status: SignalUtilityDimensionStatus;
  verdict: string;
  effect: SignalCriterionEffect;
  summary: string;
  settingRefs: string[];
  evidenceRefs: Array<{ materialId: string; fragmentId: string }>;
  uncertainty?: string;
}

export interface SignalQualityCheck {
  checkId: string;
  title: string;
  status: string;
  verdict: string;
  effect: SignalCriterionEffect;
  summary: string;
  classification?: string | null;
  applicable: boolean;
  evidenceRefs: Array<{ materialId: string; fragmentId: string }>;
}

export interface SignalRelationship {
  otherSignalId: string;
  kind: SignalRelationshipKind;
  summary: string;
  evidenceRefs: Array<{ materialId: string; fragmentId: string }>;
}

export interface SignalRelationshipReport {
  version: number;
  status: 'checked' | 'notChecked' | 'inconclusive';
  canonicalSignalId: string;
  relations: SignalRelationship[];
}

export interface SignalUtilityReport {
  version: number;
  revision: number;
  status: 'complete' | 'inconclusive' | 'stale';
  recommendation: SignalUtilityRecommendation;
  dimensions: SignalUtilityDimensionResult[];
  blockingReasons: string[];
  warnings: string[];
  evaluationPlanVersion?: number;
  radarCriteria?: SignalUtilityCriterionResult[];
  projectCriteria?: SignalUtilityCriterionResult[];
  qualityChecks?: SignalQualityCheck[];
  notApplicableSettings?: Array<{ settingId: string; title: string; reason: string }>;
  relationshipReport?: SignalRelationshipReport | null;
  staleReason?: string;
}

export interface SignalReviewEvent {
  id: string;
  actorId: string;
  occurredAt: string;
  action: string;
  fromStatus: SignalReviewStatus;
  toStatus: SignalReviewStatus;
  reason: string;
  changedFields: string[];
  reviewRevision: number;
}

export interface LegacySignalUtilityEvaluation {
  status?: SignalFilterStatus;
  evaluations: SignalFilterEvaluation[];
  source: 'legacy-client-keyword-evaluator';
  canonical: false;
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
  utilityReport?: SignalUtilityReport;
  relationshipReport?: SignalRelationshipReport | null;
  utilityRevision?: number;
  reviewRevision?: number;
  reviewHistory?: SignalReviewEvent[];
  legacyIntegrityStatus?: 'current' | 'needsReExtraction';
  legacyUtilityEvaluation?: LegacySignalUtilityEvaluation | null;
}
