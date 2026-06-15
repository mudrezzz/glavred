import type {
  ArchiveRecord,
  AuthorAttachment,
  AuthorExternalSource,
  AuthorNote,
  AuthorNoteType,
  AuthorPositionAssertion,
  BulkImportAction,
  ImportedMemoryCandidate,
  ImportCandidateFilters
} from '../../domain/editorialWorkspace';
import type { CorrectionTarget, LinkPreview, SpeechRecognitionWindow, MemoryTypeFilter } from './types';

export const MAX_AUTHOR_ATTACHMENT_BYTES = 1024 * 1024;

export function splitTags(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function formatScore(value: number): string {
  return value.toFixed(2);
}

export function formatDate(value: string): string {
  return value.slice(0, 10);
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function authorNoteTypeLabel(type: AuthorNoteType): string {
  if (type === 'linkReaction') return 'Реакция';
  if (type === 'manualCorrection') return 'Правка';
  return 'Мысль';
}

export function assertionTypeLabel(type: string): string {
  if (type === 'persona') return 'Образ';
  if (type === 'style') return 'Стиль';
  if (type === 'audience') return 'Аудитория';
  if (type === 'topic') return 'Тема';
  return 'Принцип';
}

export function deriveNoteTitle(note: AuthorNote): string {
  if (note.title.trim()) return note.title;

  const normalized = note.body.replace(/\s+/g, ' ').trim();
  if (!normalized) return authorNoteTypeLabel(note.type);

  return normalized.length > 64 ? `${normalized.slice(0, 61)}...` : normalized;
}

export function buildLinkPreview(value: string): LinkPreview {
  const trimmed = value.trim();

  if (!trimmed) {
    return { isValid: false, domain: '', normalizedUrl: '', title: '' };
  }

  try {
    const url = new URL(trimmed.startsWith('http') ? trimmed : `https://${trimmed}`);
    const domain = url.hostname.replace(/^www\./, '');

    return {
      isValid: true,
      domain,
      normalizedUrl: url.toString(),
      title: `Ссылка из ${domain}`
    };
  } catch {
    return { isValid: false, domain: '', normalizedUrl: trimmed, title: '' };
  }
}

export function getMemorySummary(notes: AuthorNote[]) {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  return notes.reduce(
    (summary, note) => {
      const capturedAt = new Date(note.capturedAt);
      const isSameYear = capturedAt.getFullYear() === currentYear;

      return {
        total: summary.total + 1,
        thoughts: summary.thoughts + (note.type === 'thought' ? 1 : 0),
        links: summary.links + (note.type === 'linkReaction' ? 1 : 0),
        corrections: summary.corrections + (note.type === 'manualCorrection' ? 1 : 0),
        thisMonth: summary.thisMonth + (isSameYear && capturedAt.getMonth() === currentMonth ? 1 : 0),
        thisYear: summary.thisYear + (isSameYear ? 1 : 0)
      };
    },
    { total: 0, thoughts: 0, links: 0, corrections: 0, thisMonth: 0, thisYear: 0 }
  );
}

export function filterAuthorNotes(notes: AuthorNote[], query: string, filter: MemoryTypeFilter): AuthorNote[] {
  const normalizedQuery = query.trim().toLowerCase();

  return notes.filter((note) => {
    const matchesType = filter === 'all' || note.type === filter;
    const haystack = [
      note.title,
      note.body,
      note.sourceUrl,
      note.targetTitle ?? '',
      ...note.tags
    ]
      .join(' ')
      .toLowerCase();

    return matchesType && (!normalizedQuery || haystack.includes(normalizedQuery));
  });
}

export function isEvidenceNote(noteId: string, assertions: AuthorPositionAssertion[]): boolean {
  return assertions.some((assertion) => assertion.evidence.some((item) => item.noteId === noteId));
}

export function buildCorrectionTargets(assertions: AuthorPositionAssertion[]): CorrectionTarget[] {
  return assertions.flatMap((assertion) => [
    { type: 'assertion' as const, id: assertion.id, title: assertion.title },
    ...assertion.evidence.map((item) => buildEvidenceCorrectionTarget(assertion, item))
  ]);
}

export function buildEvidenceCorrectionTarget(
  assertion: AuthorPositionAssertion,
  item: { noteId: string; quote: string }
): CorrectionTarget {
  return {
    type: 'evidence',
    id: `${assertion.id}:${item.noteId}`,
    title: `${assertion.title}: ${item.quote.slice(0, 60)}`
  };
}

export function correctionTargetKey(target: CorrectionTarget): string {
  return `${target.type}:${target.id}`;
}

export function hasCorrectionConflict(value: string): boolean {
  const normalized = value.toLowerCase();
  return ['не согласен', 'неверно', 'противоречит', 'убрать', 'заменить', 'не так'].some((marker) =>
    normalized.includes(marker)
  );
}

export async function createAuthorAttachment(
  file: File | undefined
): Promise<{ attachment: AuthorAttachment } | { error: string }> {
  if (!file) {
    return { error: 'Файл не выбран.' };
  }

  if (file.size > MAX_AUTHOR_ATTACHMENT_BYTES) {
    return { error: 'Файл больше 1 MB. Для локального демо добавьте ссылку или короткую выдержку.' };
  }

  return {
    attachment: {
      id: `attachment-${Date.now()}`,
      fileName: file.name,
      mimeType: file.type || 'application/octet-stream',
      sizeBytes: file.size,
      dataUrl: await readFileAsDataUrl(file),
      createdAt: new Date().toISOString(),
      localOnly: true
    }
  };
}

export function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.readAsDataURL(file);
  });
}

export function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

export function attachmentTypeLabel(attachment: AuthorAttachment): string {
  if (attachment.mimeType.includes('pdf')) return 'PDF';
  if (attachment.mimeType.includes('word') || attachment.fileName.match(/\.docx?$/i)) return 'DOC';
  if (attachment.mimeType.startsWith('text/') || attachment.fileName.match(/\.(md|txt)$/i)) return 'TXT';
  return 'FILE';
}

export function getSpeechRecognitionConstructor() {
  const speechWindow = window as SpeechRecognitionWindow;
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
}

export function sourceTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    telegramChannel: 'Telegram archive',
    socialProfile: 'Social profile',
    blogSite: 'Blog/site',
    document: 'Document',
    articleArchive: 'Article archive',
    manualUpload: 'Manual upload'
  };

  return labels[type] ?? type;
}

export function sourceStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    planned: 'Запланирован',
    connected: 'Демо подключен',
    needsReview: 'Нужен review',
    imported: 'Импортирован',
    paused: 'Пауза',
    failed: 'Ошибка'
  };

  return labels[status] ?? status;
}

export function importModeLabel(mode: string): string {
  const labels: Record<string, string> = {
    manualOnly: 'Только вручную',
    reviewedQueue: 'Через очередь',
    archiveOnly: 'Только архив',
    bulkArchive: 'Bulk archive'
  };

  return labels[mode] ?? mode;
}

export function evidencePolicyLabel(policy: string): string {
  const labels: Record<string, string> = {
    canSupportAssertions: 'Может поддержать выводы',
    archiveOnly: 'Только архив',
    ignored: 'Не evidence'
  };

  return labels[policy] ?? policy;
}

export function reviewStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    new: 'Новый',
    acceptedToMemory: 'В памяти',
    acceptedToArchive: 'В архиве',
    bulkAcceptedToArchive: 'Bulk archive',
    rejected: 'Отклонен',
    ignoredForEvidence: 'Не evidence'
  };

  return labels[status] ?? status;
}

export function duplicateRiskLabel(risk: string): string {
  if (risk === 'high') return 'high';
  if (risk === 'medium') return 'medium';
  return 'low';
}

export function getImportSummary(
  sources: AuthorExternalSource[],
  candidates: ImportedMemoryCandidate[],
  archiveRecords: ArchiveRecord[],
  actions: BulkImportAction[]
) {
  return {
    sources: sources.length,
    candidates: candidates.length,
    needsReview: candidates.filter((candidate) => candidate.reviewStatus === 'new').length,
    archived: archiveRecords.length,
    bulkAccepted: candidates.filter((candidate) => candidate.reviewStatus === 'bulkAcceptedToArchive').length,
    undoAvailable: actions.some((action) => action.canUndo) ? 1 : 0
  };
}

export function formatImportFilters(filters: ImportCandidateFilters): string {
  return [
    filters.sourceId && filters.sourceId !== 'all' ? `source=${filters.sourceId}` : '',
    filters.reviewStatus && filters.reviewStatus !== 'all' ? `status=${filters.reviewStatus}` : '',
    filters.evidencePolicy && filters.evidencePolicy !== 'all' ? `policy=${filters.evidencePolicy}` : '',
    filters.duplicateRisk && filters.duplicateRisk !== 'all' ? `risk=${filters.duplicateRisk}` : '',
    filters.query ? `query=${filters.query}` : ''
  ]
    .filter(Boolean)
    .join(', ') || 'нет';
}
