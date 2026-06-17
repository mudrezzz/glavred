import type { EditorialWorkItem, PostCandidate, SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';

export interface EditorialWorkItemContext {
  audience: string;
  candidate: PostCandidate | null;
  confidence: number | null;
  evidence: string;
  fabulaTitle: string;
  goal: string;
  platform: string;
  publication: string;
  risks: string[];
  signal: SourceSignal;
  topicTitle: string;
  value: string;
}

export function getEditorialWorkItemContext(
  workspace: WorkspaceState,
  item: EditorialWorkItem | null
): EditorialWorkItemContext {
  const planItem = workspace.contentPlanItems.find((entry) => entry.id === item?.contentPlanItemId) ?? workspace.contentPlanItem;
  const candidate = findLinkedCandidate(workspace, item?.postCandidateId, planItem?.insightId, item?.sourceSignalId);
  const signalId = item?.sourceSignalId ?? planItem?.sourceSignalId ?? candidate?.sourceSignalId;
  const signal = workspace.sourceSignals.find((entry) => entry.id === signalId) ?? workspace.sourceSignal;
  const topic = workspace.topics.find((entry) => entry.id === (item?.topicId ?? planItem?.topicId ?? candidate?.topicId));
  const fabula = workspace.fabulas.find((entry) => entry.id === (item?.fabulaId ?? planItem?.fabulaId ?? candidate?.fabulaId));

  return {
    audience: candidate?.audience ?? workspace.postBrief?.audience ?? workspace.editorialModel.audience,
    candidate,
    confidence: candidate?.confidence ?? null,
    evidence: candidate?.evidenceSummary ?? signal.rawNote ?? signal.summary,
    fabulaTitle: fabula?.title ?? item?.fabulaTitle ?? planItem?.fabulaTitle ?? candidate?.fabulaId ?? 'Не задано',
    goal: candidate?.goal ?? workspace.editorialModel.goals[0] ?? 'Не задано',
    platform: item?.platform ?? planItem?.platform ?? candidate?.platform ?? 'Не задано',
    publication: formatPublication(item?.date ?? planItem?.date, item?.time ?? planItem?.time),
    risks: candidate?.risks ?? workspace.postBrief?.risks ?? [],
    signal,
    topicTitle: topic?.title ?? item?.topicTitle ?? planItem?.topicTitle ?? candidate?.topicId ?? 'Не задано',
    value: candidate?.value ?? workspace.postBrief?.authorPosition ?? workspace.editorialModel.positioning
  };
}

function findLinkedCandidate(
  workspace: WorkspaceState,
  postCandidateId: string | undefined,
  insightId: string | undefined,
  sourceSignalId: string | undefined
): PostCandidate | null {
  const fromInsightId = insightId?.startsWith('insight-') ? insightId.replace(/^insight-/, '') : '';
  const candidates = [workspace.postCandidate, ...workspace.postCandidates].filter(Boolean) as PostCandidate[];
  return (
    candidates.find((candidate) => candidate.id === postCandidateId) ??
    candidates.find((candidate) => candidate.id === fromInsightId) ??
    candidates.find((candidate) => candidate.sourceSignalId === sourceSignalId && candidate.approvalStatus === 'approved') ??
    null
  );
}

function formatPublication(date: string | undefined, time: string | undefined): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  const formattedDate = Number.isNaN(parsed.getTime())
    ? date
    : parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
  return time ? `${formattedDate} · ${time}` : formattedDate;
}
