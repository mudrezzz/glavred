import { describe, expect, it } from 'vitest';
import { normalizeWorkspace } from './localWorkspaceStore';
import type { WorkspaceState } from '../domain/editorialWorkspace';

describe('normalizeWorkspace editorial contract compatibility', () => {
  it('synthesizes visible editorial rules from legacy model summaries', () => {
    const workspace = normalizeWorkspace({
      editorialModel: {
        author: 'Legacy author summary',
        audience: 'Legacy audience summary',
        positioning: 'Legacy position summary',
        fabula: 'Legacy fabula summary',
        rubrics: [],
        styleRules: ['Legacy style rule'],
        forbiddenTopics: ['Legacy forbidden topic'],
        goals: ['Legacy goal one', 'Legacy goal two']
      },
      editorialRules: []
    } as Partial<WorkspaceState>);

    expect(ruleStatements(workspace, 'author')).toEqual(['Legacy author summary']);
    expect(ruleStatements(workspace, 'audience')).toEqual(['Legacy audience summary']);
    expect(ruleStatements(workspace, 'goal')).toEqual(['Legacy goal one', 'Legacy goal two']);
    expect(workspace.editorialModel.author).toBe('Legacy author summary');
    expect(workspace.editorialModel.audience).toBe('Legacy audience summary');
    expect(workspace.editorialModel.goals).toEqual(['Legacy goal one', 'Legacy goal two']);
  });
});

function ruleStatements(workspace: WorkspaceState, group: string): string[] {
  return workspace.editorialRules
    .filter((rule) => rule.group === group)
    .map((rule) => rule.statement);
}
