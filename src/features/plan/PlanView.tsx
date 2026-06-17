import { useMemo, useState } from 'react';
import {
  detectBroadcastPlanConflicts,
  type ContentPlanItem,
  type ContentPlanSettings,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { summarizeBroadcastGridDemand } from '../../application/editorialServices';
import { HitlGate } from '../../shared/ui/WorkflowPrimitives';
import { BroadcastGridAside } from './BroadcastGridAside';
import { BroadcastGridCalendarView } from './BroadcastGridCalendarView';
import { BroadcastGridGroupList } from './BroadcastGridGroupList';
import { BroadcastGridList } from './BroadcastGridList';
import { BroadcastGridToolbar } from './BroadcastGridToolbar';
import { PlanSettingsPanel } from './PlanSettingsPanel';
import { useBroadcastGridController } from './useBroadcastGridController';

type PlanMode = 'grid' | 'settings';

export function PlanView({
  workspace,
  onGenerate,
  onItemChange,
  onApprove,
  onSettingsSave
}: {
  workspace: WorkspaceState;
  onGenerate: () => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onSettingsSave: (settings: ContentPlanSettings) => void;
}) {
  const [mode, setMode] = useState<PlanMode>('grid');
  const items = workspace.contentPlanItems;
  const warnings = useMemo(
    () => detectBroadcastPlanConflicts(workspace, items),
    [workspace, items]
  );
  const demandSummary = useMemo(() => summarizeBroadcastGridDemand(workspace), [workspace]);
  const topicDistribution = getPlanDistribution(items, 'topicTitle');
  const fabulaDistribution = getPlanDistribution(items, 'fabulaTitle');
  const grid = useBroadcastGridController(items, warnings);

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 1 — Сетка вещания"
        title="Соберите и утвердите слоты контент-плана"
        subtitle="Сетка использует сохраненную настройку публикаций: период, темп, дни, время, платформу и лимиты кандидатов. Ручные правки слотов сохраняются, а конфликты подсвечиваются."
        action={items.length > 0 ? 'Пересобрать сетку' : 'Собрать сетку'}
        onAction={onGenerate}
      />
      <div className="tabs memory-tabs plan-mode-tabs" role="tablist" aria-label="План">
        <button className={`tab${mode === 'grid' ? ' active' : ''}`} type="button" role="tab" aria-selected={mode === 'grid'} onClick={() => setMode('grid')}>
          Сетка
        </button>
        <button className={`tab${mode === 'settings' ? ' active' : ''}`} type="button" role="tab" aria-selected={mode === 'settings'} onClick={() => setMode('settings')}>
          Настройка сетки
        </button>
      </div>
      <div className="broadcast-layout">
        <section className="broadcast-main">
          {mode === 'settings' ? (
            <PlanSettingsPanel
              demandSummary={demandSummary}
              hasCurrentPlan={items.length > 0}
              settings={workspace.contentPlanSettings}
              onGenerate={onGenerate}
              onSave={onSettingsSave}
            />
          ) : (
            <>
              <BroadcastGridToolbar
                fabulas={workspace.fabulas}
                filters={grid.filters}
                groupMode={grid.groupMode}
                items={items}
                topics={workspace.topics}
                viewMode={grid.viewMode}
                onChangeFilters={grid.setFilters}
                onChangeGroupMode={grid.setGroupMode}
                onChangeViewMode={grid.setViewMode}
              />
              {grid.viewMode === 'calendar' ? (
                <BroadcastGridCalendarView
                  items={grid.filteredItems}
                  selectedDate={grid.selectedCalendarDate}
                  workspace={workspace}
                  warnings={warnings}
                  onApprove={onApprove}
                  onItemChange={onItemChange}
                  onSelectDate={grid.setSelectedCalendarDate}
                />
              ) : grid.viewMode === 'groups' ? (
                <BroadcastGridGroupList
                  groups={grid.groups}
                  workspace={workspace}
                  warnings={warnings}
                  onItemChange={onItemChange}
                  onApprove={onApprove}
                />
              ) : (
                <BroadcastGridList
                  items={grid.filteredItems}
                  workspace={workspace}
                  warnings={warnings}
                  onItemChange={onItemChange}
                  onApprove={onApprove}
                />
              )}
            </>
          )}
        </section>
        <BroadcastGridAside
          demandSummary={demandSummary}
          fabulaDistribution={fabulaDistribution}
          items={items}
          topicDistribution={topicDistribution}
          warnings={warnings}
        />
      </div>
    </div>
  );
}

function getPlanDistribution(
  items: ContentPlanItem[],
  field: 'topicTitle' | 'fabulaTitle'
): Array<{ title: string; count: number; share: number }> {
  const total = Math.max(items.length, 1);
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const title = item[field] ?? 'Не задано';
    counts.set(title, (counts.get(title) ?? 0) + 1);
  });

  return Array.from(counts.entries()).map(([title, count]) => ({
    title,
    count,
    share: (count / total) * 100
  }));
}
