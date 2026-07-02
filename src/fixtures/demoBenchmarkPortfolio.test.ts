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
    expect(kasha.projectProfile.name).toBe('Северная стена');
    expect(glavred.projectProfile.name).toBe('Блог Главреда');

    expect(ai.editorialModel.positioning).toContain('industrial AI');
    expect(kasha.editorialModel.positioning).toContain('туман');
    expect(glavred.editorialModel.positioning).toContain('редакционную систему');

    expect(ai.authorNotes.some((note) => note.tags.includes('industrial-ai'))).toBe(true);
    expect(ai.topics.map((topic) => topic.id)).toContain('ai-pattern-topic-decision-intelligence');
    expect(ai.fabulas.map((fabula) => fabula.id)).toContain('ai-pattern-fabula-digest');
    expect(ai.sourceSignals.map((signal) => signal.id)).toContain('ai-pattern-signal-decision-workbench');
    expect(kasha.authorNotes.some((note) => note.tags.includes('revops'))).toBe(true);
    expect(kasha.authorNotes.some((note) => note.tags.includes('belay'))).toBe(true);
    expect(kasha.topics.map((topic) => topic.id)).toContain('stena-topic-route');
    expect(kasha.fabulas.map((fabula) => fabula.id)).toContain('stena-fabula-route-note');
    expect(kasha.sourceSignals.map((signal) => signal.id)).toContain('stena-signal-lost-route');
    expect(glavred.authorNotes.some((note) => note.tags.includes('editorial-system'))).toBe(true);

    expect(ai.contentPlanItems.some((item) => item.id === demoPortfolioBenchmarkExpectations['project-ai-design-patterns'].readyScenarioId)).toBe(true);
    expect(kasha.contentPlanItems[0].id).toBe(demoPortfolioBenchmarkExpectations['project-kasha-iz-topora'].readyScenarioId);
    expect(glavred.contentPlanItems[0].id).toBe(demoPortfolioBenchmarkExpectations['project-glavred-blog'].readyScenarioId);

    expect(ai.contentPlanSettings.defaultPlatform).toBe('Telegram');
    expect(ai.contentPlanItems[0].channelId).toBe('channel-ai-telegram');
    expect(ai.publicationChannels.map((channel) => channel.id)).toEqual([
      'channel-ai-telegram',
      'channel-ai-github-pattern-book'
    ]);
    expect(ai.publicationChannels.find((channel) => channel.id === 'channel-ai-github-pattern-book')?.status).toBe('paused');
    expect(kasha.publicationChannels.map((channel) => channel.id)).toEqual(['channel-stena-telegram']);
    expect(glavred.publicationChannels.map((channel) => channel.id)).toEqual([
      'channel-glavred-telegram',
      'channel-glavred-dzen'
    ]);
    expect(kasha.contentPlanItems[0].channelId).toBe('channel-stena-telegram');
    expect(glavred.contentPlanItems[0].channelId).toBe('channel-glavred-telegram');
  });

  it('keeps memory and accepted learning isolated by project', () => {
    const portfolio = createDemoPortfolio();
    const ai = portfolio.workspacesByProjectId['project-ai-design-patterns'];
    const kasha = portfolio.workspacesByProjectId['project-kasha-iz-topora'];
    const glavred = portfolio.workspacesByProjectId['project-glavred-blog'];

    expect(ai.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('stena-'))).toBe(false);
    expect(kasha.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('ai-pattern-'))).toBe(false);
    expect(glavred.authorPositionAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.startsWith('stena-'))).toBe(false);

    expect(ai.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(true);
    expect(kasha.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(false);
    expect(glavred.authorNotes.some((note) => note.type === 'editorialLearning')).toBe(false);
  });
});
