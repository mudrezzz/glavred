import type { RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';

export type RadarTraceField = {
  label: string;
  value: string;
};

export type RadarTraceItem = {
  id: string;
  label: string;
  title: string;
  body: string;
  meta?: RadarTraceField[];
  status?: string;
};

export type RadarTraceDetail = {
  id: string;
  title: string;
  kicker: string;
  fields: RadarTraceField[];
  items: RadarTraceItem[];
  jsonPayload: unknown;
};

export type RadarTraceTimelineItem = {
  id: string;
  title: string;
  status: string;
  detailId: string;
  meta: string;
};

export type RadarRunTraceViewModel = {
  id: string;
  title: string;
  summary: RadarTraceField[];
  timeline: RadarTraceTimelineItem[];
  details: RadarTraceDetail[];
  initialDetailId: string;
};

type RadarTraceBudget = {
  usedOperations?: number;
  maxOperations?: number;
  usedExternalQueries?: number;
  maxExternalQueries?: number;
  usedUrlReads?: number;
  maxUrlReads?: number;
  usedFoundMaterials?: number;
  maxFoundMaterials?: number;
};

export function buildRadarRunTraceViewModel(bundle: RadarRunTraceBundle): RadarRunTraceViewModel {
  const rawResults = bundle.run.rawResults ?? [];
  const selected = bundle.run.selectedForRead ?? [];
  const rejected = bundle.run.rejectedBeforeRead ?? [];
  const warnings = bundle.run.warnings.length + bundle.run.errors.length + bundle.run.skippedReasons.length;
  const details = [
    overviewDetail(bundle),
    ...(bundle.run.searchPlan ? [searchPlanDetail(bundle)] : []),
    ...(bundle.run.searchPlan?.sourceStrategy || bundle.sourceHandles.length > 0 ? [sourceStrategyDetail(bundle)] : []),
    operationsDetail(bundle),
    ...(rawResults.length > 0 ? [rawResultsDetail(bundle)] : []),
    ...(selected.length > 0 || rejected.length > 0 ? [readSelectionDetail(bundle)] : []),
    ...(bundle.foundMaterials.length > 0 || bundle.run.foundMaterialIds.length > 0 ? [foundMaterialsDetail(bundle)] : []),
    ...(bundle.benchmarkReport ? [benchmarkDetail(bundle.benchmarkReport)] : []),
    ...(warnings > 0 ? [warningsDetail(bundle)] : []),
    rawDetail(bundle)
  ];
  const timeline = details.map((detail) => ({
    id: `timeline-${detail.id}`,
    title: detail.title,
    status: timelineStatus(detail),
    detailId: detail.id,
    meta: detail.kicker
  }));
  return {
    id: bundle.run.id,
    title: bundle.radar.title,
    summary: summaryFields(bundle),
    timeline,
    details,
    initialDetailId: details[0]?.id ?? ''
  };
}

function summaryFields(bundle: RadarRunTraceBundle): RadarTraceField[] {
  const run = bundle.run;
  const selected = run.selectedForRead?.length ?? 0;
  const rejected = run.rejectedBeforeRead?.length ?? 0;
  return [
    { label: 'Статус', value: run.status },
    { label: 'Проект', value: bundle.project.title },
    { label: 'Радар', value: bundle.radar.title },
    { label: 'Операции', value: String(run.operations.length) },
    { label: 'Сырые результаты', value: String(run.rawResults?.length ?? 0) },
    { label: 'Чтение', value: `${selected}/${rejected}` },
    { label: 'Материалы', value: String(bundle.foundMaterials.length) },
    { label: 'Источник', value: bundle.source }
  ];
}

function overviewDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const run = bundle.run;
  return {
    id: 'overview',
    title: 'Сводка запуска',
    kicker: 'RadarRun',
    fields: compactFields([
      ['Run ID', run.id],
      ['Project ID', bundle.project.id],
      ['Radar ID', bundle.radar.id],
      ['Status', run.status],
      ['Started', run.startedAt],
      ['Completed', run.completedAt],
      ['Warnings', run.warnings.length],
      ['Errors', run.errors.length],
      ['Budget', budgetValue(run.budget)]
    ]),
    items: [],
    jsonPayload: { project: bundle.project, radar: bundle.radar, run }
  };
}

function searchPlanDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const plan = bundle.run.searchPlan;
  return {
    id: 'search-plan',
    title: 'Карта поиска',
    kicker: plan ? plan.strategy : 'Search plan unavailable',
    fields: compactFields([
      ['Strategy', plan?.strategy],
      ['Language', plan?.language],
      ['Planner version', plan?.trace?.plannerVersion],
      ['Ownership boundary', plan?.trace?.ownershipBoundary],
      ['Queries', plan?.queries.length],
      ['Intents', plan?.intents?.length ?? 0],
      ['Skipped intents', plan?.skippedIntentDetails?.length ?? plan?.skippedIntents.length ?? 0]
    ]),
    items: [
      ...(plan?.intents ?? []).map((intent) => ({
        id: intent.id,
        label: intent.family,
        title: intent.label,
        body: [intent.evidenceType, intent.sourceHandleTitle, intent.rationale].filter(Boolean).join('\n'),
        status: intent.intentType,
        meta: compactFields([['Priority', intent.priority], ['Handle', intent.sourceHandleId]])
      })),
      ...(plan?.queries ?? []).map((query) => ({
        id: query.id,
        label: query.family ?? query.intent,
        title: query.label,
        body: query.query,
        status: query.evidenceType,
        meta: compactFields([['Intent', query.intentId ?? query.intent], ['Rationale', query.rationale]])
      })),
      ...(plan?.skippedIntentDetails ?? []).map((skip) => ({
        id: skip.id,
        label: skip.reason,
        title: skip.family ?? skip.intentType ?? skip.id,
        body: skip.rationale,
        status: 'skipped',
        meta: compactFields([['Intent', skip.intentId], ['Handle', skip.sourceHandleId]])
      }))
    ],
    jsonPayload: plan ?? { missing: true }
  };
}

function sourceStrategyDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const strategy = bundle.run.searchPlan?.sourceStrategy;
  return {
    id: 'source-strategy',
    title: 'Стратегия источников',
    kicker: strategy?.strategy ?? 'Source strategy unavailable',
    fields: compactFields([
      ['Searchable handles', strategy?.searchableSourceHandleIds?.length ?? 0],
      ['Direct-read handles', strategy?.directReadSourceHandleIds?.length ?? 0],
      ['Skipped sources', strategy?.skippedSources?.length ?? 0]
    ]),
    items: bundle.sourceHandles.map((handle) => ({
      id: handle.id,
      label: handle.type,
      title: handle.title,
      body: handle.locator || handle.notes || handle.status,
      status: handle.status,
      meta: compactFields([
        ['Obligation', handle.obligation],
        ['Search', handle.capabilities.canSearch],
        ['Read URL', handle.capabilities.canReadUrl]
      ])
    })),
    jsonPayload: { sourceStrategy: strategy ?? null, sourceHandles: bundle.sourceHandles }
  };
}

function operationsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  return {
    id: 'operations',
    title: 'Операции',
    kicker: `${bundle.run.operations.length} operations`,
    fields: compactFields([
      ['Succeeded', bundle.run.operations.filter((operation) => operation.status === 'succeeded').length],
      ['Skipped', bundle.run.operations.filter((operation) => operation.status === 'skipped').length],
      ['Failed', bundle.run.operations.filter((operation) => operation.status === 'failed').length]
    ]),
    items: bundle.run.operations.map((operation) => ({
      id: operation.id,
      label: operation.kind,
      title: operation.label,
      body: operation.error ?? operation.skippedReason ?? operation.target ?? '',
      status: operation.status,
      meta: compactFields([
        ['Handle', operation.sourceHandleId],
        ['Started', operation.startedAt],
        ['Completed', operation.completedAt],
        ['Materials', operation.foundMaterialIds.join(', ')]
      ])
    })),
    jsonPayload: bundle.run.operations
  };
}

function rawResultsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const rawResults = bundle.run.rawResults ?? [];
  return {
    id: 'raw-results',
    title: 'Сырые результаты',
    kicker: `${rawResults.length} raw results`,
    fields: compactFields([['Count', rawResults.length]]),
    items: rawResults.map((result) => ({
      id: result.id,
      label: result.domain,
      title: result.title,
      body: [result.url, result.snippet].filter(Boolean).join('\n'),
      status: `score ${result.score}`,
      meta: compactFields([['Query', result.queryId], ['Provider', result.provider], ['Duplicate key', result.duplicateKey]])
    })),
    jsonPayload: rawResults
  };
}

function readSelectionDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const selected = bundle.run.selectedForRead ?? [];
  const rejected = bundle.run.rejectedBeforeRead ?? [];
  return {
    id: 'read-selection',
    title: 'Отбор перед чтением',
    kicker: `${selected.length} selected / ${rejected.length} rejected`,
    fields: compactFields([['Selected reads', selected.length], ['Rejected before read', rejected.length]]),
    items: [
      ...selected.map((item) => ({
        id: `selected-${item.rawResultId}`,
        label: 'read',
        title: item.reason,
        body: item.url,
        status: `score ${item.score}`
      })),
      ...rejected.map((item) => ({
        id: `rejected-${item.rawResultId}`,
        label: 'skip',
        title: item.reason,
        body: item.url,
        status: `score ${item.score}`
      }))
    ],
    jsonPayload: { selectedForRead: selected, rejectedBeforeRead: rejected }
  };
}

function foundMaterialsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  return {
    id: 'found-materials',
    title: 'Найденные материалы',
    kicker: `${bundle.foundMaterials.length} materials`,
    fields: compactFields([['Found material ids', bundle.run.foundMaterialIds.join(', ')]]),
    items: bundle.foundMaterials.map((material) => ({
      id: material.id,
      label: material.type,
      title: material.title,
      body: [material.locator, material.summary || material.snippet].filter(Boolean).join('\n'),
      status: material.status,
      meta: compactFields([['Handle', material.sourceHandleId], ['Provenance', material.provenanceLabel], ['Warnings', material.warnings.join(', ')]])
    })),
    jsonPayload: bundle.foundMaterials
  };
}

function benchmarkDetail(report: NonNullable<RadarRunTraceBundle['benchmarkReport']>): RadarTraceDetail {
  const skippedRequired = report.skippedRequiredCoverage ?? [];
  return {
    id: 'benchmark',
    title: 'Benchmark verdict',
    kicker: report.status,
    fields: compactFields([
        ['Status', report.status],
        ['Scenario', report.scenarioId],
        ['Evaluation mode', report.evaluationMode],
        ['Provider health', report.providerHealth],
        ['Planned coverage', coverageSummary(report.plannedCoverage ?? report.coverage)],
        ['Executed coverage', coverageSummary(report.executedCoverage)],
        ['Skipped required coverage', skippedCoverageSummary(skippedRequired)],
        ['Verdict impact', verdictImpact(report)],
        ['Trace complete', report.traceComplete],
        ['Missing expectations', report.missingExpectations?.join(', ')],
        ['Inconclusive reasons', report.inconclusiveReasons?.join(', ')],
        ['Noise hits', report.unacceptableNoiseHits?.join(', ')],
        ['Warnings', report.warnings?.join(', ')]
      ]),
    items: skippedRequired.map((item, index) => ({
      id: `skipped-required-${index}`,
      label: String(item.kind ?? 'skipped'),
      title: String(item.value ?? 'required coverage'),
      body: String(item.reason ?? ''),
      status: 'skipped',
      meta: compactFields([['Intent', item.intentId]])
    })),
    jsonPayload: report
  };
}

function warningsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  return {
    id: 'warnings-errors',
    title: 'Предупреждения и ошибки',
    kicker: `${bundle.run.warnings.length} warnings / ${bundle.run.errors.length} errors`,
    fields: compactFields([['Warnings', bundle.run.warnings.length], ['Errors', bundle.run.errors.length], ['Skipped reasons', bundle.run.skippedReasons.join(', ')]]),
    items: [
      ...bundle.run.warnings.map((warning, index) => ({ id: `warning-${index}`, label: 'warning', title: warning, body: '', status: 'warning' })),
      ...bundle.run.errors.map((error, index) => ({ id: `error-${index}`, label: 'error', title: error, body: '', status: 'failed' }))
    ],
    jsonPayload: { warnings: bundle.run.warnings, errors: bundle.run.errors, skippedReasons: bundle.run.skippedReasons }
  };
}

function rawDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  return {
    id: 'raw-json',
    title: 'Raw JSON',
    kicker: 'Compatibility payload',
    fields: [],
    items: [],
    jsonPayload: bundle
  };
}

function budgetValue(value: RadarTraceBudget): string {
  return [
    `operations ${value.usedOperations ?? 0}/${value.maxOperations ?? 0}`,
    `queries ${value.usedExternalQueries ?? 0}/${value.maxExternalQueries ?? 0}`,
    `reads ${value.usedUrlReads ?? 0}/${value.maxUrlReads ?? 0}`,
    `materials ${value.usedFoundMaterials ?? 0}/${value.maxFoundMaterials ?? 0}`
  ].join('\n');
}

function timelineStatus(detail: RadarTraceDetail): string {
  if (detail.id === 'warnings-errors' && detail.items.some((item) => item.label === 'error')) return 'failed';
  if (detail.id === 'warnings-errors' && detail.items.length > 0) return 'warn';
  if (detail.items.some((item) => item.status === 'failed')) return 'failed';
  if (detail.items.some((item) => item.status === 'skipped')) return 'partial';
  return 'succeeded';
}

function compactFields(entries: Array<[string, unknown]>): RadarTraceField[] {
  return entries
    .map(([label, value]) => ({ label, value: displayValue(value) }))
    .filter((field) => field.value.length > 0);
}

export function displayRadarTraceValue(value: unknown): string {
  return displayValue(value);
}

function displayValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).filter(Boolean).join('\n');
  return JSON.stringify(value, null, 2);
}

function coverageSummary(value: unknown): string {
  if (!value || typeof value !== 'object') return '';
  const coverage = value as Record<string, unknown>;
  const queryFamilies = coverage.queryFamilies as Record<string, unknown> | undefined;
  const evidenceTypes = coverage.evidenceTypes as Record<string, unknown> | undefined;
  return [
    `families ${coverageCount(queryFamilies)}`,
    `evidence ${coverageCount(evidenceTypes)}`,
    missingSummary(queryFamilies, 'missing families'),
    missingSummary(evidenceTypes, 'missing evidence')
  ].filter(Boolean).join('\n');
}

function coverageCount(value: Record<string, unknown> | undefined): string {
  const covered = Array.isArray(value?.covered) ? value.covered.length : 0;
  const expected = Array.isArray(value?.expected) ? value.expected.length : 0;
  return `${covered}/${expected}`;
}

function missingSummary(value: Record<string, unknown> | undefined, label: string): string {
  const missing = Array.isArray(value?.missing) ? value.missing.map((item) => String(item)).filter(Boolean) : [];
  return missing.length > 0 ? `${label}: ${missing.join(', ')}` : '';
}

function skippedCoverageSummary(items: Array<Record<string, unknown>>): string {
  if (items.length === 0) return '';
  return items
    .map((item) => [item.kind, item.value, item.reason].filter(Boolean).join(' / '))
    .join('\n');
}

function verdictImpact(report: NonNullable<RadarRunTraceBundle['benchmarkReport']>): string {
  const skipped = report.skippedRequiredCoverage ?? [];
  if (report.status === 'warning' && skipped.length > 0) {
    return 'Required coverage was planned but not executed.';
  }
  if (report.status === 'passed') return 'Required coverage was executed.';
  if (report.status === 'failed') return 'Required quality expectations were missed.';
  if (report.status === 'inconclusive') return 'Provider/runtime state prevents a fair quality verdict.';
  return '';
}
