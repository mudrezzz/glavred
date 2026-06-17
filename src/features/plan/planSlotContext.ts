import type { ContentPlanItem, PostCandidate, SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';

export interface PlanSlotContext {
  audience: string;
  candidate: PostCandidate | null;
  confidence: number | null;
  evidence: string;
  fabulaTitle: string;
  goal: string;
  risks: string[];
  signal: SourceSignal;
  thesis: string;
  topicTitle: string;
  value: string;
}

export function getPlanSlotContext(item: ContentPlanItem, workspace: WorkspaceState): PlanSlotContext {
  const candidate = findLinkedCandidate(item, workspace);
  const signal = workspace.sourceSignals.find((source) => source.id === item.sourceSignalId) ?? workspace.sourceSignal;
  const topic = workspace.topics.find((entry) => entry.id === item.topicId);
  const fabula = workspace.fabulas.find((entry) => entry.id === item.fabulaId);
  const insight = workspace.insightCard;

  return {
    audience: candidate?.audience ?? insight?.audienceRelevance ?? workspace.editorialModel.audience,
    candidate,
    confidence: candidate?.confidence ?? null,
    evidence: candidate?.evidenceSummary ?? signal.rawNote ?? signal.summary,
    fabulaTitle: fabula?.title ?? item.fabulaTitle ?? 'Не задано',
    goal: candidate?.goal ?? workspace.editorialModel.goals[0] ?? 'Не задано',
    risks: candidate?.risks ?? insight?.factGaps ?? [],
    signal,
    thesis: candidate?.thesis ?? insight?.whyItMatters ?? item.expectedEffect,
    topicTitle: topic?.title ?? item.topicTitle ?? 'Не задано',
    value: candidate?.value ?? insight?.authorPosition ?? workspace.editorialModel.positioning
  };
}

function findLinkedCandidate(item: ContentPlanItem, workspace: WorkspaceState): PostCandidate | null {
  const fromInsightId = item.insightId.startsWith('insight-') ? item.insightId.replace(/^insight-/, '') : '';
  const candidates = [workspace.postCandidate, ...workspace.postCandidates].filter(Boolean) as PostCandidate[];
  return (
    candidates.find((candidate) => candidate.id === fromInsightId) ??
    candidates.find((candidate) => candidate.sourceSignalId === item.sourceSignalId && candidate.approvalStatus === 'approved') ??
    null
  );
}
