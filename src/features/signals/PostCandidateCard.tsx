import { useState } from 'react';
import type { Fabula, PostCandidate, PostCandidateEditPatch, SourceSignal, Topic } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { PostCandidateEditForm } from './PostCandidateEditForm';
import { getCandidateRiskLevel } from './postCandidateFilters';

export function PostCandidateCard({
  candidate,
  fabula,
  isSelected,
  signal,
  topic,
  onApprove,
  onEdit,
  onReject
}: {
  candidate: PostCandidate;
  fabula?: Fabula;
  isSelected: boolean;
  signal?: SourceSignal;
  topic?: Topic;
  onApprove: (candidate: PostCandidate) => void;
  onEdit: (candidate: PostCandidate, patch: PostCandidateEditPatch) => void;
  onReject: (candidate: PostCandidate) => void;
}) {
  const [editing, setEditing] = useState(false);
  const disabled = candidate.approvalStatus === 'rejected';
  const riskLevel = getCandidateRiskLevel(candidate);

  if (editing) {
    return (
      <article className="card candidate-card post-candidate-card" data-testid="post-candidate-card">
        <div className="candidate-body">
          <div className="candidate-head">
            <span className="sig info">{signal?.title ?? candidate.sourceSignalId}</span>
            <span className={`sc risk-${riskLevel}`}>risk {riskLevel}</span>
            <span className="sc">{candidateStatusLabel(candidate)}</span>
          </div>
          <PostCandidateEditForm
            candidate={candidate}
            onCancel={() => setEditing(false)}
            onSave={(patch) => {
              onEdit(candidate, patch);
              setEditing(false);
            }}
          />
        </div>
      </article>
    );
  }

  return (
    <article
      className={`card candidate-card post-candidate-card${isSelected ? ' selected' : ''}${disabled ? ' muted' : ''}`}
      data-testid="post-candidate-card"
    >
      <div className="candidate-body">
        <div className="candidate-head">
          <span className="sig info">{signal?.title ?? candidate.sourceSignalId}</span>
          <span className={`sc risk-${riskLevel}`}>risk {riskLevel}</span>
          <span className="sc">confidence {Math.round(candidate.confidence * 100)}%</span>
          <span className="sc">{candidateStatusLabel(candidate)}</span>
        </div>
        <h3>{candidate.title}</h3>
        <p>{candidate.thesis}</p>
        <dl className="meta-list post-candidate-meta">
          <dt>Platform</dt>
          <dd>{candidate.platform}</dd>
          <dt>Format</dt>
          <dd>{candidate.format}</dd>
          <dt>Topic</dt>
          <dd>{topic?.title ?? candidate.topicId}</dd>
          <dt>Fabula</dt>
          <dd>{fabula?.title ?? candidate.fabulaId}</dd>
        </dl>
        <div className="post-candidate-facts">
          <CandidateFact label="Сигнал" value={signal?.title ?? candidate.sourceSignalId} />
          <CandidateFact label="Аудитория" value={candidate.audience} />
          <CandidateFact label="Ценность" value={candidate.value} />
          <CandidateFact label="Цель" value={candidate.goal} />
          <CandidateFact label="Доказательство" value={candidate.evidenceSummary} wide />
        </div>
        <div className="post-candidate-risks">
          <span className="rub">Risks</span>
          <ul>
            {candidate.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </div>
        <div className="inline-actions">
          <button className="btn btn-pri btn-sm" type="button" disabled={isSelected || disabled} onClick={() => onApprove(candidate)}>
            <Icon name="check" size={16} />
            {isSelected ? 'Утвержден' : 'Утвердить'}
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => setEditing(true)}>
            Редактировать
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onReject(candidate)}>
            Отклонить
          </button>
        </div>
      </div>
    </article>
  );
}

function CandidateFact({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  return (
    <div className={wide ? 'wide' : undefined}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function candidateStatusLabel(candidate: PostCandidate): string {
  if (candidate.approvalStatus === 'approved') return 'Утвержден';
  if (candidate.approvalStatus === 'rejected') return 'Отклонен';
  return 'Новый';
}
