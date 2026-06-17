import { useState } from 'react';
import type { FinalText, PostBriefEditPatch, PostDraft, WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EditorialBriefStage } from './EditorialBriefStage';

export function EditorialWorkbench({
  workspace,
  onApproveBrief,
  onApproveFinal,
  onDraftChange,
  onEditBrief,
  onGoPlan
}: {
  workspace: WorkspaceState;
  onApproveBrief: () => void;
  onApproveFinal: () => void;
  onDraftChange: (body: string) => void;
  onEditBrief: (patch: PostBriefEditPatch) => void;
  onGoPlan: () => void;
}) {
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;
  const [tab, setTab] = useState<'brief' | 'draft' | 'final'>(() => {
    if (!brief || brief.approvalStatus !== 'approved') return 'brief';
    return finalText ? 'final' : 'draft';
  });

  if (!workspace.selectedEditorialWorkItemId) {
    return (
      <section className="card edit-empty editorial-workbench-empty">
        <div className="placeholder-icon">
          <Icon name="brief" size={28} />
        </div>
        <h2>Выберите пост из очереди</h2>
        <p>Редактура работает с конкретным утвержденным слотом: сначала откройте строку в очереди, затем готовьте фабулу, драфт и финал.</p>
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
        <button className={`tab${tab === 'final' ? ' active' : ''}`} type="button" role="tab" aria-selected={tab === 'final'} onClick={() => setTab('final')}>
          Финал
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
          {tab === 'draft' && <DraftEditor draft={draft} onDraftChange={onDraftChange} />}
          {tab === 'final' && <FinalTextView finalText={finalText} draft={draft} onApproveFinal={onApproveFinal} />}
        </section>
      )}
    </section>
  );
}

function DraftEditor({ draft, onDraftChange }: { draft: PostDraft; onDraftChange: (body: string) => void }) {
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
      <label className="draft-editor">
        <span className="k">Текст</span>
        <textarea
          aria-label="Текст драфта"
          value={draft.body}
          onChange={(event) => onDraftChange(event.target.value)}
        />
      </label>
    </>
  );
}

function FinalTextView({
  finalText,
  draft,
  onApproveFinal
}: {
  finalText: FinalText | null;
  draft: PostDraft;
  onApproveFinal: () => void;
}) {
  if (!finalText) {
    return (
      <div className="final-empty">
        <h2>Финал еще не утвержден</h2>
        <p>Проверьте драфт, замечания редакторов и нажмите «Утвердить текст».</p>
        <div className="inline-actions">
          <button className="btn btn-pri" type="button" onClick={onApproveFinal}>
            <Icon name="check" size={16} />
            Утвердить текст
          </button>
        </div>
      </div>
    );
  }

  return (
    <article className="final-doc">
      <div className="final-status">
        <span className="pill ok">
          <i />
          Финальный текст утвержден
        </span>
        <span>на основе версии {draft.version}</span>
      </div>
      <h2>{finalText.title}</h2>
      <pre>{finalText.body}</pre>
    </article>
  );
}
