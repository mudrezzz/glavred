import { Icon } from '../../shared/ui/Icon';

export function TraceRunLink({
  runId,
  label = 'Открыть трассировку DraftRun'
}: {
  runId: string;
  label?: string;
}) {
  return (
    <a
      className="trace-run-link"
      href={`/ai-runs?runId=${encodeURIComponent(runId)}`}
      target="_blank"
      rel="noreferrer"
    >
      <Icon name="search" size={14} />
      {label}
    </a>
  );
}
