import {
  type AuthorNote,
  type SourceSignal
} from '../domain/editorialWorkspace';
import type { BlogProject } from '../domain/portfolio/types';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import { rescoreRadarSignals, reviewSourceSignal } from '../infrastructure/radarRunClient';
import { applyRadarRunWorkspaceResult } from './radarRunWorkspacePatches';
import type { WorkspaceSetter } from './useWorkspacePersistence';

type SourceSignalReviewActionsParams = {
  activeProject: BlogProject;
  setToast: (message: string) => void;
  setWorkspace: WorkspaceSetter;
};

export function createSourceSignalReviewActions({ activeProject, setToast, setWorkspace }: SourceSignalReviewActionsParams) {
  function applySignalUpdate(nextSignal: SourceSignal, message: string, selectAsCurrent = false) {
    setWorkspace((current) => ({
      ...current,
      sourceSignal: selectAsCurrent ? nextSignal : current.sourceSignal,
      sourceSignals: current.sourceSignals.map((signal) => signal.id === nextSignal.id ? nextSignal : signal),
      updatedAt: new Date().toISOString()
    }));
    setToast(message);
  }

  async function applyReview(signal: SourceSignal, action: 'approve' | 'reject' | 'archive' | 'reopen' | 'restore', reason: string, message: string, selectAsCurrent = false) {
    try {
      const result = await reviewSourceSignal(activeProject.id, signal.id, {
        action,
        reason,
        expectedReviewRevision: signal.reviewRevision ?? 0
      });
      applySignalUpdate(result.sourceSignal, message, selectAsCurrent);
    } catch {
      setToast('Не удалось сохранить решение редактора');
    }
  }

  async function approveSourceSignal(signal: SourceSignal) {
    await applyReview(signal, 'approve', '', 'Сигнал утвержден', true);
  }

  async function rejectSourceSignal(signal: SourceSignal) {
    const reason = window.prompt('Почему сигнал отклоняется?')?.trim();
    if (reason) await applyReview(signal, 'reject', reason, 'Сигнал отклонен');
  }

  async function archiveSourceSignal(signal: SourceSignal) {
    const reason = window.prompt('Почему сигнал отправляется в архив?')?.trim();
    if (reason) await applyReview(signal, 'archive', reason, 'Сигнал отправлен в архив');
  }

  async function reopenSourceSignal(signal: SourceSignal) {
    await applyReview(signal, 'reopen', '', 'Сигнал возвращен на проверку');
  }

  async function restoreSourceSignal(signal: SourceSignal) {
    await applyReview(signal, 'restore', '', 'Сигнал восстановлен из архива');
  }

  async function correctSourceSignal(signal: SourceSignal, patch: Partial<SourceSignal>) {
    const reason = patch.authorCorrection?.trim();
    if (!reason) {
      setToast('Для коррекции нужна правка автора с объяснением');
      return;
    }
    try {
      const result = await reviewSourceSignal(activeProject.id, signal.id, {
        action: 'correct',
        reason,
        editorialPatch: { title: patch.title ?? signal.title, summary: patch.summary ?? signal.summary, authorCorrection: reason },
        expectedReviewRevision: signal.reviewRevision ?? 0
      });
      const nextSignal = result.sourceSignal;
      setWorkspace((current) => {
        const correctionNote: AuthorNote = {
          id: `note-signal-correction-${signal.id}-${Date.now()}`,
          type: 'manualCorrection',
          title: `Правка сигнала: ${signal.title}`,
          body: nextSignal.authorCorrection || 'Автор уточнил редакционный смысл сигнала.',
          sourceUrl: '', tags: ['signal-correction'], attachments: [], capturedAt: new Date().toISOString(),
          targetType: 'evidence', targetId: signal.id, targetTitle: signal.title
        };
        const authorNotes = [correctionNote, ...current.authorNotes];
        const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
        return {
          ...current,
          sourceSignals: current.sourceSignals.map((candidate) => candidate.id === nextSignal.id ? nextSignal : candidate),
          sourceSignal: current.sourceSignal.id === nextSignal.id ? nextSignal : current.sourceSignal,
          authorNotes,
          authorMemoryEvents,
          authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
          updatedAt: new Date().toISOString()
        };
      });
      setToast('Правка сохранена, редакционная полезность пересчитана');
    } catch {
      setToast('Не удалось сохранить коррекцию сигнала');
    }
  }

  async function rescoreSourceSignal(signal: SourceSignal) {
    if (!signal.radarRunId) {
      setToast('У сигнала нет сохраненного RadarRun для повторной оценки');
      return;
    }
    try {
      const result = await rescoreRadarSignals(activeProject.id, signal.radarRunId);
      setWorkspace((current) => applyRadarRunWorkspaceResult(current, result));
      setToast('Редакционная полезность пересчитана без нового поиска');
    } catch {
      setToast('Не удалось повторить оценку сигнала');
    }
  }

  return { approveSourceSignal, archiveSourceSignal, correctSourceSignal, rejectSourceSignal, reopenSourceSignal, rescoreSourceSignal, restoreSourceSignal };
}
