import type { WorkspaceState } from '../workspace/types';
import type {
  RadarDefinition,
  RadarEditorialFilterDimension,
  RadarEditorialFilterMode,
  RadarEditorialFilterRule,
  RadarSearchSourceType,
  SignalFilterEvaluation,
  SignalFilterEvaluationStatus,
  SignalFilterStatus,
  SourceSignal,
} from './types';

// Radar and signal transitions are local-first stubs until real radar execution exists.
export function approveSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'approved' };
}

export function rejectSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'rejected' };
}

export function archiveSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'archived' };
}

export function createDefaultRadarEditorialFilters(
  radarId: string,
  enabledDimensions: RadarEditorialFilterDimension[] = []
): RadarEditorialFilterRule[] {
  const defaults: Array<{
    dimension: RadarEditorialFilterDimension;
    mode: RadarEditorialFilterMode;
    instruction: string;
  }> = [
    {
      dimension: 'author',
      mode: 'mustMatch',
      instruction: 'Материал должен быть совместим с образом автора и его исследовательской оптикой.'
    },
    {
      dimension: 'audience',
      mode: 'shouldMatch',
      instruction: 'Материал должен быть полезен AI PM, founders, CPO или B2B SaaS командам.'
    },
    {
      dimension: 'positioning',
      mode: 'mustMatch',
      instruction: 'Материал должен поддерживать позицию: меньше demo magic, больше workflow, evals, trust loop и adoption.'
    },
    {
      dimension: 'goals',
      mode: 'shouldMatch',
      instruction: 'Материал должен помогать собирать аудиторию вокруг практики AI-B2B productization.'
    },
    {
      dimension: 'forbiddenTopics',
      mode: 'mustNotMatch',
      instruction: 'Отсекать AI-хайп без продуктовой механики, гарантированные прогнозы и магическое мышление про модели.'
    },
    {
      dimension: 'topics',
      mode: 'mustMatch',
      instruction: 'Материал должен ложиться хотя бы на одну активную тему редакционной модели.'
    }
  ];

  return defaults.map((item) => ({
    id: `filter-${radarId}-${item.dimension}`,
    dimension: item.dimension,
    enabled: enabledDimensions.includes(item.dimension),
    mode: item.mode,
    instruction: item.instruction
  }));
}

export function isRadarSourceConfigurationValid(radar: RadarDefinition): boolean {
  return radar.sourceDiscoveryMode !== 'specifiedOnly' || radar.sources.length > 0;
}

function signalText(signal: SourceSignal): string {
  return [
    signal.title,
    signal.type,
    signal.source,
    signal.summary,
    signal.rawNote,
    signal.searchNote ?? '',
    signal.suggestedValue ?? '',
    signal.authorCorrection ?? '',
    ...(signal.evidence ?? []).flatMap((item) => [item.sourceTitle, item.quote, item.summary])
  ]
    .join(' ')
    .toLowerCase();
}

function dimensionKeywords(workspace: WorkspaceState, dimension: RadarEditorialFilterDimension): string[] {
  const topicTitles = workspace.topics.map((topic) => topic.title.toLowerCase());
  const model = workspace.editorialModel;
  const map: Record<RadarEditorialFilterDimension, string[]> = {
    author: ['исслед', 'product', 'workflow', 'практик', 'trade-off', model.author.toLowerCase()],
    audience: ['pm', 'founder', 'cpo', 'b2b', 'enterprise', 'audience', model.audience.toLowerCase()],
    positioning: ['workflow', 'eval', 'trust', 'adoption', 'rollout', 'demo', 'позици', model.positioning.toLowerCase()],
    goals: ['audience', 'productization', 'practice', 'принцип', 'опыт', ...model.goals.map((goal) => goal.toLowerCase())],
    forbiddenTopics: ['hype', 'магич', 'universal', 'гарантир', 'model-first', ...model.forbiddenTopics.map((topic) => topic.toLowerCase())],
    topics: [...topicTitles, 'discovery', 'eval', 'quality', 'trust', 'gtm', 'adoption', 'workflow']
  };
  return map[dimension];
}

function hasAnyKeyword(text: string, keywords: string[]): boolean {
  return keywords.some((keyword) => keyword && text.includes(keyword));
}

function evaluateFilter(
  signal: SourceSignal,
  filter: RadarEditorialFilterRule,
  workspace: WorkspaceState
): SignalFilterEvaluation {
  const text = signalText(signal);
  const matched = hasAnyKeyword(text, dimensionKeywords(workspace, filter.dimension));
  const mode = filter.mode;

  if (mode === 'mustNotMatch') {
    return {
      filterId: filter.id,
      dimension: filter.dimension,
      status: matched ? 'failed' : 'passed',
      score: matched ? 0.25 : 0.92,
      summary: matched
        ? 'Сигнал похож на материал, который фильтр просит отсечь.'
        : 'Сигнал не попал в запрещенную область фильтра.',
      evidence: filter.instruction
    };
  }

  if (mode === 'seekTension') {
    return {
      filterId: filter.id,
      dimension: filter.dimension,
      status: matched ? 'tension' : 'warning',
      score: matched ? 0.72 : 0.54,
      summary: matched
        ? 'Есть продуктивное напряжение с выбранной редакционной рамкой.'
        : 'Напряжение задано фильтром, но в сигнале пока мало опор.',
      evidence: filter.instruction
    };
  }

  if (mode === 'shouldMatch') {
    return {
      filterId: filter.id,
      dimension: filter.dimension,
      status: matched ? 'passed' : 'warning',
      score: matched ? 0.82 : 0.58,
      summary: matched
        ? 'Сигнал достаточно хорошо совпадает с мягким фильтром.'
        : 'Сигнал можно оставить на review, но связь с фильтром слабая.',
      evidence: filter.instruction
    };
  }

  return {
    filterId: filter.id,
    dimension: filter.dimension,
    status: matched ? 'passed' : 'failed',
    score: matched ? 0.9 : 0.34,
    summary: matched
      ? 'Сигнал проходит обязательный фильтр.'
      : 'Сигнал не показывает достаточной связи с обязательным фильтром.',
    evidence: filter.instruction
  };
}

export function evaluateSignalAgainstRadarFilters(
  signal: SourceSignal,
  radar: RadarDefinition,
  workspace: WorkspaceState
): SourceSignal {
  const evaluations = (radar.filters ?? createDefaultRadarEditorialFilters(radar.id))
    .filter((filter) => filter.enabled)
    .map((filter) => evaluateFilter(signal, filter, workspace));

  const filterStatus: SignalFilterStatus =
    evaluations.some((evaluation) => evaluation.status === 'failed')
      ? 'rejected'
      : evaluations.some((evaluation) => evaluation.status === 'warning' || evaluation.status === 'tension')
        ? 'warning'
        : 'passed';

  return {
    ...signal,
    filterEvaluations: evaluations,
    filterStatus
  };
}

export function createRadarDraft(): RadarDefinition {
  const id = `radar-custom-${Date.now()}`;
  return {
    id,
    title: '',
    sourceType: 'manualResearch',
    scope: '',
    rules: [],
    sources: [],
    sourceDiscoveryMode: 'autonomous',
    filters: createDefaultRadarEditorialFilters(id),
    acceptancePolicy: 'manual',
    triggerMode: 'manual',
    status: 'active',
    lastRunAt: '',
    notes: ''
  };
}

export function addRadar(radars: RadarDefinition[], radar: RadarDefinition): RadarDefinition[] {
  return [...radars, radar];
}

export function updateRadar(radars: RadarDefinition[], radar: RadarDefinition): RadarDefinition[] {
  return radars.map((item) => (item.id === radar.id ? radar : item));
}

export function deleteRadar(radars: RadarDefinition[], radarId: string): RadarDefinition[] {
  return radars.filter((radar) => radar.id !== radarId);
}

export function toggleRadarStatus(radar: RadarDefinition): RadarDefinition {
  return {
    ...radar,
    status: radar.status === 'active' ? 'paused' : 'active'
  };
}

export function correctSignal(signal: SourceSignal, patch: Partial<SourceSignal>): SourceSignal {
  return {
    ...signal,
    ...patch,
    reviewStatus: 'corrected',
    authorCorrection:
      patch.authorCorrection ??
      signal.authorCorrection ??
      'Автор скорректировал связку сигнала с темой, фабулой или ценностью.'
  };
}
