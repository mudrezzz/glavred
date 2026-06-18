import type { EditorialCheck, EditorialLearningNote, FinalText, PostBrief, PostDraft, PostVisual, PostVisualMemeReference, PostVisualVariant, ReleasePackage, VisualMode } from './types';

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
  return {
    ...postDraft,
    body,
    version: postDraft.version + 1,
    status: 'revised',
    updatedAt: new Date().toISOString()
  };
}

export function approveFinalText(postDraft: PostDraft): FinalText {
  return {
    id: `final-${postDraft.id}`,
    draftId: postDraft.id,
    title: postDraft.title,
    body: postDraft.body,
    approvalStatus: 'approved',
    approvedAt: new Date().toISOString()
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
