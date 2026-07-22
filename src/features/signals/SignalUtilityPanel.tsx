import type {
  SignalEvidence,
  SignalQualityCheck,
  SignalRelationshipKind,
  SignalUtilityCriterionResult,
  SourceSignal,
  WorkspaceState
} from '../../domain/editorialWorkspace';
import {
  radarFilterModeLabel,
  signalUtilityRecommendationLabel
} from './helpers';

export function SignalUtilityPanel({
  projectId,
  signal,
  workspace
}: {
  projectId: string;
  signal: SourceSignal;
  workspace: WorkspaceState;
}) {
  if (signal.legacyIntegrityStatus === 'needsReExtraction') {
    return (
      <section className="radar-config-section signal-legacy-utility" data-testid="signal-legacy-utility">
        <h4>Редакционная полезность</h4>
        <strong>Требуется повторное извлечение</strong>
        <p>Старая клиентская оценка сохранена только как история и не является текущим вердиктом.</p>
      </section>
    );
  }
  if (!signal.utilityReport) {
    return (
      <section className="radar-config-section" data-testid="signal-utility-unscored">
        <h4>Редакционная полезность</h4>
        <p>Не оценена. Сигнал остается на проверке.</p>
      </section>
    );
  }
  if (signal.utilityReport.version < 2 || !signal.utilityReport.radarCriteria) {
    return (
      <section className="radar-config-section" data-testid="signal-utility-legacy-report">
        <h4>Редакционная полезность</h4>
        <p>Отчет создан по старому контракту. Для человекочитаемых критериев и проверки связей нужен пересчет.</p>
      </section>
    );
  }

  const relationshipReport = signal.relationshipReport ?? signal.utilityReport.relationshipReport;
  return (
    <div className="signal-explainability" data-testid="signal-utility-report">
      <section className="radar-config-section signal-utility">
        <div className="signal-utility-head">
          <div>
            <h4>Редакционная полезность</h4>
            <p>Рекомендация помогает редактору, но не меняет статус сигнала автоматически.</p>
          </div>
          <span className={`sc utility-${signal.utilityReport.recommendation}`}>
            {signalUtilityRecommendationLabel(signal.utilityReport.recommendation)}
          </span>
        </div>
        {signal.utilityReport.status === 'stale' ? <p>Оценка устарела после редакционной коррекции и требует пересчета.</p> : null}
      </section>

      <CriteriaSection
        title="Соответствие радару"
        description="Проверки, которые явно настроены в этом радаре."
        criteria={signal.utilityReport.radarCriteria}
        projectId={projectId}
        signal={signal}
      />
      <CriteriaSection
        title="Соответствие редакционной модели"
        description="Применимые правила проекта: автор, аудитория, позиция, цели, темы и запреты."
        criteria={signal.utilityReport.projectCriteria ?? []}
        exclusions={signal.utilityReport.notApplicableSettings ?? []}
        projectId={projectId}
        signal={signal}
      />
      <QualitySection
        checks={signal.utilityReport.qualityChecks ?? []}
        projectId={projectId}
        signal={signal}
      />
      <RelationshipSection
        report={relationshipReport}
        signal={signal}
        workspace={workspace}
      />
    </div>
  );
}

function CriteriaSection({
  title,
  description,
  criteria,
  exclusions = [],
  projectId,
  signal
}: {
  title: string;
  description: string;
  criteria: SignalUtilityCriterionResult[];
  exclusions?: Array<{ settingId: string; title: string; reason: string }>;
  projectId: string;
  signal: SourceSignal;
}) {
  return (
    <section className="radar-config-section signal-criteria-section">
      <div className="signal-section-heading">
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
      <div className="signal-criterion-list">
        {criteria.map((criterion) => (
          <article className={`signal-criterion criterion-${criterion.effect}`} key={criterion.criterionId}>
            <div className="signal-criterion-heading">
              <div>
                <strong>{criterion.title}</strong>
                <p>{criterion.statement}</p>
              </div>
              <span className={`sc criterion-verdict criterion-${criterion.effect}`}>{criterion.verdict}</span>
            </div>
            <div className="signal-criterion-meta">
              <span>{criterion.origin === 'radar' ? 'Фильтр радара' : 'Настройка проекта'}</span>
              <span>{radarFilterModeLabel(criterion.mode)}</span>
            </div>
            <p>{criterion.summary}</p>
            {criterion.uncertainty ? <small>{criterion.uncertainty}</small> : null}
            <CriterionEvidence projectId={projectId} signal={signal} refs={criterion.evidenceRefs} />
          </article>
        ))}
        {criteria.length === 0 ? <p className="muted">Для этой группы нет применимых настроек.</p> : null}
      </div>
      {exclusions.length > 0 ? (
        <details className="signal-excluded-settings">
          <summary>Что не оценивается на этапе сигнала</summary>
          <ul>
            {exclusions.map((item) => <li key={item.settingId}>{item.title}: {exclusionReason(item.reason)}</li>)}
          </ul>
        </details>
      ) : null}
    </section>
  );
}

function QualitySection({
  checks,
  projectId,
  signal
}: {
  checks: SignalQualityCheck[];
  projectId: string;
  signal: SourceSignal;
}) {
  const applicable = checks.filter((item) => item.applicable);
  return (
    <section className="radar-config-section signal-quality-section">
      <div className="signal-section-heading">
        <h4>Качество и риски</h4>
        <p>Системные проверки доказательности. Это не пользовательские фильтры радара.</p>
      </div>
      <div className="signal-criterion-list">
        {applicable.map((check) => (
          <article className={`signal-criterion criterion-${check.effect}`} key={check.checkId}>
            <div className="signal-criterion-heading">
              <strong>{check.title}</strong>
              <span className={`sc criterion-verdict criterion-${check.effect}`}>{check.verdict}</span>
            </div>
            <p>{check.summary}</p>
            <CriterionEvidence projectId={projectId} signal={signal} refs={check.evidenceRefs} />
          </article>
        ))}
      </div>
    </section>
  );
}

function RelationshipSection({
  report,
  signal,
  workspace
}: {
  report: SourceSignal['relationshipReport'];
  signal: SourceSignal;
  workspace: WorkspaceState;
}) {
  if (!report || report.status !== 'checked') {
    return (
      <section className="radar-config-section signal-relationship-section">
        <h4>Связанные сигналы</h4>
        <p>Не проверено. Система не назначает низкий риск дубля без доказательства.</p>
      </section>
    );
  }
  const meaningful = report.relations.filter((item) => item.kind !== 'distinct');
  return (
    <section className="radar-config-section signal-relationship-section">
      <div className="signal-section-heading">
        <h4>Связанные сигналы</h4>
        <p>Дубли, соседние тезисы, подтверждения и противоречия оцениваются отдельно от полезности проекту.</p>
      </div>
      {report.canonicalSignalId !== signal.id ? (
        <p className="signal-canonical-note">
          Этот сигнал входит в тот же основной тезис, что и «{signalTitle(workspace, report.canonicalSignalId)}».
        </p>
      ) : null}
      <div className="signal-relationship-list">
        {meaningful.map((relationship) => (
          <article className="signal-relationship" key={`${relationship.otherSignalId}-${relationship.kind}`}>
            <span className="sc">{relationshipLabel(relationship.kind)}</span>
            <strong>{signalTitle(workspace, relationship.otherSignalId)}</strong>
            <p>{relationship.summary}</p>
            <RelationshipEvidence signal={workspace.sourceSignals.find((item) => item.id === relationship.otherSignalId)} />
          </article>
        ))}
        {meaningful.length === 0 ? <p className="muted">Значимых связей с другими сигналами не найдено.</p> : null}
      </div>
    </section>
  );
}

function RelationshipEvidence({ signal }: { signal?: SourceSignal }) {
  const evidence = signal?.evidence?.[0];
  if (!evidence) return null;
  return (
    <div className="signal-relationship-evidence">
      <strong>{evidence.sourceTitle || sourceDomain(evidence.sourceUrl)}</strong>
      <blockquote>{evidence.quote}</blockquote>
    </div>
  );
}

function CriterionEvidence({
  projectId,
  signal,
  refs
}: {
  projectId: string;
  signal: SourceSignal;
  refs: Array<{ materialId: string; fragmentId: string }>;
}) {
  const evidence = resolveEvidence(signal, refs);
  if (evidence.length === 0) return null;
  return (
    <div className="criterion-evidence-list">
      {evidence.map((item) => (
        <div className="criterion-evidence" key={item.id}>
          <strong>{item.sourceTitle || sourceDomain(item.sourceUrl)}</strong>
          <blockquote>{item.quote}</blockquote>
          <div className="criterion-evidence-actions">
            {safeSourceUrl(item.sourceUrl) ? <a href={item.sourceUrl} target="_blank" rel="noopener noreferrer">Открыть источник</a> : null}
            {signal.radarRunId ? (
              <a href={`/radar-runs?runId=${encodeURIComponent(signal.radarRunId)}&projectId=${encodeURIComponent(projectId)}&detailId=signal-extraction&signalId=${encodeURIComponent(signal.id)}`}>
                Показать в трассе
              </a>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

function resolveEvidence(signal: SourceSignal, refs: Array<{ materialId: string; fragmentId: string }>): SignalEvidence[] {
  return refs.flatMap((ref) => {
    const item = (signal.evidence ?? []).find((candidate) =>
      candidate.materialId === ref.materialId && candidate.fragmentId === ref.fragmentId
    );
    return item ? [item] : [];
  });
}

function signalTitle(workspace: WorkspaceState, signalId: string): string {
  return workspace.sourceSignals.find((item) => item.id === signalId)?.title ?? 'Связанный сигнал';
}

function relationshipLabel(kind: SignalRelationshipKind): string {
  const labels: Record<SignalRelationshipKind, string> = {
    exactDuplicate: 'ТОЧНЫЙ ДУБЛЬ',
    sameClaim: 'ОДИН ТЕЗИС',
    relatedSameSource: 'СОСЕДНИЙ ТЕЗИС ИЗ ТОГО ЖЕ ИСТОЧНИКА',
    corroborates: 'ПОДТВЕРЖДАЕТ',
    contradicts: 'ПРОТИВОРЕЧИТ',
    inconclusive: 'СВЯЗЬ НЕ ДОКАЗАНА',
    distinct: 'ОТДЕЛЬНЫЙ СИГНАЛ'
  };
  return labels[kind];
}

function exclusionReason(reason: string): string {
  if (reason === 'notThisStage') return 'будет проверено на более позднем редакционном этапе';
  return 'не применимо к этому типу сигнала';
}

function safeSourceUrl(value: string): boolean {
  try {
    return ['http:', 'https:'].includes(new URL(value).protocol);
  } catch {
    return false;
  }
}

function sourceDomain(value: string): string {
  try {
    return new URL(value).hostname.replace(/^www\./, '');
  } catch {
    return 'Источник';
  }
}
