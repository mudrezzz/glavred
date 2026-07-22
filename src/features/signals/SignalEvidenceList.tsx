import type { SourceSignal } from '../../domain/editorialWorkspace';

export function SignalEvidenceList({ projectId, signal }: { projectId: string; signal: SourceSignal }) {
  return (
    <section className="radar-config-section" data-testid="signal-evidence-section">
      <h4>Доказательства</h4>
      <div className="signal-evidence-list">
        {(signal.evidence ?? []).map((item, index) => (
          <article className="signal-evidence" key={`${item.id}-${item.materialId ?? ''}-${item.fragmentId ?? ''}-${index}`}>
            <div className="signal-source-title">
              <span>Оригинальное название источника</span>
              <strong>{item.sourceTitle}</strong>
            </div>
            <blockquote>
              <span>Оригинальная цитата</span>
              <p>{item.quote}</p>
            </blockquote>
            {item.summary ? <small>{item.summary}</small> : null}
            <div className="signal-evidence-actions">
              {safeSourceUrl(item.sourceUrl) ? (
                <a className="btn btn-sec btn-sm" href={item.sourceUrl} target="_blank" rel="noopener noreferrer">
                  Открыть источник · {sourceDomain(item.sourceUrl)}
                </a>
              ) : null}
              {signal.radarRunId ? (
                <a
                  className="btn btn-ghost btn-sm"
                  href={`/radar-runs?runId=${encodeURIComponent(signal.radarRunId)}&projectId=${encodeURIComponent(projectId)}&detailId=signal-extraction&signalId=${encodeURIComponent(signal.id)}`}
                >
                  Показать в трассе
                </a>
              ) : null}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
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
    return 'источник';
  }
}
