import type { Fabula, PostCandidate, SourceSignal, Topic, WorkspaceState } from '../domain/editorialWorkspace';
import { isTopicFabulaEnabled } from '../domain/editorialWorkspace';

type CandidatePair = { topic: Topic; fabula: Fabula };

export function createPostCandidates(workspace: WorkspaceState): PostCandidate[] {
  const approvedSignals = workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved');
  const pairs = getActiveCandidatePairs(workspace);
  const storedById = new Map(workspace.postCandidates.map((candidate) => [candidate.id, candidate]));

  return approvedSignals
    .flatMap((signal) => pairs.map((pair, index) => createPostCandidate(workspace, signal, pair, index)))
    .slice(0, 3)
    .map((candidate) => storedById.get(candidate.id) ?? candidate)
    .map((candidate) => (workspace.postCandidate?.id === candidate.id ? workspace.postCandidate : candidate));
}

function getActiveCandidatePairs(workspace: WorkspaceState): CandidatePair[] {
  const activeTopics = workspace.topics.filter((topic) => topic.status === 'active');
  const activeFabulas = workspace.fabulas.filter((fabula) => fabula.status === 'active');
  const pairs = activeTopics.flatMap((topic) =>
    activeFabulas
      .filter((fabula) => isTopicFabulaEnabled(workspace.topicFabulaMatrix, topic.id, fabula.id))
      .map((fabula) => ({ topic, fabula }))
  );

  return pairs.length > 0 ? pairs : activeTopics.slice(0, 1).flatMap((topic) => activeFabulas.slice(0, 1).map((fabula) => ({ topic, fabula })));
}

function createPostCandidate(
  workspace: WorkspaceState,
  signal: SourceSignal,
  pair: CandidatePair,
  index: number
): PostCandidate {
  const value = signal.suggestedValue || pair.topic.audienceValue || pair.topic.purpose;
  const evidenceSummary = signal.evidence?.[0]?.summary || signal.searchNote || signal.summary;

  return {
    id: `post-candidate-${signal.id}-${pair.topic.id}-${pair.fabula.id}`,
    sourceSignalId: signal.id,
    topicId: pair.topic.id,
    fabulaId: pair.fabula.id,
    audience: workspace.editorialModel.audience,
    value,
    goal: workspace.editorialModel.goals[index % Math.max(1, workspace.editorialModel.goals.length)] ?? pair.topic.purpose,
    platform: workspace.contentPlanSettings.defaultPlatform,
    title: `${pair.topic.title} / ${pair.fabula.title}: ${signal.title}`,
    thesis: `${signal.summary} Развернуть через фабулу "${pair.fabula.title}" и ценность: ${value}`,
    evidenceSummary,
    confidence: Number((0.88 - index * 0.06).toFixed(2)),
    risks: createCandidateRisks(signal, pair),
    approvalStatus: 'draft'
  };
}

function createCandidateRisks(signal: SourceSignal, pair: CandidatePair): string[] {
  const risks = [
    `Проверить доказательства для фабулы "${pair.fabula.title}".`,
    `Не потерять авторскую позицию темы "${pair.topic.title}".`
  ];

  if (signal.duplicateRisk === 'high') {
    risks.push('Высокий риск дубля: нужен более точный угол перед планированием.');
  }

  return risks;
}
