import type { EditorialCheck, EditorialLearningNote, FinalText, PostBrief, PostDraft, PostVisual, ReleasePackage, VisualMode } from './types';

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
    approvalStatus: 'draft',
    updatedAt: now,
    approvedAt: null
  };
}

export function editPostVisual(postVisual: PostVisual, patch: PostVisualEditPatch): PostVisual {
  return {
    ...postVisual,
    ...normalizeVisualPatch(patch),
    approvalStatus: 'draft',
    updatedAt: new Date().toISOString(),
    approvedAt: null
  };
}

export function approvePostVisual(postVisual: PostVisual, patch: PostVisualEditPatch = {}): PostVisual {
  const updated = editPostVisual(postVisual, patch);
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
