import { describe, expect, it } from 'vitest';
import type { WorkspaceState } from '../domain/workspace/types';
import { createDemoPortfolio } from './demoPortfolio';
import { validateProjectBlueprintSeed } from './projectBlueprintValidation';

const baseWorkspace = (): WorkspaceState => cloneWorkspace(createDemoPortfolio().workspacesByProjectId['project-ai-design-patterns']);

describe('project blueprint fixture validation', () => {
  it('reports missing required Publisher rule groups', () => {
    const workspace = baseWorkspace();
    workspace.editorialRules = workspace.editorialRules.filter((rule) => rule.group !== 'author');

    const issues = validateProjectBlueprintSeed({ projectId: 'project-ai-design-patterns', workspace });

    expect(issues.map((issue) => issue.code)).toContain('missingPublisherGroup');
  });

  it('reports channel audience duplication', () => {
    const workspace = baseWorkspace();
    workspace.publicationChannels[0] = {
      ...workspace.publicationChannels[0],
      audience: workspace.editorialModel.audience
    };

    const issues = validateProjectBlueprintSeed({ projectId: 'project-ai-design-patterns', workspace });

    expect(issues.map((issue) => issue.code)).toContain('channelAudienceDuplication');
  });

  it('reports mojibake and question-mark replacement text', () => {
    const workspace = baseWorkspace();
    workspace.projectProfile.description = `Broken ${String.fromCharCode(0x0420, 0x045F)} text`;

    const issues = validateProjectBlueprintSeed({ projectId: 'project-ai-design-patterns', workspace });

    expect(issues.map((issue) => issue.code)).toContain('mojibake');
  });

  it('reports topic/fabula matrices that collapse into one-to-one pairs', () => {
    const workspace = baseWorkspace();
    const topicIds = workspace.topics.slice(0, 2).map((topic) => topic.id);
    const fabulaIds = workspace.fabulas.slice(0, 2).map((fabula) => fabula.id);
    workspace.topicFabulaMatrix = [
      { topicId: topicIds[0], fabulaId: fabulaIds[0], enabled: true },
      { topicId: topicIds[1], fabulaId: fabulaIds[1], enabled: true }
    ];

    const issues = validateProjectBlueprintSeed({ projectId: 'project-ai-design-patterns', workspace });

    expect(issues.map((issue) => issue.code)).toContain('topicFabulaDegeneracy');
  });

  it('reports missing or incomplete ready benchmark scenarios', () => {
    const workspace = baseWorkspace();

    const issues = validateProjectBlueprintSeed({
      projectId: 'project-ai-design-patterns',
      workspace,
      readyScenarioId: 'missing-ready-scenario'
    });

    expect(issues.map((issue) => issue.code)).toContain('missingReadyScenario');
  });
});

function cloneWorkspace(workspace: WorkspaceState): WorkspaceState {
  return JSON.parse(JSON.stringify(workspace)) as WorkspaceState;
}
