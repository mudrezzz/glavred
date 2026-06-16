import { useMemo, useState } from 'react';
import {
  createRadarDraft,
  isRadarSourceConfigurationValid,
  type ImportRiskLevel,
  type RadarDefinition,
  type RadarEditorialFilterMode,
  type RadarEditorialFilterRule,
  type RadarSearchRule,
  type RadarSearchSource,
  type RadarSourceDiscoveryMode,
  type SignalFilterStatus,
  type SignalReviewStatus,
  type SourceSignal,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import {
  EmptyState,
  SummaryItem,
  duplicateRiskLabel,
  formatDate,
  radarAcceptancePolicyLabel,
  radarFilterDimensionLabel,
  radarFilterModeLabel,
  radarRuleOperatorLabel,
  radarSearchSourceTypeLabel,
  radarSourceDiscoveryModeLabel,
  radarSourceTypeLabel,
  radarStatusLabel,
  radarTriggerModeLabel,
  signalFilterEvaluationLabel,
  signalFilterStatusLabel,
  signalReviewStatusLabel,
  type SignalsTab
} from './helpers';

export function SignalsSidePanel({
  workspace,
  summary,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  summary: { total: number; new: number; approved: number; archived: number; highRisk: number };
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  return (
    <aside className="memory-side">
      <section className="panel signal-side-panel">
        <h3>Сигналы перед кандидатами</h3>
        <p>Утвержденный сигнал становится текущим материалом для инсайта. Темы и фабулы появятся на шаге кандидатов.</p>
        <div className="signal-summary-grid">
          <SummaryItem label="Всего" value={summary.total} />
          <SummaryItem label="Новые" value={summary.new} />
          <SummaryItem label="Утверждено" value={summary.approved} />
          <SummaryItem label="В архиве" value={summary.archived} />
          <SummaryItem label="High duplicate" value={summary.highRisk} />
        </div>
        {workspace.postCandidate && (
          <div className="context-empty">
            Текущий кандидат: {workspace.postCandidate.title}
          </div>
        )}
        <button className="btn btn-sec wide" type="button" onClick={onCreateInsight}>
          <Icon name="radar" size={16} />
          Собрать инсайт
        </button>
      </section>
      {workspace.insightCard && (
        <section className="panel insight-mini">
          <span className="sig">Текущий инсайт</span>
          <h4>{workspace.insightCard.title}</h4>
          <p>{workspace.insightCard.whyItMatters}</p>
          <button className="btn btn-pri wide" type="button" onClick={onPlan}>
            В план
          </button>
        </section>
      )}
    </aside>
  );
}
