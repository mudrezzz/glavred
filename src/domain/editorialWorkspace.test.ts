import { describe, expect, it, vi } from 'vitest';
import {
  addFabula,
  addRadar,
  addTopic,
  approveFinalText,
  approvePlanItem,
  approvePostCandidate,
  approvePostBrief,
  approveSignal,
  acceptCandidateToArchive,
  acceptCandidateToMemory,
  archiveSignal,
  bulkAcceptCandidatesToArchive,
  completeTopicFabulaMatrix,
  correctSignal,
  createFabulaDraft,
  createDefaultRadarEditorialFilters,
  createDefaultTopicFabulaMatrix,
  createEditorialRule,
  createEditorialWorkItem,
  createEditorialValidationRun,
  createRadarDraft,
  createTopicDraft,
  deleteRadar,
  deleteFabula,
  deleteEditorialRule,
  deleteTopic,
  detectBroadcastPlanConflicts,
  editPostCandidate,
  evaluateSignalAgainstRadarFilters,
  filterImportCandidates,
  getRulesByGroup,
  getTopicFabulaWarnings,
  isRadarSourceConfigurationValid,
  groupImportCandidates,
  normalizeWeightRange,
  markCandidateAcceptedToMemory,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  rejectPostCandidate,
  rejectSignal,
  rejectPlanItem,
  rejectPostBrief,
  syncEditorialWorkItemArtifacts,
  undoLastBulkImportAction,
  updateEditorialRule,
  validateEditorialSetup,
  runEditorialSetupValidators,
  reviseDraft,
  toggleReleaseChecklistItem,
  toggleRadarStatus,
  updateRadar,
  updateLearningNote
} from './editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createAuthorMemoryEvent,
  createBroadcastPlan,
  createContentPlanItem,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostCandidates,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
  createWorkspaceInsightCard,
  inferAuthorPositionAssertions,
  runEditorialChecks
} from '../application/editorialServices';

describe('editorial workspace domain', () => {
  it('keeps approval transitions explicit for plan items and post briefs', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = createPostBrief(planItem, insight, workspace.editorialModel);

    expect(approvePlanItem(planItem).approvalStatus).toBe('approved');
    expect(rejectPlanItem(planItem).approvalStatus).toBe('rejected');
    expect(approvePostBrief(brief).approvalStatus).toBe('approved');
    expect(rejectPostBrief(brief).approvalStatus).toBe('rejected');
  });

  it('creates deterministic outputs for the AI Product Manager demo signal', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(
      workspace.sourceSignal,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );
    const planItem = createContentPlanItem(insight);
    const brief = createPostBrief(
      planItem,
      insight,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );

    expect(insight.title).toContain('AI-B2B');
    expect(insight.score).toBeGreaterThan(0.8);
    expect(insight.topicTitle).toBe('AI product discovery');
    expect(insight.fabulaTitle).toBe('Исследовательская заметка');
    expect(planItem.platform).toBe('Telegram');
    expect(planItem.approvalStatus).toBe('draft');
    expect(planItem.topicTitle).toBe('AI product discovery');
    expect(brief.thesis).toContain('AI-B2B продукт');
    expect(brief.topicTitle).toBe('AI product discovery');
    expect(brief.structure[0]).toContain('Исследовательская заметка');
  });

  it('keeps demo radars and reviewed source signals as the material intake layer', () => {
    const workspace = createDemoWorkspace();

    expect(workspace.radars).toHaveLength(4);
    expect(workspace.radars[0].rules.length).toBeGreaterThan(0);
    expect(workspace.radars[0].sources.length).toBeGreaterThan(0);
    expect(workspace.sourceSignals.length).toBeGreaterThan(5);
    expect(workspace.sourceSignals[0].suggestedTopicId).toBeDefined();
    expect(workspace.sourceSignals[0].evidence?.length).toBeGreaterThan(0);
    expect(workspace.sourceSignals.some((signal) => signal.reviewStatus === 'approved')).toBe(true);
    expect(workspace.sourceSignals.some((signal) => signal.reviewStatus === 'new')).toBe(true);
    expect(workspace.sourceSignal.id).toBe(workspace.sourceSignals[0].id);
    expect(workspace.sourceSignal.reviewStatus).toBe('approved');
  });

  it('assembles deterministic post candidates only from approved source signals', () => {
    const workspace = createDemoWorkspace();
    const candidates = createPostCandidates(workspace);
    const approvedSignalIds = new Set(
      workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved').map((signal) => signal.id)
    );

    expect(candidates.length).toBeGreaterThanOrEqual(2);
    expect(candidates.length).toBeLessThanOrEqual(3);
    expect(candidates.every((candidate) => approvedSignalIds.has(candidate.sourceSignalId))).toBe(true);
    expect(candidates[0]).toMatchObject({
      platform: workspace.contentPlanSettings.defaultPlatform,
      audience: workspace.editorialModel.audience,
      approvalStatus: 'draft'
    });
    expect(candidates[0].topicId).toBeTruthy();
    expect(candidates[0].fabulaId).toBeTruthy();
    expect(candidates[0].value).toBeTruthy();
    expect(candidates[0].goal).toBeTruthy();
    expect(candidates[0]).not.toHaveProperty('format');
  });

  it('returns no post candidates when no source signal is approved', () => {
    const workspace = createDemoWorkspace();
    const withoutApprovedSignals = {
      ...workspace,
      sourceSignals: workspace.sourceSignals.map((signal) => ({ ...signal, reviewStatus: 'new' as const }))
    };

    expect(createPostCandidates(withoutApprovedSignals)).toEqual([]);
  });

  it('creates insight from the approved post candidate concept', () => {
    const workspace = createDemoWorkspace();
    const approvedCandidate = approvePostCandidate(createPostCandidates(workspace)[1]);
    const insight = createWorkspaceInsightCard({ ...workspace, postCandidate: approvedCandidate });

    expect(insight.id).toBe(`insight-${approvedCandidate.id}`);
    expect(insight.title).toBe(approvedCandidate.title);
    expect(insight.signalId).toBe(approvedCandidate.sourceSignalId);
    expect(insight.topicId).toBe(approvedCandidate.topicId);
    expect(insight.fabulaId).toBe(approvedCandidate.fabulaId);
    expect(insight.authorPosition).toBe(approvedCandidate.value);
    expect(insight.factGaps).toEqual(approvedCandidate.risks);
  });

  it('edits and rejects post candidates without silently approving them', () => {
    const workspace = createDemoWorkspace();
    const candidate = createPostCandidates(workspace)[0];
    const edited = editPostCandidate(candidate, {
      fabulaId: workspace.fabulas[1].id,
      title: 'Edited candidate',
      thesis: 'Edited thesis',
      audience: candidate.audience,
      value: 'Edited value',
      goal: candidate.goal,
      platform: candidate.platform,
      evidenceSummary: candidate.evidenceSummary,
      risks: ['Проверить edited risk']
    });
    const rejected = rejectPostCandidate(edited);
    const approvedAttempt = approvePostCandidate(rejected);

    expect(edited.approvalStatus).toBe('draft');
    expect(edited.fabulaId).toBe(workspace.fabulas[1].id);
    expect(edited.title).toBe('Edited candidate');
    expect(edited.value).toBe('Edited value');
    expect(rejected.approvalStatus).toBe('rejected');
    expect(approvedAttempt.approvalStatus).toBe('rejected');
  });

  it('ignores non-approved post candidates when creating a workspace insight', () => {
    const workspace = createDemoWorkspace();
    const draftCandidate = { ...createPostCandidates(workspace)[1], title: 'Draft candidate title' };
    const rejectedCandidate = rejectPostCandidate({ ...draftCandidate, title: 'Rejected candidate title' });
    const draftInsight = createWorkspaceInsightCard({ ...workspace, postCandidate: draftCandidate });
    const rejectedInsight = createWorkspaceInsightCard({ ...workspace, postCandidate: rejectedCandidate });

    expect(draftInsight.title).not.toBe('Draft candidate title');
    expect(rejectedInsight.title).not.toBe('Rejected candidate title');
  });

  it('creates insight from an approved edited post candidate', () => {
    const workspace = createDemoWorkspace();
    const candidate = approvePostCandidate(createPostCandidates(workspace)[1]);
    const edited = editPostCandidate(candidate, {
      fabulaId: workspace.fabulas[1].id,
      title: 'Approved edited candidate title',
      thesis: candidate.thesis,
      audience: candidate.audience,
      value: 'Edited approved value',
      goal: candidate.goal,
      platform: candidate.platform,
      evidenceSummary: candidate.evidenceSummary,
      risks: candidate.risks
    });
    const insight = createWorkspaceInsightCard({ ...workspace, postCandidate: edited });

    expect(edited.approvalStatus).toBe('approved');
    expect(insight.title).toBe('Approved edited candidate title');
    expect(insight.authorPosition).toBe('Edited approved value');
    expect(insight.fabulaId).toBe(workspace.fabulas[1].id);
  });

  it('transitions source signals through approve, reject, archive, and correction states', () => {
    const workspace = createDemoWorkspace();
    const signal = workspace.sourceSignals.find((item) => item.reviewStatus === 'new')!;
    const corrected = correctSignal(signal, {
      suggestedValue: 'Trust loop value for enterprise rollout.',
      authorCorrection: 'Move this signal to trust rollout, not generic discovery.'
    });

    expect(approveSignal(signal).reviewStatus).toBe('approved');
    expect(rejectSignal(signal).reviewStatus).toBe('rejected');
    expect(archiveSignal(signal).reviewStatus).toBe('archived');
    expect(corrected.reviewStatus).toBe('corrected');
    expect(corrected.suggestedValue).toContain('Trust loop');
    expect(corrected.authorCorrection).toContain('trust rollout');
    expect(corrected.title).toBe(signal.title);
  });

  it('creates, updates, toggles, and deletes configurable radars', () => {
    const workspace = createDemoWorkspace();
    const draft = {
      ...createRadarDraft(),
      title: 'AI policy radar',
      rules: [
        {
          id: 'rule-policy',
          operator: 'and' as const,
          negate: false,
          statement: 'Искать изменения в enterprise AI policy.',
          status: 'active' as const
        }
      ],
      sources: [
        {
          id: 'source-policy',
          type: 'searchKeywords' as const,
          title: 'Policy search',
          value: 'enterprise AI policy rollout',
          notes: '',
          status: 'active' as const
        }
      ]
    };

    const added = addRadar(workspace.radars, draft);
    const paused = toggleRadarStatus(draft);
    const updated = updateRadar(added, { ...paused, notes: 'Run only on planning deficit.' });
    const removed = deleteRadar(updated, draft.id);

    expect(added).toHaveLength(workspace.radars.length + 1);
    expect(added[added.length - 1].rules[0].statement).toContain('enterprise AI policy');
    expect(updated.find((radar) => radar.id === draft.id)?.status).toBe('paused');
    expect(updated.find((radar) => radar.id === draft.id)?.notes).toContain('planning deficit');
    expect(removed.some((radar) => radar.id === draft.id)).toBe(false);
  });

  it('models radar source discovery and editorial filters without using style as a filter', () => {
    const workspace = createDemoWorkspace();
    const draft = createRadarDraft();
    const dimensions = createDefaultRadarEditorialFilters('radar-test').map((filter) => filter.dimension);

    expect(draft.sourceDiscoveryMode).toBe('autonomous');
    expect(draft.filters).toHaveLength(6);
    expect(dimensions).toEqual(['author', 'audience', 'positioning', 'goals', 'forbiddenTopics', 'topics']);
    expect(dimensions).not.toContain('style');
    expect(isRadarSourceConfigurationValid({ ...draft, sourceDiscoveryMode: 'specifiedOnly', sources: [] })).toBe(false);
    expect(isRadarSourceConfigurationValid({ ...draft, sourceDiscoveryMode: 'autonomous', sources: [] })).toBe(true);
    expect(workspace.radars.every((radar) => radar.sourceDiscoveryMode)).toBe(true);
    expect(workspace.radars.some((radar) => radar.filters?.some((filter) => filter.mode === 'seekTension'))).toBe(true);
  });

  it('evaluates signals against radar filters deterministically without hiding failed material', () => {
    const workspace = createDemoWorkspace();
    const radar = {
      ...workspace.radars[0],
      filters: createDefaultRadarEditorialFilters(workspace.radars[0].id, ['positioning', 'forbiddenTopics'])
    };
    const rejected = evaluateSignalAgainstRadarFilters(
      {
        ...workspace.sourceSignals[0],
        title: 'Гарантированные прогнозы рынка AI без workflow',
        summary: 'AI-хайп обещает универсальную автоматизацию и гарантированные прогнозы рынка.',
        rawNote: 'Гарантированные прогнозы рынка, model-first hype и магическое мышление про модели.'
      },
      radar,
      workspace
    );
    const passed = evaluateSignalAgainstRadarFilters(workspace.sourceSignals[0], radar, workspace);

    expect(passed.filterEvaluations?.length).toBe(2);
    expect(passed.filterStatus).toBe('passed');
    expect(rejected.id).toBe(workspace.sourceSignals[0].id);
    expect(rejected.filterStatus).toBe('rejected');
    expect(rejected.filterEvaluations?.some((evaluation) => evaluation.status === 'failed')).toBe(true);
  });

  it('creates a deterministic broadcast grid with compatible topic and fabula slots', () => {
    const workspace = createDemoWorkspace();
    const items = createBroadcastPlan(workspace);
    const warnings = detectBroadcastPlanConflicts(workspace, items);

    expect(items.length).toBeGreaterThan(1);
    expect(items.every((item) => item.platform === 'Telegram')).toBe(true);
    expect(items.every((item) => item.topicId && item.fabulaId)).toBe(true);
    expect(items.every((item) => item.manualOverride === false)).toBe(true);
    expect(warnings.every((warning) => warning.targetType !== 'slot' || !warning.message.includes('не включены'))).toBe(true);
  });

  it('creates stable editorial work items from approved broadcast slots and syncs artifacts', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const brief = approvePostBrief(createPostBrief(item, createWorkspaceInsightCard(workspace), workspace.editorialModel));
    const workItem = createEditorialWorkItem(item, { brief }, 'candidate-test');
    const draft = createPostDraft(brief, workspace.editorialModel);
    const synced = syncEditorialWorkItemArtifacts([workItem], workItem.id, {
      brief,
      draft,
      editorialChecks: [],
      editorNotes: [],
      finalText: null
    });

    expect(workItem.id).toBe(`editorial-work-${item.id}`);
    expect(workItem.contentPlanItemId).toBe(item.id);
    expect(workItem.postCandidateId).toBe('candidate-test');
    expect(workItem.sourceSignalId).toBe(item.sourceSignalId);
    expect(workItem.topicTitle).toBe(item.topicTitle);
    expect(workItem.fabulaTitle).toBe(item.fabulaTitle);
    expect(workItem.stage).toBe('draft');
    expect(synced[0].stage).toBe('final');
    expect(synced[0].draft?.briefId).toBe(brief.id);
  });

  it('detects broadcast grid conflicts for incompatible matrix pairs and paused entities', () => {
    const workspace = createDemoWorkspace();
    const items = createBroadcastPlan(workspace);
    const changed = {
      ...workspace,
      topics: workspace.topics.map((topic, index) => index === 0 ? { ...topic, status: 'paused' as const } : topic),
      topicFabulaMatrix: workspace.topicFabulaMatrix.map((entry) =>
        entry.topicId === items[0].topicId && entry.fabulaId === items[0].fabulaId
          ? { ...entry, enabled: false }
          : entry
      )
    };
    const warnings = detectBroadcastPlanConflicts(changed, items);

    expect(warnings.some((warning) => warning.id.startsWith('slot-paused-topic'))).toBe(true);
    expect(warnings.some((warning) => warning.id.startsWith('slot-matrix'))).toBe(true);
  });

  it('normalizes topic and fabula weights and detects compatibility warnings', () => {
    const workspace = createDemoWorkspace();
    const topic = workspace.topics[0];
    const fabula = workspace.fabulas[0];
    const fullMatrix = createDefaultTopicFabulaMatrix(workspace.topics, workspace.fabulas);
    const isolatedMatrix = completeTopicFabulaMatrix(workspace.topics, workspace.fabulas, fullMatrix).map((entry) =>
      entry.topicId === topic.id || entry.fabulaId === fabula.id ? { ...entry, enabled: false } : entry
    );
    const warnings = getTopicFabulaWarnings(workspace.topics, workspace.fabulas, isolatedMatrix);

    expect(normalizeWeightRange({ min: 120, max: -10 })).toEqual({ min: 0, max: 100 });
    expect(fullMatrix).toHaveLength(workspace.topics.length * workspace.fabulas.length);
    expect(warnings.some((warning) => warning.targetType === 'topic' && warning.targetId === topic.id)).toBe(true);
    expect(warnings.some((warning) => warning.targetType === 'fabula' && warning.targetId === fabula.id)).toBe(true);
  });

  it('creates, adds, and deletes topics and fabulas with matrix links', () => {
    const workspace = createDemoWorkspace();
    const now = vi.spyOn(Date, 'now').mockReturnValue(123456);
    const topicDraft = { ...createTopicDraft(), title: 'AI trust onboarding' };
    const fabulaDraft = { ...createFabulaDraft(), title: 'Field note' };
    now.mockRestore();

    const topicsWithNew = addTopic(workspace.topics, topicDraft);
    const matrixWithTopic = completeTopicFabulaMatrix(topicsWithNew, workspace.fabulas, workspace.topicFabulaMatrix);
    const topicEntries = matrixWithTopic.filter((entry) => entry.topicId === topicDraft.id);
    const fabulasWithNew = addFabula(workspace.fabulas, fabulaDraft);
    const matrixWithFabula = completeTopicFabulaMatrix(workspace.topics, fabulasWithNew, workspace.topicFabulaMatrix);
    const fabulaEntries = matrixWithFabula.filter((entry) => entry.fabulaId === fabulaDraft.id);
    const deletedTopic = deleteTopic(topicsWithNew, matrixWithTopic, topicDraft.id);
    const deletedFabula = deleteFabula(fabulasWithNew, matrixWithFabula, fabulaDraft.id);

    expect(topicDraft.id).toBe('topic-custom-123456');
    expect(fabulaDraft.id).toBe('fabula-custom-123456');
    expect(topicDraft.weightRange).toEqual({ min: 5, max: 15 });
    expect(fabulaDraft.weightRange).toEqual({ min: 5, max: 15 });
    expect(topicEntries).toHaveLength(workspace.fabulas.length);
    expect(topicEntries.every((entry) => entry.enabled)).toBe(true);
    expect(fabulaEntries).toHaveLength(workspace.topics.length);
    expect(fabulaEntries.every((entry) => entry.enabled)).toBe(true);
    expect(deletedTopic.topics.some((topic) => topic.id === topicDraft.id)).toBe(false);
    expect(deletedTopic.matrix.some((entry) => entry.topicId === topicDraft.id)).toBe(false);
    expect(deletedFabula.fabulas.some((fabula) => fabula.id === fabulaDraft.id)).toBe(false);
    expect(deletedFabula.matrix.some((entry) => entry.fabulaId === fabulaDraft.id)).toBe(false);
  });

  it('keeps project profile and editorial rules as structured demo entities', () => {
    const workspace = createDemoWorkspace();
    const validation = validateEditorialSetup(workspace);

    expect(workspace.projectProfile.name).toBe('TG-блог AI Product Manager');
    expect(workspace.editorialRules.length).toBeGreaterThan(10);
    expect(getRulesByGroup(workspace.editorialRules, 'antiAiPattern').length).toBeGreaterThan(0);
    expect(validation.items.some((item) => item.status === 'green')).toBe(true);
    expect(validation.items.some((item) => item.status === 'yellow')).toBe(true);
    expect(validation.items.some((item) => item.recommendation.length > 0)).toBe(true);
  });

  it('runs editorial setup validators with scores, evidence, and suggestions', () => {
    const workspace = createDemoWorkspace();
    const run = runEditorialSetupValidators(workspace);
    const validationRun = createEditorialValidationRun(workspace, '2026-06-11T10:00:00.000Z');

    expect(run.results.map((result) => result.validatorId)).toEqual([
      'author-position-clarity',
      'anti-ai-style-coverage',
      'audience-value-fit',
      'goal-consistency',
      'topic-fabula-coverage'
    ]);
    expect(run.results.every((result) => result.score >= 0 && result.score <= 1)).toBe(true);
    expect(run.results.every((result) => Array.isArray(result.evidence))).toBe(true);
    expect(run.results.every((result) => Array.isArray(result.suggestions))).toBe(true);
    expect(run.results.some((result) => result.status === 'green')).toBe(true);
    expect(run.results.some((result) => result.status === 'yellow')).toBe(true);
    expect(run.results.some((result) => result.suggestions.length > 0)).toBe(true);
    expect(validationRun.checkedAt).toBe('2026-06-11T10:00:00.000Z');
    expect(validationRun.results).toHaveLength(5);
    expect(validationRun.aggregateScore).toBeGreaterThan(0);
  });

  it('degrades validators when anti-AI rules or matrix links are missing', () => {
    const workspace = createDemoWorkspace();
    const withoutAntiAi = {
      ...workspace,
      editorialRules: workspace.editorialRules.filter((rule) => rule.group !== 'antiAiPattern')
    };
    const antiAiResult = runEditorialSetupValidators(withoutAntiAi).results.find(
      (result) => result.validatorId === 'anti-ai-style-coverage'
    );
    const brokenMatrix = {
      ...workspace,
      topicFabulaMatrix: workspace.topicFabulaMatrix.map((entry) =>
        entry.topicId === workspace.topics[0].id ? { ...entry, enabled: false } : entry
      )
    };
    const matrixResult = runEditorialSetupValidators(brokenMatrix).results.find(
      (result) => result.validatorId === 'topic-fabula-coverage'
    );

    expect(['yellow', 'red']).toContain(antiAiResult?.status);
    expect(antiAiResult?.suggestions[0]?.id).toBe('anti-ai-missing');
    expect(matrixResult?.status).toBe('red');
    expect(matrixResult?.evidence.some((item) => item.sourceId === workspace.topics[0].id)).toBe(true);
  });

  it('adds, updates, and deletes editorial rules without changing unrelated rules', () => {
    const workspace = createDemoWorkspace();
    const rule = createEditorialRule('author', 'Тестовое правило', 'Проверять авторскую оптику.');
    const withRule = [rule, ...workspace.editorialRules];
    const updated = updateEditorialRule(withRule, { ...rule, statement: 'Проверять авторскую исследовательскую оптику.' });
    const deleted = deleteEditorialRule(updated, rule.id);

    expect(withRule[0].title).toBe('Тестовое правило');
    expect(updated.find((item) => item.id === rule.id)?.statement).toContain('исследовательскую');
    expect(deleted.find((item) => item.id === rule.id)).toBeUndefined();
    expect(deleted.length).toBe(workspace.editorialRules.length);
  });

  it('creates author memory events and evidence-backed position assertions', () => {
    const workspace = createDemoWorkspace();
    const note = workspace.authorNotes[0];
    const event = createAuthorMemoryEvent(note);
    const assertions = inferAuthorPositionAssertions(workspace.authorNotes, workspace.authorMemoryEvents);

    expect(note.type).toBe('thought');
    expect(note.title).toContain('Workflow risk');
    expect(note.tags).toContain('workflow');
    expect(event.noteId).toBe(note.id);
    expect(event.detectedSignals).toContain('workflow-risk');
    expect(assertions).toHaveLength(5);
    expect(assertions[0].evidence.length).toBeGreaterThan(0);
    expect(assertions.some((assertion) => assertion.statement.includes('AI-B2B'))).toBe(true);
  });

  it('strengthens author-position evidence when a relevant note is added', () => {
    const workspace = createDemoWorkspace();
    const note = {
      id: 'note-extra-evals',
      type: 'thought' as const,
      title: 'Evals как доверие',
      body: 'Еще одна мысль: evals нужны не только команде, но и пользователю как интерфейс доверия к AI-фиче.',
      sourceUrl: '',
      tags: ['evals', 'trust'],
      attachments: [],
      capturedAt: '2026-06-10T12:00:00.000Z'
    };
    const notes = [note, ...workspace.authorNotes];
    const events = [createAuthorMemoryEvent(note), ...workspace.authorMemoryEvents];
    const assertions = inferAuthorPositionAssertions(notes, events);
    const topicAssertion = assertions.find((assertion) => assertion.type === 'topic');

    expect(topicAssertion?.evidence.some((item) => item.noteId === note.id)).toBe(true);
  });

  it('supports titleless notes and targeted manual correction metadata', () => {
    const note = {
      id: 'note-titleless-correction',
      type: 'manualCorrection' as const,
      title: '',
      body: 'Не согласен: вывод про стиль нужно сделать жестче и привязать к anti-demo позиции.',
      sourceUrl: '',
      tags: ['manual-correction'],
      attachments: [],
      capturedAt: '2026-06-10T12:00:00.000Z',
      targetType: 'assertion' as const,
      targetId: 'assertion-style-research-notes',
      targetTitle: 'Стиль: исследовательские заметки без демо-магии'
    };

    const event = createAuthorMemoryEvent(note);

    expect(event.summary).toContain('Не согласен');
    expect(note.targetType).toBe('assertion');
    expect(note.targetId).toBe('assertion-style-research-notes');
  });

  it('marks notes with attachments as attached material without analyzing file content', () => {
    const note = {
      id: 'note-with-attachment',
      type: 'thought' as const,
      title: '',
      body: 'Прикладываю материал к мысли про workflow risk.',
      sourceUrl: '',
      tags: ['workflow'],
      attachments: [
        {
          id: 'attachment-test',
          fileName: 'workflow-note.txt',
          mimeType: 'text/plain',
          sizeBytes: 128,
          dataUrl: 'data:text/plain;base64,d29ya2Zsb3c=',
          createdAt: '2026-06-10T12:00:00.000Z',
          localOnly: true
        }
      ],
      capturedAt: '2026-06-10T12:00:00.000Z'
    };

    const event = createAuthorMemoryEvent(note);

    expect(event.detectedSignals).toContain('attached-material');
    expect(event.detectedSignals).toContain('workflow-risk');
  });

  it('accepts import candidates to memory as author notes', () => {
    const workspace = createDemoWorkspace();
    const candidate = workspace.importCandidates.find((item) => item.evidencePolicy === 'canSupportAssertions');
    expect(candidate).toBeDefined();
    const source = workspace.externalSources.find((item) => item.id === candidate?.sourceId);
    expect(source).toBeDefined();

    const note = acceptCandidateToMemory(candidate!, source!);
    const updatedCandidate = markCandidateAcceptedToMemory(candidate!);

    expect(note.id).toBe(`note-import-${candidate!.id}`);
    expect(note.type).toBe('linkReaction');
    expect(note.tags).toContain('imported');
    expect(updatedCandidate.reviewStatus).toBe('acceptedToMemory');
    expect(updatedCandidate.evidencePolicy).toBe('canSupportAssertions');
  });

  it('accepts import candidates to archive without creating author notes', () => {
    const workspace = createDemoWorkspace();
    const candidate = workspace.importCandidates[0];
    const source = workspace.externalSources.find((item) => item.id === candidate.sourceId)!;
    const record = acceptCandidateToArchive(candidate, source);

    expect(record.id).toBe(`archive-${candidate.id}`);
    expect(record.title).toBe(candidate.title);
    expect(record.evidencePolicy).toBe(candidate.evidencePolicy);
    expect(record.acceptanceMode).toBe('manual');
  });

  it('bulk archives filtered candidates and can undo the latest bulk action', () => {
    const workspace = createDemoWorkspace();
    const filtered = filterImportCandidates(workspace.importCandidates, {
      sourceId: 'source-tg-archive',
      reviewStatus: 'new',
      evidencePolicy: 'archiveOnly',
      duplicateRisk: 'all'
    });
    const result = bulkAcceptCandidatesToArchive(filtered, workspace.externalSources);
    const changedById = new Map(result.candidates.map((candidate) => [candidate.id, candidate]));
    const changedWorkspace = {
      ...workspace,
      importCandidates: workspace.importCandidates.map((candidate) => changedById.get(candidate.id) ?? candidate),
      archiveRecords: [...result.archiveRecords, ...workspace.archiveRecords],
      bulkImportActions: [result.action]
    };
    const restored = undoLastBulkImportAction(changedWorkspace);

    expect(filtered.length).toBeGreaterThan(0);
    expect(result.candidates.every((candidate) => candidate.reviewStatus === 'bulkAcceptedToArchive')).toBe(true);
    expect(result.archiveRecords.every((record) => record.acceptanceMode === 'bulk')).toBe(true);
    expect(restored.bulkImportActions).toEqual([]);
    expect(restored.archiveRecords.some((record) => result.action.createdArchiveRecordIds.includes(record.id))).toBe(false);
    expect(restored.importCandidates.find((candidate) => candidate.id === filtered[0].id)?.reviewStatus).toBe('new');
  });

  it('groups import candidates without changing author-position assertions', () => {
    const workspace = createDemoWorkspace();
    const beforeAssertions = workspace.authorPositionAssertions;
    const groups = groupImportCandidates(workspace.importCandidates, 'source');
    const archiveOnly = workspace.importCandidates.filter((candidate) => candidate.evidencePolicy === 'archiveOnly');

    expect(groups.length).toBeGreaterThan(1);
    expect(archiveOnly.length).toBeGreaterThan(0);
    expect(workspace.authorPositionAssertions).toBe(beforeAssertions);
  });

  it('creates a deterministic draft with thesis, conflict, and CTA from an approved brief', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);

    expect(draft.briefId).toBe(brief.id);
    expect(draft.body).toContain(brief.thesis);
    expect(draft.body).toContain(brief.conflict);
    expect(draft.body).toContain(brief.cta);
  });

  it('creates four editorial checks in a stable order with fact-check warnings', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const checks = runEditorialChecks(draft, brief, workspace.editorialModel);
    const notes = createEditorNotes(checks);

    expect(checks.map((check) => check.type)).toEqual(['style', 'antiAi', 'factCheck', 'policy']);
    expect(checks.find((check) => check.type === 'factCheck')?.status).toBe('warning');
    expect(notes).toHaveLength(4);
  });

  it('revises a draft and approves final text from the current draft body', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const revised = reviseDraft(draft, `${draft.body}\n\nРучная редакторская правка перед финалом.`);
    const finalText = approveFinalText(revised);

    expect(revised.version).toBe(2);
    expect(revised.status).toBe('revised');
    expect(finalText.approvalStatus).toBe('approved');
    expect(finalText.body).toContain('Ручная редакторская правка');
  });

  it('creates a release package from approved final text with platform targets and markdown', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);

    expect(releasePackage.targets).toEqual(['telegram']);
    expect(releasePackage.markdown).toContain(finalText.title);
    expect(releasePackage.markdown).toContain(finalText.body);
    expect(releasePackage.markdown).toContain('Telegram');
    expect(releasePackage.status).toBe('draft');
  });

  it('does not create a release package from a non-approved final text', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = { ...approveFinalText(draft), approvalStatus: 'draft' as const };

    expect(() => createReleasePackage(finalText, planItem)).toThrow(/approved final text/i);
  });

  it('marks release ready only after checklist completion and then exported', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);

    expect(markReleaseReady(releasePackage).status).toBe('draft');

    const completed = releasePackage.checklist.reduce(
      (current, item) => (item.done ? current : toggleReleaseChecklistItem(current, item.id)),
      releasePackage
    );

    expect(markReleaseReady(completed).status).toBe('ready');
    expect(markReleaseExported(completed).status).toBe('exported');
  });

  it('creates analytics scaffold only after manual export', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);
    const exported = markReleaseExported(releasePackage);
    const note = createEditorialLearningNote(exported, finalText, planItem);

    expect(() => createEditorialLearningNote(releasePackage, finalText, planItem)).toThrow(/manual export/i);
    expect(note.releasePackageId).toBe(exported.id);
    expect(note.metricSnapshot).toEqual({ views: 0, reactions: 0, comments: 0, saves: 0, leads: 0 });
    expect(note.status).toBe('draft');
  });

  it('captures and reopens editorial learning notes after edits', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const exported = markReleaseExported(createReleasePackage(finalText, planItem));
    const note = createEditorialLearningNote(exported, finalText, planItem);
    const captured = markLearningNoteCaptured(note);
    const updated = updateLearningNote(captured, {
      observedResult: 'Тезис про demo-to-adoption gap собрал комментарии AI PM и founders.'
    });

    expect(captured.status).toBe('captured');
    expect(captured.capturedAt).not.toBeNull();
    expect(updated.status).toBe('draft');
    expect(updated.capturedAt).toBeNull();
    expect(updated.observedResult).toContain('demo-to-adoption');
  });
});
