import type { WorkspaceState } from '../domain/editorialWorkspace';
import { summarizeEditorialContract } from '../domain/editorial-contract/summary';

export function buildDraftRunEditorialModel(
  workspace: WorkspaceState,
  audienceOverride?: string | null
) {
  const summary = summarizeEditorialContract(workspace.editorialModel, workspace.editorialRules, audienceOverride);
  return {
    author: summary.author,
    audience: summary.audience,
    positioning: summary.positioning,
    fabula: workspace.editorialModel.fabula,
    rubrics: workspace.editorialModel.rubrics,
    styleRules: summary.styleRules,
    forbiddenTopics: summary.forbiddenTopics,
    goals: summary.goals
  };
}
