import type { SourceSignal } from '../../domain/editorialWorkspace';
import { formatDate, signalReviewStatusLabel } from './helpers';

export function SignalReviewHistory({ signal }: { signal: SourceSignal }) {
  if ((signal.reviewHistory ?? []).length === 0) return null;
  return (
    <section className="radar-config-section signal-review-history" data-testid="signal-review-history">
      <h4>История решений</h4>
      {(signal.reviewHistory ?? []).map((event) => (
        <article key={event.id}>
          <strong>{signalReviewStatusLabel(event.fromStatus)} → {signalReviewStatusLabel(event.toStatus)}</strong>
          <span>{formatDate(event.occurredAt)} · {event.actorId}</span>
          {event.reason ? <p>{event.reason}</p> : null}
        </article>
      ))}
    </section>
  );
}
