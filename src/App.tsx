import { useMemo, useState } from 'react';
import {
  createBroadcastPlan,
  createContentPlanItem,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
  runEditorialChecks
} from './application/editorialServices';
import {
  approveFinalText,
  approveContentPlanSlot,
  approvePlanItem,
  approvePostBrief,
  applyPlanWarnings,
  approveSignal,
  addRadar,
  archiveSignal,
  createEditorialValidationRun,
  correctSignal,
  deleteRadar,
  detectBroadcastPlanConflicts,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  rejectSignal,
  reviseDraft,
  toggleReleaseChecklistItem,
  toggleRadarStatus,
  updateContentPlanItem,
  updateLearningNote,
  updateRadar,
  type ContentPlanItem,
  type EditorialCheck,
  type EditorialLearningNote,
  type FinalText,
  type ManualMetricSnapshot,
  type PostBrief,
  type PostDraft,
  type ReleasePackage,
  type WorkspaceSection,
  type WorkspaceState
} from './domain/editorialWorkspace';
import { AppShell } from './app/AppShell';
import { ContextChatOverlay } from './app/ContextChatOverlay';
import { useWorkspaceController } from './app/useWorkspaceController';
import { Icon } from './shared/ui/Icon';
import { AuthorMemoryView } from './features/author-memory/AuthorMemoryView';
import { EditorialModelView } from './features/editorial-model/EditorialModelView';
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
          onGoBrief={() => controller.go('brief')}
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
function PlanView({
  workspace,
  onGenerate,
  onItemChange,
  onApprove,
  onBrief
}: {
  workspace: WorkspaceState;
  onGenerate: () => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(workspace.contentPlanItems[0]?.id ?? null);
  const [editingItem, setEditingItem] = useState<ContentPlanItem | null>(null);
  const items = workspace.contentPlanItems;
  const warnings = useMemo(
    () => detectBroadcastPlanConflicts(workspace, items),
    [workspace, items]
  );
  const activeWarnings = warnings.filter((warning) => warning.severity !== 'green');
  const topicDistribution = getPlanDistribution(items, 'topicTitle');
  const fabulaDistribution = getPlanDistribution(items, 'fabulaTitle');

  function startEdit(item: ContentPlanItem) {
    setExpandedId(item.id);
    setEditingItem({ ...item });
  }

  function saveEdit() {
    if (!editingItem) return;
    onItemChange({ ...editingItem, manualOverride: true });
    setExpandedId(editingItem.id);
    setEditingItem(null);
  }

  function updateEditingItem(patch: Partial<ContentPlanItem>) {
    setEditingItem((current) => (current ? { ...current, ...patch } : current));
  }

  function updateEditingTopic(topicId: string) {
    const topic = workspace.topics.find((item) => item.id === topicId);
    updateEditingItem({ topicId, topicTitle: topic?.title ?? '' });
  }

  function updateEditingFabula(fabulaId: string) {
    const fabula = workspace.fabulas.find((item) => item.id === fabulaId);
    updateEditingItem({ fabulaId, fabulaTitle: fabula?.title ?? '' });
  }

  return (
    <div className="page wide fade-up">
      <div className="broadcast-layout">
        <section className="broadcast-main">
          <HitlGate
            tag="HITL · Gate 1 — Сетка вещания"
            title="Соберите и утвердите слоты контент-плана"
            subtitle="Сетка распределяет темы и фабулы по датам, форматам и площадкам. Ручные правки важнее весов, но конфликты подсвечиваются."
            action={items.length > 0 ? 'Пересобрать сетку' : 'Собрать сетку'}
            onAction={onGenerate}
          />
          {items.length > 0 ? (
            <div className="broadcast-list" data-testid="broadcast-grid">
              <div className="broadcast-toolbar">
                <div>
                  <h2>Сетка на {workspace.contentPlanSettings.planningHorizonDays} дней</h2>
                  <p>{workspace.contentPlanSettings.postsPerWeek} поста в неделю · {items.length} слотов</p>
                </div>
                <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                  {activeWarnings.length > 0 ? `${activeWarnings.length} предупрежд.` : 'OK'}
                </span>
              </div>
              {items.map((item) => {
                const isExpanded = expandedId === item.id;
                const isEditing = editingItem?.id === item.id;
                const itemWarnings = warnings.filter((warning) =>
                  warning.targetType === 'slot' && warning.targetId === item.id
                );
                const current = isEditing ? editingItem : item;

                return (
                  <article className={`card broadcast-row${isExpanded ? ' expanded' : ''}`} key={item.id}>
                    <button
                      className="broadcast-row-main"
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : item.id)}
                    >
                      <span className="broadcast-date">{formatPlanDate(item.date)}</span>
                      <span className="broadcast-title">{item.title}</span>
                      <span className="broadcast-meta">{item.platform}</span>
                      <span className="broadcast-meta">{item.format}</span>
                      <span className="broadcast-meta">{item.topicTitle}</span>
                      <span className="broadcast-meta">{item.fabulaTitle}</span>
                      <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
                        <i />
                        {statusLabel(item.approvalStatus)}
                      </span>
                      {itemWarnings.length > 0 ? <span className="validation-badge yellow">warning</span> : null}
                    </button>
                    {isExpanded ? (
                      <div className="broadcast-details">
                        {isEditing && current ? (
                          <div className="broadcast-edit-grid">
                            <label>
                              Заголовок
                              <input
                                value={current.title}
                                onChange={(event) => updateEditingItem({ title: event.target.value })}
                              />
                            </label>
                            <label>
                              Дата
                              <input
                                type="date"
                                value={current.date}
                                onChange={(event) => updateEditingItem({ date: event.target.value })}
                              />
                            </label>
                            <label>
                              Площадка
                              <input
                                value={current.platform}
                                onChange={(event) => updateEditingItem({ platform: event.target.value })}
                              />
                            </label>
                            <label>
                              Формат
                              <select
                                value={current.format}
                                onChange={(event) => updateEditingItem({ format: event.target.value })}
                              >
                                {workspace.contentPlanSettings.allowedFormats.map((format) => (
                                  <option value={format} key={format}>{format}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Тема
                              <select value={current.topicId ?? ''} onChange={(event) => updateEditingTopic(event.target.value)}>
                                {workspace.topics.map((topic) => (
                                  <option value={topic.id} key={topic.id}>{topic.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Фабула
                              <select value={current.fabulaId ?? ''} onChange={(event) => updateEditingFabula(event.target.value)}>
                                {workspace.fabulas.map((fabula) => (
                                  <option value={fabula.id} key={fabula.id}>{fabula.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Приоритет
                              <input
                                value={current.priority}
                                onChange={(event) => updateEditingItem({ priority: event.target.value })}
                              />
                            </label>
                            <label className="broadcast-edit-wide">
                              Ожидаемый эффект
                              <textarea
                                value={current.expectedEffect}
                                onChange={(event) => updateEditingItem({ expectedEffect: event.target.value })}
                              />
                            </label>
                            <div className="entity-actions broadcast-edit-actions">
                              <button className="btn btn-pri" type="button" onClick={saveEdit}>
                                Сохранить
                              </button>
                              <button className="btn btn-sec" type="button" onClick={() => setEditingItem(null)}>
                                Отменить
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <dl className="entity-detail-list">
                              <div>
                                <dt>Ожидаемый эффект</dt>
                                <dd>{item.expectedEffect}</dd>
                              </div>
                              <div>
                                <dt>Связка</dt>
                                <dd>{item.topicTitle} · {item.fabulaTitle}</dd>
                              </div>
                              <div>
                                <dt>Источник</dt>
                                <dd>{item.sourceSignalId ?? item.insightId}</dd>
                              </div>
                              <div>
                                <dt>Режим</dt>
                                <dd>{item.manualOverride ? 'Ручная правка сетки' : 'Собрано deterministic-сервисом'}</dd>
                              </div>
                            </dl>
                            {itemWarnings.length > 0 ? (
                              <div className="matrix-warnings">
                                {itemWarnings.map((warning) => <p key={warning.id}>{warning.message}</p>)}
                              </div>
                            ) : null}
                            <div className="entity-actions">
                              <button className="btn btn-sec" type="button" onClick={() => startEdit(item)}>
                                Редактировать
                              </button>
                              <button
                                className="btn btn-sec"
                                type="button"
                                disabled={item.approvalStatus === 'approved'}
                                onClick={() => onApprove(item.id)}
                              >
                                Утвердить
                              </button>
                              <button
                                className="btn btn-pri"
                                type="button"
                                disabled={item.approvalStatus !== 'approved'}
                                onClick={() => onBrief(item)}
                              >
                                <Icon name="brief" size={16} />
                                Подготовить фабулу поста
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          ) : (
            <EmptyState text="Соберите сетку вещания из текущего радара, тем и фабул редакционной модели." />
          )}
        </section>
        <aside className="aside broadcast-aside">
          <div className="panel validation-panel">
            <div className="validation-head">
              <h3>Сетка вещания</h3>
              <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                {activeWarnings.length > 0 ? 'Есть конфликты' : 'Баланс OK'}
              </span>
              <p>Ручные правки слотов сохраняются, даже если выходят за declared weights. Конфликт нужен как сигнал редактору.</p>
            </div>
            <div className="validator-summary">
              <div><strong>{items.length}</strong><span>слотов</span></div>
              <div><strong>{workspace.contentPlanSettings.postsPerWeek}</strong><span>в неделю</span></div>
              <div><strong>{topicDistribution.length}</strong><span>тем</span></div>
              <div><strong>{fabulaDistribution.length}</strong><span>фабул</span></div>
            </div>
            <DistributionList title="Темы" items={topicDistribution} />
            <DistributionList title="Фабулы" items={fabulaDistribution} />
            {activeWarnings.length > 0 ? (
              <div className="validation-warnings">
                {activeWarnings.slice(0, 6).map((warning) => <p key={warning.id}>{warning.message}</p>)}
              </div>
            ) : null}
          </div>
        </aside>
      </div>
    </div>
  );
}

function DistributionList({ title, items }: { title: string; items: Array<{ title: string; count: number; share: number }> }) {
  return (
    <div className="plan-distribution">
      <h4>{title}</h4>
      {items.length > 0 ? (
        items.map((item) => (
          <div className="plan-distribution-row" key={item.title}>
            <span>{item.title}</span>
            <b>{Math.round(item.share)}%</b>
          </div>
        ))
      ) : (
        <p className="panel-note">Нет слотов для расчета.</p>
      )}
    </div>
  );
}

function getPlanDistribution(
  items: ContentPlanItem[],
  field: 'topicTitle' | 'fabulaTitle'
): Array<{ title: string; count: number; share: number }> {
  const total = Math.max(items.length, 1);
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const title = item[field] ?? 'Не задано';
    counts.set(title, (counts.get(title) ?? 0) + 1);
  });

  return Array.from(counts.entries()).map(([title, count]) => ({
    title,
    count,
    share: (count / total) * 100
  }));
}

function formatPlanDate(date: string): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
}

function BriefView({
  workspace,
  onBriefChange,
  onBackToPlan,
  onApprove
}: {
  workspace: WorkspaceState;
  onBriefChange: (brief: PostBrief) => void;
  onBackToPlan: () => void;
  onApprove: () => void;
}) {
  const brief = workspace.postBrief;

  if (!brief) {
    return (
      <div className="page fade-up">
        <button className="btn btn-sec" type="button" onClick={onBackToPlan}>
          Вернуться в план
        </button>
        <EmptyState text="Сначала подготовьте фабулу из утвержденного элемента плана." />
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 2 — Замысел"
        title="Утвердите фабулу перед написанием"
        subtitle="Слабые тексты обычно проваливаются на замысле. Решение остается за главным редактором."
        action="Утвердить фабулу"
        onAction={onApprove}
      />
      <div className="inline-actions">
        <button className="btn btn-sec" type="button" onClick={onBackToPlan}>
          Вернуться в план
        </button>
      </div>
      <div className="brief-grid">
        <section className="brief-body">
          <span className="rub">{brief.rubric}</span>
          <FieldInput label="Заголовок" value={brief.title} onChange={(title) => onBriefChange({ ...brief, title })} />
          <FieldInput
            label="Главный тезис"
            value={brief.thesis}
            onChange={(thesis) => onBriefChange({ ...brief, thesis })}
            serif
          />
          <FieldInput
            label="Конфликт"
            value={brief.conflict}
            onChange={(conflict) => onBriefChange({ ...brief, conflict })}
          />
          <FieldInput
            label="Авторская позиция"
            value={brief.authorPosition}
            onChange={(authorPosition) => onBriefChange({ ...brief, authorPosition })}
          />
          <FieldList label="Доказательства" items={brief.evidence} onChange={(evidence) => onBriefChange({ ...brief, evidence })} />
          <FieldList label="Структура" items={brief.structure} onChange={(structure) => onBriefChange({ ...brief, structure })} />
          <FieldInput label="CTA" value={brief.cta} onChange={(cta) => onBriefChange({ ...brief, cta })} />
          <FieldList label="Риски" items={brief.risks} onChange={(risks) => onBriefChange({ ...brief, risks })} />
        </section>
        <aside className="aside">
          <div className="panel">
            <h4>Статус</h4>
            <span className={`pill ${brief.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
              <i />
              {statusLabel(brief.approvalStatus)}
            </span>
          </div>
          <div className="panel">
            <h4>Источники</h4>
            <ul className="bullets">
              {brief.sources.map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

function EditView({
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

function ReleaseView({
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

function AnalyticsView({
  workspace,
  onGoRelease,
  onCreateNote,
  onChangeNote,
  onCapture
}: {
  workspace: WorkspaceState;
  onGoRelease: () => void;
  onCreateNote: () => void;
  onChangeNote: (note: EditorialLearningNote) => void;
  onCapture: () => void;
}) {
  const releasePackage = workspace.releasePackage;
  const note = workspace.editorialLearningNote;

  if (!releasePackage || releasePackage.status !== 'exported') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="release" size={28} />
          </div>
          <h2>Сначала завершите ручной выпуск</h2>
          <p>Аналитика открывается после статуса «Экспортировано вручную» в разделе «Выпуск».</p>
          <button className="btn btn-pri" type="button" onClick={onGoRelease}>
            <Icon name="release" size={16} />
            Перейти в выпуск
          </button>
        </section>
      </div>
    );
  }

  if (!note) {
    return (
      <div className="page wide fade-up">
        <section className="card draft-start">
          <span className="rub">Analytics prep</span>
          <h2>Подготовить редакционные выводы</h2>
          <p>
            Метрики вводятся вручную. Этот слой фиксирует не просмотры ради просмотров,
            а выводы для следующего редакционного цикла.
          </p>
          <button className="btn btn-pri" type="button" onClick={onCreateNote}>
            <Icon name="analytics" size={16} />
            Подготовить аналитику
          </button>
        </section>
      </div>
    );
  }

  const currentNote = note;

  function patchNote(patch: Partial<EditorialLearningNote>) {
    onChangeNote(updateLearningNote(currentNote, patch));
  }

  function patchMetric(metric: keyof ManualMetricSnapshot, value: string) {
    patchNote({
      metricSnapshot: {
        ...currentNote.metricSnapshot,
        [metric]: Number(value) || 0
      }
    });
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="Analytics · Learning"
        title={`Статус: ${analyticsStatusLabel(note.status)}`}
        subtitle="Площадочные API не подключены: редакция вручную заносит метрики и фиксирует выводы."
        action="Зафиксировать выводы"
        onAction={onCapture}
      />
      <div className="analytics-grid">
        <section className="analytics-doc">
          <div className="doc-head">
            <div>
              <span className="rub">Ручные метрики</span>
              <h2>Редакционный разбор выпуска</h2>
            </div>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
          </div>
          <div className="metric-grid">
            <MetricInput label="Просмотры" value={note.metricSnapshot.views} onChange={(value) => patchMetric('views', value)} />
            <MetricInput label="Реакции" value={note.metricSnapshot.reactions} onChange={(value) => patchMetric('reactions', value)} />
            <MetricInput label="Комментарии" value={note.metricSnapshot.comments} onChange={(value) => patchMetric('comments', value)} />
            <MetricInput label="Сохранения" value={note.metricSnapshot.saves} onChange={(value) => patchMetric('saves', value)} />
            <MetricInput label="Лиды" value={note.metricSnapshot.leads} onChange={(value) => patchMetric('leads', value)} />
          </div>
          <div className="learning-fields">
            <LearningTextArea label="Что сработало" value={note.observedResult} onChange={(observedResult) => patchNote({ observedResult })} />
            <LearningTextArea label="Реакция аудитории" value={note.audienceReaction} onChange={(audienceReaction) => patchNote({ audienceReaction })} />
            <LearningTextArea label="Какие тезисы работают" value={note.workingTheses} onChange={(workingTheses) => patchNote({ workingTheses })} />
            <LearningTextArea label="Какие рубрики усиливают доверие" value={note.trustRubrics} onChange={(trustRubrics) => patchNote({ trustRubrics })} />
            <LearningTextArea label="Какие темы приводят качественную аудиторию" value={note.qualityAudienceTopics} onChange={(qualityAudienceTopics) => patchNote({ qualityAudienceTopics })} />
            <LearningTextArea label="Где автор звучит сильнее" value={note.strongerVoice} onChange={(strongerVoice) => patchNote({ strongerVoice })} />
            <LearningTextArea label="Какие форматы стоит повторить" value={note.repeatFormats} onChange={(repeatFormats) => patchNote({ repeatFormats })} />
            <LearningTextArea label="Что развить в серию" value={note.seriesCandidates} onChange={(seriesCandidates) => patchNote({ seriesCandidates })} />
          </div>
        </section>
        <aside className="edit-side">
          <section className="panel">
            <h4>Контекст выпуска</h4>
            <dl className="meta-list">
              <dt>Release</dt>
              <dd>{note.releasePackageId}</dd>
              <dt>Статус</dt>
              <dd>{releaseStatusLabel(releasePackage.status)}</dd>
              <dt>Площадки</dt>
              <dd>{releasePackage.targets.map(targetLabel).join(' + ')}</dd>
            </dl>
          </section>
          <section className="panel">
            <h4>Learning note</h4>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
            <dl className="meta-list analytics-meta">
              <dt>Обновлено</dt>
              <dd>{note.updatedAt}</dd>
              <dt>Зафиксировано</dt>
              <dd>{note.capturedAt ?? 'еще нет'}</dd>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}

function MetricInput({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="metric-input">
      <span>{label}</span>
      <input type="number" min="0" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function LearningTextArea({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="learning-field">
      <span>{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function HitlGate({
  tag,
  title,
  subtitle,
  action,
  disabled,
  onAction
}: {
  tag: string;
  title: string;
  subtitle: string;
  action: string;
  disabled?: boolean;
  onAction: () => void;
}) {
  return (
    <section className="gate">
      <div className="gm">
        <Icon name="caret" size={24} />
      </div>
      <div>
        <div className="gtag">{tag}</div>
        <div className="gttl">{title}</div>
        <div className="gsub">{subtitle}</div>
      </div>
      <div className="gbtns">
        <button className="btn btn-pri" type="button" disabled={disabled} onClick={onAction}>
          <Icon name="check" size={16} />
          {action}
        </button>
      </div>
    </section>
  );
}

function FieldInput({
  label,
  value,
  onChange,
  serif
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  serif?: boolean;
}) {
  return (
    <label className="field-row">
      <span className="k">{label}</span>
      <textarea className={serif ? 'serif' : ''} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function FieldList({
  label,
  items,
  onChange
}: {
  label: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  return <FieldInput label={label} value={items.join('\n')} onChange={(value) => onChange(splitLines(value))} />;
}

function Placeholder({ icon, title, text }: { icon: string; title: string; text: string }) {
  return (
    <div className="page fade-up placeholder">
      <div className="placeholder-icon">
        <Icon name={icon} size={30} />
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}

function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatScore(value: number): string {
  return value.toFixed(2);
}

function formatDate(value: string): string {
  return value.slice(0, 10);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function statusLabel(status: string): string {
  if (status === 'approved') return 'Утверждено';
  if (status === 'rejected') return 'Отклонено';
  return 'Черновик';
}

function checkStatusLabel(status: string): string {
  if (status === 'passed') return 'Пройдено';
  if (status === 'warning') return 'Есть warning';
  return 'Блокер';
}

function releaseStatusLabel(status: string): string {
  if (status === 'ready') return 'Готово к выпуску';
  if (status === 'exported') return 'Экспортировано вручную';
  return 'Черновик выпуска';
}

function analyticsStatusLabel(status: string): string {
  if (status === 'captured') return 'Выводы зафиксированы';
  return 'Черновик аналитики';
}

function targetLabel(target: string): string {
  if (target === 'telegram') return 'Telegram';
  if (target === 'linkedin') return 'LinkedIn';
  return target;
}
