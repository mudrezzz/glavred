import type { WorkspaceState } from '../domain/editorialWorkspace';
import { findLinkedPostCandidate } from './postCandidateLinking';
import { buildPublicationSizeContext } from './draftRunPublicationContext';
import { buildSourceIntentDefaults } from './draftRunSourceIntentContext';
import { buildDraftRunEditorialModel } from './draftRunEditorialContract';

export type DraftRunMissingContext = {
  entity: string;
  id: string | null;
  reason: string;
};

export type DraftRunContextSnapshot = {
  workItem: Record<string, unknown> | null;
  planSlot: Record<string, unknown> | null;
  candidate: Record<string, unknown> | null;
  sourceSignal: Record<string, unknown> | null;
  topic: Record<string, unknown> | null;
  fabula: Record<string, unknown> | null;
  projectProfile: Record<string, unknown>;
  editorialModel: Record<string, unknown>;
  publisherRules: Record<string, unknown>[];
  authorPositionEvidence: Record<string, unknown>[];
  publicationSize: Record<string, unknown>;
  sourceIntentDefaults: Record<string, unknown>;
  missingContext: DraftRunMissingContext[];
};

export function buildDraftRunContext(workspace: WorkspaceState): DraftRunContextSnapshot {
  const missingContext: DraftRunMissingContext[] = [];
  const workItem = findSelectedWorkItem(workspace, missingContext);
  const planSlot = findPlanSlot(workspace, workItem, missingContext);
  const candidate = findCandidate(workspace, workItem, planSlot, missingContext);
  const sourceSignal = findSourceSignal(workspace, workItem, candidate, planSlot, missingContext);
  const topic = findTopic(workspace, workItem, candidate, planSlot, missingContext);
  const fabula = findFabula(workspace, workItem, candidate, planSlot, missingContext);
  const publicationSize = buildPublicationSizeContext(workspace, workItem, planSlot, fabula);
  const briefAudience = workItem?.brief?.audience ?? workspace.postBrief?.audience ?? null;

  return {
    workItem: workItem ? compactWorkItem(workItem) : null,
    planSlot: planSlot ? compactPlanSlot(planSlot) : null,
    candidate: candidate ? compactCandidate(candidate) : null,
    sourceSignal: sourceSignal ? compactSourceSignal(sourceSignal) : null,
    topic: topic ? compactTopic(topic) : null,
    fabula: fabula ? compactFabula(fabula) : null,
    projectProfile: {
      name: workspace.projectProfile.name,
      description: workspace.projectProfile.description,
      setupStatus: workspace.projectProfile.setupStatus
    },
    editorialModel: buildDraftRunEditorialModel(workspace, briefAudience),
    publisherRules: workspace.editorialRules.map((rule) => ({
      id: rule.id,
      group: rule.group,
      title: rule.title,
      statement: rule.statement,
      status: rule.status,
      evidenceNoteId: rule.evidenceNoteId ?? null
    })),
    authorPositionEvidence: [...workspace.authorPositionAssertions]
      .sort((left, right) => {
        if (left.status !== right.status) return left.status === 'confirmed' ? -1 : 1;
        return right.confidence - left.confidence;
      })
      .slice(0, 10)
      .map((assertion) => ({
        id: assertion.id,
        type: assertion.type,
        title: assertion.title,
        statement: assertion.statement,
        confidence: assertion.confidence,
        status: assertion.status,
        evidence: assertion.evidence
    })),
    publicationSize,
    sourceIntentDefaults: buildSourceIntentDefaults(workspace, workItem, planSlot, candidate, sourceSignal, topic, fabula),
    missingContext
  };
}

type WorkItem = WorkspaceState['editorialWorkItems'][number];
type PlanSlot = WorkspaceState['contentPlanItems'][number];
type Candidate = WorkspaceState['postCandidates'][number];
type SourceSignal = WorkspaceState['sourceSignals'][number];
type Topic = WorkspaceState['topics'][number];
type Fabula = WorkspaceState['fabulas'][number];

function findSelectedWorkItem(
  workspace: WorkspaceState,
  missingContext: DraftRunMissingContext[]
): WorkItem | null {
  if (!workspace.selectedEditorialWorkItemId) {
    missingContext.push({ entity: 'editorialWorkItem', id: null, reason: 'No selected work item' });
    return null;
  }
  const workItem = workspace.editorialWorkItems.find(
    (item) => item.id === workspace.selectedEditorialWorkItemId
  );
  if (!workItem) {
    missingContext.push({
      entity: 'editorialWorkItem',
      id: workspace.selectedEditorialWorkItemId,
      reason: 'Selected work item was not found'
    });
  }
  return workItem ?? null;
}

function findPlanSlot(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  missingContext: DraftRunMissingContext[]
): PlanSlot | null {
  const planItemId = workItem?.contentPlanItemId ?? workspace.postBrief?.planItemId ?? workspace.contentPlanItem?.id;
  if (!planItemId) return workspace.contentPlanItem;
  const planSlot =
    workspace.contentPlanItems.find((item) => item.id === planItemId) ??
    (workspace.contentPlanItem?.id === planItemId ? workspace.contentPlanItem : null);
  if (!planSlot) {
    missingContext.push({ entity: 'contentPlanItem', id: planItemId, reason: 'Plan slot was not found' });
  }
  return planSlot;
}

function findCandidate(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  planSlot: PlanSlot | null,
  missingContext: DraftRunMissingContext[]
): Candidate | null {
  return findLinkedPostCandidate(workspace, workItem, planSlot, (entity, id, reason) =>
    missingContext.push({ entity, id, reason })
  );
}

function findSourceSignal(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  candidate: Candidate | null,
  planSlot: PlanSlot | null,
  missingContext: DraftRunMissingContext[]
): SourceSignal | null {
  const signalId =
    workItem?.sourceSignalId ?? candidate?.sourceSignalId ?? planSlot?.sourceSignalId ?? workspace.sourceSignal?.id;
  if (!signalId) return workspace.sourceSignal;
  const signal =
    workspace.sourceSignals.find((item) => item.id === signalId) ??
    (workspace.sourceSignal?.id === signalId ? workspace.sourceSignal : null);
  if (!signal) {
    missingContext.push({ entity: 'sourceSignal', id: signalId, reason: 'Source signal was not found' });
  }
  return signal;
}

function findTopic(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  candidate: Candidate | null,
  planSlot: PlanSlot | null,
  missingContext: DraftRunMissingContext[]
): Topic | null {
  const topicId = workItem?.topicId ?? candidate?.topicId ?? planSlot?.topicId ?? workspace.postBrief?.topicId;
  if (!topicId) return null;
  const topic = workspace.topics.find((item) => item.id === topicId) ?? null;
  if (!topic) {
    missingContext.push({ entity: 'topic', id: topicId, reason: 'Topic was not found' });
  }
  return topic;
}

function findFabula(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  candidate: Candidate | null,
  planSlot: PlanSlot | null,
  missingContext: DraftRunMissingContext[]
): Fabula | null {
  const fabulaId = workItem?.fabulaId ?? candidate?.fabulaId ?? planSlot?.fabulaId ?? workspace.postBrief?.fabulaId;
  if (!fabulaId) return null;
  const fabula = workspace.fabulas.find((item) => item.id === fabulaId) ?? null;
  if (!fabula) {
    missingContext.push({ entity: 'fabula', id: fabulaId, reason: 'Fabula was not found' });
  }
  return fabula;
}

function compactWorkItem(item: WorkItem) {
  return {
    id: item.id,
    contentPlanItemId: item.contentPlanItemId,
    postCandidateId: item.postCandidateId ?? null,
    sourceSignalId: item.sourceSignalId ?? null,
    title: item.title,
    platform: item.platform,
    date: item.date,
    time: item.time,
    topicId: item.topicId ?? null,
    topicTitle: item.topicTitle ?? null,
    fabulaId: item.fabulaId ?? null,
    fabulaTitle: item.fabulaTitle ?? null,
    stage: item.stage,
    status: item.status
  };
}

function compactPlanSlot(item: PlanSlot) {
  return {
    id: item.id,
    title: item.title,
    platform: item.platform,
    channelId: item.channelId ?? null,
    date: item.date,
    time: item.time,
    priority: item.priority,
    expectedEffect: item.expectedEffect,
    approvalStatus: item.approvalStatus,
    topicId: item.topicId ?? null,
    topicTitle: item.topicTitle ?? null,
    fabulaId: item.fabulaId ?? null,
    fabulaTitle: item.fabulaTitle ?? null,
    sourceSignalId: item.sourceSignalId ?? null,
    publicationSizeProfileId: item.publicationSizeProfileId ?? null
  };
}

function compactCandidate(candidate: Candidate) {
  return {
    id: candidate.id,
    sourceSignalId: candidate.sourceSignalId,
    topicId: candidate.topicId,
    fabulaId: candidate.fabulaId,
    title: candidate.title,
    thesis: candidate.thesis,
    audience: candidate.audience,
    value: candidate.value,
    goal: candidate.goal,
    platform: candidate.platform,
    confidence: candidate.confidence,
    risks: candidate.risks,
    evidenceSummary: candidate.evidenceSummary,
    approvalStatus: candidate.approvalStatus
  };
}

function compactSourceSignal(signal: SourceSignal) {
  return {
    id: signal.id,
    type: signal.type,
    title: signal.title,
    source: signal.source,
    capturedAt: signal.capturedAt,
    summary: signal.summary,
    rawNote: signal.rawNote,
    evidence: signal.evidence ?? [],
    authorCorrection: signal.authorCorrection ?? null,
    reviewStatus: signal.reviewStatus ?? null,
    duplicateRisk: signal.duplicateRisk ?? null
  };
}

function compactTopic(topic: Topic) {
  return {
    id: topic.id,
    title: topic.title,
    description: topic.description,
    purpose: topic.purpose,
    audienceValue: topic.audienceValue,
    authorStance: topic.authorStance,
    rules: topic.rules,
    forbiddenAngles: topic.forbiddenAngles,
    weightRange: topic.weightRange,
    status: topic.status
  };
}

function compactFabula(fabula: Fabula) {
  return {
    id: fabula.id,
    title: fabula.title,
    description: fabula.description,
    dramaturgy: fabula.dramaturgy,
    structure: fabula.structure,
    proofRequirements: fabula.proofRequirements,
    rules: fabula.rules,
    weightRange: fabula.weightRange,
    sizeIntent: fabula.sizeIntent,
    researchDepth: fabula.researchDepth,
    researchStrategy: fabula.researchStrategy,
    status: fabula.status
  };
}
