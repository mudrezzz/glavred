import { describe, expect, it } from 'vitest';
import {
  approveFinalText,
  approvePlanItem,
  approvePostBrief,
  acceptCandidateToArchive,
  acceptCandidateToMemory,
  bulkAcceptCandidatesToArchive,
  completeTopicFabulaMatrix,
  createDefaultTopicFabulaMatrix,
  createEditorialRule,
  deleteEditorialRule,
  filterImportCandidates,
  getRulesByGroup,
  getTopicFabulaWarnings,
  groupImportCandidates,
  normalizeWeightRange,
  markCandidateAcceptedToMemory,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  rejectPlanItem,
  rejectPostBrief,
  undoLastBulkImportAction,
  updateEditorialRule,
  validateEditorialSetup,
  reviseDraft,
  toggleReleaseChecklistItem,
  updateLearningNote
} from './editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createAuthorMemoryEvent,
  createContentPlanItem,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
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
