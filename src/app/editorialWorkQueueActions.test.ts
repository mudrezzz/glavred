import { describe, expect, it } from 'vitest';
import { createPostDraft } from '../application/editorialServices';
import { approveFinalText, approvePostBrief } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  buildApproveBriefAndCreateDraftPatch,
  buildApproveDraftTextPatch,
  buildApproveVisualPatch,
  buildApprovePlanSlotPatch,
  buildEditCurrentBriefPatch,
  buildPrepareMemeReferencesPatch,
  buildPrepareMemeRemixVariantsPatch,
  buildPrepareVisualVariantsPatch,
  buildPrepareBriefPatch,
  buildReturnEditorialWorkItemToCandidatesPatch,
  buildSaveDraftTextPatch,
  buildSaveVisualDraftPatch,
  buildSelectMemeReferencePatch,
  buildSelectVisualVariantPatch,
  buildSelectEditorialWorkItemPatch,
  withEditorialWorkItemSync
} from './editorialWorkQueueActions';
import { createEditorialLearningNote, createReleasePackage } from '../application/editorialServices';

describe('editorial work queue actions', () => {
  it('approves a plan slot into one stable editorial work item', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const firstPatch = buildApprovePlanSlotPatch(workspace, item.id);
    const secondPatch = buildApprovePlanSlotPatch({ ...workspace, ...firstPatch }, item.id);

    expect(firstPatch.contentPlanItem?.id).toBe(item.id);
    expect(firstPatch.postBrief?.planItemId).toBe(item.id);
    expect(firstPatch.editorialWorkItems).toHaveLength(1);
    expect(firstPatch.editorialWorkItems?.[0].id).toBe(`editorial-work-${item.id}`);
    expect(firstPatch.editorialWorkItems?.[0].brief?.id).toBe(firstPatch.postBrief?.id);
    expect(firstPatch.selectedEditorialWorkItemId).toBe(`editorial-work-${item.id}`);
    expect(secondPatch.editorialWorkItems).toHaveLength(1);
  });

  it('keeps the recovered post candidate link when approving a plan slot', () => {
    const workspace = createDemoWorkspace();
    const signal = workspace.sourceSignals[0];
    const topic = workspace.topics[0];
    const fabula = workspace.fabulas[0];
    const candidate = {
      id: 'candidate-recovered',
      sourceSignalId: signal.id,
      topicId: topic.id,
      fabulaId: fabula.id,
      audience: 'AI PM',
      value: 'Показать adoption gap',
      goal: 'Собрать аудиторию',
      platform: 'Telegram',
      title: 'Demo не равно adoption',
      thesis: 'Пилот не доказывает регулярное использование.',
      evidenceSummary: 'Usage не стал регулярным после пилота.',
      confidence: 88,
      risks: ['Не звучать противником прототипов'],
      approvalStatus: 'approved' as const
    };
    const slot = {
      id: 'slot-recovered',
      insightId: 'insight-recovered',
      title: candidate.title,
      platform: 'Telegram',
      date: '2026-06-22',
      time: '10:00',
      priority: 'high',
      format: 'research',
      expectedEffect: 'Проверить adoption gap',
      sourceSignalId: signal.id,
      topicId: topic.id,
      topicTitle: topic.title,
      fabulaId: fabula.id,
      fabulaTitle: fabula.title,
      approvalStatus: 'draft' as const
    };
    const patch = buildApprovePlanSlotPatch(
      { ...workspace, contentPlanItems: [slot], postCandidates: [candidate], postCandidate: null },
      slot.id
    );

    expect(patch.editorialWorkItems?.[0].postCandidateId).toBe(candidate.id);
  });

  it('keeps selected work item artifacts tied to the chosen plan slot', () => {
    const workspace = createDemoWorkspace();
    const firstPatch = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withFirst = { ...workspace, ...firstPatch };
    const secondPatch = buildApprovePlanSlotPatch(withFirst, workspace.contentPlanItems[1].id);
    const withSecond = { ...withFirst, ...secondPatch };
    const firstSelected = buildSelectEditorialWorkItemPatch(withSecond, firstPatch.selectedEditorialWorkItemId!);
    const secondSelected = buildSelectEditorialWorkItemPatch(
      { ...withSecond, ...firstSelected },
      secondPatch.selectedEditorialWorkItemId!
    );

    expect(firstPatch.postBrief?.id).toBe(`brief-${workspace.contentPlanItems[0].id}`);
    expect(secondPatch.postBrief?.id).toBe(`brief-${workspace.contentPlanItems[1].id}`);
    expect(firstSelected.postBrief?.title).toBe(workspace.contentPlanItems[0].title);
    expect(secondSelected.postBrief?.title).toBe(workspace.contentPlanItems[1].title);
    expect(firstSelected.postBrief?.title).not.toBe(secondSelected.postBrief?.title);
  });

  it('approves a brief and creates the first draft in the selected work item', () => {
    const workspace = createDemoWorkspace();
    const approved = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const current = { ...workspace, ...approved };
    const patch = buildApproveBriefAndCreateDraftPatch(current);

    expect(patch.postBrief?.approvalStatus).toBe('approved');
    expect(patch.postDraft?.briefId).toBe(patch.postBrief?.id);
    expect(patch.editorialChecks?.length).toBeGreaterThan(0);
    expect(patch.editorNotes?.length).toBeGreaterThan(0);
    expect(patch.editorialWorkItems?.[0].brief?.approvalStatus).toBe('approved');
    expect(patch.editorialWorkItems?.[0].draft?.id).toBe(patch.postDraft?.id);
    expect(patch.editorialWorkItems?.[0].stage).toBe('draft');
  });

  it('approves draft text into visual readiness without marking the post ready for release', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const approvedBrief = buildApproveBriefAndCreateDraftPatch(withSlot);
    const withDraft = { ...withSlot, ...approvedBrief };
    const patch = buildApproveDraftTextPatch(withDraft, 'Approved text with inline edits');

    expect(patch.postDraft?.body).toBe('Approved text with inline edits');
    expect(patch.finalText?.body).toBe('Approved text with inline edits');
    expect(patch.finalText?.approvalStatus).toBe('approved');
    expect(patch.releasePackage).toBeNull();
    expect(patch.editorialLearningNote).toBeNull();
    expect(patch.editorialWorkItems?.[0].finalText?.id).toBe(patch.finalText?.id);
    expect(patch.editorialWorkItems?.[0].stage).toBe('visual');
    expect(patch.editorialWorkItems?.[0].status).toBe('todo');
  });

  it('saving draft edits clears stale approved text and release artifacts', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const approvedBrief = buildApproveBriefAndCreateDraftPatch(withSlot);
    const withDraft = { ...withSlot, ...approvedBrief };
    const approvedText = buildApproveDraftTextPatch(withDraft);
    const releasePackage = createReleasePackage(approvedText.finalText!, withDraft.contentPlanItem!);
    const editorialLearningNote = createEditorialLearningNote(
      { ...releasePackage, status: 'exported' as const },
      approvedText.finalText!,
      withDraft.contentPlanItem!
    );
    const visualPatch = buildApproveVisualPatch({ ...withDraft, ...approvedText }, {
      mode: 'generate',
      brief: 'Old visual brief',
      prompt: 'Old prompt'
    });
    const current = {
      ...withDraft,
      ...approvedText,
      ...visualPatch,
      releasePackage,
      editorialLearningNote
    };
    const patch = buildSaveDraftTextPatch(current, 'Saved revised draft');

    expect(patch.postDraft?.body).toBe('Saved revised draft');
    expect(patch.finalText).toBeNull();
    expect(patch.postVisual).toBeNull();
    expect(patch.releasePackage).toBeNull();
    expect(patch.editorialLearningNote).toBeNull();
    expect(patch.editorialWorkItems?.[0].draft?.body).toBe('Saved revised draft');
    expect(patch.editorialWorkItems?.[0].finalText).toBeNull();
    expect(patch.editorialWorkItems?.[0].visual).toBeNull();
    expect(patch.editorialWorkItems?.[0].stage).toBe('draft');
  });

  it('prepares, selects, and approves visual variants without marking the post ready for release', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const approvedBrief = buildApproveBriefAndCreateDraftPatch(withSlot);
    const withDraft = { ...withSlot, ...approvedBrief };
    const approvedText = buildApproveDraftTextPatch(withDraft);
    const withText = { ...withDraft, ...approvedText };
    const prepared = buildPrepareVisualVariantsPatch(withText, {
      mode: 'memeSearch',
      brief: 'Найти мем про фальшивый прогресс после demo.'
    });
    const blockedApproval = buildApproveVisualPatch({ ...withText, ...prepared });
    const selected = buildSelectVisualVariantPatch(
      { ...withText, ...prepared },
      prepared.postVisual!.variants[1].id
    );
    const approved = buildApproveVisualPatch({ ...withText, ...prepared, ...selected });

    expect(prepared.postVisual?.mode).toBe('memeSearch');
    expect(prepared.postVisual?.brief).toBe('Найти мем про фальшивый прогресс после demo.');
    expect(prepared.postVisual?.memeSearchQuery).toBe('');
    expect(prepared.postVisual?.variants).toHaveLength(3);
    expect(prepared.postVisual?.selectedVariantId).toBeNull();
    expect(prepared.postVisual?.variantBatch).toBe(1);
    expect(prepared.postVisual?.approvalStatus).toBe('draft');
    expect(prepared.editorialWorkItems?.[0].visual?.id).toBe(prepared.postVisual?.id);
    expect(prepared.editorialWorkItems?.[0].stage).toBe('visual');
    expect(blockedApproval.postVisual?.approvalStatus).toBe('draft');
    expect(selected.postVisual?.selectedVariantId).toBe(prepared.postVisual?.variants[1].id);
    expect(approved.postVisual?.approvalStatus).toBe('approved');
    expect(approved.editorialWorkItems?.[0].visual?.approvalStatus).toBe('approved');
    expect(approved.editorialWorkItems?.[0].stage).toBe('visual');
    expect(approved.editorialWorkItems?.[0].stage).not.toBe('readyForRelease');
  });

  it('supports all visual modes as local placeholder variant artifacts', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const withDraft = { ...withSlot, ...buildApproveBriefAndCreateDraftPatch(withSlot) };
    const withText = { ...withDraft, ...buildApproveDraftTextPatch(withDraft) };

    expect(buildPrepareVisualVariantsPatch(withText, { mode: 'generate', brief: 'Сгенерировать образ про adoption gap' }).postVisual?.variants).toHaveLength(3);
    expect(buildPrepareVisualVariantsPatch(withText, { mode: 'memeSearch', brief: 'Найти мем про demo magic' }).postVisual?.variants).toHaveLength(3);
    expect(buildPrepareVisualVariantsPatch(withText, { mode: 'memeRemix', brief: 'Взять мем и кастомизировать под AI-B2B' })).toEqual({});
    expect(buildApproveVisualPatch(withText, { mode: 'noVisual', brief: '', notes: '' }).postVisual?.mode).toBe('noVisual');
  });

  it('keeps visual approval draft when selecting an unknown variant and resets variants after brief edits', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const withDraft = { ...withSlot, ...buildApproveBriefAndCreateDraftPatch(withSlot) };
    const withText = { ...withDraft, ...buildApproveDraftTextPatch(withDraft) };
    const prepared = buildPrepareVisualVariantsPatch(withText, {
      mode: 'generate',
      brief: 'Initial visual brief'
    });
    const unknownSelection = buildSelectVisualVariantPatch({ ...withText, ...prepared }, 'missing-variant');
    const selected = buildSelectVisualVariantPatch(
      { ...withText, ...prepared },
      prepared.postVisual!.variants[0].id
    );
    const approved = buildApproveVisualPatch({ ...withText, ...prepared, ...selected });
    const edited = buildSaveVisualDraftPatch({ ...withText, ...prepared, ...selected, ...approved }, {
      mode: 'generate',
      brief: 'Edited visual brief'
    });

    expect(unknownSelection.postVisual?.selectedVariantId).toBeNull();
    expect(approved.postVisual?.approvalStatus).toBe('approved');
    expect(edited.postVisual?.variants).toEqual([]);
    expect(edited.postVisual?.selectedVariantId).toBeNull();
    expect(edited.postVisual?.approvalStatus).toBe('draft');
  });

  it('requires a selected meme reference before generating and approving meme remix variants', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const withDraft = { ...withSlot, ...buildApproveBriefAndCreateDraftPatch(withSlot) };
    const withText = { ...withDraft, ...buildApproveDraftTextPatch(withDraft) };
    const oldOneStep = buildPrepareVisualVariantsPatch(withText, {
      mode: 'memeRemix',
      brief: 'Взять мем и сделать кастом про demo adoption gap'
    });
    const preparedReferences = buildPrepareMemeReferencesPatch(withText, {
      mode: 'memeRemix',
      brief: 'Взять мем и сделать кастом про demo adoption gap'
    });
    const blockedVariants = buildPrepareMemeRemixVariantsPatch({ ...withText, ...preparedReferences });
    const referenceSelection = buildSelectMemeReferencePatch(
      { ...withText, ...preparedReferences },
      preparedReferences.postVisual!.memeReferences[1].id
    );
    const blockedApproval = buildApproveVisualPatch({ ...withText, ...preparedReferences, ...referenceSelection });
    const remixVariants = buildPrepareMemeRemixVariantsPatch({ ...withText, ...preparedReferences, ...referenceSelection });
    const variantSelection = buildSelectVisualVariantPatch(
      { ...withText, ...preparedReferences, ...referenceSelection, ...remixVariants },
      remixVariants.postVisual!.variants[0].id
    );
    const approved = buildApproveVisualPatch({
      ...withText,
      ...preparedReferences,
      ...referenceSelection,
      ...remixVariants,
      ...variantSelection
    });

    expect(oldOneStep).toEqual({});
    expect(preparedReferences.postVisual?.memeReferences).toHaveLength(3);
    expect(preparedReferences.postVisual?.variants).toEqual([]);
    expect(blockedVariants).toEqual({});
    expect(referenceSelection.postVisual?.selectedMemeReferenceId).toBe(preparedReferences.postVisual?.memeReferences[1].id);
    expect(referenceSelection.postVisual?.selectedVariantId).toBeNull();
    expect(blockedApproval.postVisual?.approvalStatus).toBe('draft');
    expect(remixVariants.postVisual?.variants).toHaveLength(3);
    expect(remixVariants.postVisual?.selectedMemeReferenceId).toBe(preparedReferences.postVisual?.memeReferences[1].id);
    expect(variantSelection.postVisual?.selectedVariantId).toBe(remixVariants.postVisual?.variants[0].id);
    expect(approved.postVisual?.approvalStatus).toBe('approved');
    expect(approved.editorialWorkItems?.[0].stage).toBe('visual');
  });

  it('edits the selected brief and clears stale downstream artifacts', () => {
    const workspace = createDemoWorkspace();
    const approvedSlot = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withSlot = { ...workspace, ...approvedSlot };
    const approvedBrief = buildApproveBriefAndCreateDraftPatch(withSlot);
    const withDraft = { ...withSlot, ...approvedBrief };
    const finalText = approveFinalText(withDraft.postDraft!);
    const releasePackage = createReleasePackage(finalText, withDraft.contentPlanItem!);
    const editorialLearningNote = createEditorialLearningNote(
      { ...releasePackage, status: 'exported' as const },
      finalText,
      withDraft.contentPlanItem!
    );
    const current = {
      ...withDraft,
      finalText,
      releasePackage,
      editorialLearningNote,
      editorialWorkItems: withEditorialWorkItemSync(withDraft, {
        postBrief: withDraft.postBrief,
        postDraft: withDraft.postDraft,
        editorialChecks: withDraft.editorialChecks,
        editorNotes: withDraft.editorNotes,
        finalText
      }).editorialWorkItems!
    };
    const patch = buildEditCurrentBriefPatch(current, {
      title: 'Edited brief title',
      thesis: 'Edited thesis',
      conflict: current.postBrief!.conflict,
      authorPosition: current.postBrief!.authorPosition,
      audience: current.postBrief!.audience,
      evidence: ['Edited evidence'],
      examples: current.postBrief!.examples,
      structure: current.postBrief!.structure,
      cta: current.postBrief!.cta,
      risks: ['Edited risk'],
      sources: current.postBrief!.sources
    });

    expect(patch.postBrief?.title).toBe('Edited brief title');
    expect(patch.postBrief?.approvalStatus).toBe('draft');
    expect(patch.postDraft).toBeNull();
    expect(patch.editorialChecks).toEqual([]);
    expect(patch.editorNotes).toEqual([]);
    expect(patch.finalText).toBeNull();
    expect(patch.releasePackage).toBeNull();
    expect(patch.editorialLearningNote).toBeNull();
    expect(patch.editorialWorkItems?.[0].brief?.title).toBe('Edited brief title');
    expect(patch.editorialWorkItems?.[0].brief?.approvalStatus).toBe('draft');
    expect(patch.editorialWorkItems?.[0].draft).toBeNull();
    expect(patch.editorialWorkItems?.[0].finalText).toBeNull();
    expect(patch.editorialWorkItems?.[0].stage).toBe('brief');
  });

  it('returns an editorial work item to candidates and clears production artifacts', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const approved = buildApprovePlanSlotPatch(workspace, item.id);
    const current = { ...workspace, ...approved };
    const patch = buildReturnEditorialWorkItemToCandidatesPatch(current, approved.selectedEditorialWorkItemId!);

    expect(patch.contentPlanItems?.find((planItem) => planItem.id === item.id)?.approvalStatus).toBe('draft');
    expect(patch.editorialWorkItems).toEqual([]);
    expect(patch.selectedEditorialWorkItemId).toBeNull();
    expect(patch.postBrief).toBeNull();
    expect(patch.postDraft).toBeNull();
    expect(patch.finalText).toBeNull();
  });

  it('prepares a brief inside the selected work item and opens editing', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const patch = buildPrepareBriefPatch(workspace, item);

    expect(patch.activeSection).toBe('edit');
    expect(patch.postBrief?.planItemId).toBe(item.id);
    expect(patch.editorialWorkItems).toHaveLength(1);
    expect(patch.editorialWorkItems?.[0].brief?.id).toBe(patch.postBrief?.id);
    expect(patch.postDraft).toBeNull();
    expect(patch.finalText).toBeNull();
  });

  it('saves current compatibility artifacts before selecting another work item', () => {
    const workspace = createDemoWorkspace();
    const first = buildPrepareBriefPatch(workspace, workspace.contentPlanItems[0]);
    const second = buildPrepareBriefPatch(
      { ...workspace, ...first },
      workspace.contentPlanItems[1]
    );
    const selected = { ...workspace, ...second };
    const approvedBrief = approvePostBrief(selected.postBrief!);
    const postDraft = createPostDraft(approvedBrief, workspace.editorialModel);
    const syncedWorkspace = {
      ...selected,
      postBrief: approvedBrief,
      postDraft,
      editorialWorkItems: withEditorialWorkItemSync(selected, { postBrief: approvedBrief, postDraft }).editorialWorkItems!
    };
    const patch = buildSelectEditorialWorkItemPatch(syncedWorkspace, first.selectedEditorialWorkItemId!);

    expect(patch.selectedEditorialWorkItemId).toBe(first.selectedEditorialWorkItemId);
    expect(patch.postBrief?.id).toBe(first.postBrief?.id);
    expect(patch.postDraft).toBeNull();
    expect(patch.editorialWorkItems?.find((item) => item.id === second.selectedEditorialWorkItemId)?.draft?.id).toBe(postDraft.id);
  });
});
