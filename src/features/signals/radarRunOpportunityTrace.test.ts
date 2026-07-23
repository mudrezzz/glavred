import { describe, expect, it } from 'vitest';
import type { RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';
import { searchOpportunityTraceDetail, searchRequirementsTraceDetail } from './radarRunOpportunityTrace';
import { enrichedRadarRun, radar, sourceHandle } from './radarRunTraceTestFixtures';

describe('radarRunOpportunityTrace', () => {
  it('renders filter requirements as readable search evidence instead of raw handles', () => {
    const bundle = traceBundle({
      searchPlan: {
        ...enrichedRadarRun.searchPlan!,
        requirementProfile: {
          version: 'radar-search-requirements-v1',
          radarId: radar.id,
          requirements: [{
            id: 'search-requirement-filter-topic',
            filterId: 'filter-topic',
            dimension: 'topics',
            mode: 'mustMatch',
            role: 'required',
            title: 'Промышленный контекст',
            statement: 'Найти промышленный кейс с механизмом внедрения.',
            priority: 100,
            queryFamilies: ['caseExample'],
            evidenceTypes: ['caseExample'],
            terms: ['промышленный', 'механизм'],
            sourceHints: []
          }],
          notSearchApplicable: [{ filterId: 'filter-author', dimension: 'author', mode: 'shouldMatch', reason: 'project-setting-is-scoring-only' }],
          retainedCounts: { filters: 2 },
          trimmedCounts: { filters: 0 },
          suppressedFields: ['workspace']
        },
        queries: enrichedRadarRun.searchPlan!.queries.map((query) => ({
          ...query,
          requirementIds: ['search-requirement-filter-topic']
        })),
        uncoveredRequiredSearchRequirements: []
      }
    });

    const detail = searchRequirementsTraceDetail(bundle);

    expect(detail.title).toBe('Что требовалось найти');
    expect(detail.items[0]).toEqual(expect.objectContaining({
      label: 'Обязательно найти',
      title: 'Промышленный контекст',
      body: 'Найти промышленный кейс с механизмом внедрения.'
    }));
    expect(detail.items.map((item) => item.body).join(' ')).not.toContain('search-requirement-filter-topic');
    expect(detail.items[detail.items.length - 1]?.label).toBe('Только для оценки');
  });

  it('shows counts and the first failed stage without fake percentages', () => {
    const detail = searchOpportunityTraceDetail(traceBundle({
      searchOpportunityCoverage: {
        version: 'search-opportunity-coverage-v1',
        status: 'zeroYield',
        plannedRequirementIds: ['requirement-topic'],
        executedRequirementIds: ['requirement-topic'],
        uncoveredRequiredSearchRequirements: [],
        familyCoverage: { planned: ['caseExample'], executed: ['caseExample'] },
        evidenceCoverage: { planned: ['caseExample'], executed: ['caseExample'] },
        counts: { readableMaterialCount: 2, signalCount: 1, reviewEligibleCount: 0, notRecommendedCount: 1 },
        extractedSignalYield: { count: 1, denominator: 2, ratio: 0.5 },
        reviewEligibleYield: { count: 0, denominator: 1, ratio: 0 },
        rejectedYield: { count: 1, denominator: 1, ratio: 1 },
        recommendationDistribution: { notRecommended: 1 },
        reasonDistribution: { 'zero-review-eligible-yield': 1 },
        firstFailureStage: 'signalScoring',
        reasonCodes: ['zero-review-eligible-yield'],
        remediation: ['Проверить причины blocking-критериев.'],
        lineage: [],
        unresolvedHandles: { requirement: 0, query: 0, material: 0, fragment: 0 }
      }
    }));

    expect(detail.fields).toContainEqual({ label: 'Первый проблемный этап', value: 'Оценка редакционной полезности' });
    expect(detail.items[0].title).toBe('0 из 1 сигналов можно передать редактору');
    expect(JSON.stringify(detail)).not.toContain('%');
  });
});

function traceBundle(runPatch: Partial<typeof enrichedRadarRun>): RadarRunTraceBundle {
  return {
    project: { id: 'project-1', ownerUserId: 'user-1', title: 'Project', description: '', language: 'ru', status: 'active', benchmarkRole: 'demo', createdAt: '', updatedAt: '' },
    workspace: {} as RadarRunTraceBundle['workspace'],
    radar,
    run: { ...enrichedRadarRun, ...runPatch },
    sourceHandles: [sourceHandle],
    foundMaterials: [],
    sourceSignals: [],
    benchmarkReport: null,
    source: 'backend'
  };
}
