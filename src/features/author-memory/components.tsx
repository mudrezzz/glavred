import type {
  AuthorAttachment,
  AuthorNote,
  AuthorPositionAssertion
} from '../../domain/editorialWorkspace';
import {
  assertionTypeLabel,
  attachmentTypeLabel,
  authorNoteTypeLabel,
  buildEvidenceCorrectionTarget,
  buildLinkPreview,
  deriveNoteTitle,
  formatBytes,
  formatDate,
  formatScore,
  isEvidenceNote
} from './helpers';
import type { CorrectionTarget, LinkPreview, MemoryInternalTab } from './types';

export function AuthorNoteCard({
  assertions,
  editBody,
  editAttachmentError,
  editAttachments,
  editSourceUrl,
  editTags,
  editTitle,
  editingId,
  expanded,
  note,
  onBeginEdit,
  onCancelEdit,
  onChangeEditBody,
  onChangeEditSourceUrl,
  onChangeEditTags,
  onChangeEditTitle,
  onDelete,
  onEditAttach,
  onEditRemoveAttachment,
  onSaveEdit,
  onToggleExpanded
}: {
  assertions: AuthorPositionAssertion[];
  editBody: string;
  editAttachmentError: string;
  editAttachments: AuthorAttachment[];
  editSourceUrl: string;
  editTags: string;
  editTitle: string;
  editingId: string | null;
  expanded: boolean;
  note: AuthorNote;
  onBeginEdit: (note: AuthorNote) => void;
  onCancelEdit: () => void;
  onChangeEditBody: (value: string) => void;
  onChangeEditSourceUrl: (value: string) => void;
  onChangeEditTags: (value: string) => void;
  onChangeEditTitle: (value: string) => void;
  onDelete: (note: AuthorNote) => void;
  onEditAttach: (file: File | undefined) => Promise<void>;
  onEditRemoveAttachment: () => void;
  onSaveEdit: (note: AuthorNote) => void;
  onToggleExpanded: () => void;
}) {
  const isEditing = editingId === note.id;
  const preview = buildLinkPreview(note.sourceUrl);
  const noteAttachments = note.attachments ?? [];
  const bodyIsLong = note.body.length > 420;
  const visibleBody = !bodyIsLong || expanded ? note.body : `${note.body.slice(0, 420)}...`;

  return (
    <article className="card memory-note">
      <div className="note-top">
        <span className="sig info">{authorNoteTypeLabel(note.type)}</span>
        <span className="sc">{formatDate(note.capturedAt)}</span>
        {isEvidenceNote(note.id, assertions) ? <span className="sc">evidence</span> : null}
        <div className="note-actions">
          <button className="link-button" type="button" onClick={() => onBeginEdit(note)}>
            Редактировать
          </button>
          <button className="link-button danger" type="button" onClick={() => onDelete(note)}>
            Удалить
          </button>
        </div>
      </div>
      {isEditing ? (
        <div className="note-edit">
          <label>
            Заголовок
            <input value={editTitle} onChange={(event) => onChangeEditTitle(event.target.value)} />
          </label>
          {note.type === 'linkReaction' ? (
            <label>
              Ссылка
              <input value={editSourceUrl} onChange={(event) => onChangeEditSourceUrl(event.target.value)} />
            </label>
          ) : null}
          <label>
            Текст
            <textarea value={editBody} onChange={(event) => onChangeEditBody(event.target.value)} />
          </label>
          <label>
            Теги
            <input value={editTags} onChange={(event) => onChangeEditTags(event.target.value)} />
          </label>
          {note.type !== 'manualCorrection' ? (
            <FileAttachmentPicker
              attachments={editAttachments}
              error={editAttachmentError}
              inputLabel="Файл заметки"
              onAttach={onEditAttach}
              onRemove={onEditRemoveAttachment}
            />
          ) : null}
          <div className="inline-actions">
            <button className="btn btn-pri btn-sm" type="button" onClick={() => onSaveEdit(note)} disabled={!editBody.trim()}>
              Сохранить
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={onCancelEdit}>
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <>
          <h3>{deriveNoteTitle(note)}</h3>
          {note.targetTitle ? <span className="target-chip">Корректировка: {note.targetTitle}</span> : null}
          <p>{visibleBody}</p>
          {bodyIsLong ? (
            <button className="link-button" type="button" onClick={onToggleExpanded}>
              {expanded ? 'Свернуть' : 'Показать полностью'}
            </button>
          ) : null}
          {preview.isValid ? <LinkPreviewCard preview={preview} /> : null}
          {noteAttachments.length > 0 ? <AttachmentList attachments={noteAttachments} /> : null}
          <div className="tag-row">
            {note.tags.map((tag) => (
              <span className="rub" key={tag}>
                {tag}
              </span>
            ))}
          </div>
        </>
      )}
    </article>
  );
}

export function AssertionCard({
  assertion,
  onCorrect
}: {
  assertion: AuthorPositionAssertion;
  onCorrect: (target: CorrectionTarget) => void;
}) {
  return (
    <article className="assertion">
      <div className="assertion-head">
        <span className="rub">{assertionTypeLabel(assertion.type)}</span>
        <span className="sc">confidence {formatScore(assertion.confidence)}</span>
      </div>
      <h3>{assertion.title}</h3>
      <p>{assertion.statement}</p>
      <button
        className="btn btn-sec btn-sm"
        type="button"
        onClick={() => onCorrect({ type: 'assertion', id: assertion.id, title: assertion.title })}
      >
        Корректировать
      </button>
      <details>
        <summary>Evidence</summary>
        <div className="evidence-list">
          {assertion.evidence.map((item) => (
            <blockquote key={`${assertion.id}-${item.noteId}-${item.quote}`}>
              <p>{item.quote}</p>
              <cite>{item.reason}</cite>
              <button
                className="link-button"
                type="button"
                onClick={() => onCorrect(buildEvidenceCorrectionTarget(assertion, item))}
              >
                Корректировать evidence
              </button>
            </blockquote>
          ))}
        </div>
      </details>
    </article>
  );
}

export function LinkPreviewCard({ preview }: { preview: LinkPreview }) {
  return (
    <a className="link-preview" href={preview.normalizedUrl} target="_blank" rel="noreferrer">
      <span>{preview.domain}</span>
      <b>{preview.title}</b>
      <small>{preview.normalizedUrl}</small>
    </a>
  );
}

export function FileAttachmentPicker({
  attachments,
  error,
  inputLabel,
  onAttach,
  onRemove
}: {
  attachments: AuthorAttachment[];
  error: string;
  inputLabel: string;
  onAttach: (file: File | undefined) => Promise<void>;
  onRemove: () => void;
}) {
  return (
    <div className="file-picker">
      <label>
        {inputLabel}
        <input
          accept=".txt,.md,.pdf,.doc,.docx,image/*"
          aria-label={inputLabel}
          type="file"
          onChange={(event) => {
            void onAttach(event.target.files?.[0]);
            event.target.value = '';
          }}
        />
      </label>
      <p>До 1 MB. Файл хранится локально как материал к заметке и пока не анализируется.</p>
      {error ? <span className="form-error">{error}</span> : null}
      {attachments.length > 0 ? <AttachmentList attachments={attachments} onRemove={onRemove} /> : null}
    </div>
  );
}

export function AttachmentList({
  attachments,
  onRemove
}: {
  attachments: AuthorAttachment[];
  onRemove?: () => void;
}) {
  return (
    <div className="attachment-list">
      {attachments.map((attachment) => (
        <div className="attachment-card" key={attachment.id}>
          {attachment.mimeType.startsWith('image/') ? (
            <img alt="" src={attachment.dataUrl} />
          ) : (
            <span className="attachment-icon">{attachmentTypeLabel(attachment)}</span>
          )}
          <div>
            <b>{attachment.fileName}</b>
            <small>
              {attachment.mimeType || 'file'} · {formatBytes(attachment.sizeBytes)} · локально
            </small>
          </div>
          {onRemove ? (
            <button className="link-button danger" type="button" onClick={onRemove}>
              Удалить файл
            </button>
          ) : null}
        </div>
      ))}
    </div>
  );
}

export function SummaryItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="summary-item">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

export function MemoryTabNav({
  active,
  onChange
}: {
  active: MemoryInternalTab;
  onChange: (tab: MemoryInternalTab) => void;
}) {
  const tabs: Array<[MemoryInternalTab, string]> = [
    ['feed', 'Лента'],
    ['sources', 'Источники'],
    ['queue', 'Очередь разбора'],
    ['archive', 'Архив']
  ];

  return (
    <div className="tabs memory-tabs" role="tablist" aria-label="Память автора">
      {tabs.map(([id, label]) => (
        <button
          className={`tab${active === id ? ' active' : ''}`}
          key={id}
          role="tab"
          type="button"
          aria-selected={active === id}
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

export function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}
