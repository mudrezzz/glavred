import { describe, expect, it } from 'vitest';
import { createDemoPortfolio } from './demoPortfolio';
import { demoPortfolioBenchmarkExpectations } from './demoBenchmarkPortfolio';

describe('three-blog benchmark demo portfolio', () => {
  it('seeds two users and three distinct benchmark blogs', () => {
    const portfolio = createDemoPortfolio();

    expect(portfolio.users).toHaveLength(2);
    expect(portfolio.projects.map((project) => project.id)).toEqual([
      'project-ai-design-patterns',
      'project-kasha-iz-topora',
      'project-glavred-blog'
    ]);
    expect(Object.keys(portfolio.workspacesByProjectId)).toEqual([
      'project-ai-design-patterns',
      'project-kasha-iz-topora',
      'project-glavred-blog'
    ]);
  });

  it('gives every blog distinct editorial memory, model and ready scenario', () => {
    const portfolio = createDemoPortfolio();
    const ai = portfolio.workspacesByProjectId['project-ai-design-patterns'];
    const kasha = portfolio.workspacesByProjectId['project-kasha-iz-topora'];
    const glavred = portfolio.workspacesByProjectId['project-glavred-blog'];

    expect(ai.projectProfile.name).toBe('AI Design Patterns');
    expect(kasha.projectProfile.name).toBe('Каша из топора');
    expect(glavred.projectProfile.name).toBe('Блог Главреда');

    expect(ai.editorialModel.positioning).toContain('Anti-hype synthesis');
    expect(kasha.editorialModel.positioning).toContain('сложный B2B');
    expect(glavred.editorialModel.positioning).toContain('редакционную систему');

    expect(ai.authorNotes.some((note) => note.tags.includes('execution-layer'))).toBe(true);
    expect(kasha.authorNotes.some((note) => note.tags.includes('revops'))).toBe(true);
    expect(glavred.authorNotes.some((note) => note.tags.includes('editorial-system'))).toBe(true);

    expect(ai.contentPlanItems.some((item) => item.id === demoPortfolioBenchmarkExpectations['project-ai-design-patterns'].readyScenarioId)).toBe(true);
    expect(kasha.contentPlanItems[0].id).toBe(demoPortfolioBenchmarkExpectations['project-kasha-iz-topora'].readyScenarioId);
    expect(glavred.contentPlanItems[0].id).toBe(demoPortfolioBenchmarkExpectations['project-glavred-blog'].readyScenarioId);
  });

  it('keeps memory and accepted learning isolated by project', () => {
    const portfolio = createDemoPortfolio();
    const ai = portfolio.workspacesByProjectId['project-ai-design-patterns'];
    const kasha = portfolio.workspacesByProjectId['project-kasha-iz-topora'];
    const glavred = portfolio.workspacesByProjectId['project-glavred-blog'];

    expect(ai.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('kasha-'))).toBe(false);
    expect(kasha.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('ai-pattern-'))).toBe(false);
    expect(glavred.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('kasha-'))).toBe(false);

    expect(ai.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(true);
    expect(kasha.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(false);
    expect(glavred.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(false);
  });
});
