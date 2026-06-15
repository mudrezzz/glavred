import { ignoreCandidateForEvidence, rejectCandidate, type AuthorNote, type WorkspaceState } from '../../domain/editorialWorkspace';
import { ArchiveView, ExternalSourcesView, ImportQueueView } from './ImportViews';
import { MemoryDialogs } from './MemoryDialogs';
import { MemoryFeedTab } from './MemoryFeedTab';
import { MemorySidePanel } from './MemorySidePanel';
import { MemoryTabNav } from './components';
import type { MemoryInternalTab } from './types';
import { useImportReviewController } from './useImportReviewController';
import { useMemoryFeedController } from './useMemoryFeedController';

export function AuthorMemoryView({
  activeTab,
  workspace,
  onChangeTab,
  onPatchWorkspace,
  onChangeNotes
}: {
  activeTab: MemoryInternalTab;
  workspace: WorkspaceState;
  onChangeTab: (tab: MemoryInternalTab) => void;
  onPatchWorkspace: (patch: Partial<WorkspaceState>, message?: string) => void;
  onChangeNotes: (notes: AuthorNote[], message?: string) => void;
}) {
  const feed = useMemoryFeedController({
    assertions: workspace.authorPositionAssertions,
    notes: workspace.authorNotes,
    onChangeNotes
  });
  const imports = useImportReviewController({ workspace, onChangeTab, onPatchWorkspace });

  return (
    <div className="page wide fade-up">
      <div className="sec-head">
        <div>
          <h2>Авторская память</h2>
          <p className="section-help">
            Фиксируйте мысли, реакции на ссылки и ручные правки без обязательной структуры. Система связывает
            записи с выводами о вашей позиции, а вы можете уточнять эти выводы прямо из evidence.
          </p>
        </div>
      </div>
      <MemoryTabNav active={activeTab} onChange={onChangeTab} />
      <div className="memory-grid">
        <section className="memory-main">
          {activeTab === 'feed' ? <MemoryFeedTab feed={feed} /> : null}
          {activeTab === 'sources' ? (
            <ExternalSourcesView
              candidates={imports.importCandidates}
              sources={imports.externalSources}
              onOpenQueue={imports.openQueueForSource}
              onPatchSource={imports.patchSource}
            />
          ) : null}
          {activeTab === 'queue' ? (
            <ImportQueueView
              candidates={imports.importCandidates}
              filteredCandidates={imports.filteredCandidates}
              filters={imports.candidateFilters}
              groups={imports.importGroups}
              groupMode={imports.groupMode}
              selectedCandidateIds={imports.selectedCandidateIds}
              sources={imports.externalSources}
              viewMode={imports.importViewMode}
              onAcceptToArchive={imports.acceptToArchive}
              onAcceptToMemory={imports.acceptToMemory}
              onChangeFilters={(nextFilters) => {
                imports.setCandidateFilters(nextFilters);
                imports.clearCandidateSelection();
              }}
              onChangeGroupMode={imports.setGroupMode}
              onChangeViewMode={imports.setImportViewMode}
              onIgnoreEvidence={(candidate) =>
                imports.replaceImportCandidate(ignoreCandidateForEvidence(candidate), 'Кандидат помечен как не evidence')
              }
              onOpenBulk={imports.setPendingBulkAction}
              onReject={(candidate) => imports.replaceImportCandidate(rejectCandidate(candidate), 'Кандидат отклонен')}
              onClearSelection={imports.clearCandidateSelection}
              onSelect={imports.toggleCandidateSelection}
              onSelectAllFiltered={() => imports.selectCandidates(imports.filteredCandidates.map((candidate) => candidate.id))}
              onSelectPage={() => imports.selectCandidates(imports.filteredCandidates.slice(0, 10).map((candidate) => candidate.id))}
              onUnselectAllFiltered={() =>
                imports.unselectCandidates(imports.filteredCandidates.map((candidate) => candidate.id))
              }
              onUnselectPage={() =>
                imports.unselectCandidates(imports.filteredCandidates.slice(0, 10).map((candidate) => candidate.id))
              }
            />
          ) : null}
          {activeTab === 'archive' ? (
            <ArchiveView
              records={imports.archiveRecords}
              sources={imports.externalSources}
              onAcceptToMemory={imports.acceptArchiveRecordToMemory}
              onDelete={imports.deleteArchiveRecord}
              onIgnoreEvidence={imports.ignoreArchiveRecord}
              onRestoreToQueue={imports.restoreArchiveRecordToQueue}
            />
          ) : null}
        </section>

        <MemorySidePanel feed={feed} imports={imports} />
      </div>
      <MemoryDialogs feed={feed} imports={imports} />
    </div>
  );
}
