import { useEffect, useMemo, useState } from 'react';
import type { PostVisualEditPatch, VisualMode, WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EditorialVisualFields, modeLabels, toVisualDraft, toVisualPatch, type VisualDraft } from './EditorialVisualFields';

export function EditorialVisualStage({
  workspace,
  onApproveVisual,
  onOpenDraft,
  onSaveVisual
}: {
  workspace: WorkspaceState;
  onApproveVisual: (patch: PostVisualEditPatch) => void;
  onOpenDraft: () => void;
  onSaveVisual: (patch: PostVisualEditPatch) => void;
}) {
  const finalText = workspace.finalText;
  const selected = workspace.editorialWorkItems.find((item) => item.id === workspace.selectedEditorialWorkItemId) ?? null;
  const savedVisual = workspace.postVisual;
  const [draft, setDraft] = useState<VisualDraft>(() => toVisualDraft(savedVisual));

  useEffect(() => {
    setDraft(toVisualDraft(savedVisual));
  }, [savedVisual?.id, savedVisual?.updatedAt]);

  const hasUnsavedChanges = useMemo(
    () => JSON.stringify(draft) !== JSON.stringify(toVisualDraft(savedVisual)),
    [draft, savedVisual]
  );

  if (finalText?.approvalStatus !== 'approved') {
    return (
      <section className="card edit-empty editorial-workbench-empty" data-testid="editorial-visual-blocked">
        <div className="placeholder-icon">
          <Icon name="edit" size={28} />
        </div>
        <h2>Сначала утвердите текст</h2>
        <p>Визуальное решение появляется после утверждения текста в `Драфт`.</p>
        <button className="btn btn-sec" type="button" onClick={onOpenDraft}>
          Вернуться к драфту
        </button>
      </section>
    );
  }

  const isApproved = savedVisual?.approvalStatus === 'approved' && !hasUnsavedChanges;

  return (
    <section className="visual-stage" data-testid="editorial-visual-stage">
      <div className="doc-head">
        <div>
          <span className="rub">{selected?.topicTitle ?? 'Визуал'}</span>
          <h2>{finalText.title}</h2>
        </div>
        <span className={`pill ${isApproved ? 'ok' : 'pin'}`}>
          <i />
          {isApproved ? 'Визуал утвержден' : 'Визуал в работе'}
        </span>
      </div>

      <div className="post-candidate-facts visual-context">
        <div><span>Платформа</span><b>{selected?.platform ?? 'Не задана'}</b></div>
        <div><span>Публикация</span><b>{selected ? `${selected.date} · ${selected.time}` : 'Не задана'}</b></div>
        <div><span>Фабула</span><b>{selected?.fabulaTitle ?? 'Не задана'}</b></div>
        <div><span>Статус текста</span><b>Текст утвержден</b></div>
      </div>

      <article className="visual-approved-text">
        <span className="k">Утвержденный текст</span>
        <p>{finalText.body}</p>
      </article>

      <div className="visual-mode-selector" aria-label="Режим визуала">
        {(Object.keys(modeLabels) as VisualMode[]).map((mode) => (
          <button
            className={`visual-mode-option${draft.mode === mode ? ' active' : ''}`}
            key={mode}
            type="button"
            onClick={() => setDraft((current) => ({ ...current, mode }))}
          >
            {modeLabels[mode]}
          </button>
        ))}
      </div>

      <EditorialVisualFields draft={draft} onChange={setDraft} />

      {hasUnsavedChanges ? <p className="muted">Есть несохраненные правки визуала.</p> : null}
      <div className="inline-actions">
        <button className="btn btn-pri" type="button" onClick={() => onApproveVisual(toVisualPatch(draft))}>
          <Icon name="check" size={16} />
          {draft.mode === 'noVisual' ? 'Подтвердить без визуала' : 'Утвердить визуал'}
        </button>
        <button className="btn btn-sec" type="button" disabled={!hasUnsavedChanges} onClick={() => onSaveVisual(toVisualPatch(draft))}>
          Сохранить правки
        </button>
        <button className="btn btn-sec" type="button" onClick={onOpenDraft}>
          Вернуться к драфту
        </button>
      </div>
    </section>
  );
}
