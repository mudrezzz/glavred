import { describe, expect, it } from 'vitest';
import { buildRadarRunTraceViewModel } from './radarRunTraceViewModel';
import { createRadarTracePortfolio } from './radarRunTraceTestFixtures';
import type { RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';

describe('radarRunTraceViewModel', () => {
  it('builds semantic trace sections for an enriched RadarRun', () => {
    const viewModel = buildRadarRunTraceViewModel(traceBundle());

    expect(viewModel.summary.map((field) => field.label)).toContain('Сырые результаты');
    expect(viewModel.timeline.map((item) => item.title)).toEqual([
      'Сводка запуска',
      'Карта поиска',
      'Стратегия источников',
      'Операции',
      'Сырые результаты',
      'Отбор перед чтением',
      'Найденные материалы',
      'Предупреждения и ошибки',
      'Raw JSON'
    ]);
    expect(viewModel.details.find((detail) => detail.id === 'search-plan')?.items).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ title: 'Industrial case examples' }),
        expect.objectContaining({ body: 'industrial AI maintenance case study' }),
        expect.objectContaining({ title: 'freshness', status: 'skipped' })
      ])
    );
    expect(viewModel.details.find((detail) => detail.id === 'read-selection')?.items).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ label: 'read', title: 'best-diverse-result' }),
        expect.objectContaining({ label: 'skip', title: 'vendor-pricing-noise' })
      ])
    );
  });

  it('keeps minimal legacy RadarRun payloads readable', () => {
    const viewModel = buildRadarRunTraceViewModel(traceBundle({
      searchPlan: undefined,
      rawResults: undefined,
      selectedForRead: undefined,
      rejectedBeforeRead: undefined,
      warnings: [],
      errors: []
    }));

    expect(viewModel.details.some((detail) => detail.id === 'search-plan')).toBe(false);
    expect(viewModel.details.some((detail) => detail.id === 'benchmark')).toBe(false);
    expect(viewModel.details.some((detail) => detail.id === 'raw-results')).toBe(false);
    expect(viewModel.details[viewModel.details.length - 1]?.id).toBe('raw-json');
  });

  it('renders benchmark verdict only when the run has benchmark report metadata', () => {
    const viewModel = buildRadarRunTraceViewModel({
      ...traceBundle(),
      benchmarkReport: {
        status: 'passed',
        scenarioId: 'benchmark-industrial-ai-maintenance-cases',
        plannedCoverage: {
          queryFamilies: { expected: ['caseExample'], covered: ['caseExample'], missing: [] },
          evidenceTypes: { expected: ['caseExample'], covered: ['caseExample'], missing: [] }
        },
        executedCoverage: {
          queryFamilies: { expected: ['caseExample'], covered: ['caseExample'], missing: [] },
          evidenceTypes: { expected: ['caseExample'], covered: ['caseExample'], missing: [] }
        },
        traceComplete: true
      }
    });

    expect(viewModel.details.find((detail) => detail.id === 'benchmark')?.fields).toEqual(
      expect.arrayContaining([
        { label: 'Status', value: 'passed' },
        { label: 'Scenario', value: 'benchmark-industrial-ai-maintenance-cases' },
        { label: 'Planned coverage', value: 'families 1/1\nevidence 1/1' },
        { label: 'Executed coverage', value: 'families 1/1\nevidence 1/1' },
        { label: 'Verdict impact', value: 'Required coverage was executed.' }
      ])
    );
  });

  it('renders live benchmark provider and inconclusive fields', () => {
    const viewModel = buildRadarRunTraceViewModel({
      ...traceBundle(),
      benchmarkReport: {
        status: 'inconclusive',
        scenarioId: 'benchmark-industrial-ai-maintenance-cases',
        evaluationMode: 'live',
        providerHealth: 'unavailable',
        coverage: { traceComplete: false },
        plannedCoverage: {
          queryFamilies: { expected: ['limitationCritique'], covered: ['limitationCritique'], missing: [] },
          evidenceTypes: { expected: ['limitationCritique'], covered: ['limitationCritique'], missing: [] }
        },
        executedCoverage: {
          queryFamilies: { expected: ['limitationCritique'], covered: [], missing: ['limitationCritique'] },
          evidenceTypes: { expected: ['limitationCritique'], covered: [], missing: ['limitationCritique'] }
        },
        skippedRequiredCoverage: [
          {
            kind: 'queryFamily',
            value: 'limitationCritique',
            reason: 'budget-max-external-queries',
            intentId: 'intent-limits'
          }
        ],
        inconclusiveReasons: ['openrouter-not-configured'],
        traceComplete: false
      }
    });

    const benchmark = viewModel.details.find((detail) => detail.id === 'benchmark');

    expect(benchmark?.fields).toEqual(
      expect.arrayContaining([
        { label: 'Status', value: 'inconclusive' },
        { label: 'Evaluation mode', value: 'live' },
        { label: 'Provider health', value: 'unavailable' },
        {
          label: 'Skipped required coverage',
          value: 'queryFamily / limitationCritique / budget-max-external-queries'
        },
        { label: 'Inconclusive reasons', value: 'openrouter-not-configured' }
      ])
    );
    expect(benchmark?.items).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          label: 'queryFamily',
          title: 'limitationCritique',
          body: 'budget-max-external-queries',
          status: 'skipped'
        })
      ])
    );
  });
});

function traceBundle(runOverrides = {}): RadarRunTraceBundle {
  const portfolio = createRadarTracePortfolio(runOverrides);
  const project = portfolio.projects[0];
  const workspace = portfolio.workspacesByProjectId[project.id];
  const run = workspace.radarRuns[0];
  return {
    project,
    workspace,
    radar: workspace.radars[0],
    run,
    sourceHandles: workspace.sourceRegistry.handles,
    foundMaterials: workspace.foundMaterials,
    benchmarkReport: null,
    source: 'local'
  };
}
