import { AssertionCard, SummaryItem } from './components';
import type { ImportReviewController } from './useImportReviewController';
import type { MemoryFeedController } from './useMemoryFeedController';

export function MemorySidePanel({
  feed,
  imports
}: {
  feed: MemoryFeedController;
  imports: ImportReviewController;
}) {
  return (
    <aside className="memory-side">
      <section className="panel import-summary">
        <h4>Импорт и архив</h4>
        <div className="summary-grid">
          <SummaryItem label="Источники" value={imports.importSummary.sources} />
          <SummaryItem label="Кандидаты" value={imports.importSummary.candidates} />
          <SummaryItem label="Review" value={imports.importSummary.needsReview} />
          <SummaryItem label="Архив" value={imports.importSummary.archived} />
          <SummaryItem label="Bulk" value={imports.importSummary.bulkAccepted} />
          <SummaryItem label="Undo" value={imports.importSummary.undoAvailable} />
        </div>
        <p className="panel-note">Архивные и неразобранные материалы не меняют выводы о позиции автора.</p>
        {imports.bulkImportActions.some((action) => action.canUndo) ? (
          <button className="btn btn-sec btn-sm" type="button" onClick={imports.undoLatestBulkAction}>
            Отменить последнее групповое действие
          </button>
        ) : null}
      </section>
      <section className="panel memory-summary">
        <h4>Сводка памяти</h4>
        <div className="summary-grid">
          <SummaryItem label="Всего" value={feed.summary.total} />
          <SummaryItem label="Мысли" value={feed.summary.thoughts} />
          <SummaryItem label="Ссылки" value={feed.summary.links} />
          <SummaryItem label="Правки" value={feed.summary.corrections} />
          <SummaryItem label="Месяц" value={feed.summary.thisMonth} />
          <SummaryItem label="Год" value={feed.summary.thisYear} />
        </div>
      </section>
      <section className="panel">
        <h4>Как система поняла автора</h4>
        <div className="assertions">
          {feed.assertions.map((assertion) => (
            <AssertionCard assertion={assertion} key={assertion.id} onCorrect={feed.beginCorrection} />
          ))}
        </div>
      </section>
    </aside>
  );
}
