import type {
  DraftVersion,
  EditorDecisionMachineTraceSummary,
  EditorDecisionSnapshot,
  EditorialCheck,
  EditorialLearningNote,
  FinalText,
  PostBrief,
  PostDraft,
  PostVisual,
  PostVisualMemeReference,
  PostVisualVariant,
  ReleasePackage,
  VisualMode
} from './types';

export type PostBriefEditPatch = Pick<
  PostBrief,
  'title' | 'thesis' | 'conflict' | 'authorPosition' | 'audience' | 'evidence' | 'examples' | 'structure' | 'cta' | 'risks' | 'sources'
>;

export type PostVisualEditPatch = Partial<
  Pick<
    PostVisual,
    | 'mode'
    | 'brief'
    | 'prompt'
    | 'memeSearchQuery'
    | 'memeReferenceTitle'
    | 'memeReferenceUrl'
    | 'transformationInstructions'
    | 'assetPlaceholder'
    | 'notes'
  >
>;

// Production transitions preserve the HITL gates from brief approval to learning capture.
export function approvePostBrief(postBrief: PostBrief): PostBrief {
  return { ...postBrief, approvalStatus: 'approved' };
}

export function rejectPostBrief(postBrief: PostBrief): PostBrief {
  return { ...postBrief, approvalStatus: 'rejected' };
}

export function editPostBrief(postBrief: PostBrief, patch: PostBriefEditPatch): PostBrief {
  return {
    ...postBrief,
    ...patch,
    evidence: normalizeLines(patch.evidence),
    examples: normalizeLines(patch.examples),
    structure: normalizeLines(patch.structure),
    risks: normalizeLines(patch.risks),
    sources: normalizeLines(patch.sources),
    approvalStatus: 'draft'
  };
}

function normalizeLines(items: string[]): string[] {
  return items.map((item) => item.trim()).filter(Boolean);
}

export function reviseDraft(postDraft: PostDraft, body: string): PostDraft {
  return addDraftVersion(postDraft, {
    source: 'manualEdit',
    title: getActiveDraftVersion(postDraft).title,
    body,
    revisionSummary: 'Ручная редакторская правка.'
  });
}

export function approveFinalText(
  postDraft: PostDraft,
  options: {
    versionId?: string;
    machineTrace?: EditorDecisionMachineTraceSummary;
  } = {}
): FinalText {
  const normalizedDraft = normalizePostDraftVersions(postDraft);
  const selectedVersion = findDraftVersion(normalizedDraft, options.versionId) ?? getActiveDraftVersion(normalizedDraft);
  const now = new Date().toISOString();
  const snapshot = createEditorDecisionSnapshot(normalizedDraft, selectedVersion, options.machineTrace, now);

  return {
    id: `final-${postDraft.id}`,
    draftId: postDraft.id,
    draftVersionId: selectedVersion.id,
    versionNumber: selectedVersion.versionNumber,
    title: selectedVersion.title,
    body: selectedVersion.body,
    approvalStatus: 'approved',
    approvedAt: now,
    editorDecisionSnapshot: snapshot
  };
}

export function normalizePostDraftVersions(postDraft: PostDraft): PostDraft {
  const versions = normalizeDraftVersions(postDraft);
  const activeVersion =
    versions.find((version) => version.id === postDraft.activeVersionId) ??
    versions.find((version) => version.versionNumber === postDraft.version) ??
    versions[versions.length - 1];

  return mirrorDraftVersion(postDraft, activeVersion, {
    versions,
    activeVersionId: activeVersion.id,
    finalVersionId: postDraft.finalVersionId
  });
}

export function getActiveDraftVersion(postDraft: PostDraft): DraftVersion {
  const normalizedDraft = normalizePostDraftVersions(postDraft);
  return (
    normalizedDraft.versions?.find((version) => version.id === normalizedDraft.activeVersionId) ??
    normalizedDraft.versions?.[0] ??
    createInitialDraftVersion(postDraft)
  );
}

export function selectDraftVersion(postDraft: PostDraft, versionId: string): PostDraft {
  const normalizedDraft = normalizePostDraftVersions(postDraft);
  const selectedVersion = findDraftVersion(normalizedDraft, versionId);
  if (!selectedVersion) return normalizedDraft;

  return mirrorDraftVersion(normalizedDraft, selectedVersion, {
    versions: normalizedDraft.versions ?? [selectedVersion],
    activeVersionId: selectedVersion.id,
    finalVersionId: normalizedDraft.finalVersionId
  });
}

export function addHumanCommentRevisionVersion(
  postDraft: PostDraft,
  patch: {
    title: string;
    body: string;
    editorComment: string;
    revisionSummary?: string;
    aiRunId?: string | null;
    qualityCheck?: DraftVersion['qualityCheck'];
  }
): PostDraft {
  const active = getActiveDraftVersion(postDraft);
  return addDraftVersion(postDraft, {
    source: 'humanCommentRevision',
    baseVersionId: active.id,
    title: patch.title,
    body: patch.body,
    editorComment: patch.editorComment,
    revisionSummary: patch.revisionSummary,
    aiRunId: patch.aiRunId ?? null,
    qualityCheck: patch.qualityCheck
  });
}

function addDraftVersion(
  postDraft: PostDraft,
  patch: {
    source: DraftVersion['source'];
    title: string;
    body: string;
    baseVersionId?: string;
    editorComment?: string;
    revisionSummary?: string;
    aiRunId?: string | null;
    qualityCheck?: DraftVersion['qualityCheck'];
  }
): PostDraft {
  const normalizedDraft = normalizePostDraftVersions(postDraft);
  const current = getActiveDraftVersion(normalizedDraft);
  if (patch.body === current.body && patch.title === current.title) return normalizedDraft;

  const versions = normalizedDraft.versions ?? [current];
  const nextNumber = Math.max(...versions.map((version) => version.versionNumber), 0) + 1;
  const createdAt = new Date().toISOString();
  const nextVersion: DraftVersion = {
    id: `${normalizedDraft.id}-v${nextNumber}`,
    versionNumber: nextNumber,
    source: patch.source,
    baseVersionId: patch.baseVersionId ?? current.id,
    title: patch.title,
    body: patch.body,
    editorComment: patch.editorComment?.trim() || undefined,
    revisionSummary: patch.revisionSummary?.trim() || undefined,
    draftRunId: normalizedDraft.generation?.draftRunId ?? null,
    aiRunId: patch.aiRunId ?? null,
    qualityCheck: patch.qualityCheck,
    createdAt
  };

  return mirrorDraftVersion(normalizedDraft, nextVersion, {
    versions: [...versions, nextVersion],
    activeVersionId: nextVersion.id,
    finalVersionId: undefined
  });
}

function normalizeDraftVersions(postDraft: PostDraft): DraftVersion[] {
  const versions = Array.isArray(postDraft.versions) && postDraft.versions.length > 0
    ? postDraft.versions
    : [createInitialDraftVersion(postDraft)];

  return versions
    .map((version, index) => ({
      ...version,
      id: version.id || `${postDraft.id}-v${index + 1}`,
      versionNumber: version.versionNumber || index + 1,
      source: version.source ?? 'machineFinal',
      title: version.title || postDraft.title,
      body: version.body || postDraft.body,
      draftRunId: version.draftRunId ?? postDraft.generation?.draftRunId ?? null,
      aiRunId: version.aiRunId ?? null,
      createdAt: version.createdAt || postDraft.updatedAt
    }))
    .sort((left, right) => left.versionNumber - right.versionNumber);
}

function createInitialDraftVersion(postDraft: PostDraft): DraftVersion {
  return {
    id: `${postDraft.id}-v1`,
    versionNumber: 1,
    source: 'machineFinal',
    title: postDraft.title,
    body: postDraft.body,
    draftRunId: postDraft.generation?.draftRunId ?? null,
    aiRunId: postDraft.generation?.aiRunId ?? null,
    createdAt: postDraft.updatedAt
  };
}

function mirrorDraftVersion(
  postDraft: PostDraft,
  version: DraftVersion,
  patch: Pick<PostDraft, 'versions' | 'activeVersionId' | 'finalVersionId'>
): PostDraft {
  return {
    ...postDraft,
    ...patch,
    title: version.title,
    body: version.body,
    version: version.versionNumber,
    status: version.source === 'machineFinal' ? postDraft.status : 'revised',
    updatedAt: version.createdAt
  };
}

function findDraftVersion(postDraft: PostDraft, versionId: string | undefined): DraftVersion | undefined {
  if (!versionId) return undefined;
  return (postDraft.versions ?? []).find((version) => version.id === versionId);
}

function createEditorDecisionSnapshot(
  postDraft: PostDraft,
  selectedVersion: DraftVersion,
  machineTrace: EditorDecisionMachineTraceSummary | undefined,
  createdAt: string
): EditorDecisionSnapshot {
  const versions = postDraft.versions ?? [selectedVersion];
  const comments = versions
    .filter((version) => version.editorComment)
    .map((version) => ({
      versionId: version.id,
      versionNumber: version.versionNumber,
      comment: version.editorComment ?? ''
    }));

  return {
    id: `editor-decision-${postDraft.id}-${selectedVersion.id}`,
    draftId: postDraft.id,
    selectedVersionId: selectedVersion.id,
    selectedVersionNumber: selectedVersion.versionNumber,
    selectedVersionSource: selectedVersion.source,
    machineFinalVersionId: versions.find((version) => version.source === 'machineFinal')?.id ?? null,
    humanRevisionCount: versions.filter((version) => version.source === 'humanCommentRevision').length,
    manualEditCount: versions.filter((version) => version.source === 'manualEdit').length,
    comments,
    machineTrace: machineTrace ?? {
      draftRunId: postDraft.generation?.draftRunId ?? null,
      traceStatus: 'unavailable',
      unresolvedRisks: []
    },
    createdAt
  };
}

export function createPostVisual(workItemId: string, mode: VisualMode = 'generate'): PostVisual {
  const now = new Date().toISOString();

  return {
    id: `visual-${workItemId}`,
    workItemId,
    mode,
    brief: '',
    prompt: '',
    memeSearchQuery: '',
    memeReferenceTitle: '',
    memeReferenceUrl: '',
    transformationInstructions: '',
    assetPlaceholder: '',
    notes: '',
    memeReferences: [],
    selectedMemeReferenceId: null,
    memeReferenceBatch: 0,
    variants: [],
    selectedVariantId: null,
    variantBatch: 0,
    approvalStatus: 'draft',
    updatedAt: now,
    approvedAt: null
  };
}

export function editPostVisual(postVisual: PostVisual, patch: PostVisualEditPatch): PostVisual {
  const normalizedPatch = normalizeVisualPatch(patch);
  const shouldResetVariants =
    Object.prototype.hasOwnProperty.call(normalizedPatch, 'mode') ||
    Object.prototype.hasOwnProperty.call(normalizedPatch, 'brief');

  return {
    ...postVisual,
    ...normalizedPatch,
    memeReferences: shouldResetVariants ? [] : postVisual.memeReferences,
    selectedMemeReferenceId: shouldResetVariants ? null : postVisual.selectedMemeReferenceId,
    variants: shouldResetVariants ? [] : postVisual.variants,
    selectedVariantId: shouldResetVariants ? null : postVisual.selectedVariantId,
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function preparePostVisualMemeReferences(
  postVisual: PostVisual,
  patch: PostVisualEditPatch,
  memeReferences: PostVisualMemeReference[]
): PostVisual {
  if ((patch.mode ?? postVisual.mode) !== 'memeRemix') return postVisual;
  const nextBatch = postVisual.memeReferenceBatch + 1;
  const updated = editPostVisual(postVisual, patch);

  return {
    ...updated,
    memeReferences,
    selectedMemeReferenceId: null,
    memeReferenceBatch: nextBatch,
    variants: [],
    selectedVariantId: null,
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function selectPostVisualMemeReference(postVisual: PostVisual, referenceId: string): PostVisual {
  if (postVisual.mode !== 'memeRemix') return postVisual;
  if (!postVisual.memeReferences.some((reference) => reference.id === referenceId)) return postVisual;

  return {
    ...postVisual,
    selectedMemeReferenceId: referenceId,
    memeReferenceTitle: postVisual.memeReferences.find((reference) => reference.id === referenceId)?.title ?? postVisual.memeReferenceTitle,
    memeReferenceUrl: postVisual.memeReferences.find((reference) => reference.id === referenceId)?.sourceUrl ?? postVisual.memeReferenceUrl,
    variants: [],
    selectedVariantId: null,
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function preparePostVisualVariants(
  postVisual: PostVisual,
  patch: PostVisualEditPatch,
  variants: PostVisualVariant[]
): PostVisual {
  if ((patch.mode ?? postVisual.mode) === 'memeRemix' && !postVisual.selectedMemeReferenceId) return postVisual;
  const nextBatch = postVisual.variantBatch + 1;
  const updated = editPostVisual(postVisual, patch);

  return {
    ...updated,
    memeReferences: postVisual.memeReferences,
    selectedMemeReferenceId: postVisual.selectedMemeReferenceId,
    memeReferenceTitle: postVisual.memeReferenceTitle,
    memeReferenceUrl: postVisual.memeReferenceUrl,
    variants,
    selectedVariantId: null,
    variantBatch: nextBatch,
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function selectPostVisualVariant(postVisual: PostVisual, variantId: string): PostVisual {
  if (!postVisual.variants.some((variant) => variant.id === variantId)) return postVisual;

  return {
    ...postVisual,
    selectedVariantId: variantId,
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function approvePostVisual(postVisual: PostVisual, patch: PostVisualEditPatch = {}): PostVisual {
  const updated = editPostVisual(postVisual, patch);
  const canApprove =
    updated.mode === 'noVisual' ||
    Boolean(updated.selectedVariantId && updated.variants.some((variant) => variant.id === updated.selectedVariantId));

  if (!canApprove) return updated;

  const now = new Date().toISOString();

  return {
    ...updated,
    approvalStatus: 'approved',
    updatedAt: now,
    approvedAt: now
  };
}

function normalizeVisualPatch(patch: PostVisualEditPatch): PostVisualEditPatch {
  return Object.fromEntries(
    Object.entries(patch).map(([key, value]) => [key, typeof value === 'string' ? value.trim() : value])
  ) as PostVisualEditPatch;
}

export function markCheckResolved(check: EditorialCheck): EditorialCheck {
  return { ...check, status: 'passed' };
}

export function toggleReleaseChecklistItem(
  releasePackage: ReleasePackage,
  itemId: string
): ReleasePackage {
  return {
    ...releasePackage,
    checklist: releasePackage.checklist.map((item) =>
      item.id === itemId ? { ...item, done: !item.done } : item
    ),
    status: 'draft',
    updatedAt: new Date().toISOString()
  };
}

export function markReleaseReady(releasePackage: ReleasePackage): ReleasePackage {
  const allItemsDone = releasePackage.checklist.every((item) => item.done);

  if (!allItemsDone) {
    return { ...releasePackage, status: 'draft', updatedAt: new Date().toISOString() };
  }

  return { ...releasePackage, status: 'ready', updatedAt: new Date().toISOString() };
}

export function markReleaseExported(releasePackage: ReleasePackage): ReleasePackage {
  return { ...releasePackage, status: 'exported', updatedAt: new Date().toISOString() };
}

export function markLearningNoteCaptured(note: EditorialLearningNote): EditorialLearningNote {
  const now = new Date().toISOString();

  return {
    ...note,
    status: 'captured',
    updatedAt: now,
    capturedAt: now
  };
}

export function updateLearningNote(
  note: EditorialLearningNote,
  patch: Partial<Omit<EditorialLearningNote, 'id' | 'releasePackageId' | 'updatedAt' | 'capturedAt'>>
): EditorialLearningNote {
  return {
    ...note,
    ...patch,
    status: 'draft',
    updatedAt: new Date().toISOString(),
    capturedAt: null
  };
}
