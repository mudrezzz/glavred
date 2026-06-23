import type { WorkspaceState } from '../domain/editorialWorkspace';
import { createBriefResearchSources, detectBriefResearchSourceOrigin } from './fabulaResearchStrategyService';

type WorkItem = WorkspaceState['editorialWorkItems'][number] | null;
type PlanSlot = WorkspaceState['contentPlanItems'][number] | null;
type Candidate = WorkspaceState['postCandidates'][number] | null;
type SourceSignal = WorkspaceState['sourceSignals'][number] | null;
type Topic = WorkspaceState['topics'][number] | null;
type Fabula = WorkspaceState['fabulas'][number] | null;

export function buildSourceIntentDefaults(
  workspace: WorkspaceState,
  _workItem: WorkItem,
  planSlot: PlanSlot,
  candidate: Candidate,
  sourceSignal: SourceSignal,
  topic: Topic,
  fabula: Fabula
): Record<string, unknown> {
  const autoSources = planSlot && workspace.insightCard
    ? createBriefResearchSources({ planItem: planSlot, insight: workspace.insightCard, topic, fabula, candidate, sourceSignal })
    : [];
  return {
    sourcesOrigin: detectBriefResearchSourceOrigin({
      sources: workspace.postBrief?.sources ?? [],
      fabula,
      expectedAutoSources: autoSources
    }),
    autoSourceCount: autoSources.length
  };
}
