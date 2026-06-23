import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { createContentPlanItem, createInsightCard, createPostBrief } from './editorialServices';

describe('fabula research strategy defaults', () => {
  it('copies manual fabula research strategy into a new post brief', () => {
    const workspace = createDemoWorkspace();
    const fabula = workspace.fabulas[0];
    const insight = createInsightCard(
      workspace.sourceSignal,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );
    const planItem = createContentPlanItem(insight);

    const brief = createPostBrief(
      { ...planItem, fabulaId: fabula.id },
      insight,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );

    expect(fabula.researchStrategy.mode).toBe('manual');
    expect(brief.sources).toEqual(fabula.researchStrategy.instructions);
  });

  it('creates human-readable auto research instructions from available context', () => {
    const workspace = createDemoWorkspace();
    const fabula = workspace.fabulas.find((item) => item.researchStrategy.mode === 'auto') ?? workspace.fabulas[1];
    const topic = workspace.topics[0];
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel, [topic], [fabula], workspace.topicFabulaMatrix);
    const planItem = createContentPlanItem({ ...insight, topicId: topic.id, fabulaId: fabula.id });
    const candidate = {
      ...workspace.postCandidates[0],
      topicId: topic.id,
      fabulaId: fabula.id,
      sourceSignalId: workspace.sourceSignal.id,
      approvalStatus: 'approved' as const
    };

    const brief = createPostBrief(
      { ...planItem, topicId: topic.id, fabulaId: fabula.id },
      insight,
      workspace.editorialModel,
      [topic],
      [fabula],
      workspace.topicFabulaMatrix,
      { candidate, sourceSignal: workspace.sourceSignal }
    );

    expect(fabula.researchStrategy.mode).toBe('auto');
    expect(brief.sources.some((source) => source.startsWith('найти:'))).toBe(true);
    expect(brief.sources.some((source) => source.startsWith('проверить:'))).toBe(true);
    expect(brief.sources.join('\n')).not.toMatch(/^AI product discovery$/m);
  });
});
