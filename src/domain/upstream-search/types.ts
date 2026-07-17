export type SourceHandleType =
  | 'authorMemory'
  | 'archive'
  | 'previousPosts'
  | 'manualNotes'
  | 'externalUrl'
  | 'openWebQuery'
  | 'socialProfile'
  | 'document'
  | 'sourcePlaceholder';

export type SourceHandleStatus = 'active' | 'paused' | 'needsReview';
export type SourceObligation = 'required' | 'preferred' | 'fallback' | 'disabled' | 'internalOnly' | 'verificationOnly';

export interface SourceCapability {
  canScanInternal: boolean;
  canSearch: boolean;
  canReadUrl: boolean;
  canImport: boolean;
  canVerify: boolean;
  broadDiscovery: boolean;
}

export interface SourceHandle {
  id: string;
  type: SourceHandleType;
  title: string;
  locator: string;
  status: SourceHandleStatus;
  obligation: SourceObligation;
  capabilities: SourceCapability;
  notes: string;
  tags: string[];
  language?: string;
  legacySourceId?: string;
}

export interface SourceRegistry {
  id: string;
  handles: SourceHandle[];
  updatedAt: string;
}

export type RadarRunStatus = 'running' | 'succeeded' | 'failed' | 'partial';
export type RadarRunOperationStatus = 'running' | 'succeeded' | 'failed' | 'skipped';
export type RadarRunOperationKind =
  | 'internalScan'
  | 'openWebQuery'
  | 'readUrl'
  | 'importDocument'
  | 'metadataOnly'
  | 'signalExtraction'
  | 'skip';

export interface RadarRunBudget {
  maxOperations: number;
  maxInternalItems: number;
  maxExternalQueries: number;
  maxUrlReads: number;
  maxFoundMaterials: number;
  usedOperations: number;
  usedInternalItems: number;
  usedExternalQueries: number;
  usedUrlReads: number;
  usedFoundMaterials: number;
  maxProviderInputChars?: number;
  maxProviderInputTokens?: number;
  maxResultsPerQuery?: number;
  usedProviderInputChars?: number;
  usedProviderInputTokens?: number;
}

export interface RadarRunOperation {
  id: string;
  runId: string;
  sourceHandleId: string;
  kind: RadarRunOperationKind;
  label: string;
  status: RadarRunOperationStatus;
  startedAt: string;
  completedAt?: string;
  target?: string;
  foundMaterialIds: string[];
  skippedReason?: string;
  error?: string;
  providerInput?: Record<string, unknown>;
  payloadBudget?: Record<string, unknown>;
  inputStats?: Record<string, unknown>;
  payloadStats?: Record<string, unknown>;
  messageCharCount?: number;
  providerUsage?: Record<string, unknown>;
  selectedModel?: string;
  maxResults?: number;
}

export interface RadarSearchQuery {
  id: string;
  sourceHandleId: string;
  intent: string;
  label: string;
  query: string;
  rationale: string;
  intentId?: string;
  family?: string;
  evidenceType?: string;
  priority?: number;
  queryLanguage?: string;
}

export interface RadarSearchIntent {
  id: string;
  intentType: string;
  family: string;
  evidenceType: string;
  label: string;
  sourceHandleId: string;
  sourceHandleTitle: string;
  rationale: string;
  priority: number;
  queryTerms: string[];
  queryLanguage?: string;
}

export interface RadarSkippedSearchIntent {
  id: string;
  reason: string;
  rationale: string;
  sourceHandleId?: string;
  intentId?: string;
  intentType?: string;
  family?: string;
  queryLanguage?: string;
}

export interface RadarSearchCampaignTrace {
  plannerVersion: string;
  inputSummary: Record<string, unknown>;
  intentCoverage: Array<{
    intentId: string;
    family: string;
    evidenceType: string;
    sourceHandleId: string;
    queryCount: number;
    skippedCount: number;
    status: string;
  }>;
  budgetLimits: Record<string, unknown>;
  sourceEligibility: Array<Record<string, unknown>>;
  skippedReasons: string[];
  ownershipBoundary: string;
}

export interface RadarSearchPlan {
  strategy: string;
  language: string;
  queries: RadarSearchQuery[];
  skippedIntents: string[];
  intents?: RadarSearchIntent[];
  sourceStrategy?: {
    searchableSourceHandleIds: string[];
    directReadSourceHandleIds: string[];
    skippedSources: Array<Record<string, unknown>>;
    strategy: string;
  };
  trace?: RadarSearchCampaignTrace;
  skippedIntentDetails?: RadarSkippedSearchIntent[];
  languageContext?: RadarLanguageContextTrace;
  languageCoverageGaps?: Array<{ language: string; reason: string }>;
}

export interface RadarLanguageContextTrace {
  projectId: string;
  editorialLanguage: string;
  sourceLanguagePolicy: 'editorialOnly' | 'editorialAndEnglish' | 'any';
  queryLanguages: string[];
  allowedSourceLanguages: string[];
  allowUnknownSourceLanguage: boolean;
  fallbackReason?: string;
}

export interface RadarSourceLanguageTrace {
  language: string;
  confidence: string;
  mixed: boolean;
  reasonCodes: string[];
  allowed?: boolean;
  eligibilityReason?: string;
}

export interface RadarRawSearchResult {
  id: string;
  sourceHandleId: string;
  queryId: string;
  title: string;
  url: string;
  snippet: string;
  domain: string;
  score: number;
  duplicateKey: string;
  provider: string;
  intentId?: string;
  family?: string;
  evidenceType?: string;
  query?: string;
  candidateId?: string;
  duplicateGroupId?: string;
  dimensionScores?: RadarSearchResultDimensionScores;
  queryLanguage?: string;
  sourceLanguage?: RadarSourceLanguageTrace;
}

export interface RadarSearchResultDimensionScores {
  relevance: number;
  evidenceFit: number;
  projectFit: number;
  sourceQuality: number;
  novelty: number;
  noiseRisk: number;
  total: number;
  reasonCodes: string[];
  explanation: string;
}

export interface RadarReadDecision {
  rawResultId: string;
  candidateId?: string;
  duplicateGroupId?: string;
  status?: 'selected' | 'rejected' | 'duplicate' | 'invalid' | 'deferredByBudget';
  url: string;
  reason: string;
  score: number;
  families?: string[];
  evidenceTypes?: string[];
  domain?: string;
  duplicateRawResultIds?: string[];
  queryIds?: string[];
  intentIds?: string[];
  sourceLanguage?: RadarSourceLanguageTrace;
}

export type RadarReadSelection = RadarReadDecision;
export type RadarReadRejection = RadarReadDecision;

export interface RadarSearchDuplicateGroup {
  id: string;
  representativeCandidateId: string;
  candidateIds: string[];
  rawResultIds: string[];
  queryIds: string[];
  intentIds: string[];
  families: string[];
  evidenceTypes: string[];
  domains: string[];
  matchReasons: string[];
}

export interface RadarSearchTriageCandidate {
  id: string;
  rawResultId: string;
  sourceHandleId: string;
  queryId: string;
  intentId: string;
  family: string;
  evidenceType: string;
  title: string;
  url: string;
  canonicalUrl: string;
  snippet: string;
  domain: string;
  provider: string;
  fingerprint: string;
  valid: boolean;
  invalidReason?: string;
  scores?: RadarSearchResultDimensionScores | null;
  sourceLanguage?: RadarSourceLanguageTrace;
}

export interface RadarSearchReadOutcome {
  rawResultId: string;
  candidateId: string;
  duplicateGroupId?: string;
  status: 'succeeded' | 'failed' | 'notRun';
  materialId?: string;
  readable: boolean;
  reason?: string;
}

export interface RadarSearchTriageReport {
  policyVersion: string;
  candidates: RadarSearchTriageCandidate[];
  duplicateGroups: RadarSearchDuplicateGroup[];
  readPlan: {
    maxReads: number;
    qualityFloor: number;
    requiredFamilies: string[];
    selectedCandidateIds: string[];
    decisions: RadarReadDecision[];
    coveredFamilies: string[];
    readCoverageGaps: Array<{ family: string; reason: string }>;
  };
  readCoverage: {
    requiredFamilies: string[];
    coveredFamilies: string[];
  };
  readCoverageGaps: Array<{ family: string; reason: string }>;
  readOutcomes: RadarSearchReadOutcome[];
  decisionCounts: Record<string, number>;
  languageContext?: RadarLanguageContextTrace;
}

export interface RadarBenchmarkReport {
  status: string;
  scenarioId?: string;
  evaluationMode?: string;
  providerHealth?: string;
  coverage?: Record<string, unknown>;
  plannedCoverage?: Record<string, unknown>;
  executedCoverage?: Record<string, unknown>;
  skippedRequiredCoverage?: Array<Record<string, unknown>>;
  counters?: Record<string, unknown>;
  missingExpectations?: string[];
  warnings?: string[];
  unacceptableNoiseHits?: string[];
  inconclusiveReasons?: string[];
  traceComplete?: boolean;
}

export interface RadarRun {
  id: string;
  radarId: string;
  status: RadarRunStatus;
  startedAt: string;
  completedAt?: string;
  budget: RadarRunBudget;
  operations: RadarRunOperation[];
  foundMaterialIds: string[];
  skippedReasons: string[];
  warnings: string[];
  errors: string[];
  searchPlan?: RadarSearchPlan;
  rawResults?: RadarRawSearchResult[];
  selectedForRead?: RadarReadSelection[];
  rejectedBeforeRead?: RadarReadRejection[];
  benchmarkReport?: RadarBenchmarkReport;
  searchTriage?: RadarSearchTriageReport;
  signalExtraction?: RadarSignalExtractionReport;
  languageContext?: RadarLanguageContextTrace;
}

export type RadarMaterialExtractionDecision =
  | 'signalProducing'
  | 'insufficient'
  | 'duplicate'
  | 'corroborating'
  | 'contradiction'
  | 'noise'
  | 'extractionFailed';

export interface RadarSignalExtractionReport {
  status: 'succeeded' | 'partial' | 'failed' | 'notRun';
  revision: number;
  revisions?: Array<{ revision: number; status: string }>;
  retryOutcome?: 'succeeded' | 'partial' | 'failed' | 'notRun';
  preservedPreviousSignalIds?: string[];
  materialDecisions: Array<{
    materialId: string;
    decision: RadarMaterialExtractionDecision;
    reasonCodes: string[];
    signalIds: string[];
  }>;
  decisionCounts?: Record<string, number>;
  signalIds?: string[];
  signalCount?: number;
  providerAttempts?: Array<Record<string, unknown>>;
  groundingViolations?: Array<Record<string, unknown>>;
  warnings?: string[];
  dossier?: Record<string, unknown>;
  decisionCoverageComplete?: boolean;
  unresolvedEvidenceHandleCount?: number;
  createdDownstreamArtifacts?: Record<string, number>;
}

export type FoundMaterialType =
  | 'authorNote'
  | 'archiveRecord'
  | 'previousPost'
  | 'manualNote'
  | 'searchResult'
  | 'urlMetadata'
  | 'socialMetadata'
  | 'documentPlaceholder'
  | 'externalPlaceholder';

export type FoundMaterialStatus = 'found' | 'metadataOnly' | 'duplicate' | 'skipped' | 'readyForSignal';

export interface FoundMaterial {
  id: string;
  radarRunId: string;
  sourceHandleId: string;
  type: FoundMaterialType;
  title: string;
  locator: string;
  snippet: string;
  summary: string;
  capturedAt: string;
  status: FoundMaterialStatus;
  warnings: string[];
  provenanceLabel: string;
  sourceLanguage?: RadarSourceLanguageTrace;
  contentFragments?: Array<{
    id: string;
    ordinal: number;
    text: string;
    startChar: number;
    endChar: number;
    hash: string;
    kind: string;
  }>;
  discoveryTrace?: {
    rawResultIds: string[];
    queryIds: string[];
    intentIds: string[];
    families: string[];
    evidenceTypes: string[];
    duplicateGroupId?: string;
    decisionReason?: string;
    queryLanguage?: string;
    sourceLanguage?: RadarSourceLanguageTrace;
  };
}
