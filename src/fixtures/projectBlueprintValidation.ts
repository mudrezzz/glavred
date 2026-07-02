import type { WorkspaceState } from '../domain/workspace/types';

export interface ProjectBlueprintValidationIssue {
  code:
    | 'missingPublisherGroup'
    | 'channelAudienceDuplication'
    | 'mojibake'
    | 'topicFabulaDegeneracy'
    | 'missingReadyScenario';
  message: string;
  projectId?: string;
}

export interface ProjectBlueprintValidationInput {
  projectId: string;
  workspace: WorkspaceState;
  readyScenarioId?: string;
}

const REQUIRED_PUBLISHER_GROUPS = ['author', 'audience', 'goal'] as const;
const MOJIBAKE_MARKERS = [
  'Рђ',
  'Р‘',
  'Р’',
  'Р“',
  'Р”',
  'Р•',
  'Р–',
  'Р—',
  'Р',
  'Р™',
  'Рљ',
  'Р›',
  'Рњ',
  'Рќ',
  'Рћ',
  'Рџ',
  'Р ',
  'РЎ',
  'Рў',
  'РЈ',
  'Р¤',
  'РҐ',
  'Р¦',
  'Р§',
  'РЁ',
  'Р©',
  'Р­',
  'Р®',
  'РЇ',
  'СЃ',
  'С‚',
  'СЂ',
  'Сѓ',
  'С„',
  'С…',
  'С†',
  'С‡',
  'С€',
  'С‰',
  'СЊ',
  'С‹',
  'СЌ',
  'СЋ',
  'СЏ',
  'В«',
  'В»',
  'вЂ'
];
const QUESTION_MARK_REPLACEMENT_PATTERN = /\?{4,}/u;

export function validateProjectBlueprintSeed(input: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  return [
    ...validatePublisherContract(input),
    ...validateChannelBoundary(input),
    ...validateTextEncoding(input),
    ...validateTopicFabulaMatrix(input),
    ...validateReadyScenario(input)
  ];
}

export function validateProjectBlueprintSeeds(inputs: ProjectBlueprintValidationInput[]): ProjectBlueprintValidationIssue[] {
  return inputs.flatMap(validateProjectBlueprintSeed);
}

function validatePublisherContract({ projectId, workspace }: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  const activeGroups = new Set(workspace.editorialRules.filter((rule) => rule.status === 'active').map((rule) => rule.group));
  return REQUIRED_PUBLISHER_GROUPS
    .filter((group) => !activeGroups.has(group))
    .map((group) => ({
      code: 'missingPublisherGroup' as const,
      projectId,
      message: `${projectId} is missing active Publisher rule group "${group}".`
    }));
}

function validateChannelBoundary({ projectId, workspace }: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  return workspace.publicationChannels
    .filter((channel) => typeof channel.audience === 'string' && channel.audience.trim().length > 0)
    .map((channel) => ({
      code: 'channelAudienceDuplication' as const,
      projectId,
      message: `${projectId} channel "${channel.id}" duplicates project audience.`
    }));
}

function validateTextEncoding({ projectId, workspace }: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  const text = JSON.stringify(workspace);
  if (!QUESTION_MARK_REPLACEMENT_PATTERN.test(text) && !MOJIBAKE_MARKERS.some((marker) => text.includes(marker))) return [];
  return [{
    code: 'mojibake',
    projectId,
    message: `${projectId} contains mojibake or question-mark replacement text.`
  }];
}

function validateTopicFabulaMatrix({ projectId, workspace }: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  const activeTopicIds = workspace.topics.filter((topic) => topic.status === 'active').map((topic) => topic.id);
  const activeFabulaIds = workspace.fabulas.filter((fabula) => fabula.status === 'active').map((fabula) => fabula.id);
  if (activeTopicIds.length < 2 || activeFabulaIds.length < 2) return [];

  const enabledPairs = workspace.topicFabulaMatrix.filter((entry) => entry.enabled);
  const enabledTopicIds = new Set(enabledPairs.map((entry) => entry.topicId));
  const enabledFabulaIds = new Set(enabledPairs.map((entry) => entry.fabulaId));

  if (enabledPairs.length <= Math.min(activeTopicIds.length, activeFabulaIds.length) && enabledTopicIds.size === enabledPairs.length && enabledFabulaIds.size === enabledPairs.length) {
    return [{
      code: 'topicFabulaDegeneracy',
      projectId,
      message: `${projectId} topic/fabula matrix looks like one-to-one pairs, not reusable story mechanics.`
    }];
  }
  return [];
}

function validateReadyScenario({ projectId, readyScenarioId, workspace }: ProjectBlueprintValidationInput): ProjectBlueprintValidationIssue[] {
  if (!readyScenarioId) return [];
  const planItem = workspace.contentPlanItems.find((item) => item.id === readyScenarioId);
  if (!planItem) {
    return [{
      code: 'missingReadyScenario',
      projectId,
      message: `${projectId} is missing ready benchmark scenario "${readyScenarioId}".`
    }];
  }
  if (!planItem.sourceSignalId || !planItem.topicId || !planItem.fabulaId || !planItem.channelId) {
    return [{
      code: 'missingReadyScenario',
      projectId,
      message: `${projectId} ready benchmark scenario "${readyScenarioId}" must include source signal, topic, fabula, and channel.`
    }];
  }
  return [];
}
