import type {
  EditorialRuleGroup,
  TopicFabulaMatrixEntry,
  WorkspaceState
} from '../../domain/editorialWorkspace';
import type { EditorialModelTab } from './types';

export const EDITORIAL_TABS: Array<[EditorialModelTab, string]> = [
  ['publisher', 'Издательство'],
  ['topics', 'Темы'],
  ['fabulas', 'Фабулы'],
  ['channels', 'Каналы'],
  ['matrix', 'Матрица']
];

export const RULE_SECTIONS: Array<{ title: string; description: string; groups: EditorialRuleGroup[] }> = [
  {
    title: 'Автор',
    description: 'Характеристики образа автора, которые потом должны проверяться в тексте.',
    groups: ['author']
  },
  {
    title: 'Аудитория',
    description: 'Кому пишем и какую пользу читатель должен получать.',
    groups: ['audience']
  },
  {
    title: 'Позиция',
    description: 'Что автор утверждает, с чем спорит и какую оптику удерживает.',
    groups: ['positioning']
  },
  {
    title: 'Стиль',
    description: 'Голос, язык, ритм, anti-AI-паттерны и запрещенные формулировки.',
    groups: ['styleVoice', 'styleLanguage', 'styleRhythm', 'antiAiPattern']
  },
  {
    title: 'Цели',
    description: 'Зачем существует блог и что должно поддерживаться каждым выпуском.',
    groups: ['goal']
  },
  {
    title: 'Запреты',
    description: 'Темы и формулировки, которые не должны появляться в публикациях.',
    groups: ['forbiddenTopic']
  }
];

export function editorialRuleGroupLabel(group: EditorialRuleGroup): string {
  const labels: Record<EditorialRuleGroup, string> = {
    author: 'Образ автора',
    audience: 'Аудитория',
    positioning: 'Позиция',
    styleVoice: 'Голос',
    styleLanguage: 'Язык',
    styleRhythm: 'Ритм',
    antiAiPattern: 'Anti-AI',
    goal: 'Цель',
    forbiddenTopic: 'Запрет'
  };
  return labels[group];
}

export function editorialTabLabel(tab: EditorialModelTab): string {
  if (tab === 'publisher') return 'Издательство';
  if (tab === 'topics') return 'Темы';
  if (tab === 'fabulas') return 'Фабулы';
  if (tab === 'channels') return 'Каналы';
  return 'Матрица';
}

export function getReferencedTopicIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.topicId, workspace.contentPlanItem?.topicId, workspace.postBrief?.topicId].filter(
      Boolean
    ) as string[]
  );
}

export function getReferencedFabulaIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.fabulaId, workspace.contentPlanItem?.fabulaId, workspace.postBrief?.fabulaId].filter(
      Boolean
    ) as string[]
  );
}

export function countCompatibleFabulas(topicId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.topicId === topicId && entry.enabled).length;
}

export function countCompatibleTopics(fabulaId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.fabulaId === fabulaId && entry.enabled).length;
}

export function isMatrixEnabled(topicId: string, fabulaId: string, matrix: TopicFabulaMatrixEntry[]): boolean {
  return matrix.some((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId && entry.enabled);
}

export function sameMatrix(left: TopicFabulaMatrixEntry[], right: TopicFabulaMatrixEntry[]): boolean {
  if (left.length !== right.length) return false;
  return left.every((entry) => {
    const other = right.find((item) => item.topicId === entry.topicId && item.fabulaId === entry.fabulaId);
    return other ? other.enabled === entry.enabled : false;
  });
}

export function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
