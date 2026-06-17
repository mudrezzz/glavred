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
import { BroadcastGridList } from './BroadcastGridList';
import { PlanSettingsPanel } from './PlanSettingsPanel';

type PlanMode = 'grid' | 'settings';

export function PlanView({
  workspace,
  onGenerate,
  onItemChange,
  onApprove,
  onBrief,
  onSettingsSave
}: {
  workspace: WorkspaceState;
  onGenerate: () => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
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

  return (
    <div className="page wide fade-up">
      <div className="plan-mode-tabs segmented memory-tabs" role="tablist" aria-label="План">
        <button
          className={mode === 'grid' ? 'active' : ''}
          type="button"
          role="tab"
          aria-selected={mode === 'grid'}
          onClick={() => setMode('grid')}
        >
          Сетка
        </button>
        <button
          className={mode === 'settings' ? 'active' : ''}
          type="button"
          role="tab"
          aria-selected={mode === 'settings'}
          onClick={() => setMode('settings')}
        >
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
              <HitlGate
                tag="HITL · Gate 1 — Сетка вещания"
                title="Соберите и утвердите слоты контент-плана"
                subtitle="Сетка использует сохраненную настройку публикаций: период, темп, дни, время, платформу и лимиты кандидатов. Ручные правки слотов сохраняются, а конфликты подсвечиваются."
                action={items.length > 0 ? 'Пересобрать сетку' : 'Собрать сетку'}
                onAction={onGenerate}
              />
              <BroadcastGridList
                items={items}
                workspace={workspace}
                warnings={warnings}
                onGenerate={onGenerate}
                onItemChange={onItemChange}
                onApprove={onApprove}
                onBrief={onBrief}
              />
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
