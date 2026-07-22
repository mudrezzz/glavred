import type { RadarDefinition, SourceSignal } from '../../domain/editorialWorkspace';
import { formatDate } from './helpers';

export function SignalReadOnlyDetails({ signal, radar }: { signal: SourceSignal; radar?: RadarDefinition }) {
  const structured = Boolean(signal.editorialLanguage || signal.mechanism || signal.outcome || (signal.evidenceRefs ?? []).length > 0);
  const outcomeCheck = signal.utilityReport?.qualityChecks?.find((item) => item.checkId === 'outcome-support');
  const mechanismApplicable = signal.utilityReport?.qualityChecks?.find((item) => item.checkId === 'mechanism-support')?.applicable
    ?? ['case', 'practice', 'change', 'problemFailureMode', 'recurringPattern'].includes(signal.type);
  const outcomeApplicable = outcomeCheck?.applicable
    ?? ['case', 'practice', 'change', 'problemFailureMode', 'eventFact'].includes(signal.type);
  return (
    <>
      <section className="signal-detail-section">
        <h4>Что утверждает источник</h4>
        <p>{signal.summary}</p>
      </section>
      <dl className="meta-list signal-facts">
        <dt>Радар</dt>
        <dd>{radar?.title ?? signal.source}</dd>
        <dt>Дата</dt>
        <dd>{formatDate(signal.capturedAt)}</dd>
        <dt>Источник</dt>
        <dd>{signal.source}</dd>
        {!structured ? <><dt>Рабочая заметка</dt><dd>{signal.rawNote}</dd></> : null}
        {signal.confidence ? <><dt>Уверенность извлечения</dt><dd>{confidenceLabel(signal.confidence)}</dd></> : null}
        {signal.uncertainty ? <><dt>Неопределенность</dt><dd>{signal.uncertainty}</dd></> : null}
        {signal.mechanism && mechanismApplicable ? <><dt>Как это работает</dt><dd>{signal.mechanism}</dd></> : null}
        {signal.outcome && outcomeApplicable ? <><dt>{outcomeLabel(outcomeCheck?.classification)}</dt><dd>{signal.outcome}</dd></> : null}
        {(signal.limitations ?? []).length > 0 ? <><dt>Ограничения</dt><dd>{signal.limitations?.join('; ')}</dd></> : null}
        <dt>Правка автора</dt>
        <dd>{signal.authorCorrection || 'нет'}</dd>
      </dl>
    </>
  );
}

function outcomeLabel(classification: string | null | undefined): string {
  if (classification === 'observed') return 'Наблюдаемый результат';
  if (classification === 'reported') return 'Заявленный результат';
  if (classification === 'capabilityOnly') return 'Описанная функция';
  if (classification === 'expected') return 'Ожидаемый эффект';
  return 'Что получилось';
}

function confidenceLabel(value: NonNullable<SourceSignal['confidence']>): string {
  return value === 'high' ? 'Высокая' : value === 'medium' ? 'Средняя' : 'Низкая';
}
