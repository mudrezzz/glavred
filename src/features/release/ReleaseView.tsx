import type { WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { HitlGate } from '../../shared/ui/WorkflowPrimitives';
import { releaseStatusLabel, targetLabel } from '../../shared/format/production';

export function ReleaseView({
  workspace,
  onGoEdit,
  onCreatePackage,
  onToggleChecklist,
  onMarkReady,
  onCopy,
  onDownload
}: {
  workspace: WorkspaceState;
  onGoEdit: () => void;
  onCreatePackage: () => void;
  onToggleChecklist: (itemId: string) => void;
  onMarkReady: () => void;
  onCopy: () => void;
  onDownload: () => void;
}) {
  const finalText = workspace.finalText;
  const releasePackage = workspace.releasePackage;
  const allChecklistDone = releasePackage?.checklist.every((item) => item.done) ?? false;

  if (!finalText || finalText.approvalStatus !== 'approved') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="edit" size={28} />
          </div>
          <h2>Сначала утвердите финальный текст</h2>
          <p>Выпуск открывается после Gate 3: утвержденного текста в разделе «Редактура».</p>
          <button className="btn btn-pri" type="button" onClick={onGoEdit}>
            <Icon name="edit" size={16} />
            Перейти в редактуру
          </button>
        </section>
      </div>
    );
  }

  if (!releasePackage) {
    return (
      <div className="page wide fade-up">
        <section className="card draft-start">
          <span className="rub">Manual export</span>
          <h2>{finalText.title}</h2>
          <p>Финальный текст утвержден. Подготовьте пакет выпуска для Telegram и LinkedIn без автопостинга.</p>
          <button className="btn btn-pri" type="button" onClick={onCreatePackage}>
            <Icon name="release" size={16} />
            Подготовить выпуск
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="Release · Manual export"
        title={`Статус: ${releaseStatusLabel(releasePackage.status)}`}
        subtitle="Пакет выпуска не публикует пост автоматически. Он готовит текст, markdown и чеклист для ручной публикации."
        action="Готово к выпуску"
        disabled={!allChecklistDone}
        onAction={onMarkReady}
      />
      <div className="release-grid">
        <section className="release-doc">
          <div className="doc-head">
            <div>
              <span className="rub">Финальный текст</span>
              <h2>{finalText.title}</h2>
            </div>
            <span className={`pill ${releasePackage.status === 'exported' ? 'ok' : 'pin'}`}>
              <i />
              {releaseStatusLabel(releasePackage.status)}
            </span>
          </div>
          <pre className="release-text">{finalText.body}</pre>
          <div className="markdown-preview">
            <div className="doc-head">
              <h3>Markdown export</h3>
              <div className="actions">
                <button className="btn btn-sec btn-sm" type="button" onClick={onCopy}>
                  <Icon name="check" size={14} />
                  Скопировать текст
                </button>
                <button className="btn btn-pri btn-sm" type="button" onClick={onDownload}>
                  <Icon name="release" size={14} />
                  Скачать Markdown
                </button>
              </div>
            </div>
            <pre>{releasePackage.markdown}</pre>
          </div>
        </section>
        <aside className="edit-side">
          <section className="panel">
            <h4>Площадки</h4>
            <div className="target-list">
              {releasePackage.targets.map((target) => (
                <span className="sig info" key={target}>
                  {targetLabel(target)}
                </span>
              ))}
            </div>
          </section>
          <section className="panel">
            <h4>Release checklist</h4>
            <div className="release-checklist">
              {releasePackage.checklist.map((item) => (
                <label className="check-row" key={item.id}>
                  <input
                    type="checkbox"
                    checked={item.done}
                    onChange={() => onToggleChecklist(item.id)}
                  />
                  <span>{item.label}</span>
                </label>
              ))}
            </div>
          </section>
          <section className="panel">
            <h4>Метаданные</h4>
            <dl className="meta-list">
              <dt>Обновлено</dt>
              <dd>{releasePackage.updatedAt}</dd>
              <dt>Статус</dt>
              <dd>{releaseStatusLabel(releasePackage.status)}</dd>
              <dt>Тип выпуска</dt>
              <dd>ручной export</dd>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}
