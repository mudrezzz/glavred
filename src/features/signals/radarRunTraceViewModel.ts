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
  lifecycleStatus?: string;
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
    ...(bundle.run.searchTriage ? [triageQualityDetail(bundle)] : []),
    ...(bundle.run.searchTriage?.duplicateGroups?.some((group) => group.candidateIds.length > 1)
      ? [duplicateGroupsDetail(bundle)]
      : []),
    ...(bundle.run.searchTriage ? [readPlanDetail(bundle)] : []),
    ...(selected.length > 0 || rejected.length > 0 ? [readSelectionDetail(bundle)] : []),
    ...(bundle.foundMaterials.length > 0 || bundle.run.foundMaterialIds.length > 0 ? [foundMaterialsDetail(bundle)] : []),
    ...(bundle.foundMaterials.some((material) => (material.contentFragments ?? []).length > 0)
      ? [evidenceFragmentsDetail(bundle)]
      : []),
    ...(bundle.run.signalExtraction ? [signalExtractionDetail(bundle)] : []),
    ...(bundle.run.signalScoring ? [signalScoringDetail(bundle)] : []),
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
    { label: 'Сигналы', value: String(bundle.sourceSignals.length) },
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
      ['Редакционный язык', plan?.languageContext?.editorialLanguage],
      ['Политика языков источников', plan?.languageContext?.sourceLanguagePolicy],
      ['Языки запросов', plan?.languageContext?.queryLanguages?.join(', ')],
      ['Пробелы языкового покрытия', plan?.languageCoverageGaps?.map((gap) => `${gap.language}: ${gap.reason}`).join('\n')],
      ['Причина fallback', plan?.languageContext?.fallbackReason],
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
        meta: compactFields([['Priority', intent.priority], ['Handle', intent.sourceHandleId], ['Язык запроса', intent.queryLanguage]])
      })),
      ...(plan?.queries ?? []).map((query) => ({
        id: query.id,
        label: query.family ?? query.intent,
        title: query.label,
        body: query.query,
        status: query.evidenceType,
        meta: compactFields([['Intent', query.intentId ?? query.intent], ['Язык запроса', query.queryLanguage], ['Rationale', query.rationale]])
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
        ['Materials', operation.foundMaterialIds?.join(', ')],
        ['Model', operation.selectedModel],
        ['Message chars', operation.messageCharCount],
        ['Provider usage', operation.providerUsage]
      ])
    })),
    jsonPayload: bundle.run.operations
  };
}

function triageQualityDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const triage = bundle.run.searchTriage!;
  return {
    id: 'triage-quality',
    title: 'Оценка результатов',
    kicker: triage.policyVersion,
    fields: compactFields([
      ['Кандидаты', triage.candidates.length],
      ['Порог качества', triage.readPlan.qualityFloor],
      ['Выбрано', triage.decisionCounts.selected],
      ['Ниже порога', triage.decisionCounts.rejected],
      ['Дубли', triage.decisionCounts.duplicate],
      ['Отложено бюджетом', triage.decisionCounts.deferredByBudget],
      ['Некорректные', triage.decisionCounts.invalid]
    ]),
    items: triage.candidates.map((candidate) => ({
      id: `triage-${candidate.id}`,
      label: candidate.family || 'результат',
      title: candidate.title,
      body: candidate.scores?.explanation || candidate.invalidReason || candidate.url,
      status: candidate.valid ? `score ${candidate.scores?.total ?? 0}` : 'invalid',
      meta: compactFields([
        ['Релевантность', candidate.scores?.relevance],
        ['Тип доказательства', candidate.scores?.evidenceFit],
        ['Проект', candidate.scores?.projectFit],
        ['Качество источника', candidate.scores?.sourceQuality],
        ['Новизна', candidate.scores?.novelty],
        ['Риск шума', candidate.scores?.noiseRisk],
        ['Домен', candidate.domain],
        ['Язык источника', candidate.sourceLanguage?.language],
        ['Уверенность языка', candidate.sourceLanguage?.confidence],
        ['Допущен политикой', candidate.sourceLanguage?.allowed],
        ['Решение по языку', candidate.sourceLanguage?.eligibilityReason],
        ['Сигналы', candidate.scores?.reasonCodes?.join(', ')]
      ])
    })),
    jsonPayload: {
      policyVersion: triage.policyVersion,
      candidates: triage.candidates,
      decisionCounts: triage.decisionCounts
    }
  };
}

function duplicateGroupsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const groups = bundle.run.searchTriage!.duplicateGroups;
  const duplicates = groups.filter((group) => group.candidateIds.length > 1);
  return {
    id: 'duplicate-groups',
    title: 'Группы дублей',
    kicker: `${duplicates.length} групп с дублями`,
    fields: compactFields([
      ['Все группы', groups.length],
      ['Группы с дублями', duplicates.length],
      ['Объединено результатов', duplicates.reduce((total, group) => total + group.rawResultIds.length, 0)]
    ]),
    items: duplicates.map((group) => ({
      id: group.id,
      label: group.matchReasons.join(', '),
      title: `${group.rawResultIds.length} результатов`,
      body: group.domains.join('\n'),
      status: 'duplicate',
      meta: compactFields([
        ['Представитель', group.representativeCandidateId],
        ['Запросы', group.queryIds.join(', ')],
        ['Направления', group.families.join(', ')],
        ['Типы доказательств', group.evidenceTypes.join(', ')]
      ])
    })),
    jsonPayload: groups
  };
}

function readPlanDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const triage = bundle.run.searchTriage!;
  const plan = triage.readPlan;
  return {
    id: 'read-plan',
    title: 'План чтения',
    kicker: `${plan.selectedCandidateIds.length}/${plan.maxReads} выбрано`,
    fields: compactFields([
      ['Лимит чтения', plan.maxReads],
      ['Порог качества', plan.qualityFloor],
      ['Обязательные направления', plan.requiredFamilies.join(', ')],
      ['Покрытые направления', plan.coveredFamilies.join(', ')],
      ['Пробелы покрытия', plan.readCoverageGaps.map((gap) => `${gap.family}: ${gap.reason}`).join('\n')],
      ['Успешно прочитано', triage.readOutcomes.filter((item) => item.readable).length],
      ['Ошибки чтения', triage.readOutcomes.filter((item) => item.status === 'failed').length]
    ]),
    items: [
      ...plan.decisions.map((decision) => ({
        id: `plan-${decision.rawResultId}`,
        label: decision.status || 'decision',
        title: decision.reason,
        body: decision.url,
        status: decision.status,
        meta: compactFields([
          ['Балл', decision.score],
          ['Направления', decision.families?.join(', ')],
          ['Доказательства', decision.evidenceTypes?.join(', ')],
          ['Группа дублей', decision.duplicateGroupId]
        ])
      })),
      ...triage.readOutcomes.map((outcome) => ({
        id: `outcome-${outcome.rawResultId}`,
        label: 'исход чтения',
        title: outcome.readable ? 'Страница прочитана' : 'Страница не прочитана',
        body: outcome.reason || outcome.materialId || '',
        status: outcome.status,
        meta: compactFields([
          ['Материал', outcome.materialId],
          ['Группа дублей', outcome.duplicateGroupId]
        ])
      }))
    ],
    jsonPayload: {
      readPlan: plan,
      readCoverage: triage.readCoverage,
      readCoverageGaps: triage.readCoverageGaps,
      readOutcomes: triage.readOutcomes
    }
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
      meta: compactFields([
        ['Query', result.queryId],
        ['Язык запроса', result.queryLanguage],
        ['Язык источника', result.sourceLanguage?.language],
        ['Уверенность языка', result.sourceLanguage?.confidence],
        ['Provider', result.provider],
        ['Duplicate key', result.duplicateKey]
      ])
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
    kicker: `${bundle.foundMaterials.length} материалов`,
    fields: compactFields([['Идентификаторы материалов', bundle.run.foundMaterialIds.join(', ')]]),
    items: bundle.foundMaterials.map((material) => ({
      id: material.id,
      label: material.type,
      title: material.title,
      body: [material.locator, material.summary || material.snippet].filter(Boolean).join('\n'),
      status: material.status,
      meta: compactFields([
        ['Источник', material.sourceHandleId],
        ['Происхождение', material.provenanceLabel],
        ['Предупреждения', material.warnings.join(', ')],
        ['Сырые результаты', material.discoveryTrace?.rawResultIds.join(', ')],
        ['Запросы', material.discoveryTrace?.queryIds.join(', ')],
        ['Направления', material.discoveryTrace?.families.join(', ')],
        ['Типы доказательств', material.discoveryTrace?.evidenceTypes.join(', ')],
        ['Группа дублей', material.discoveryTrace?.duplicateGroupId],
        ['Причина выбора', material.discoveryTrace?.decisionReason]
      ])
    })),
    jsonPayload: bundle.foundMaterials
  };
}

function evidenceFragmentsDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const fragments = bundle.foundMaterials.flatMap((material) =>
    (material.contentFragments ?? []).map((fragment) => ({ material, fragment }))
  );
  return {
    id: 'evidence-fragments',
    title: 'Доказательные фрагменты',
    kicker: `${fragments.length} сохранено`,
    fields: compactFields([
      ['Материалы с фрагментами', new Set(fragments.map((item) => item.material.id)).size],
      ['Всего фрагментов', fragments.length]
    ]),
    items: fragments.map(({ material, fragment }) => ({
      id: fragment.id,
      label: fragment.kind,
      title: material.title,
      body: fragment.text,
      status: 'evidence',
      meta: compactFields([
        ['Материал', material.id],
        ['Смещение', `${fragment.startChar}-${fragment.endChar}`],
        ['Hash', fragment.hash]
      ])
    })),
    jsonPayload: fragments.map(({ material, fragment }) => ({ materialId: material.id, ...fragment }))
  };
}

function signalExtractionDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const report = bundle.run.signalExtraction!;
  const attempts = report.providerAttempts ?? [];
  return {
    id: 'signal-extraction',
    title: 'Извлечение сигналов',
    kicker: `${report.status}, ревизия ${report.revision}`,
    lifecycleStatus: report.status,
    fields: compactFields([
      ['Статус', report.status],
      ['Ревизия', report.revision],
      ['Результат повтора', report.retryOutcome],
      ['Сохранены сигналы прошлой ревизии', report.preservedPreviousSignalIds?.length],
      ['Материалы обработаны', report.materialDecisions.length],
      ['Сигналы-кандидаты', bundle.sourceSignals.length],
      ['Полное покрытие решений', report.decisionCoverageComplete],
      ['Неразрешенные evidence handles', report.unresolvedEvidenceHandleCount],
      ['Grounding violations', report.groundingViolations?.length ?? 0],
      ['Попытки провайдера', attempts.length],
      ['Предупреждения', report.warnings?.join(', ')]
    ]),
    items: [
      ...bundle.sourceSignals.map((signal) => ({
        id: signal.id,
        label: signal.type,
        title: signal.title,
        body: [signal.summary, signal.uncertainty, ...(signal.limitations ?? [])].filter(Boolean).join('\n'),
        status: signal.confidence ?? 'candidate',
        meta: compactFields([
          ['Механизм', signal.mechanism],
          ['Результат', signal.outcome],
          ['Evidence refs', signal.evidenceRefs?.map((ref) => `${ref.materialId}/${ref.fragmentId}`).join('\n')]
        ])
      })),
      ...report.materialDecisions.map((decision) => ({
        id: `decision-${decision.materialId}`,
        label: 'решение по материалу',
        title: decision.materialId,
        body: decision.reasonCodes.join(', '),
        status: decision.decision,
        meta: compactFields([['Сигналы', decision.signalIds.join(', ')]])
      })),
      ...attempts.map((attempt, index) => ({
        id: `attempt-${index}`,
        label: String(attempt.attemptLabel ?? 'attempt'),
        title: String(attempt.model ?? 'provider'),
        body: String(attempt.error ?? ''),
        status: String(attempt.status ?? ''),
        meta: compactFields([
          ['AiRun', attempt.aiRunId],
          ['Размер сообщений', attempt.messageCharCount],
          ['Repair context', attempt.repairContextCharCount],
          ['Usage', attempt.providerUsage],
          ['Usage status', attempt.providerUsageStatus]
        ])
      }))
    ],
    jsonPayload: { report, sourceSignals: bundle.sourceSignals }
  };
}

function signalScoringDetail(bundle: RadarRunTraceBundle): RadarTraceDetail {
  const report = bundle.run.signalScoring!;
  const attempts = report.providerAttempts ?? [];
  return {
    id: 'signal-scoring',
    title: 'Редакционная полезность',
    kicker: `${report.status}, ревизия ${report.revision}`,
    lifecycleStatus: report.status,
    fields: compactFields([
      ['Статус', report.status],
      ['Ревизия', report.revision],
      ['Сигналов оценено', report.signalIds.length],
      ['Полное покрытие решений', report.decisionCoverageComplete],
      ['Неразрешенные настройки', report.unresolvedSettingRefCount],
      ['Неразрешенные доказательства', report.unresolvedEvidenceRefCount],
      ['Попытки провайдера', attempts.length]
    ]),
    items: [
      ...bundle.sourceSignals.map((signal) => ({
        id: `utility-${signal.id}`,
        label: signal.reviewStatus ?? 'candidate',
        title: signal.title,
        body: signalUtilityTraceSummary(signal),
        status: signal.utilityReport?.recommendation ?? 'unscored',
        meta: compactFields([
          ['Utility revision', signal.utilityRevision],
          ['Review revision', signal.reviewRevision],
          ['Review events', signal.reviewHistory?.length ?? 0],
          ['Relationship status', signal.relationshipReport?.status ?? signal.utilityReport?.relationshipReport?.status],
          ['Canonical signal', signal.relationshipReport?.canonicalSignalId ?? signal.utilityReport?.relationshipReport?.canonicalSignalId]
        ])
      })),
      ...attempts.map((attempt, index) => ({
        id: `scoring-attempt-${index}`,
        label: String(attempt.attemptLabel ?? 'attempt'),
        title: String(attempt.model ?? 'provider'),
        body: String(attempt.error ?? ''),
        status: String(attempt.status ?? ''),
        meta: compactFields([
          ['AiRun', attempt.aiRunId],
          ['Размер сообщений', attempt.messageCharCount],
          ['Repair context', attempt.repairContextCharCount],
          ['Usage', attempt.providerUsage]
        ])
      }))
    ],
    jsonPayload: { report, sourceSignals: bundle.sourceSignals }
  };
}

function signalUtilityTraceSummary(signal: RadarRunTraceBundle['sourceSignals'][number]): string {
  const utility = signal.utilityReport;
  if (!utility) return '';
  if (utility.version < 2) return utility.dimensions.map((item) => `${item.dimension}: ${item.summary}`).join('\n');
  return [
    ...(utility.radarCriteria ?? []).map((item) => `Радар · ${item.title} · ${item.verdict}: ${item.summary}`),
    ...(utility.projectCriteria ?? []).map((item) => `Проект · ${item.title} · ${item.verdict}: ${item.summary}`),
    ...(utility.qualityChecks ?? [])
      .filter((item) => item.applicable)
      .map((item) => `Система · ${item.title} · ${item.verdict}: ${item.summary}`),
    ...(utility.relationshipReport?.relations ?? [])
      .filter((item) => item.kind !== 'distinct')
      .map((item) => `Связь · ${item.kind}: ${item.summary}`)
  ].join('\n');
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
  if (detail.lifecycleStatus) return detail.lifecycleStatus;
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
