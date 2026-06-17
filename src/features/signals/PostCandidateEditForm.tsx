import { useState } from 'react';
import type {
  Fabula,
  PostCandidate,
  PostCandidateEditPatch,
  SourceSignal,
  Topic,
  TopicFabulaMatrixEntry
} from '../../domain/editorialWorkspace';
import { PostCandidateEditContext } from './PostCandidateEditContext';

export function PostCandidateEditForm({
  candidate,
  fabulas,
  matrix,
  signal,
  topic,
  onCancel,
  onSave
}: {
  candidate: PostCandidate;
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  signal?: SourceSignal;
  topic?: Topic;
  onCancel: () => void;
  onSave: (patch: PostCandidateEditPatch) => void;
}) {
  const [draft, setDraft] = useState({
    fabulaId: candidate.fabulaId,
    title: candidate.title,
    thesis: candidate.thesis,
    audience: candidate.audience,
    value: candidate.value,
    goal: candidate.goal,
    platform: candidate.platform,
    evidenceSummary: candidate.evidenceSummary,
    risks: candidate.risks.join('\n')
  });

  function patchDraft(patch: Partial<typeof draft>) {
    setDraft((current) => ({ ...current, ...patch }));
  }

  function save() {
    onSave({
      ...draft,
      risks: draft.risks
        .split('\n')
        .map((risk) => risk.trim())
        .filter(Boolean)
    });
  }

  return (
    <div className="post-candidate-edit-form">
      <PostCandidateEditContext
        fabulaId={draft.fabulaId}
        fabulas={fabulas}
        matrix={matrix}
        signal={signal}
        topic={topic}
        onFabulaChange={(fabulaId) => patchDraft({ fabulaId })}
      />
      <label>
        Название
        <input value={draft.title} onChange={(event) => patchDraft({ title: event.target.value })} />
      </label>
      <label>
        Тезис
        <textarea value={draft.thesis} onChange={(event) => patchDraft({ thesis: event.target.value })} />
      </label>
      <label>
        Аудитория
        <textarea value={draft.audience} onChange={(event) => patchDraft({ audience: event.target.value })} />
      </label>
      <label>
        Ценность
        <textarea value={draft.value} onChange={(event) => patchDraft({ value: event.target.value })} />
      </label>
      <label>
        Цель
        <textarea value={draft.goal} onChange={(event) => patchDraft({ goal: event.target.value })} />
      </label>
      <div className="post-candidate-edit-row">
        <label>
          Платформа
          <input value={draft.platform} onChange={(event) => patchDraft({ platform: event.target.value })} />
        </label>
      </div>
      <label>
        Доказательство
        <textarea value={draft.evidenceSummary} onChange={(event) => patchDraft({ evidenceSummary: event.target.value })} />
      </label>
      <label>
        Risks
        <textarea value={draft.risks} onChange={(event) => patchDraft({ risks: event.target.value })} />
      </label>
      <div className="inline-actions">
        <button className="btn btn-pri btn-sm" type="button" onClick={save}>
          Сохранить
        </button>
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
      </div>
    </div>
  );
}
