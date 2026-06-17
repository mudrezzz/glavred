import type { EditorialCheck, EditorialLearningNote, FinalText, PostBrief, PostDraft, ReleasePackage } from './types';

export type PostBriefEditPatch = Pick<
  PostBrief,
  'title' | 'thesis' | 'conflict' | 'authorPosition' | 'audience' | 'evidence' | 'examples' | 'structure' | 'cta' | 'risks' | 'sources'
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
