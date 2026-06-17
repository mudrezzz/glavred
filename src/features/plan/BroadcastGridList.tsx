import type { ContentPlanItem, PlanWeightWarning, WorkspaceState } from '../../domain/editorialWorkspace';
import { EmptyState } from '../../shared/ui/WorkflowPrimitives';
import { BroadcastGridRow } from './BroadcastGridRow';

export function BroadcastGridList({
  items,
  workspace,
  warnings,
  onItemChange,
  onApprove,
  onBrief
}: {
  items: ContentPlanItem[];
  workspace: WorkspaceState;
  warnings: PlanWeightWarning[];
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
}) {
  const activeWarnings = warnings.filter((warning) => warning.severity !== 'green');

  if (items.length === 0) {
    return (
      <EmptyState text="Сохраните настройку сетки и соберите план из текущего инсайта, тем и фабул редакционной модели." />
    );
  }

  return (
    <div className="broadcast-list" data-testid="broadcast-grid">
      <div className="broadcast-toolbar">
        <div>
          <h2>{periodLabel(workspace.contentPlanSettings.period)}</h2>
          <p>
            {workspace.contentPlanSettings.postsPerWeek} поста в неделю · {items.length} слотов ·{' '}
            {workspace.contentPlanSettings.publishingTimes.join(', ')}
          </p>
        </div>
        <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
          {activeWarnings.length > 0 ? `${activeWarnings.length} предупрежд.` : 'OK'}
        </span>
      </div>
      {items.map((item, index) => {
        const itemWarnings = warnings.filter((warning) =>
          warning.targetType === 'slot' && warning.targetId === item.id
        );

        return (
          <BroadcastGridRow
            defaultExpanded={index === 0}
            item={item}
            itemWarnings={itemWarnings}
            key={item.id}
            workspace={workspace}
            onApprove={onApprove}
            onBrief={onBrief}
            onItemChange={onItemChange}
          />
        );
      })}
    </div>
  );
}

function periodLabel(period: WorkspaceState['contentPlanSettings']['period']): string {
  if (period === 'week') return 'Сетка на неделю';
  if (period === 'quarter') return 'Сетка на квартал';
  return 'Сетка на месяц';
}
