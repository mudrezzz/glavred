import type { PostCandidate } from '../../domain/editorialWorkspace';

export function CandidateFact({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  return (
    <div className={wide ? 'wide' : undefined}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

export function candidateStatusLabel(candidate: PostCandidate): string {
  if (candidate.approvalStatus === 'approved') return 'Утвержден';
  if (candidate.approvalStatus === 'rejected') return 'Отклонен';
  return 'Новый';
}
