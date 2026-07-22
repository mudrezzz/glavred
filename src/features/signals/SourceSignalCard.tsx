import type { SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';
import { SignalEditPanel } from './SignalEditPanel';
import { SignalEvidenceList } from './SignalEvidenceList';
import { SignalReadOnlyDetails } from './SignalReadOnlyDetails';
import { SignalReviewHistory } from './SignalReviewHistory';
import { SignalUtilityPanel } from './SignalUtilityPanel';
import {
  formatDate,
  signalReviewStatusLabel,
  signalUtilityRecommendationLabel
} from './helpers';
import type { SignalsController } from './useSignalsController';

export function SourceSignalCard({
  projectId,
  signal,
  workspace,
  controller,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onReopenSignal,
  onRestoreSignal,
  onRescoreSignal
}: {
  projectId: string;
  signal: SourceSignal;
  workspace: WorkspaceState;
  controller: SignalsController;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onReopenSignal?: (signal: SourceSignal) => void;
  onRestoreSignal?: (signal: SourceSignal) => void;
  onRescoreSignal?: (signal: SourceSignal) => void;
}) {
  const radar = workspace.radars.find((item) => item.id === signal.radarId);
  const expanded = controller.expandedSignalId === signal.id;
  const editing = controller.editingSignal?.id === signal.id;
  return (
    <article className={`entity-row signal-card ${expanded ? 'expanded' : ''}`} data-testid="source-signal-row">
      <button className="signal-row-main" type="button" onClick={() => controller.setExpandedSignalId(expanded ? '' : signal.id)}>
        <span className="signal-row-top">
          <span className="signal-radar">{radar?.title ?? signal.source}</span>
          <span className={`pill signal-status ${signal.reviewStatus === 'approved' ? 'ok' : 'pin'}`}>
            {signalReviewStatusLabel(signal.reviewStatus)}
          </span>
        </span>
        <strong className="signal-title">{signal.title}</strong>
        <span className="signal-row-meta">
          <span className="signal-date">{formatDate(signal.capturedAt)}</span>
          <span className="sc signal-relationship-summary">{relationshipSummary(signal)}</span>
          <span className="sc signal-utility-summary">{utilityLabel(signal)}</span>
        </span>
      </button>

      {expanded ? (
        <div className="radar-details signal-details">
          <SignalReadOnlyDetails signal={signal} radar={radar} />
          <SignalUtilityPanel projectId={projectId} signal={signal} workspace={workspace} />
          <SignalEvidenceList projectId={projectId} signal={signal} />
          <SignalReviewHistory signal={signal} />
          {editing ? <SignalEditPanel controller={controller} /> : null}
          {!editing ? (
            <div className="row-actions signal-actions entity-actions-footer">
              {['candidate', 'new', 'corrected'].includes(signal.reviewStatus ?? 'candidate') ? (
                <button className="btn btn-pri btn-sm" type="button" onClick={() => onApproveSignal(signal)}>Утвердить</button>
              ) : null}
              {['candidate', 'new', 'corrected'].includes(signal.reviewStatus ?? 'candidate') ? (
                <button className="btn btn-sec btn-sm" type="button" onClick={() => controller.startSignalEdit(signal)}>Корректировать</button>
              ) : null}
              {['approved', 'rejected'].includes(signal.reviewStatus ?? '') ? (
                <button className="btn btn-sec btn-sm" type="button" onClick={() => onReopenSignal?.(signal)}>Вернуть на проверку</button>
              ) : null}
              {signal.reviewStatus === 'archived' ? (
                <button className="btn btn-sec btn-sm" type="button" onClick={() => onRestoreSignal?.(signal)}>Восстановить</button>
              ) : null}
              {signal.radarRunId && signal.legacyIntegrityStatus !== 'needsReExtraction' && onRescoreSignal ? <button className="btn btn-sec btn-sm" type="button" onClick={() => onRescoreSignal(signal)}>Пересчитать полезность</button> : null}
              {['candidate', 'new', 'corrected'].includes(signal.reviewStatus ?? 'candidate') ? (
                <button className="btn btn-ghost btn-sm" type="button" onClick={() => onArchiveSignal(signal)}>В архив</button>
              ) : null}
              {['candidate', 'new', 'corrected'].includes(signal.reviewStatus ?? 'candidate') ? (
                <button className="btn btn-ghost btn-sm" type="button" onClick={() => onRejectSignal(signal)}>Отклонить</button>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </article>
  );
}

function utilityLabel(signal: SourceSignal): string {
  if (signal.legacyIntegrityStatus === 'needsReExtraction') return 'Требуется повторное извлечение';
  if (!signal.utilityReport) return 'Редакционная полезность не оценена';
  return signalUtilityRecommendationLabel(signal.utilityReport.recommendation);
}

function relationshipSummary(signal: SourceSignal): string {
  const report = signal.relationshipReport ?? signal.utilityReport?.relationshipReport;
  if (!report || report.status !== 'checked') return 'Связи: не проверено';
  if (report.canonicalSignalId !== signal.id) return 'Связь: один тезис';
  if (report.relations.some((item) => item.kind === 'exactDuplicate' || item.kind === 'sameClaim')) return 'Есть объединенные дубли';
  if (report.relations.some((item) => item.kind === 'relatedSameSource')) return 'Есть соседний тезис';
  return 'Дубли не найдены';
}
