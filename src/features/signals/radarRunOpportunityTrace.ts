import type { RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';
import type { RadarSearchQuery } from '../../domain/upstream-search/types';

const roleLabels: Record<string, string> = {
  required: 'Обязательно найти',
  optional: 'Желательно найти',
  exclusion: 'Исключать как шум',
  tension: 'Искать напряжение'
};

const failureLabels: Record<string, string> = {
  providerSearch: 'Поиск у провайдера',
  triage: 'Отбор результатов',
  read: 'Чтение источников',
  signalExtraction: 'Извлечение сигналов',
  signalScoring: 'Оценка редакционной полезности'
};

const deliveryStageLabels: Record<string, string> = {
  planned: 'Запланировано',
  queryExecuted: 'Запрос выполнен',
  resultFound: 'Результат найден',
  selectedForRead: 'Выбрано для чтения',
  readableEvidence: 'Материал прочитан',
  usedBySignal: 'Доказательство использовано сигналом',
  corroborated: 'Подтверждено независимым материалом'
};

const deliveryReasonLabels: Record<string, string> = {
  'provider-search-not-executed': 'Поисковый запрос не был выполнен',
  'no-result-found': 'Поиск не вернул результатов',
  'evidence-target-not-supported': 'Результаты не поддерживают требуемый тип доказательства',
  'below-quality-floor': 'Результаты не прошли минимальный порог качества',
  'url-read-budget': 'Результат не поместился в бюджет чтения',
  'not-selected-for-read': 'Результат уступил более сильным материалам',
  'read-failed': 'Материал не удалось прочитать',
  'evidence-not-used-by-review-eligible-signal': 'Прочитанный материал не дал подходящего сигнала',
  'corroboration-not-found': 'Независимое подтверждение не найдено'
};

export function searchRequirementsTraceDetail(bundle: RadarRunTraceBundle) {
  const plan = bundle.run.searchPlan;
  const profile = plan?.requirementProfile;
  const uncovered = new Map(
    (plan?.uncoveredRequiredSearchRequirements ?? []).map((item) => [item.requirementId, item.reason])
  );
  const queryByRequirement = new Map<string, RadarSearchQuery[]>();
  const coverageByRequirement = new Map(
    (bundle.run.searchOpportunityCoverage?.requirementCoverage ?? [])
      .map((item) => [item.requirementId, item])
  );
  for (const query of plan?.queries ?? []) {
    for (const requirementId of query.requirementIds ?? []) {
      queryByRequirement.set(requirementId, [...(queryByRequirement.get(requirementId) ?? []), query]);
    }
  }
  return {
    id: 'search-requirements',
    title: 'Что требовалось найти',
    kicker: 'Фильтры → требования → запросы',
    lifecycleStatus: uncovered.size > 0 ? 'partial' : 'succeeded',
    fields: [
      { label: 'Требований', value: String(profile?.requirements.length ?? 0) },
      { label: 'Не применимо к поиску', value: String(profile?.notSearchApplicable.length ?? 0) },
      { label: 'Не покрыто', value: String(uncovered.size) }
    ],
    items: [
      ...(profile?.requirements ?? []).map((requirement) => {
        const queries = queryByRequirement.get(requirement.id) ?? [];
        const coverage = coverageByRequirement.get(requirement.id);
        return {
          id: `search-requirement-${requirement.id}`,
          label: roleLabels[requirement.role] ?? requirement.role,
          title: requirement.title,
          body: requirement.statement,
          status: uncovered.has(requirement.id)
            ? 'skipped'
            : coverage?.delivered
              ? 'succeeded'
              : coverage
                ? 'partial'
                : queries.length > 0 ? 'planned' : 'skipped',
          meta: [
            { label: 'Режим', value: requirement.mode },
            { label: 'Цель доказательства', value: requirement.evidenceTypes.join(', ') || 'не задана' },
            { label: 'Запросы', value: queries.map((query) => query.query).join(' · ') || uncovered.get(requirement.id) || 'не требуется' },
            ...(coverage ? [
              { label: 'Доставка доказательства', value: deliveryStageLabels[coverage.furthestStage] ?? coverage.furthestStage },
              { label: 'Материалы', value: String(coverage.materialIds.length) },
              { label: 'Сигналы', value: String(coverage.signalIds.length) },
              ...(coverage.stopReason ? [{
                label: 'Почему остановилось',
                value: deliveryReasonLabels[coverage.stopReason] ?? coverage.stopReason
              }] : [])
            ] : [])
          ]
        };
      }),
      ...(profile?.notSearchApplicable ?? []).map((item) => ({
        id: `search-not-applicable-${item.filterId}`,
        label: 'Только для оценки',
        title: item.dimension,
        body: 'Эта настройка применяется после извлечения сигнала и не подменяет поисковое доказательство.',
        status: 'notApplicable',
        meta: [{ label: 'Причина', value: item.reason }]
      }))
    ],
    jsonPayload: { requirementProfile: profile, uncovered: plan?.uncoveredRequiredSearchRequirements ?? [] }
  };
}

export function searchOpportunityTraceDetail(bundle: RadarRunTraceBundle) {
  const report = bundle.run.searchOpportunityCoverage;
  const counts = report?.counts ?? {};
  const firstFailure = report?.firstFailureStage ? failureLabels[report.firstFailureStage] ?? report.firstFailureStage : 'Нет';
  return {
    id: 'search-opportunity-coverage',
    title: 'Полезный выход',
    kicker: 'Материалы → сигналы → редакционная рекомендация',
    lifecycleStatus: report?.status ?? 'notRun',
    fields: [
      { label: 'Статус', value: report?.status ?? 'Нет данных' },
      { label: 'Прочитано материалов', value: String(counts.readableMaterialCount ?? 0) },
      { label: 'Извлечено сигналов', value: String(counts.signalCount ?? 0) },
      { label: 'Можно рассматривать', value: String(counts.reviewEligibleCount ?? 0) },
      { label: 'Не рекомендовано', value: String(counts.notRecommendedCount ?? 0) },
      { label: 'Первый проблемный этап', value: firstFailure }
    ],
    items: [
      {
        id: 'useful-yield-summary',
        label: 'Результат',
        title: `${report?.reviewEligibleYield.count ?? 0} из ${report?.reviewEligibleYield.denominator ?? 0} сигналов можно передать редактору`,
        body: report?.reasonCodes.join(' · ') || 'Сквозная диагностика недоступна для этого legacy-запуска.',
        status: report?.status,
        meta: [
          { label: 'Покрытые семейства', value: report?.familyCoverage.executed.join(', ') || 'нет' },
          { label: 'Рекомендации', value: Object.entries(report?.recommendationDistribution ?? {}).map(([key, value]) => `${key}: ${value}`).join(' · ') || 'нет' }
        ]
      },
      ...(report?.remediation ?? []).map((item, index) => ({
        id: `useful-yield-remediation-${index}`,
        label: 'Следующее действие',
        title: firstFailure,
        body: item
      }))
    ],
    jsonPayload: report
  };
}
