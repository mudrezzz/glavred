import { render, screen } from '@testing-library/react';
import { fireEvent } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { RadarCard } from './RadarCard';
import { RadarRunTraceSection } from './RadarRunTraceSection';
import type { FoundMaterial, RadarRun, SourceHandle } from '../../domain/editorialWorkspace';
import { createRadarTracePortfolio } from './radarRunTraceTestFixtures';

describe('RadarRunTraceSection', () => {
  it('renders search plan, pre-read triage, and found materials separately', () => {
    render(
      <RadarRunTraceSection
        latestRun={run}
        sourceHandles={[handle]}
        foundMaterials={[material]}
      />
    );

    expect(screen.getByText('Карта поиска')).toBeInTheDocument();
    expect(screen.getByText("Поисковые intent'ы")).toBeInTheDocument();
    expect(screen.getByText('deterministic-search-campaign-v2')).toBeInTheDocument();
    expect(screen.getByText('benchmarkPaper · Industrial AI web')).toBeInTheDocument();
    expect(screen.getByText("Пропущенные intent'ы")).toBeInTheDocument();
    expect(screen.getByText('budget-max-external-queries')).toBeInTheDocument();
    expect(screen.getByText('industrial AI maintenance case study')).toBeInTheDocument();
    expect(screen.getByText('Отбор перед чтением')).toBeInTheDocument();
    expect(screen.getByText('best-diverse-result')).toBeInTheDocument();
    expect(screen.getByText('duplicate-url')).toBeInTheDocument();
    expect(screen.getByText('Найденные материалы')).toBeInTheDocument();
    expect(screen.getByText('Read case')).toBeInTheDocument();
  });

  it('links the compact radar trace tab to the dedicated RadarRun trace page', () => {
    const portfolio = createRadarTracePortfolio();
    const workspace = portfolio.workspacesByProjectId[portfolio.projects[0].id];
    const radar = workspace.radars[0];
    const latestRun = workspace.radarRuns[0];
    render(
      <RadarCard
        radar={radar}
        controller={{
          expandedRadarId: radar.id,
          editingRadar: null,
          isNewRadar: false,
          latestRunsByRadar: { [radar.id]: latestRun },
          radarRunSummaries: { [radar.id]: { found: 1, skipped: 0, status: 'succeeded' } },
          sourceHandlesByRadar: { [radar.id]: workspace.sourceRegistry.handles },
          foundMaterialsByRun: { [latestRun.id]: workspace.foundMaterials },
          setExpandedRadarId: () => undefined,
          setRadarFilter: () => undefined,
          setTab: () => undefined,
          startRadarEdit: () => undefined
        } as never}
        signalCount={0}
        onDeleteRadar={() => undefined}
        onRunRadar={() => undefined}
        onToggleRadarStatus={() => undefined}
      />
    );

    fireEvent.click(screen.getAllByRole('tab')[1]);

    expect(screen.getByRole('link', { name: 'Открыть трассу' })).toHaveAttribute(
      'href',
      '/radar-runs?runId=radar-run-industrial-1'
    );
  });
});

const handle: SourceHandle = {
  id: 'source-open-web',
  type: 'openWebQuery',
  title: 'Industrial AI web',
  locator: 'industrial AI',
  status: 'active',
  obligation: 'preferred',
  capabilities: { canScanInternal: false, canSearch: true, canReadUrl: false, canImport: false, canVerify: true, broadDiscovery: true },
  notes: '',
  tags: []
};

const run: RadarRun = {
  id: 'run-1',
  radarId: 'radar-1',
  status: 'succeeded',
  startedAt: '2026-07-03T10:00:00.000Z',
  completedAt: '2026-07-03T10:00:01.000Z',
  budget: { maxOperations: 3, maxInternalItems: 0, maxExternalQueries: 1, maxUrlReads: 1, maxFoundMaterials: 1, usedOperations: 2, usedInternalItems: 0, usedExternalQueries: 1, usedUrlReads: 1, usedFoundMaterials: 1 },
  operations: [],
  foundMaterialIds: ['material-1'],
  skippedReasons: [],
  warnings: [],
  errors: [],
  searchPlan: {
    strategy: 'deterministic-search-campaign-v2',
    language: 'en',
    skippedIntents: ['budget-max-external-queries'],
    intents: [{
      id: 'intent-1',
      intentType: 'caseStudy',
      family: 'caseExample',
      evidenceType: 'benchmarkPaper',
      label: 'case studies',
      sourceHandleId: 'source-open-web',
      sourceHandleTitle: 'Industrial AI web',
      rationale: 'Find implementation examples.',
      priority: 1,
      queryTerms: ['industrial', 'AI']
    }],
    sourceStrategy: {
      searchableSourceHandleIds: ['source-open-web'],
      directReadSourceHandleIds: [],
      skippedSources: [],
      strategy: 'search-active-handles-read-readable-handles'
    },
    trace: {
      plannerVersion: 'deterministic-search-campaign-v2',
      inputSummary: { radarId: 'radar-1' },
      intentCoverage: [{
        intentId: 'intent-1',
        family: 'caseExample',
        evidenceType: 'benchmarkPaper',
        sourceHandleId: 'source-open-web',
        queryCount: 1,
        skippedCount: 0,
        status: 'queryPlanned'
      }],
      budgetLimits: { maxExternalQueries: 1 },
      sourceEligibility: [],
      skippedReasons: ['budget-max-external-queries'],
      ownershipBoundary: 'Search campaign may use topics and fabulas as context, but raw FoundMaterial does not own topic or fabula decisions.'
    },
    skippedIntentDetails: [{
      id: 'skip-intent-1',
      reason: 'budget-max-external-queries',
      rationale: 'Budget exhausted.',
      intentId: 'intent-2',
      intentType: 'benchmark',
      family: 'benchmarkPaper'
    }],
    queries: [{
      id: 'query-1',
      sourceHandleId: 'source-open-web',
      intent: 'caseStudy',
      intentId: 'intent-1',
      family: 'caseExample',
      evidenceType: 'benchmarkPaper',
      priority: 1,
      label: 'case studies',
      query: 'industrial AI maintenance case study',
      rationale: 'Find implementation examples.'
    }]
  },
  rawResults: [{
    id: 'raw-1',
    sourceHandleId: 'source-open-web',
    queryId: 'query-1',
    title: 'Case',
    url: 'https://example.com/case',
    snippet: 'Case',
    domain: 'example.com',
    score: 4,
    duplicateKey: 'https://example.com/case',
    provider: 'openrouter:web_search'
  }],
  selectedForRead: [{ rawResultId: 'raw-1', url: 'https://example.com/case', reason: 'best-diverse-result', score: 4 }],
  rejectedBeforeRead: [{ rawResultId: 'raw-2', url: 'https://example.com/case', reason: 'duplicate-url', score: 2 }]
};

const material: FoundMaterial = {
  id: 'material-1',
  radarRunId: 'run-1',
  sourceHandleId: 'source-open-web',
  type: 'searchResult',
  title: 'Read case',
  locator: 'https://example.com/case',
  snippet: 'Useful case',
  summary: 'Useful case',
  capturedAt: '2026-07-03T10:00:01.000Z',
  status: 'found',
  warnings: [],
  provenanceLabel: 'openrouter'
};
