import type { AuthorNote, DraftVersion, FinalText, PostDraft } from '../domain/editorialWorkspace';

const LEARNING_TAGS = ['editorial-learning', 'hitl', 'draft-version'];

export function upsertEditorialLearningAuthorNote(
  notes: AuthorNote[],
  postDraft: PostDraft,
  finalText: FinalText
): AuthorNote[] {
  const note = createEditorialLearningAuthorNote(postDraft, finalText);
  const learning = note.editorialLearning;
  const existingIndex = notes.findIndex((item) => item.id === note.id);

  if (!learning) return notes;
  if (existingIndex === -1) return [note, ...notes];

  return notes.map((item, index): AuthorNote => {
    if (index !== existingIndex) return item;

    return {
          ...note,
          editorialLearning: {
            ...learning,
            status: item.editorialLearning?.status ?? 'pendingReview'
          }
        };
  });
}

export function updateEditorialLearningStatus(
  notes: AuthorNote[],
  noteId: string,
  status: 'accepted' | 'rejected'
): AuthorNote[] {
  return notes.map((note): AuthorNote => {
    if (note.id !== noteId || note.type !== 'editorialLearning' || !note.editorialLearning) return note;
    return { ...note, editorialLearning: { ...note.editorialLearning, status } };
  });
}

export function isEditorialLearningInferenceEligible(note: AuthorNote): boolean {
  return note.type !== 'editorialLearning' || note.editorialLearning?.status === 'accepted';
}

function createEditorialLearningAuthorNote(postDraft: PostDraft, finalText: FinalText): AuthorNote {
  const versions = postDraft.versions ?? [];
  const snapshot = finalText.editorDecisionSnapshot;
  const selectedVersionId = finalText.draftVersionId ?? snapshot?.selectedVersionId ?? postDraft.activeVersionId ?? '';
  const selectedVersion = versions.find((version) => version.id === selectedVersionId);
  const machineVersion = versions.find((version) => version.source === 'machineFinal');
  const rejectedVersions = getRejectedVersions(versions, selectedVersionId);
  const comments = snapshot?.comments.map((comment) => comment.comment).filter(Boolean) ?? [];
  const qualitySummaries = rejectedVersions
    .map((version) => summarizeQuality(version))
    .filter(Boolean);
  const unresolvedRisks = snapshot?.machineTrace.unresolvedRisks ?? [];
  const tags = Array.from(new Set([...LEARNING_TAGS, ...deriveLearningTags(comments, versions, unresolvedRisks)]));
  const takeaway = buildSuggestedTakeaway(selectedVersion, comments, rejectedVersions, unresolvedRisks);

  return {
    id: `editorial-learning-${finalText.id}`,
    type: 'editorialLearning',
    title: `Редакторское наблюдение: ${finalText.title}`,
    body: buildLearningBody(finalText, selectedVersion, rejectedVersions, comments, qualitySummaries, unresolvedRisks, takeaway),
    sourceUrl: '',
    tags,
    attachments: [],
    capturedAt: new Date().toISOString(),
    targetType: 'evidence',
    targetId: finalText.id,
    targetTitle: finalText.title,
    editorialLearning: {
      status: 'pendingReview',
      finalTextId: finalText.id,
      draftId: postDraft.id,
      draftRunId: postDraft.generation?.draftRunId ?? snapshot?.machineTrace.draftRunId ?? null,
      selectedVersionId,
      selectedVersionNumber: finalText.versionNumber ?? selectedVersion?.versionNumber ?? postDraft.version,
      selectedVersionSource: selectedVersion?.source ?? snapshot?.selectedVersionSource ?? 'machineFinal',
      machineFinalVersionId: snapshot?.machineFinalVersionId ?? machineVersion?.id ?? null,
      humanRevisionCount: snapshot?.humanRevisionCount ?? versions.filter((version) => version.source === 'humanCommentRevision').length,
      manualEditCount: snapshot?.manualEditCount ?? versions.filter((version) => version.source === 'manualEdit').length,
      rejectedVersionIds: rejectedVersions.map((version) => version.id),
      comments,
      qualitySummaries,
      unresolvedRisks,
      suggestedMemoryTakeaway: takeaway
    }
  };
}

function getRejectedVersions(versions: DraftVersion[], selectedVersionId: string): DraftVersion[] {
  return versions.filter((version) => version.id !== selectedVersionId && version.source !== 'machineFinal');
}

function summarizeQuality(version: DraftVersion): string {
  const check = version.qualityCheck;
  if (!check || check.status === 'passed') return '';

  const reasons = [
    ...check.missedCommentIntents.map((item) => `не закрыто: ${item}`),
    ...check.regressionWarnings,
    ...check.internalJargonLeaks.map((item) => `внутренний термин: ${item}`)
  ].filter(Boolean);

  return `v${version.versionNumber}: ${check.status}${reasons.length > 0 ? ` — ${reasons.join('; ')}` : ''}`;
}

function deriveLearningTags(comments: string[], versions: DraftVersion[], risks: string[]): string[] {
  const haystack = [
    ...comments,
    ...risks,
    ...versions.flatMap((version) => [
      version.editorComment ?? '',
      version.qualityCheck?.summary ?? '',
      ...(version.qualityCheck?.missedCommentIntents ?? []),
      ...(version.qualityCheck?.regressionWarnings ?? [])
    ])
  ].join(' ').toLowerCase();
  const tags: string[] = [];

  if (containsAny(haystack, ['позици', 'stance', 'тезис', 'автор'])) tags.push('author-stance');
  if (containsAny(haystack, ['тон', 'сух', 'отчет', 'voice', 'реклам'])) tags.push('tone');
  if (containsAny(haystack, ['источник', 'source', 'marker', 'citation', 'атрибуц'])) tags.push('source-integration');
  if (containsAny(haystack, ['структур', 'критери', 'список', 'section'])) tags.push('structure');
  if (containsAny(haystack, ['не закрыто', 'missed', 'comment', 'комментар'])) tags.push('comment-compliance');

  return tags;
}

function buildSuggestedTakeaway(
  selectedVersion: DraftVersion | undefined,
  comments: string[],
  rejectedVersions: DraftVersion[],
  risks: string[]
): string {
  if (comments.some((comment) => containsAny(comment.toLowerCase(), ['позици', 'автор', 'stance']))) {
    return 'Автору важно, чтобы правка усиливала явную позицию, а не только переставляла факты.';
  }

  if (comments.some((comment) => containsAny(comment.toLowerCase(), ['тон', 'сух', 'отчет']))) {
    return 'Автор отвергает сухой отчетный тон; правки должны сохранять живой публичный голос.';
  }

  if (rejectedVersions.length > 0) {
    return `Выбор ${selectedVersion ? `v${selectedVersion.versionNumber}` : 'ранней версии'} показывает, что не всякая машинная правка улучшает публичный текст.`;
  }

  if (risks.length > 0) {
    return 'При финальном выборе редактор оставил видимые риски; их нужно учитывать как контекст будущих драфтов.';
  }

  return 'Финальный выбор редактора зафиксирован как пример предпочтений автора для будущих драфтов.';
}

function buildLearningBody(
  finalText: FinalText,
  selectedVersion: DraftVersion | undefined,
  rejectedVersions: DraftVersion[],
  comments: string[],
  qualitySummaries: string[],
  risks: string[],
  takeaway: string
): string {
  const lines = [
    `Пост: ${finalText.title}`,
    `Выбрана версия: v${finalText.versionNumber ?? selectedVersion?.versionNumber ?? 1}${selectedVersion ? ` (${sourceLabel(selectedVersion.source)})` : ''}.`,
    rejectedVersions.length > 0
      ? `Отклоненные машинные или редакторские версии: ${rejectedVersions.map((version) => `v${version.versionNumber}`).join(', ')}.`
      : 'Отклоненных последующих версий нет.',
    comments.length > 0 ? `Комментарии редактора: ${comments.join(' / ')}` : 'Комментарии редактора не использовались.',
    qualitySummaries.length > 0 ? `Риски отвергнутых версий: ${qualitySummaries.join(' | ')}` : 'Quality-check не зафиксировал критичных причин для отклоненных версий.',
    risks.length > 0 ? `Оставшиеся риски: ${risks.join('; ')}` : 'Оставшиеся машинные риски не указаны.',
    `Что запомнить: ${takeaway}`
  ];

  return lines.join('\n');
}

function sourceLabel(source: DraftVersion['source']): string {
  if (source === 'humanCommentRevision') return 'правка по комментарию';
  if (source === 'manualEdit') return 'ручная правка';
  return 'машинный финал';
}

function containsAny(value: string, needles: string[]): boolean {
  return needles.some((needle) => value.includes(needle));
}
