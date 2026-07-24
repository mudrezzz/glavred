import { describe, expect, it } from 'vitest';
import type { RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';
import type { RadarSearchRequirement } from '../../domain/upstream-search/types';
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

  it('shows delivered evidence stage and a human stop reason', () => {
    const basePlan = enrichedRadarRun.searchPlan!;
    const requirement: RadarSearchRequirement = {
      id: 'requirement-source',
      filterId: 'filter-source',
      dimension: 'sourceCredibility',
      mode: 'mustMatch',
      role: 'required',
      title: 'Надежность источника',
      statement: 'Найти независимое подтверждение.',
      priority: 100,
      queryFamilies: ['benchmarkPaper'],
      evidenceTypes: ['benchmarkPaper'],
      terms: ['independent', 'report'],
      sourceHints: []
    };
    const detail = searchRequirementsTraceDetail(traceBundle({
      searchPlan: {
        ...basePlan,
        requirementProfile: {
          version: 'radar-search-requirements-v1',
          radarId: radar.id,
          requirements: [requirement],
          notSearchApplicable: [],
          retainedCounts: { filters: 1 },
          trimmedCounts: { filters: 0 },
          suppressedFields: []
        },
        queries: basePlan.queries.map((query) => ({
          ...query,
          requirementIds: ['requirement-source']
        })),
        uncoveredRequiredSearchRequirements: []
      },
      searchOpportunityCoverage: {
        version: 'search-opportunity-coverage-v2',
        status: 'partial',
        plannedRequirementIds: ['requirement-source'],
        executedRequirementIds: ['requirement-source'],
        uncoveredRequiredSearchRequirements: [],
        familyCoverage: { planned: ['benchmarkPaper'], executed: ['benchmarkPaper'] },
        evidenceCoverage: { planned: ['benchmarkPaper'], executed: ['benchmarkPaper'] },
        counts: {},
        extractedSignalYield: { count: 1, denominator: 1, ratio: 1 },
        reviewEligibleYield: { count: 1, denominator: 1, ratio: 1 },
        rejectedYield: { count: 0, denominator: 1, ratio: 0 },
        recommendationDistribution: { reviewWithCaution: 1 },
        reasonDistribution: {},
        reasonCodes: [],
        remediation: [],
        lineage: [],
        unresolvedHandles: {},
        requirementCoverage: [{
          requirementId: 'requirement-source',
          role: 'required',
          mode: 'mustMatch',
          title: 'Надежность источника',
          furthestStage: 'usedBySignal',
          delivered: true,
          stopReason: 'corroboration-not-found',
          queryIds: ['query-1'],
          rawResultIds: ['raw-1'],
          supportedRawResultIds: ['raw-1'],
          readDecisionRawResultIds: ['raw-1'],
          materialIds: ['material-1'],
          fragmentIds: ['fragment-1'],
          signalIds: ['signal-1'],
          corroboratingMaterialIds: []
        }]
      }
    }));

    expect(detail.items[0]?.meta).toContainEqual({
      label: 'Доставка доказательства',
      value: 'Доказательство использовано сигналом'
    });
    expect(detail.items[0]?.meta).toContainEqual({
      label: 'Почему остановилось',
      value: 'Независимое подтверждение не найдено'
    });
    expect(JSON.stringify(detail.items)).not.toContain('raw-1');
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
