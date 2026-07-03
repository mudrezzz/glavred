import { createBroadcastPlan } from '../application/editorialServices';
import { runLocalRadar } from '../application/upstreamRadarRunService';
import type { WorkspaceState } from '../domain/editorialWorkspace';

export function withDemoContentPlanAndRadarRun(workspace: WorkspaceState): WorkspaceState {
  const workspaceWithPlan = { ...workspace, contentPlanItems: createBroadcastPlan(workspace) };
  return runLocalRadar(workspaceWithPlan, workspaceWithPlan.radars[0]?.id ?? '', '2026-07-01T09:00:00.000Z');
}
