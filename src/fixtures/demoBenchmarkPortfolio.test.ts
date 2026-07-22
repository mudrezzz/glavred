import { describe, expect, it } from 'vitest';
import { createDemoPortfolio } from './demoPortfolio';
import { demoPortfolioBenchmarkExpectations } from './demoBenchmarkPortfolio';
import { validateProjectBlueprintSeeds } from './projectBlueprintValidation';

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

    expect(ai.projectProfile.name).toBe('Опытный цех «Сборочная»');
    expect(kasha.projectProfile.name).toBe('Северная стена');
    expect(glavred.projectProfile.name).toBe('Главред: быть интересным');

    expect(ai.editorialModel.positioning).toContain('Опытный цех');
    expect(kasha.editorialModel.positioning).toContain('туман');
    expect(glavred.editorialModel.positioning).toContain('быть интересным');

    expect(ai.authorNotes.some((note) => note.tags.includes('industrial-ai'))).toBe(true);
    expect(ai.topics.map((topic) => topic.id)).toContain('ai-pattern-topic-industrial-artifacts');
    expect(ai.fabulas.map((fabula) => fabula.id)).toContain('ai-pattern-fabula-test-journal');
    expect(ai.sourceSignals.map((signal) => signal.id)).toContain('ai-pattern-signal-decision-workbench');
    expect(kasha.authorNotes.some((note) => note.tags.includes('revops'))).toBe(true);
    expect(kasha.authorNotes.some((note) => note.tags.includes('belay'))).toBe(true);
    expect(kasha.topics.map((topic) => topic.id)).toContain('stena-topic-deal-route');
    expect(kasha.topics.map((topic) => topic.id)).toContain('stena-topic-lost-route');
    expect(kasha.fabulas.map((fabula) => fabula.id)).toContain('stena-fabula-failure-analysis');
    expect(kasha.sourceSignals.map((signal) => signal.id)).toContain('stena-signal-lost-route');
    expect(glavred.authorNotes.some((note) => note.tags.includes('be-interesting'))).toBe(true);

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
    expect([...ai.publicationChannels, ...kasha.publicationChannels, ...glavred.publicationChannels].every(
      (channel) => channel.audience === undefined
    )).toBe(true);
    expect(kasha.contentPlanItems[0].channelId).toBe('channel-stena-telegram');
    expect(glavred.contentPlanItems[0].channelId).toBe('channel-glavred-telegram');
  });

  it('calibrates Glavred as a being-interesting editorial philosophy benchmark', () => {
    const portfolio = createDemoPortfolio();
    const glavred = portfolio.workspacesByProjectId['project-glavred-blog'];

    expect(glavred.projectProfile.name).toBe('Главред: быть интересным');
    expect(glavred.projectProfile.description).toContain('author voice');
    expect(glavred.editorialModel.author).toContain('редакционный цех');
    expect(glavred.editorialModel.audience).toContain('Эксперты');
    expect(glavred.editorialModel.positioning).toContain('не обещает волшебную кнопку');
    expect(glavred.editorialModel.goals.join(' ')).toContain('AI помогает быть интересным');
    expect(glavred.editorialModel.forbiddenTopics.join(' ')).toContain('Generic AI copywriting tips');

    const ruleIdsByGroup = (group: string) =>
      glavred.editorialRules.filter((rule) => rule.group === group).map((rule) => rule.id);
    expect(ruleIdsByGroup('author')).toContain('glavred-rule-author-product-editor');
    expect(ruleIdsByGroup('audience')).toContain('glavred-rule-audience-authors-teams');
    expect(ruleIdsByGroup('goal')).toEqual(
      expect.arrayContaining(['glavred-rule-goal-interesting-content', 'glavred-rule-goal-practical-templates'])
    );
    expect(ruleIdsByGroup('positioning')).toContain('glavred-rule-positioning-not-autoposter');
    expect(ruleIdsByGroup('styleVoice')).toContain('glavred-rule-style-pain-first');
    expect(ruleIdsByGroup('antiAiPattern')).toContain('glavred-rule-anti-pattern-feature-marketing');

    expect(glavred.topics.map((topic) => topic.id)).toEqual([
      'glavred-topic-be-interesting',
      'glavred-topic-editorial-system',
      'glavred-topic-ai-without-flattening',
      'glavred-topic-template-library',
      'glavred-topic-before-after',
      'glavred-topic-adoption-practice'
    ]);
    expect(glavred.fabulas.map((fabula) => fabula.id)).toEqual([
      'glavred-fabula-flat-draft',
      'glavred-fabula-editorial-method',
      'glavred-fabula-inside-mechanism',
      'glavred-fabula-role-template',
      'glavred-fabula-before-after',
      'glavred-fabula-anti-pattern'
    ]);

    const enabledPairs = glavred.topicFabulaMatrix.filter((entry) => entry.enabled);
    expect(glavred.topicFabulaMatrix).toHaveLength(glavred.topics.length * glavred.fabulas.length);
    expect(enabledPairs).toHaveLength(18);
    for (const fabula of glavred.fabulas) {
      expect(enabledPairs.filter((entry) => entry.fabulaId === fabula.id).length).toBeGreaterThanOrEqual(3);
    }
    expect(enabledPairs.filter((entry) => entry.topicId === 'glavred-topic-be-interesting').map((entry) => entry.fabulaId)).toEqual(
      expect.arrayContaining(['glavred-fabula-flat-draft', 'glavred-fabula-editorial-method'])
    );

    const ready = glavred.contentPlanItems.find((item) => item.id === 'glavred-plan-flat-ai-draft');
    expect(ready?.topicId).toBe('glavred-topic-be-interesting');
    expect(ready?.fabulaId).toBe('glavred-fabula-flat-draft');
    expect(ready?.sourceSignalId).toBe('glavred-signal-flat-ai-content');
    expect(ready?.channelId).toBe('channel-glavred-telegram');
  });

  it('calibrates Sborochnaya author, goals, positioning and reusable topic-fabula matrix', () => {
    const portfolio = createDemoPortfolio();
    const ai = portfolio.workspacesByProjectId['project-ai-design-patterns'];

    expect(ai.projectProfile.name).toBe('Опытный цех «Сборочная»');
    expect(ai.projectProfile.description).toContain('промышленных AI-паттернах');
    expect(ai.editorialModel.author).toContain('руководитель опытного цеха');
    expect(ai.editorialModel.goals.join(' ')).toContain('Привлекать клиентов');
    expect(ai.editorialModel.goals.join(' ')).toContain('industrial AI patterns');
    expect(ai.editorialModel.positioning).toContain('стенд');
    expect(ai.editorialModel.styleRules.join(' ')).toContain('Публичный артефакт выпуска');

    const ruleIdsByGroup = (group: string) =>
      ai.editorialRules.filter((rule) => rule.group === group).map((rule) => rule.id);
    expect(ruleIdsByGroup('author')).toContain('ai-pattern-rule-author-workshop-lead');
    expect(ruleIdsByGroup('audience')).toContain('ai-pattern-rule-industrial-audience');
    expect(ruleIdsByGroup('goal')).toEqual(
      expect.arrayContaining(['ai-pattern-rule-client-attraction-goal', 'ai-pattern-rule-pattern-book-goal'])
    );
    expect(ruleIdsByGroup('author')).not.toContain('ai-pattern-rule-pattern-output');
    expect(ruleIdsByGroup('positioning')).not.toContain('ai-pattern-rule-proof-limits');
    expect(ruleIdsByGroup('styleVoice')).toContain('ai-pattern-rule-pattern-output');
    expect(ruleIdsByGroup('styleLanguage')).toContain('ai-pattern-rule-proof-limits');

    expect(ai.topics.map((topic) => topic.id)).toEqual([
      'ai-pattern-topic-industrial-artifacts',
      'ai-pattern-topic-reliability-contours',
      'ai-pattern-topic-hybrid-assembly',
      'ai-pattern-topic-data-raw-material',
      'ai-pattern-topic-implementation-field',
      'ai-pattern-topic-open-catalog'
    ]);
    expect(ai.fabulas.map((fabula) => fabula.id)).toEqual([
      'ai-pattern-fabula-pattern-card',
      'ai-pattern-fabula-test-protocol',
      'ai-pattern-fabula-artifact-teardown',
      'ai-pattern-fabula-field-note',
      'ai-pattern-fabula-anti-pattern',
      'ai-pattern-fabula-test-journal'
    ]);

    const enabledPairs = ai.topicFabulaMatrix.filter((entry) => entry.enabled);
    expect(ai.topicFabulaMatrix).toHaveLength(ai.topics.length * ai.fabulas.length);
    expect(enabledPairs).toHaveLength(18);
    expect(enabledPairs.filter((entry) => entry.topicId === 'ai-pattern-topic-industrial-artifacts').map((entry) => entry.fabulaId)).toEqual(
      expect.arrayContaining(['ai-pattern-fabula-pattern-card', 'ai-pattern-fabula-test-protocol'])
    );
    expect(enabledPairs.filter((entry) => entry.fabulaId === 'ai-pattern-fabula-pattern-card').length).toBeGreaterThanOrEqual(3);

    const ready = ai.contentPlanItems.find((item) => item.id === 'ai-patterns-plan-decision-workbench');
    expect(ready?.topicId).toBe('ai-pattern-topic-industrial-artifacts');
    expect(ready?.fabulaId).toBe('ai-pattern-fabula-pattern-card');
    expect(ready?.channelId).toBe('channel-ai-telegram');
  });

  it('calibrates Severnaya Stena author, goals, audience and pain-first dramaturgy', () => {
    const portfolio = createDemoPortfolio();
    const stena = portfolio.workspacesByProjectId['project-kasha-iz-topora'];

    expect(stena.projectProfile.name).toBe('Северная стена');
    expect(stena.editorialModel.author).toContain('коммерциализации сложных технических B2B-продуктов');
    expect(stena.editorialModel.author).toContain('пресейла');
    expect(stena.editorialModel.author).toContain('Не sales coach');
    expect(stena.editorialModel.goals).toHaveLength(5);
    expect(stena.editorialModel.goals.join(' ')).toContain('Привлекать клиентов');
    expect(stena.editorialModel.goals.join(' ')).toContain('рынок дозрел до RevOps');
    expect(stena.editorialModel.goals.join(' ')).not.toContain('AI как');

    expect(stena.editorialModel.audience).toContain('Фаундеры B2B-компаний');
    expect(stena.editorialModel.audience).not.toContain('начинаться');
    expect(stena.editorialModel.audience).not.toContain('узнаваемой боли');

    const ruleIdsByGroup = (group: string) =>
      stena.editorialRules.filter((rule) => rule.group === group).map((rule) => rule.id);
    expect(ruleIdsByGroup('author')).toContain('stena-rule-author-field-practitioner');
    expect(ruleIdsByGroup('audience')).toContain('stena-rule-audience-commercial-fog');
    expect(ruleIdsByGroup('goal')).toEqual(
      expect.arrayContaining([
        'stena-rule-goal-client-attraction',
        'stena-rule-goal-revops-maturity',
        'stena-rule-goal-sales-engineering',
        'stena-rule-goal-practical-team'
      ])
    );
    expect(ruleIdsByGroup('goal')).not.toContain('stena-rule-goal-ai-light-gear');
    expect(ruleIdsByGroup('positioning')).toContain('stena-rule-ai-light-gear');

    const painRule = stena.editorialRules.find((rule) => rule.id === 'stena-rule-reader-pain');
    expect(painRule?.group).toBe('styleVoice');
    expect(stena.editorialModel.styleRules.some((rule) => rule.includes('начинать с узнаваемой сцены сделки'))).toBe(true);
    expect(
      stena.fabulas
        .find((fabula) => fabula.id === 'stena-fabula-fog-removal')
        ?.researchStrategy.instructions.some((instruction) => instruction.includes('узнаваемой боли сделки'))
    ).toBe(true);
  });

  it('calibrates Severnaya Stena topics, reusable fabulas and curated matrix', () => {
    const portfolio = createDemoPortfolio();
    const stena = portfolio.workspacesByProjectId['project-kasha-iz-topora'];

    expect(stena.topics.map((topic) => topic.id)).toEqual([
      'stena-topic-deal-route',
      'stena-topic-client-relief',
      'stena-topic-gear',
      'stena-topic-belay',
      'stena-topic-rope-team',
      'stena-topic-lost-route'
    ]);
    expect(stena.fabulas.map((fabula) => fabula.id)).toEqual([
      'stena-fabula-fog-removal',
      'stena-fabula-failure-analysis',
      'stena-fabula-gear-check',
      'stena-fabula-route-note',
      'stena-fabula-checkpoint',
      'stena-fabula-climb-plan'
    ]);
    expect(stena.fabulas.map((fabula) => fabula.title)).not.toContain('RevOps без тумана');

    const enabledPairs = stena.topicFabulaMatrix.filter((entry) => entry.enabled);
    expect(stena.topicFabulaMatrix).toHaveLength(stena.topics.length * stena.fabulas.length);
    expect(enabledPairs).toHaveLength(18);

    for (const fabula of stena.fabulas) {
      expect(enabledPairs.filter((entry) => entry.fabulaId === fabula.id).length).toBeGreaterThanOrEqual(3);
    }
    expect(enabledPairs.filter((entry) => entry.topicId === 'stena-topic-lost-route').map((entry) => entry.fabulaId)).toEqual(
      expect.arrayContaining(['stena-fabula-failure-analysis', 'stena-fabula-route-note'])
    );

    const ready = stena.contentPlanItems.find((item) => item.id === 'stena-plan-lost-route');
    expect(ready?.topicId).toBe('stena-topic-lost-route');
    expect(ready?.fabulaId).toBe('stena-fabula-failure-analysis');
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

  it('seeds isolated upstream registries, radar runs and found materials for each benchmark project', () => {
    const portfolio = createDemoPortfolio();
    const workspaces = Object.values(portfolio.workspacesByProjectId);

    for (const workspace of workspaces) {
      expect(workspace.sourceRegistry.handles.length).toBeGreaterThan(0);
      expect(workspace.radars.every((radar) => (radar.sourceHandleIds ?? []).length > 0)).toBe(true);
      expect(workspace.radarRuns.length).toBeGreaterThan(0);
      expect(workspace.foundMaterials.length).toBeGreaterThan(0);
      expect(workspace.sourceSignals.length).toBeGreaterThan(0);
    }

    const aiHandleIds = new Set(portfolio.workspacesByProjectId['project-ai-design-patterns'].sourceRegistry.handles.map((handle) => handle.id));
    const stenaHandleIds = new Set(portfolio.workspacesByProjectId['project-kasha-iz-topora'].sourceRegistry.handles.map((handle) => handle.id));
    const sharedProjectSpecificHandles = [...aiHandleIds].filter((id) => id.includes('ai-pattern') && stenaHandleIds.has(id));

    expect(sharedProjectSpecificHandles).toEqual([]);
    expect(portfolio.workspacesByProjectId['project-ai-design-patterns'].radarRuns[0].foundMaterialIds.length).toBeGreaterThan(0);
    expect(portfolio.workspacesByProjectId['project-kasha-iz-topora'].sourceRegistry.handles.some(
      (handle) => handle.capabilities.canSearch
    )).toBe(true);
  });

  it('keeps project blueprint seeds ready for fixture and backend snapshot refresh', () => {
    const portfolio = createDemoPortfolio();
    const issues = validateProjectBlueprintSeeds(Object.entries(portfolio.workspacesByProjectId).map(([projectId, workspace]) => ({
      projectId,
      workspace,
      readyScenarioId: demoPortfolioBenchmarkExpectations[projectId as keyof typeof demoPortfolioBenchmarkExpectations]?.readyScenarioId
    })));

    expect(issues).toEqual([]);
  });
});
