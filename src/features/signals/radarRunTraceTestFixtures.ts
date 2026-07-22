import { createDemoPortfolio } from '../../fixtures/demoPortfolio';
import type { PortfolioState } from '../../domain/portfolio/types';
import type { FoundMaterial, RadarDefinition, RadarRun, SourceHandle } from '../../domain/editorialWorkspace';

export function createRadarTracePortfolio(overrides: Partial<RadarRun> = {}): PortfolioState {
  const portfolio = createDemoPortfolio();
  const project = portfolio.projects[0];
  const workspace = portfolio.workspacesByProjectId[project.id];
  const run = { ...enrichedRadarRun, ...overrides };
  return {
    ...portfolio,
    activeProjectId: project.id,
    workspacesByProjectId: {
      ...portfolio.workspacesByProjectId,
      [project.id]: {
        ...workspace,
        radars: [radar],
        sourceRegistry: { id: 'source-registry-test', handles: [sourceHandle], updatedAt: workspace.updatedAt },
        radarRuns: [run],
        foundMaterials: run.foundMaterialIds.includes(foundMaterial.id) ? [foundMaterial] : []
      }
    }
  };
}

export const sourceHandle: SourceHandle = {
  id: 'source-open-web',
  type: 'openWebQuery',
  title: 'Industrial AI web',
  locator: 'industrial AI maintenance',
  status: 'active',
  obligation: 'preferred',
  capabilities: {
    canScanInternal: false,
    canSearch: true,
    canReadUrl: false,
    canImport: false,
    canVerify: true,
    broadDiscovery: true
  },
  notes: 'Open web search handle',
  tags: ['benchmark']
};

export const radar: RadarDefinition = {
  id: 'ai-pattern-radar-industrial-cases',
  title: 'Industrial AI cases',
  sourceType: 'externalSource',
  scope: 'Industrial AI maintenance cases',
  rules: [],
  sources: [],
  sourceHandleIds: [sourceHandle.id],
  acceptancePolicy: 'manual',
  triggerMode: 'manual',
  status: 'active',
  lastRunAt: '2026-07-06T10:00:00.000Z',
  notes: ''
};

export const foundMaterialId = 'material-case';

export const enrichedRadarRun: RadarRun = {
  id: 'radar-run-industrial-1',
  radarId: radar.id,
  status: 'succeeded',
  startedAt: '2026-07-06T10:00:00.000Z',
  completedAt: '2026-07-06T10:00:05.000Z',
  budget: {
    maxOperations: 8,
    maxInternalItems: 0,
    maxExternalQueries: 4,
    maxUrlReads: 2,
    maxFoundMaterials: 2,
    usedOperations: 3,
    usedInternalItems: 0,
    usedExternalQueries: 2,
    usedUrlReads: 1,
    usedFoundMaterials: 1
  },
  operations: [{
    id: 'op-search',
    runId: 'radar-run-industrial-1',
    sourceHandleId: sourceHandle.id,
    kind: 'openWebQuery',
    label: 'Search industrial cases',
    status: 'succeeded',
    startedAt: '2026-07-06T10:00:00.000Z',
    completedAt: '2026-07-06T10:00:02.000Z',
    target: 'industrial AI maintenance case study',
    foundMaterialIds: [foundMaterialId],
    providerInput: { operationId: 'openWebQuery', queryId: 'query-case' },
    payloadBudget: { profileId: 'upstream-open-web-query-v1-standard', status: 'directlyBudgeted' },
    messageCharCount: 420,
    providerUsage: { prompt_tokens: 105 },
    selectedModel: 'test-model'
  }],
  foundMaterialIds: [foundMaterialId],
  skippedReasons: ['duplicate-url'],
  warnings: ['one noisy result rejected'],
  errors: [],
  searchPlan: {
    strategy: 'deterministic-search-campaign-v2',
    language: 'en',
    skippedIntents: ['budget-max-external-queries'],
    intents: [{
      id: 'intent-case',
      intentType: 'caseStudy',
      family: 'caseExample',
      evidenceType: 'industrial case/example',
      label: 'Industrial case examples',
      sourceHandleId: sourceHandle.id,
      sourceHandleTitle: sourceHandle.title,
      rationale: 'Find real implementation evidence.',
      priority: 1,
      queryTerms: ['industrial', 'AI', 'maintenance']
    }],
    sourceStrategy: {
      searchableSourceHandleIds: [sourceHandle.id],
      directReadSourceHandleIds: [],
      skippedSources: [],
      strategy: 'search-active-handles-read-readable-handles'
    },
    trace: {
      plannerVersion: 'deterministic-search-campaign-v2',
      inputSummary: { radarId: radar.id },
      intentCoverage: [{
        intentId: 'intent-case',
        family: 'caseExample',
        evidenceType: 'industrial case/example',
        sourceHandleId: sourceHandle.id,
        queryCount: 1,
        skippedCount: 0,
        status: 'queryPlanned'
      }],
      budgetLimits: { maxExternalQueries: 4 },
      sourceEligibility: [],
      skippedReasons: ['budget-max-external-queries'],
      ownershipBoundary: 'Search campaign may use topics and fabulas as context, but raw FoundMaterial does not own topic or fabula decisions.'
    },
    skippedIntentDetails: [{
      id: 'skip-1',
      reason: 'budget-max-external-queries',
      rationale: 'External query cap was reached.',
      intentId: 'intent-extra',
      family: 'freshness'
    }],
    queries: [{
      id: 'query-case',
      sourceHandleId: sourceHandle.id,
      intent: 'caseStudy',
      intentId: 'intent-case',
      family: 'caseExample',
      evidenceType: 'industrial case/example',
      priority: 1,
      label: 'Industrial case examples',
      query: 'industrial AI maintenance case study',
      rationale: 'Find real implementation evidence.'
    }]
  },
  rawResults: [{
    id: 'raw-case',
    sourceHandleId: sourceHandle.id,
    queryId: 'query-case',
    title: 'Maintenance workbench case',
    url: 'https://example.com/case',
    snippet: 'Industrial AI maintenance implementation.',
    domain: 'example.com',
    score: 8,
    duplicateKey: 'https://example.com/case',
    provider: 'openrouter:web_search'
  }],
  selectedForRead: [{ rawResultId: 'raw-case', url: 'https://example.com/case', reason: 'best-diverse-result', score: 8 }],
  rejectedBeforeRead: [{ rawResultId: 'raw-noise', url: 'https://vendor.example/pricing', reason: 'vendor-pricing-noise', score: 1 }],
  searchTriage: {
    policyVersion: 'deterministic-search-triage-v2',
    candidates: [
      {
        id: 'candidate-case',
        rawResultId: 'raw-case',
        sourceHandleId: sourceHandle.id,
        queryId: 'query-case',
        intentId: 'intent-case',
        family: 'caseExample',
        evidenceType: 'caseExample',
        title: 'Maintenance workbench case',
        url: 'https://example.com/case',
        canonicalUrl: 'https://example.com/case',
        snippet: 'Industrial AI maintenance implementation.',
        domain: 'example.com',
        provider: 'openrouter:web_search',
        fingerprint: 'fingerprint-case',
        valid: true,
        scores: {
          relevance: 85,
          evidenceFit: 90,
          projectFit: 80,
          sourceQuality: 60,
          novelty: 70,
          noiseRisk: 0,
          total: 79,
          reasonCodes: ['query-term-match', 'industrial-context'],
          explanation: 'caseExample: итог 79; есть практический кейс и данные.'
        }
      },
      {
        id: 'candidate-duplicate',
        rawResultId: 'raw-case-duplicate',
        sourceHandleId: sourceHandle.id,
        queryId: 'query-case',
        intentId: 'intent-case',
        family: 'caseExample',
        evidenceType: 'caseExample',
        title: 'Maintenance workbench case duplicate',
        url: 'https://example.com/case',
        canonicalUrl: 'https://example.com/case',
        snippet: 'Duplicate citation.',
        domain: 'example.com',
        provider: 'openrouter:web_search',
        fingerprint: 'fingerprint-duplicate',
        valid: true,
        scores: {
          relevance: 60,
          evidenceFit: 60,
          projectFit: 60,
          sourceQuality: 60,
          novelty: 40,
          noiseRisk: 0,
          total: 57,
          reasonCodes: ['query-term-match'],
          explanation: 'Дубликат более сильного результата.'
        }
      }
    ],
    duplicateGroups: [{
      id: 'duplicate-group-case',
      representativeCandidateId: 'candidate-case',
      candidateIds: ['candidate-case', 'candidate-duplicate'],
      rawResultIds: ['raw-case', 'raw-case-duplicate'],
      queryIds: ['query-case'],
      intentIds: ['intent-case'],
      families: ['caseExample'],
      evidenceTypes: ['caseExample'],
      domains: ['example.com'],
      matchReasons: ['canonical-url']
    }],
    readPlan: {
      maxReads: 2,
      qualityFloor: 45,
      requiredFamilies: ['caseExample', 'limitationCritique'],
      selectedCandidateIds: ['candidate-case'],
      decisions: [
        { rawResultId: 'raw-case', candidateId: 'candidate-case', duplicateGroupId: 'duplicate-group-case', status: 'selected', url: 'https://example.com/case', reason: 'coverage-aware-best-result', score: 79, families: ['caseExample'], evidenceTypes: ['caseExample'] },
        { rawResultId: 'raw-case-duplicate', candidateId: 'candidate-duplicate', duplicateGroupId: 'duplicate-group-case', status: 'duplicate', url: 'https://example.com/case', reason: 'duplicate-url', score: 57, families: ['caseExample'], evidenceTypes: ['caseExample'] }
      ],
      coveredFamilies: ['caseExample'],
      readCoverageGaps: [{ family: 'limitationCritique', reason: 'no-candidate' }]
    },
    readCoverage: { requiredFamilies: ['caseExample', 'limitationCritique'], coveredFamilies: ['caseExample'] },
    readCoverageGaps: [{ family: 'limitationCritique', reason: 'no-candidate' }],
    readOutcomes: [{ rawResultId: 'raw-case', candidateId: 'candidate-case', duplicateGroupId: 'duplicate-group-case', status: 'succeeded', materialId: foundMaterialId, readable: true }],
    decisionCounts: { selected: 1, rejected: 0, duplicate: 1, invalid: 0, deferredByBudget: 0, total: 2 }
  }
};

export const foundMaterial: FoundMaterial = {
  id: foundMaterialId,
  radarRunId: enrichedRadarRun.id,
  sourceHandleId: sourceHandle.id,
  type: 'searchResult',
  title: 'Maintenance workbench case',
  locator: 'https://example.com/case',
  snippet: 'Industrial AI maintenance implementation.',
  summary: 'A concrete maintenance workflow case with implementation constraints.',
  capturedAt: '2026-07-06T10:00:05.000Z',
  status: 'found',
  warnings: [],
  provenanceLabel: 'openrouter',
  discoveryTrace: {
    rawResultIds: ['raw-case', 'raw-case-duplicate'],
    queryIds: ['query-case'],
    intentIds: ['intent-case'],
    families: ['caseExample'],
    evidenceTypes: ['caseExample'],
    duplicateGroupId: 'duplicate-group-case',
    decisionReason: 'coverage-aware-best-result'
  }
};
