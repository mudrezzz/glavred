import type { RadarDefinition, WorkspaceState } from '../../domain/editorialWorkspace';
import { RadarEditor } from './RadarEditor';
import { RadarCard } from './RadarCard';
import { SignalsSidePanel } from './SignalsSidePanel';
import type { SignalsController } from './useSignalsController';

export function RadarsTab({
  workspace,
  controller,
  onDeleteRadar,
  onToggleRadarStatus,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  controller: SignalsController;
  onDeleteRadar: (radar: RadarDefinition) => void;
  onToggleRadarStatus: (radar: RadarDefinition) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  return (
    <div className="memory-grid signals-workspace-grid">
      <section className="memory-main">
        <div className="entity-list-toolbar signals-entity-toolbar" data-testid="signals-radar-toolbar">
          <div className="entity-toolbar-copy">
            <h2>{workspace.radars.length} радара</h2>
            <p>Настраиваемые поисковики</p>
          </div>
          <button className="btn btn-sec btn-sm" data-testid="add-radar-button" type="button" onClick={controller.openNewRadar}>
            + Радар
          </button>
        </div>

        {controller.editingRadar && controller.isNewRadar && (
          <RadarEditor
            radar={controller.editingRadar}
            isNew={controller.isNewRadar}
            onPatch={controller.patchRadarDraft}
            onPatchRule={controller.patchRadarRule}
            onAddRule={controller.addRadarRule}
            onDeleteRule={controller.deleteRadarRule}
            onPatchSource={controller.patchRadarSource}
            onAddSource={controller.addRadarSource}
            onDeleteSource={controller.deleteRadarSource}
            onPatchFilter={controller.patchRadarFilter}
            onSave={controller.saveRadarDraft}
            onCancel={controller.cancelRadarDraft}
          />
        )}

        <div className="entity-list signals-entity-list" data-testid="radar-list">
          {workspace.radars.map((radar) => (
            <RadarCard
              key={radar.id}
              radar={radar}
              controller={controller}
              signalCount={controller.signalCountsByRadar[radar.id] ?? 0}
              onDeleteRadar={onDeleteRadar}
              onToggleRadarStatus={onToggleRadarStatus}
            />
          ))}
        </div>
      </section>

      <SignalsSidePanel workspace={workspace} summary={controller.signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
    </div>
  );
}
