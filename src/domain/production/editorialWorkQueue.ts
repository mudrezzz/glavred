import type { ContentPlanItem } from '../planning/types';
import type {
  EditorialCheck,
  EditorialWorkItem,
  EditorialWorkStage,
  EditorialWorkStatus,
  EditorNote,
  FinalText,
  PostBrief,
  PostDraft,
  PostVisual
} from './types';

export type EditorialWorkArtifacts = {
  brief: PostBrief | null;
  draft: PostDraft | null;
  editorialChecks: EditorialCheck[];
  editorNotes: EditorNote[];
  finalText: FinalText | null;
  visual: PostVisual | null;
};

const emptyArtifacts: EditorialWorkArtifacts = {
  brief: null,
  draft: null,
  editorialChecks: [],
  editorNotes: [],
  finalText: null,
  visual: null
};

export function createEditorialWorkItem(
  item: ContentPlanItem,
  artifacts: Partial<EditorialWorkArtifacts> = {},
  postCandidateId?: string
): EditorialWorkItem {
  const normalizedArtifacts = normalizeArtifacts(artifacts);

  return {
    id: getEditorialWorkItemId(item.id),
    contentPlanItemId: item.id,
    postCandidateId,
    sourceSignalId: item.sourceSignalId,
    title: item.title,
    platform: item.platform,
    date: item.date,
    time: item.time,
    topicId: item.topicId,
    topicTitle: item.topicTitle,
    fabulaId: item.fabulaId,
    fabulaTitle: item.fabulaTitle,
    ...deriveEditorialWorkState(normalizedArtifacts),
    ...normalizedArtifacts
  };
}

export function getEditorialWorkItemId(contentPlanItemId: string): string {
  return `editorial-work-${contentPlanItemId}`;
}

export function upsertEditorialWorkItem(items: EditorialWorkItem[], next: EditorialWorkItem): EditorialWorkItem[] {
  const index = items.findIndex((item) => item.id === next.id);
  if (index === -1) return [...items, next];

  return items.map((item, currentIndex) => (currentIndex === index ? mergeEditorialWorkItem(item, next) : item));
}

export function syncEditorialWorkItemArtifacts(
  items: EditorialWorkItem[],
  itemId: string | null,
  artifacts: Partial<EditorialWorkArtifacts>
): EditorialWorkItem[] {
  if (!itemId) return items;

  return items.map((item) =>
    item.id === itemId
      ? {
          ...item,
          ...normalizeArtifacts(artifacts),
          ...deriveEditorialWorkState(normalizeArtifacts(artifacts))
        }
      : item
  );
}

export function normalizeArtifacts(artifacts: Partial<EditorialWorkArtifacts>): EditorialWorkArtifacts {
  return {
    ...emptyArtifacts,
    ...artifacts,
    editorialChecks: artifacts.editorialChecks ?? [],
    editorNotes: artifacts.editorNotes ?? []
  };
}

function mergeEditorialWorkItem(current: EditorialWorkItem, next: EditorialWorkItem): EditorialWorkItem {
  const artifacts = normalizeArtifacts({
    brief: next.brief ?? current.brief,
    draft: next.draft ?? current.draft,
    editorialChecks: next.editorialChecks.length > 0 ? next.editorialChecks : current.editorialChecks,
    editorNotes: next.editorNotes.length > 0 ? next.editorNotes : current.editorNotes,
    finalText: next.finalText ?? current.finalText,
    visual: next.visual ?? current.visual
  });

  return {
    ...current,
    ...next,
    ...artifacts,
    ...deriveEditorialWorkState(artifacts)
  };
}

function deriveEditorialWorkState(artifacts: EditorialWorkArtifacts): {
  stage: EditorialWorkStage;
  status: EditorialWorkStatus;
} {
  if (artifacts.visual) {
    return { stage: 'visual', status: 'inProgress' };
  }

  if (artifacts.finalText?.approvalStatus === 'approved') {
    return { stage: 'visual', status: 'todo' };
  }

  if (artifacts.finalText) {
    return { stage: 'draft', status: 'inProgress' };
  }

  if (artifacts.draft) {
    return { stage: 'draft', status: 'inProgress' };
  }

  if (artifacts.brief?.approvalStatus === 'approved') {
    return { stage: 'draft', status: 'todo' };
  }

  if (artifacts.brief) {
    return { stage: 'brief', status: 'inProgress' };
  }

  return { stage: 'brief', status: 'todo' };
}
