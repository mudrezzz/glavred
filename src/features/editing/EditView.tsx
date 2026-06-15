import { useState } from 'react';
import { approveFinalText, reviseDraft, type EditorialCheck, type FinalText, type PostBrief, type PostDraft, type WorkspaceState } from '../../domain/editorialWorkspace';
import { createEditorNotes, createPostDraft, runEditorialChecks } from '../../application/editorialServices';
import { Icon } from '../../shared/ui/Icon';
import { HitlGate } from '../../shared/ui/WorkflowPrimitives';
import { checkStatusLabel, formatDate, formatDateTime } from '../../shared/format/production';

export function EditView({
  workspace,
  onGoBrief,
  onCreateDraft,
  onDraftChange,
  onApproveFinal
}: {
  workspace: WorkspaceState;
  onGoBrief: () => void;
  onCreateDraft: () => void;
  onDraftChange: (body: string) => void;
  onApproveFinal: () => void;
}) {
  const [tab, setTab] = useState<'brief' | 'draft' | 'final'>(() => (workspace.finalText ? 'final' : 'draft'));
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;

  if (!brief || brief.approvalStatus !== 'approved') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="brief" size={28} />
          </div>
          <h2>Сначала утвердите фабулу</h2>
          <p>Редактура открывается только после Gate 2: утвержденной фабулы поста.</p>
          <button className="btn btn-pri" type="button" onClick={onGoBrief}>
            <Icon name="brief" size={16} />
            Перейти к фабуле
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 3 — Финальный текст"
        title="Проверьте драфт и утвердите финальную версию"
        subtitle="Warnings не блокируют утверждение: человек остается главным редактором и видит риски перед решением."
        action="Утвердить текст"
        disabled={!draft}
        onAction={onApproveFinal}
      />
      <div className="tabs" role="tablist" aria-label="Редакторские вкладки">
        <button className={`tab${tab === 'brief' ? ' active' : ''}`} type="button" onClick={() => setTab('brief')}>
          Фабула
        </button>
        <button className={`tab${tab === 'draft' ? ' active' : ''}`} type="button" onClick={() => setTab('draft')}>
          Драфт
        </button>
        <button className={`tab${tab === 'final' ? ' active' : ''}`} type="button" onClick={() => setTab('final')}>
          Финал
        </button>
      </div>

      {!draft ? (
        <section className="card draft-start">
          <span className="rub">{brief.rubric}</span>
          <h2>{brief.title}</h2>
          <p>{brief.thesis}</p>
          <button className="btn btn-pri" type="button" onClick={onCreateDraft}>
            <Icon name="edit" size={16} />
            Написать драфт
          </button>
        </section>
      ) : (
        <div className="edit-grid">
          <section className="doc">
            {tab === 'brief' && <BriefSnapshot brief={brief} />}
            {tab === 'draft' && (
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
            )}
            {tab === 'final' && <FinalTextView finalText={finalText} draft={draft} />}
          </section>
          <aside className="edit-side">
            <section className="panel">
              <h4>Проверки</h4>
              <div className="checks">
                {workspace.editorialChecks.map((check) => (
                  <CheckCard key={check.id} check={check} />
                ))}
              </div>
            </section>
            <section className="panel">
              <h4>Заметки редакторов</h4>
              <div className="notes">
                {workspace.editorNotes.map((note) => (
                  <article className="note" key={note.id}>
                    <div className="note-head">
                      <span className="av">{note.agent.slice(0, 2)}</span>
                      <div>
                        <b>{note.agent}</b>
                        <span>{note.tone} · {note.target}</span>
                      </div>
                    </div>
                    <p>{note.text}</p>
                  </article>
                ))}
              </div>
            </section>
          </aside>
        </div>
      )}
    </div>
  );
}

function BriefSnapshot({ brief }: { brief: PostBrief }) {
  return (
    <div className="brief-snapshot">
      <span className="rub">{brief.rubric}</span>
      <h2>{brief.title}</h2>
      <p className="lead">{brief.thesis}</p>
      <div className="snapshot-grid">
        <InfoBlock title="Конфликт" items={[brief.conflict]} />
        <InfoBlock title="Позиция" items={[brief.authorPosition]} />
        <InfoBlock title="Доказательства" items={brief.evidence} />
        <InfoBlock title="Риски" items={brief.risks} />
      </div>
    </div>
  );
}

function FinalTextView({ finalText, draft }: { finalText: FinalText | null; draft: PostDraft }) {
  if (!finalText) {
    return (
      <div className="final-empty">
        <h2>Финал еще не утвержден</h2>
        <p>Проверьте драфт, замечания редакторов и нажмите «Утвердить текст».</p>
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

function InfoBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="info-block">
      <h4>{title}</h4>
      <ul className="bullets">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function CheckCard({ check }: { check: EditorialCheck }) {
  return (
    <article className={`check check-${check.status}`}>
      <div className="check-head">
        <span className="ci">{check.title.slice(0, 1)}</span>
        <div>
          <b>{check.title}</b>
          <span>{checkStatusLabel(check.status)}</span>
        </div>
      </div>
      <p>{check.summary}</p>
      <ul className="bullets">
        {check.findings.map((finding) => (
          <li key={finding}>{finding}</li>
        ))}
      </ul>
    </article>
  );
}
