import { useEffect, useState } from 'react';
import type { PostBriefEditPatch, PostDraft, PostVisualEditPatch, WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EditorialBriefStage } from './EditorialBriefStage';
import { EditorialVisualStage } from './EditorialVisualStage';

export function EditorialWorkbench({
  workspace,
  onApproveBrief,
  onApproveFinal,
  onApproveVisual,
  onDraftChange,
  onEditBrief,
  onGoPlan,
  onPrepareVisualVariants,
  onSelectVisualVariant,
  onSaveVisual
}: {
  workspace: WorkspaceState;
  onApproveBrief: () => void;
  onApproveFinal: (body?: string) => void;
  onApproveVisual: (patch: PostVisualEditPatch) => void;
  onDraftChange: (body: string) => void;
  onEditBrief: (patch: PostBriefEditPatch) => void;
  onGoPlan: () => void;
  onPrepareVisualVariants: (patch: PostVisualEditPatch) => void;
  onSelectVisualVariant: (variantId: string) => void;
  onSaveVisual: (patch: PostVisualEditPatch) => void;
}) {
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;
  const [tab, setTab] = useState<'brief' | 'draft' | 'visual'>(() => {
    if (!brief || brief.approvalStatus !== 'approved') return 'brief';
    if (finalText?.approvalStatus === 'approved') return 'visual';
    return 'draft';
  });

  if (!workspace.selectedEditorialWorkItemId) {
    return (
      <section className="card edit-empty editorial-workbench-empty">
        <div className="placeholder-icon">
          <Icon name="brief" size={28} />
        </div>
        <h2>Выберите пост из очереди</h2>
        <p>Редактура работает с конкретным утвержденным слотом: сначала откройте строку в очереди, затем готовьте фабулу, драфт и визуал.</p>
      </section>
    );
  }

  if (!brief) {
    return (
      <section className="card edit-empty editorial-workbench-empty">
        <div className="placeholder-icon">
          <Icon name="brief" size={28} />
        </div>
        <h2>Фабула еще не подготовлена</h2>
        <p>Для этого поста уже есть work item, но фабулу нужно подготовить из утвержденного слота в плане.</p>
        <button className="btn btn-sec" type="button" onClick={onGoPlan}>
          Вернуться в план
        </button>
      </section>
    );
  }

  return (
    <section className="editorial-workbench" data-testid="editorial-workbench">
      <div className="tabs" role="tablist" aria-label="Редакторские стадии">
        <button className={`tab${tab === 'brief' ? ' active' : ''}`} type="button" role="tab" aria-selected={tab === 'brief'} onClick={() => setTab('brief')}>
          Фабула
        </button>
        <button className={`tab${tab === 'draft' ? ' active' : ''}`} type="button" role="tab" aria-selected={tab === 'draft'} onClick={() => setTab('draft')}>
          Драфт
        </button>
        <button className={`tab${tab === 'visual' ? ' active' : ''}`} type="button" role="tab" aria-selected={tab === 'visual'} onClick={() => setTab('visual')}>
          Визуал
        </button>
      </div>
      {tab === 'brief' ? (
        <EditorialBriefStage
          brief={brief}
          workspace={workspace}
          onApproveBrief={onApproveBrief}
          onEditBrief={(patch) => {
            onEditBrief(patch);
            setTab('brief');
          }}
          onGoPlan={onGoPlan}
          onOpenDraft={() => setTab('draft')}
        />
      ) : tab === 'visual' ? (
        <EditorialVisualStage
          workspace={workspace}
          onApproveVisual={onApproveVisual}
          onOpenDraft={() => setTab('draft')}
          onPrepareVisualVariants={onPrepareVisualVariants}
          onSaveVisual={onSaveVisual}
          onSelectVisualVariant={onSelectVisualVariant}
        />
      ) : !draft ? (
        <section className="card draft-start">
          <span className="rub">{brief.rubric}</span>
          <h2>{brief.title}</h2>
          <p>Драфт появится после утверждения фабулы.</p>
          <button className="btn btn-sec" type="button" onClick={() => setTab('brief')}>
            Вернуться к фабуле
          </button>
        </section>
      ) : (
        <section className="doc">
          <DraftEditor
            draft={draft}
            isTextApproved={finalText?.approvalStatus === 'approved'}
            onApproveDraft={onApproveFinal}
            onDraftChange={onDraftChange}
            onOpenBrief={() => setTab('brief')}
          />
        </section>
      )}
    </section>
  );
}

function DraftEditor({
  draft,
  isTextApproved,
  onApproveDraft,
  onDraftChange,
  onOpenBrief
}: {
  draft: PostDraft;
  isTextApproved: boolean;
  onApproveDraft: (body: string) => void;
  onDraftChange: (body: string) => void;
  onOpenBrief: () => void;
}) {
  const [body, setBody] = useState(draft.body);
  const hasUnsavedChanges = body !== draft.body;

  useEffect(() => {
    setBody(draft.body);
  }, [draft.body, draft.id]);

  return (
    <>
      <div className="doc-head">
        <div>
          <span className="rub">Версия {draft.version}</span>
          <h2>{draft.title}</h2>
        </div>
        <span className={`pill ${draft.status === 'revised' ? 'pin' : 'ok'}`}>
          <i />
          {draft.status === 'revised' ? 'Отредактирован' : 'Драфт'}
        </span>
      </div>
      {isTextApproved ? (
        <div className="final-status">
          <span className="pill ok">
            <i />
            Текст утвержден
          </span>
          <span>следующий шаг: Визуал</span>
        </div>
      ) : null}
      <label className="draft-editor">
        <span className="k">Текст</span>
        <textarea
          aria-label="Текст драфта"
          value={body}
          onChange={(event) => setBody(event.target.value)}
        />
      </label>
      {hasUnsavedChanges ? <p className="muted">Есть несохраненные правки.</p> : null}
      <div className="inline-actions">
        <button className="btn btn-pri" type="button" onClick={() => onApproveDraft(body)}>
          <Icon name="check" size={16} />
          Утвердить текст
        </button>
        <button className="btn btn-sec" type="button" disabled={!hasUnsavedChanges} onClick={() => onDraftChange(body)}>
          Сохранить правки
        </button>
        <button className="btn btn-sec" type="button" onClick={onOpenBrief}>
          Вернуться к фабуле
        </button>
      </div>
    </>
  );
}
