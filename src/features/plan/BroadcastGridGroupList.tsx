import type { ContentPlanItem, PlanWeightWarning, WorkspaceState } from '../../domain/editorialWorkspace';
import { BroadcastGridRow } from './BroadcastGridRow';

export function BroadcastGridGroupList({
  groups,
  workspace,
  warnings,
  onApprove,
  onBrief,
  onItemChange
}: {
  groups: Array<{ id: string; title: string; items: ContentPlanItem[] }>;
  workspace: WorkspaceState;
  warnings: PlanWeightWarning[];
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
  onItemChange: (item: ContentPlanItem) => void;
}) {
  return (
    <div className="broadcast-groups" data-testid="broadcast-groups">
      {groups.map((group) => (
        <section className="broadcast-group" key={group.id}>
          <div className="entity-list-toolbar compact">
            <div className="entity-toolbar-copy">
              <h2>{group.title}</h2>
              <p>{group.items.length} слотов</p>
            </div>
          </div>
          <div className="broadcast-list">
            {group.items.map((item, index) => (
              <BroadcastGridRow
                defaultExpanded={index === 0}
                item={item}
                itemWarnings={warnings.filter((warning) => warning.targetType === 'slot' && warning.targetId === item.id)}
                key={item.id}
                workspace={workspace}
                onApprove={onApprove}
                onBrief={onBrief}
                onItemChange={onItemChange}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
