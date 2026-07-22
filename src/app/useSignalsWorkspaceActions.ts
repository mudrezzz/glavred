import {
  addRadar,
  deleteRadar,
  toggleRadarStatus,
  updateRadar,
  type RadarDefinition,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import type { BlogProject } from '../domain/portfolio/types';
import { runLocalRadar } from '../application/upstreamRadarRunService';
import { runExternalRadar } from '../infrastructure/radarRunClient';
import { applyRadarRunWorkspaceResult } from './radarRunWorkspacePatches';
import { createSourceSignalReviewActions } from './sourceSignalReviewActions';
import type { WorkspaceSetter } from './useWorkspacePersistence';

type SignalsWorkspaceActionsParams = {
  activeProject: BlogProject;
  setToast: (message: string) => void;
  setWorkspace: WorkspaceSetter;
  workspace: WorkspaceState;
};

export function useSignalsWorkspaceActions({ activeProject, setToast, setWorkspace, workspace }: SignalsWorkspaceActionsParams) {
  const signalReview = createSourceSignalReviewActions({ activeProject, setToast, setWorkspace });

  function saveRadar(nextRadar: RadarDefinition, isNew: boolean) {
    setWorkspace((current) => {
      const radars = isNew ? addRadar(current.radars, nextRadar) : updateRadar(current.radars, nextRadar);
      return {
        ...current,
        radars,
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

  async function runRadar(radar: RadarDefinition) {
    try {
      const result = await runExternalRadar(workspace, radar.id, {
        projectId: activeProject.id,
        editorialLanguage: activeProject.language
      });
      setWorkspace((current) => applyRadarRunWorkspaceResult(current, result, { prependRun: true }));
      setToast(`Радар завершен: найдено сигналов-кандидатов ${result.sourceSignals.length}`);
    } catch {
      setWorkspace((current) => runLocalRadar(current, radar.id));
      setToast('Backend-поиск недоступен: создан локальный contract-run');
    }
  }

  return {
    ...signalReview,
    removeRadar,
    runRadar,
    saveRadar,
    switchRadarStatus
  };
}
