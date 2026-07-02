import { describe, expect, it } from 'vitest';
import { buildDraftRunContext } from './draftRunContext';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import type { WorkspaceState } from '../domain/editorialWorkspace';

describe('buildDraftRunContext editorial contract ownership', () => {
  it('prefers post brief audience over editorial rules and legacy model summary', () => {
    const workspace = createWorkspace();

    const context = buildDraftRunContext({
      ...workspace,
      postBrief: {
        ...workspace.postBrief!,
        audience: 'Brief audience'
      }
    });

    expect(context.editorialModel.audience).toBe('Brief audience');
  });

  it('uses visible editorial rules before stale legacy model summaries', () => {
    const context = buildDraftRunContext({ ...createWorkspace(), postBrief: null });

    expect(context.editorialModel).toMatchObject({
      author: 'Visible author rule',
      audience: 'Visible audience rule',
      positioning: 'Visible position rule',
      goals: ['Visible goal rule'],
      styleRules: ['Visible style rule'],
      forbiddenTopics: ['Visible forbidden rule']
    });
  });

  it('does not use publication channel audience as generation audience', () => {
    const workspace = createWorkspace();
    const context = buildDraftRunContext({
      ...workspace,
      postBrief: null,
      editorialRules: [],
      publicationChannels: [
        {
          ...workspace.publicationChannels[0],
          audience: 'Channel audience must not be used'
        }
      ]
    });

    expect(context.editorialModel.audience).toBe('Legacy model audience');
    expect(context.editorialModel.audience).not.toBe('Channel audience must not be used');
  });
});

function createWorkspace(): WorkspaceState {
  const workspace = createDemoWorkspace();
  const brief = workspace.postBrief ?? {
    id: 'brief-1',
    planItemId: workspace.contentPlanItems[0]?.id,
    title: 'Brief',
    rubric: 'Rubric',
    audience: 'Brief audience',
    thesis: 'Thesis',
    conflict: 'Conflict',
    authorPosition: 'Position',
    evidence: [],
    examples: [],
    structure: [],
    cta: 'CTA',
    risks: [],
    sources: [],
    approvalStatus: 'approved' as const
  };

  return {
    ...workspace,
    postBrief: brief,
    editorialModel: {
      ...workspace.editorialModel,
      author: 'Legacy model author',
      audience: 'Legacy model audience',
      positioning: 'Legacy model position',
      goals: ['Legacy model goal'],
      styleRules: ['Legacy model style'],
      forbiddenTopics: ['Legacy model forbidden']
    },
    editorialRules: [
      rule('author', 'Visible author rule'),
      rule('audience', 'Visible audience rule'),
      rule('positioning', 'Visible position rule'),
      rule('goal', 'Visible goal rule'),
      rule('styleVoice', 'Visible style rule'),
      rule('forbiddenTopic', 'Visible forbidden rule')
    ],
    publicationChannels: [
      {
        ...workspace.publicationChannels[0],
        audience: 'Channel audience must not be used'
      }
    ]
  };
}

function rule(group: WorkspaceState['editorialRules'][number]['group'], statement: string) {
  return {
    id: `rule-${group}`,
    group,
    title: statement,
    statement,
    status: 'active' as const
  };
}
