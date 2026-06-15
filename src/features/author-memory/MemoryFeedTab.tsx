import type { AuthorNoteType } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import {
  AuthorNoteCard,
  EmptyState,
  FileAttachmentPicker,
  LinkPreviewCard
} from './components';
import { correctionTargetKey } from './helpers';
import type { MemoryFeedController } from './useMemoryFeedController';

export function MemoryFeedTab({ feed }: { feed: MemoryFeedController }) {
  return (
    <>
      <div className="card memory-composer">
        <div className="form-row">
          <label>
            Тип записи
            <select value={feed.type} onChange={(event) => feed.changeNoteType(event.target.value as AuthorNoteType)}>
              <option value="thought">Мысль</option>
              <option value="linkReaction">Реакция на ссылку</option>
              <option value="manualCorrection">Ручная корректировка</option>
            </select>
          </label>
          {feed.isManualCorrection ? (
            <label>
              Что корректируем
              <select
                value={feed.correctionTarget ? correctionTargetKey(feed.correctionTarget) : ''}
                onChange={(event) =>
                  feed.setCorrectionTarget(
                    feed.correctionTargets.find((target) => correctionTargetKey(target) === event.target.value) ?? null
                  )
                }
              >
                <option value="">Выберите вывод или evidence</option>
                {feed.correctionTargets.map((target) => (
                  <option key={correctionTargetKey(target)} value={correctionTargetKey(target)}>
                    {target.type === 'assertion' ? 'Вывод' : 'Evidence'} · {target.title}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          {feed.type === 'linkReaction' ? (
            <label>
              Ссылка
              <input
                value={feed.sourceUrl}
                onChange={(event) => feed.setSourceUrl(event.target.value)}
                placeholder="https://..."
              />
            </label>
          ) : null}
        </div>
        {!feed.isManualCorrection && (
          <div className="optional-tools">
            <button
              className="btn btn-sec btn-sm"
              type="button"
              onClick={() => {
                feed.setShowTitle((current) => !current);
                if (feed.showTitle) feed.setTitle('');
              }}
            >
              <Icon name={feed.showTitle ? 'minus' : 'plus'} size={14} />
              Заголовок
            </button>
            <button
              className="btn btn-sec btn-sm"
              type="button"
              onClick={() => {
                feed.setShowFile((current) => !current);
                if (feed.showFile) {
                  feed.setAttachments([]);
                  feed.setAttachmentError('');
                }
              }}
            >
              <Icon name={feed.showFile ? 'minus' : 'plus'} size={14} />
              Файл
            </button>
          </div>
        )}
        {!feed.isManualCorrection && feed.showTitle ? (
          <label>
            Заголовок
            <input value={feed.title} onChange={(event) => feed.setTitle(event.target.value)} />
          </label>
        ) : null}
        {!feed.isManualCorrection && feed.showFile ? (
          <FileAttachmentPicker
            attachments={feed.attachments}
            error={feed.attachmentError}
            inputLabel="Файл"
            onAttach={feed.attachComposerFile}
            onRemove={() => {
              feed.setAttachments([]);
              feed.setAttachmentError('');
            }}
          />
        ) : null}
        {feed.type === 'linkReaction' && feed.linkPreview.isValid ? <LinkPreviewCard preview={feed.linkPreview} /> : null}
        <label>
          {feed.isManualCorrection ? 'Корректировка' : 'Заметка автора'}
          <textarea value={feed.body} onChange={(event) => feed.setBody(event.target.value)} />
        </label>
        {!feed.isManualCorrection ? (
          <label>
            Теги
            <input
              value={feed.tags}
              onChange={(event) => feed.setTags(event.target.value)}
              placeholder="workflow, evals, adoption"
            />
          </label>
        ) : null}
        <div className="composer-actions">
          <button
            className="btn btn-sec"
            type="button"
            onClick={feed.startVoiceInput}
            disabled={!feed.canUseVoice}
            title={feed.canUseVoice ? 'Добавить голосом' : 'Голосовой ввод недоступен в этом браузере'}
          >
            <Icon name="mic" size={16} />
            Голосом
          </button>
          <button
            className="btn btn-pri"
            type="button"
            onClick={feed.submitNote}
            disabled={
              !feed.body.trim() ||
              (feed.type === 'linkReaction' && !feed.linkPreview.isValid) ||
              (feed.isManualCorrection && !feed.correctionTarget)
            }
          >
            <Icon name="plus" size={16} />
            Добавить в память
          </button>
        </div>
        {feed.pendingConflict ? (
          <div className="conflict-box" role="status">
            <b>Корректировка спорит с текущим evidence</b>
            <p>
              Вы уточняете: {feed.pendingConflict.targetTitle}. Выберите, как зафиксировать позицию в памяти.
            </p>
            <div className="inline-actions">
              <button className="btn btn-sec btn-sm" type="button" onClick={() => feed.resolveCorrectionConflict('merge')}>
                Смержить
              </button>
              <button className="btn btn-sec btn-sm" type="button" onClick={() => feed.resolveCorrectionConflict('replace')}>
                Заменить вывод
              </button>
              <button className="btn btn-sec btn-sm" type="button" onClick={() => feed.resolveCorrectionConflict('rollback')}>
                Откатить корректировку
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <div className="card memory-toolbar">
        <div className="memory-search">
          <Icon name="search" size={16} />
          <input
            aria-label="Поиск по памяти"
            value={feed.query}
            onChange={(event) => {
              feed.setQuery(event.target.value);
              feed.setVisibleCount(5);
            }}
            placeholder="Искать по заметкам, тегам, ссылкам..."
          />
        </div>
        <select
          aria-label="Фильтр типа заметки"
          value={feed.filter}
          onChange={(event) => {
            feed.setFilter(event.target.value as typeof feed.filter);
            feed.setVisibleCount(5);
          }}
        >
          <option value="all">Все</option>
          <option value="thought">Мысли</option>
          <option value="linkReaction">Ссылки</option>
          <option value="manualCorrection">Правки</option>
        </select>
      </div>

      <div className="memory-feed">
        {feed.visibleNotes.map((note) => (
          <AuthorNoteCard
            assertions={feed.assertions}
            editingId={feed.editingId}
            editBody={feed.editBody}
            editAttachmentError={feed.editAttachmentError}
            editAttachments={feed.editAttachments}
            editSourceUrl={feed.editSourceUrl}
            editTags={feed.editTags}
            editTitle={feed.editTitle}
            expanded={feed.expandedNoteIds.includes(note.id)}
            key={note.id}
            note={note}
            onBeginEdit={feed.beginEdit}
            onCancelEdit={() => feed.setEditingId(null)}
            onChangeEditBody={feed.setEditBody}
            onChangeEditSourceUrl={feed.setEditSourceUrl}
            onChangeEditTags={feed.setEditTags}
            onChangeEditTitle={feed.setEditTitle}
            onDelete={feed.requestDelete}
            onEditAttach={feed.attachEditFile}
            onEditRemoveAttachment={() => {
              feed.setEditAttachments([]);
              feed.setEditAttachmentError('');
            }}
            onSaveEdit={feed.saveEdit}
            onToggleExpanded={() => feed.toggleExpanded(note.id)}
          />
        ))}
        {feed.filteredNotes.length === 0 ? <EmptyState text="По этому запросу в памяти ничего не найдено." /> : null}
        {feed.visibleCount < feed.filteredNotes.length ? (
          <button className="btn btn-sec load-more" type="button" onClick={() => feed.setVisibleCount((count) => count + 5)}>
            Показать еще
          </button>
        ) : null}
      </div>
    </>
  );
}
