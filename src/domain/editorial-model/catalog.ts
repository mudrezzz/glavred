import { clampPercent } from '../shared/numbers';
import type { WeightRange } from '../shared/types';
import type {
  CompatibleTopicFabula,
  Fabula,
  Topic,
  TopicFabulaMatrixEntry,
  TopicFabulaWarning,
} from './types';

// Topic/fabula catalog transitions preserve matrix compatibility and advisory weights.
export function normalizeWeightRange(range: WeightRange): WeightRange {
  const min = clampPercent(range.min);
  const max = clampPercent(range.max);

  return min <= max ? { min, max } : { min: max, max: min };
}

export function createTopicDraft(): Topic {
  return {
    id: `topic-custom-${Date.now()}`,
    title: '',
    description: '',
    purpose: '',
    audienceValue: '',
    authorStance: '',
    rules: [],
    forbiddenAngles: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function createFabulaDraft(): Fabula {
  return {
    id: `fabula-custom-${Date.now()}`,
    title: '',
    description: '',
    dramaturgy: '',
    structure: [],
    proofRequirements: [],
    rules: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function addTopic(topics: Topic[], topic: Topic): Topic[] {
  return [...topics, { ...topic, weightRange: normalizeWeightRange(topic.weightRange) }];
}

export function addFabula(fabulas: Fabula[], fabula: Fabula): Fabula[] {
  return [...fabulas, { ...fabula, weightRange: normalizeWeightRange(fabula.weightRange) }];
}

export function deleteTopic(
  topics: Topic[],
  matrix: TopicFabulaMatrixEntry[],
  topicId: string
): { topics: Topic[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    topics: topics.filter((topic) => topic.id !== topicId),
    matrix: matrix.filter((entry) => entry.topicId !== topicId)
  };
}

export function deleteFabula(
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[],
  fabulaId: string
): { fabulas: Fabula[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    fabulas: fabulas.filter((fabula) => fabula.id !== fabulaId),
    matrix: matrix.filter((entry) => entry.fabulaId !== fabulaId)
  };
}

export function createDefaultTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[]
): TopicFabulaMatrixEntry[] {
  return topics.flatMap((topic) =>
    fabulas.map((fabula) => ({
      topicId: topic.id,
      fabulaId: fabula.id,
      enabled: true
    }))
  );
}

export function completeTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaMatrixEntry[] {
  const existing = new Map(matrix.map((entry) => [`${entry.topicId}:${entry.fabulaId}`, entry.enabled]));

  return topics.flatMap((topic) =>
    fabulas.map((fabula) => {
      const key = `${topic.id}:${fabula.id}`;

      return {
        topicId: topic.id,
        fabulaId: fabula.id,
        enabled: existing.get(key) ?? true
      };
    })
  );
}

export function isTopicFabulaEnabled(
  matrix: TopicFabulaMatrixEntry[],
  topicId: string,
  fabulaId: string
): boolean {
  return matrix.find((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId)?.enabled ?? true;
}

export function selectCompatibleTopicFabula(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): CompatibleTopicFabula | null {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');

  for (const topic of activeTopics) {
    const fabula = activeFabulas.find((item) => isTopicFabulaEnabled(matrix, topic.id, item.id));

    if (fabula) {
      return { topic, fabula };
    }
  }

  return null;
}

export function getTopicFabulaWarnings(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaWarning[] {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');
  const topicWarnings = activeTopics
    .filter((topic) => !activeFabulas.some((fabula) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((topic) => ({
      targetType: 'topic' as const,
      targetId: topic.id,
      title: topic.title,
      message: 'У темы нет активных фабул. Она не попадет в план, пока матрица не включит хотя бы одну связку.'
    }));
  const fabulaWarnings = activeFabulas
    .filter((fabula) => !activeTopics.some((topic) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((fabula) => ({
      targetType: 'fabula' as const,
      targetId: fabula.id,
      title: fabula.title,
      message: 'Фабула не применима ни к одной активной теме. Она не будет использоваться в планировании.'
    }));

  return [...topicWarnings, ...fabulaWarnings];
}
