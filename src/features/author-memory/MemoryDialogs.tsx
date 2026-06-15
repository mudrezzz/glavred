import { BulkActionDialog } from './ImportViews';
import type { ImportReviewController } from './useImportReviewController';
import type { MemoryFeedController } from './useMemoryFeedController';

export function MemoryDialogs({
  feed,
  imports
}: {
  feed: MemoryFeedController;
  imports: ImportReviewController;
}) {
  return (
    <>
      {imports.pendingBulkAction ? (
        <BulkActionDialog
          action={imports.pendingBulkAction}
          candidates={imports.importCandidates.filter((candidate) =>
            imports.pendingBulkAction?.candidateIds.includes(candidate.id)
          )}
          filters={imports.candidateFilters}
          onCancel={() => imports.setPendingBulkAction(null)}
          onConfirm={() => {
            if (imports.pendingBulkAction) imports.performPendingBulkAction(imports.pendingBulkAction);
          }}
        />
      ) : null}
      {feed.pendingDeleteNote ? (
        <div className="confirm-popover" role="dialog" aria-label="Подтверждение удаления">
          <div className="card">
            <h3>Удалить заметку из evidence?</h3>
            <p>
              Заметка "{feed.deriveNoteTitle(feed.pendingDeleteNote)}" участвует в выводах о позиции автора. После удаления
              assertions будут пересчитаны.
            </p>
            <div className="inline-actions">
              <button className="btn btn-sec btn-sm" type="button" onClick={() => feed.setPendingDeleteNote(null)}>
                Отмена
              </button>
              <button className="btn btn-pri btn-sm" type="button" onClick={() => feed.deleteNote(feed.pendingDeleteNote!.id)}>
                Удалить
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
