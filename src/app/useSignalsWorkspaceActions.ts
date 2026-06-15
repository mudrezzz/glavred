import {
  approveSignal,
  addRadar,
  archiveSignal,
  correctSignal,
  deleteRadar,
  evaluateSignalAgainstRadarFilters,
  rejectSignal,
  toggleRadarStatus,
  updateRadar,
  type AuthorNote,
  type RadarDefinition,
  type SourceSignal
} from '../domain/editorialWorkspace';
import {
  createAuthorMemoryEvent,
  inferAuthorPositionAssertions
} from '../application/editorialServices';
import type { WorkspaceSetter } from './useWorkspacePersistence';

type SignalsWorkspaceActionsParams = {
  setToast: (message: string) => void;
  setWorkspace: WorkspaceSetter;
};

export function useSignalsWorkspaceActions({ setToast, setWorkspace }: SignalsWorkspaceActionsParams) {
  function applySignalUpdate(nextSignal: SourceSignal, message: string, selectAsCurrent = false) {
    setWorkspace((current) => {
      const sourceSignals = current.sourceSignals.map((signal) =>
        signal.id === nextSignal.id ? nextSignal : signal
      );
      return {
        ...current,
        sourceSignal: selectAsCurrent ? nextSignal : current.sourceSignal,
        sourceSignals,
        updatedAt: new Date().toISOString()
      };
    });
    setToast(message);
  }

  function approveSourceSignal(signal: SourceSignal) {
    applySignalUpdate(approveSignal(signal), 'Сигнал утвержден и выбран для production-flow', true);
  }

  function rejectSourceSignal(signal: SourceSignal) {
    applySignalUpdate(rejectSignal(signal), 'Сигнал отклонен');
  }

  function archiveSourceSignal(signal: SourceSignal) {
    applySignalUpdate(archiveSignal(signal), 'Сигнал отправлен в архив');
  }

  function saveRadar(nextRadar: RadarDefinition, isNew: boolean) {
    setWorkspace((current) => {
      const radars = isNew ? addRadar(current.radars, nextRadar) : updateRadar(current.radars, nextRadar);
      const sourceSignals = current.sourceSignals.map((signal) =>
        signal.radarId === nextRadar.id ? evaluateSignalAgainstRadarFilters(signal, nextRadar, { ...current, radars }) : signal
      );
      const sourceSignal =
        current.sourceSignal.radarId === nextRadar.id
          ? sourceSignals.find((signal) => signal.id === current.sourceSignal.id) ?? current.sourceSignal
          : current.sourceSignal;

      return {
        ...current,
        radars,
        sourceSignal,
        sourceSignals,
        updatedAt: new Date().toISOString()
      };
    });
    setToast(isNew ? 'Радар добавлен' : 'Радар сохранен');
  }

  function removeRadar(radar: RadarDefinition) {
    setWorkspace((current) => ({
      ...current,
      radars: deleteRadar(current.radars, radar.id),
      updatedAt: new Date().toISOString()
    }));
    setToast('Радар удален. Сигналы остаются в истории разбора.');
  }

  function switchRadarStatus(radar: RadarDefinition) {
    const nextRadar = toggleRadarStatus(radar);
    setWorkspace((current) => ({
      ...current,
      radars: updateRadar(current.radars, nextRadar),
      updatedAt: new Date().toISOString()
    }));
    setToast(nextRadar.status === 'paused' ? 'Радар остановлен' : 'Радар запущен');
  }

  function correctSourceSignal(signal: SourceSignal, patch: Partial<SourceSignal>) {
    const nextSignal = correctSignal(signal, patch);
    setWorkspace((current) => {
      const correctionNote: AuthorNote = {
        id: `note-signal-correction-${signal.id}-${Date.now()}`,
        type: 'manualCorrection',
        title: `Правка сигнала: ${signal.title}`,
        body:
          nextSignal.authorCorrection ||
          'Автор уточнил, как этот сигнал связан с темой, фабулой или ценностью.',
        sourceUrl: '',
        tags: ['signal-correction'],
        attachments: [],
        capturedAt: new Date().toISOString(),
        targetType: 'evidence',
        targetId: signal.id,
        targetTitle: signal.title
      };
      const authorNotes = [correctionNote, ...current.authorNotes];
      const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
      return {
        ...current,
        sourceSignals: current.sourceSignals.map((candidate) =>
          candidate.id === nextSignal.id ? nextSignal : candidate
        ),
        sourceSignal: current.sourceSignal.id === nextSignal.id ? nextSignal : current.sourceSignal,
        authorNotes,
        authorMemoryEvents,
        authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
        updatedAt: new Date().toISOString()
      };
    });
    setToast('Правка сигнала добавлена в память автора');
  }

  return {
    approveSourceSignal,
    archiveSourceSignal,
    correctSourceSignal,
    rejectSourceSignal,
    removeRadar,
    saveRadar,
    switchRadarStatus
  };
}
