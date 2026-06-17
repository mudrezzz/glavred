import { AppShell } from './app/AppShell';
import { ContextChatOverlay } from './app/ContextChatOverlay';
import { useWorkspaceController } from './app/useWorkspaceController';
import { AuthorMemoryView } from './features/author-memory/AuthorMemoryView';
import { AnalyticsView } from './features/analytics/AnalyticsView';
import { BriefView } from './features/briefing/BriefView';
import { EditorialModelView } from './features/editorial-model/EditorialModelView';
import { EditView } from './features/editing/EditView';
import { PlanView } from './features/plan/PlanView';
import { ReleaseView } from './features/release/ReleaseView';
import { SignalsView } from './features/signals/SignalsView';

export function App() {
  const controller = useWorkspaceController();
  const {
    active,
    contextChatIntent,
    contextChatMessages,
    contextChatOpen,
    contextChatScope,
    contextChatTab,
    editorialModelTab,
    memoryTab,
    toast,
    visibleContextChatSuggestions,
    workspace
  } = controller;

  return (
    <AppShell
      active={active}
      chatOpen={contextChatOpen}
      suggestionCount={visibleContextChatSuggestions.length}
      toast={toast}
      workspace={workspace}
      onNav={controller.go}
      onOpenChat={() => controller.openContextChat('chat')}
      onReset={controller.resetDemo}
      overlay={
        <ContextChatOverlay
          messages={contextChatMessages}
          open={contextChatOpen}
          scope={contextChatScope}
          activeTab={contextChatTab}
          suggestions={visibleContextChatSuggestions}
          onAcceptSuggestion={controller.acceptContextChatSuggestion}
          onClose={() => controller.setContextChatOpen(false)}
          onDismissSuggestion={controller.dismissContextChatSuggestion}
          onSendMessage={controller.sendContextChatMessage}
          onSwitchTab={controller.setContextChatTab}
        />
      }
    >
      {active === 'memory' && (
        <AuthorMemoryView
          activeTab={memoryTab}
          workspace={workspace}
          onChangeTab={controller.setMemoryTab}
          onPatchWorkspace={controller.patchWorkspace}
          onChangeNotes={controller.changeAuthorNotes}
        />
      )}
      {active === 'editorialModel' && (
        <EditorialModelView
          activeTab={editorialModelTab}
          chatIntent={contextChatIntent}
          workspace={workspace}
          model={workspace.editorialModel}
          projectProfile={workspace.projectProfile}
          editorialRules={workspace.editorialRules}
          topics={workspace.topics}
          fabulas={workspace.fabulas}
          matrix={workspace.topicFabulaMatrix}
          onModelChange={(editorialModel) => controller.patchEditorialSetup({ editorialModel })}
          onProjectProfileChange={(projectProfile) => controller.patchEditorialSetup({ projectProfile })}
          onEditorialRulesChange={(editorialRules) => controller.patchEditorialSetup({ editorialRules })}
          onTopicsChange={(topics) => controller.patchEditorialSetup({ topics })}
          onFabulasChange={(fabulas) => controller.patchEditorialSetup({ fabulas })}
          onMatrixChange={(topicFabulaMatrix) => controller.patchEditorialSetup({ topicFabulaMatrix })}
          onTopicsAndMatrixChange={(topics, topicFabulaMatrix) =>
            controller.patchEditorialSetup({ topics, topicFabulaMatrix })
          }
          onFabulasAndMatrixChange={(fabulas, topicFabulaMatrix) =>
            controller.patchEditorialSetup({ fabulas, topicFabulaMatrix })
          }
          onChangeTab={controller.setEditorialModelTab}
          onChatIntentConsumed={() => controller.setContextChatIntent(null)}
          onRunValidation={controller.runEditorialValidation}
        />
      )}
      {active === 'signals' && (
        <SignalsView
          workspace={workspace}
          onSaveRadar={controller.saveRadar}
          onDeleteRadar={controller.removeRadar}
          onToggleRadarStatus={controller.switchRadarStatus}
          onApproveSignal={controller.approveSourceSignal}
          onRejectSignal={controller.rejectSourceSignal}
          onArchiveSignal={controller.archiveSourceSignal}
          onCorrectSignal={controller.correctSourceSignal}
          onApprovePostCandidate={controller.approveCandidate}
          onEditPostCandidate={controller.editCandidate}
          onRejectPostCandidate={controller.rejectCandidate}
          onCreateInsight={controller.createInsightFromCurrentSignal}
          onPlan={controller.addInsightToPlan}
        />
      )}
      {active === 'plan' && (
        <PlanView
          workspace={workspace}
          onGenerate={controller.generateBroadcastPlan}
          onItemChange={controller.updatePlanItemAndWarnings}
          onApprove={controller.approvePlanSlot}
          onBrief={controller.prepareBrief}
          onSettingsSave={controller.saveContentPlanSettings}
        />
      )}
      {active === 'brief' && (
        <BriefView
          workspace={workspace}
          onBriefChange={(postBrief) => controller.patchWorkspace({ postBrief })}
          onBackToPlan={() => controller.go('plan')}
          onApprove={controller.approveCurrentBrief}
        />
      )}
      {active === 'edit' && (
        <EditView
          workspace={workspace}
          onApproveBrief={controller.approveCurrentBrief}
          onGoPlan={() => controller.go('plan')}
          onSelectWorkItem={controller.selectEditorialWorkItem}
          onCreateDraft={controller.createDraftFromBrief}
          onDraftChange={controller.updateDraftBody}
          onApproveFinal={controller.approveCurrentFinalText}
        />
      )}
      {active === 'release' && (
        <ReleaseView
          workspace={workspace}
          onGoEdit={() => controller.go('edit')}
          onCreatePackage={controller.createReleaseFromFinalText}
          onToggleChecklist={controller.toggleReleaseChecklist}
          onMarkReady={controller.markCurrentReleaseReady}
          onCopy={controller.copyCurrentFinalText}
          onDownload={controller.downloadCurrentRelease}
        />
      )}
      {active === 'analytics' && (
        <AnalyticsView
          workspace={workspace}
          onGoRelease={() => controller.go('release')}
          onCreateNote={controller.createLearningNote}
          onChangeNote={controller.updateCurrentLearningNote}
          onCapture={controller.captureLearningNote}
        />
      )}
    </AppShell>
  );
}
