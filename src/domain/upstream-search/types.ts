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
}

export interface RadarSearchQuery {
  id: string;
  sourceHandleId: string;
  intent: string;
  label: string;
  query: string;
  rationale: string;
}

export interface RadarSearchPlan {
  strategy: string;
  language: string;
  queries: RadarSearchQuery[];
  skippedIntents: string[];
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
}

export interface RadarReadSelection {
  rawResultId: string;
  url: string;
  reason: string;
  score: number;
}

export interface RadarReadRejection {
  rawResultId: string;
  url: string;
  reason: string;
  score: number;
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
}
