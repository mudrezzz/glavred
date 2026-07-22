import type {
  RadarDefinition,
  RadarEditorialFilterMode,
  RadarEditorialFilterRule,
  RadarSearchRule,
  RadarSearchSource,
  RadarSourceDiscoveryMode,
  SignalFilterEvaluationStatus,
  SignalFilterStatus,
  SignalReviewStatus,
  SignalUtilityDimensionStatus,
  SignalUtilityRecommendation
} from '../../domain/editorialWorkspace';

export type SignalsTab = 'radars' | 'signals' | 'candidates';

export function formatDate(value: string): string {
  return value.slice(0, 10);
}

export function duplicateRiskLabel(risk: string): string {
  if (risk === 'high') return 'высокий';
  if (risk === 'medium') return 'средний';
  return 'низкий';
}

export function SummaryItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="summary-item">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}

export function radarSourceTypeLabel(sourceType: RadarDefinition['sourceType']): string {
  if (sourceType === 'authorMemory') return 'Память';
  if (sourceType === 'archive') return 'Архив';
  if (sourceType === 'externalSource') return 'Внешний источник';
  return 'Ручной ввод';
}

export function radarAcceptancePolicyLabel(policy: RadarDefinition['acceptancePolicy']): string {
  if (policy === 'automatic') return 'Автоматически';
  if (policy === 'automaticWithReview') return 'Авто + review';
  return 'Вручную';
}

export function radarTriggerModeLabel(mode: RadarDefinition['triggerMode']): string {
  if (mode === 'scheduled') return 'По расписанию';
  if (mode === 'deficitDriven') return 'По дефициту плана';
  return 'Вручную';
}

export function radarStatusLabel(status: RadarDefinition['status']): string {
  if (status === 'active') return 'Активен';
  if (status === 'paused') return 'Пауза';
  return 'Нужен review';
}

export function radarRuleOperatorLabel(operator: RadarSearchRule['operator']): string {
  return operator === 'or' ? 'ИЛИ' : 'И';
}

export function radarSearchSourceTypeLabel(type: RadarSearchSource['type']): string {
  const labels: Record<RadarSearchSource['type'], string> = {
    authorArchive: 'Архив автора',
    externalUrl: 'URL',
    mcpServer: 'MCP',
    api: 'API',
    searchKeywords: 'Ключевые слова',
    manualSource: 'Ручной источник',
    socialProfile: 'Соцпрофиль',
    document: 'Документ',
    openWeb: 'Открытый web'
  };

  return labels[type] ?? type;
}

export function radarSourceDiscoveryModeLabel(mode: RadarSourceDiscoveryMode | undefined): string {
  if (mode === 'specifiedOnly') return 'Только указанные';
  if (mode === 'specifiedAndAdditional') return 'Указанные + дополнительные';
  return 'Самостоятельный поиск';
}

export function radarFilterDimensionLabel(dimension: RadarEditorialFilterRule['dimension']): string {
  const labels: Record<RadarEditorialFilterRule['dimension'], string> = {
    author: 'Автор',
    audience: 'Аудитория',
    positioning: 'Позиция',
    goals: 'Цели',
    forbiddenTopics: 'Запреты',
    topics: 'Темы',
    evidenceStrength: 'Сила доказательств',
    factualSpecificity: 'Фактическая конкретность',
    sourceCredibility: 'Надежность источника',
    mechanism: 'Механизм',
    observableOutcome: 'Наблюдаемый результат',
    actionability: 'Практическая применимость',
    novelty: 'Новизна',
    productiveTension: 'Продуктивное противоречие',
    freshness: 'Свежесть',
    duplicationRisk: 'Риск повтора',
    promotionalNoise: 'Рекламность и AI-шум'
  };
  return labels[dimension];
}

export function signalUtilityRecommendationLabel(value: SignalUtilityRecommendation): string {
  if (value === 'recommended') return 'Рекомендуется';
  if (value === 'reviewWithCaution') return 'Проверить с осторожностью';
  if (value === 'notRecommended') return 'Не рекомендуется';
  return 'Оценка не завершена';
}

export function signalUtilityDimensionStatusLabel(value: SignalUtilityDimensionStatus): string {
  if (value === 'matched') return 'Подтверждено';
  if (value === 'partial') return 'Частично';
  if (value === 'conflict') return 'Конфликт';
  return 'Не доказано';
}

export function signalUtilityDimensionLabel(value: string): string {
  const labels: Record<string, string> = {
    evidenceStrength: 'Сила доказательств',
    factualSpecificity: 'Фактическая конкретность',
    sourceCredibility: 'Надежность источника',
    mechanism: 'Механизм',
    observableOutcome: 'Наблюдаемый результат',
    actionability: 'Практическая применимость',
    topicAffinity: 'Соответствие темам',
    authorFit: 'Соответствие автору',
    audienceValue: 'Ценность для аудитории',
    positioningContribution: 'Вклад в позиционирование',
    projectGoalContribution: 'Вклад в цели проекта',
    novelty: 'Новизна',
    productiveTension: 'Продуктивное противоречие',
    freshness: 'Свежесть',
    duplicationRisk: 'Риск повтора',
    promotionalNoise: 'Рекламность и AI-шум',
    prohibitedContent: 'Запрещенный контент'
  };
  return labels[value] ?? value;
}

export function radarFilterModeLabel(mode: RadarEditorialFilterMode): string {
  const labels: Record<RadarEditorialFilterMode, string> = {
    mustMatch: 'Должно совпадать',
    shouldMatch: 'Желательно совпадение',
    mustNotMatch: 'Должно отсекаться',
    seekTension: 'Искать напряжение'
  };
  return labels[mode];
}

export function signalFilterStatusLabel(status: SignalFilterStatus | undefined): string {
  if (status === 'passed') return 'Прошел';
  if (status === 'warning') return 'С предупреждением';
  return 'Отсечен';
}

export function signalFilterEvaluationLabel(status: SignalFilterEvaluationStatus): string {
  if (status === 'passed') return 'OK';
  if (status === 'warning') return 'Внимание';
  if (status === 'tension') return 'Напряжение';
  return 'Отсечено';
}

export function signalReviewStatusLabel(status: SignalReviewStatus | undefined): string {
  if (status === 'candidate') return 'На проверке';
  if (status === 'approved') return 'Утвержден';
  if (status === 'rejected') return 'Отклонен';
  if (status === 'archived') return 'В архиве';
  if (status === 'corrected') return 'Исправлен';
  return 'Новый';
}
