import { useEffect, useState } from 'react';
import {
  getActiveDraftVersion,
  normalizePostDraftVersions,
  type DraftGenerationUiState,
  type DraftVersion,
  type PostBriefEditPatch,
  type PostDraft,
  type PostVisualEditPatch,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EditorialBriefStage } from './EditorialBriefStage';
import { EditorialVisualStage } from './EditorialVisualStage';
import { TraceRunLink } from './TraceRunLink';

export function EditorialWorkbench({
  workspace,
  draftGenerationState,
  onApproveBrief,
  onApproveFinal,
  onApproveVisual,
  onDraftChange,
  onEditBrief,
  onGoPlan,
  onPrepareMemeReferences,
  onPrepareMemeRemixVariants,
  onPrepareVisualVariants,
  onReviseDraftWithComment,
  onSelectMemeReference,
  onSelectVisualVariant,
  onSelectDraftVersion,
  onSaveVisual
}: {
  workspace: WorkspaceState;
  draftGenerationState: DraftGenerationUiState;
  onApproveBrief: () => void;
  onApproveFinal: (versionId?: string) => void | Promise<void>;
  onApproveVisual: (patch: PostVisualEditPatch) => void;
  onDraftChange: (body: string) => void;
  onEditBrief: (patch: PostBriefEditPatch) => void;
  onGoPlan: () => void;
  onPrepareMemeReferences: (patch: PostVisualEditPatch) => void;
  onPrepareMemeRemixVariants: () => void;
  onPrepareVisualVariants: (patch: PostVisualEditPatch) => void;
  onReviseDraftWithComment: (comment: string) => Promise<void>;
  onSelectMemeReference: (referenceId: string) => void;
  onSelectVisualVariant: (variantId: string) => void;
  onSelectDraftVersion: (versionId: string) => void;
  onSaveVisual: (patch: PostVisualEditPatch) => void;
}) {
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;
  const [tab, setTab] = useState<'brief' | 'draft' | 'visual'>(() => {
    if (!brief || brief.approvalStatus !== 'approved') return 'brief';
    if (finalText?.approvalStatus === 'approved') return 'visual';
    return 'draft';
  });

  useEffect(() => {
    if (draftGenerationState.status === 'generating') {
      setTab('draft');
    }
  }, [draftGenerationState.status]);

  if (!workspace.selectedEditorialWorkItemId) {
    return (
      <section className="card edit-empty editorial-workbench-empty">
        <div className="placeholder-icon">
          <Icon name="brief" size={28} />
        </div>
        <h2>Выберите пост из очереди</h2>
        <p>Редактура работает с конкретным утвержденным слотом: сначала откройте строку в очереди, затем готовьте фабулу, драфт и визуал.</p>
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
        <button className={`tab${tab === 'visual' ? ' active' : ''}`} type="button" role="tab" aria-selected={tab === 'visual'} onClick={() => setTab('visual')}>
          Визуал
        </button>
      </div>
      {tab === 'brief' ? (
        <EditorialBriefStage
          brief={brief}
          workspace={workspace}
          isDraftGenerating={draftGenerationState.status === 'generating'}
          onApproveBrief={onApproveBrief}
          onEditBrief={(patch) => {
            onEditBrief(patch);
            setTab('brief');
          }}
          onGoPlan={onGoPlan}
          onOpenDraft={() => setTab('draft')}
        />
      ) : tab === 'visual' ? (
        <EditorialVisualStage
          workspace={workspace}
          onApproveVisual={onApproveVisual}
          onOpenDraft={() => setTab('draft')}
          onPrepareMemeReferences={onPrepareMemeReferences}
          onPrepareMemeRemixVariants={onPrepareMemeRemixVariants}
          onPrepareVisualVariants={onPrepareVisualVariants}
          onSaveVisual={onSaveVisual}
          onSelectMemeReference={onSelectMemeReference}
          onSelectVisualVariant={onSelectVisualVariant}
        />
      ) : draftGenerationState.status === 'generating' ? (
        <section className="card draft-start draft-generation-pending" aria-live="polite">
          <span className="rub">{brief.rubric}</span>
          <h2>Генерируем драфт</h2>
          <p>Backend поставил DraftRun в очередь и выполняет шаги раннера. Драфт появится здесь автоматически, когда run завершится.</p>
          {draftGenerationState.runId ? (
            <div className="trace-run-box">
              <span>DraftRun ID</span>
              <code>{draftGenerationState.runId}</code>
              <TraceRunLink runId={draftGenerationState.runId} />
            </div>
          ) : null}
          {draftGenerationState.stepLabel ? (
            <p className="muted">Текущий шаг: {draftGenerationState.stepLabel}</p>
          ) : null}
          <p className="muted">Идет: {formatElapsed(draftGenerationState.startedAt)}</p>
          {draftGenerationState.lastProgressAt ? (
            <p className="muted">Последний прогресс: {formatDateTime(draftGenerationState.lastProgressAt)}</p>
          ) : null}
          {draftGenerationState.isStale ? (
            <div className="draft-generation-summary warning">
              <b>Нет прогресса больше 5 минут</b>
              <span>{draftGenerationState.staleReason ?? 'Runner еще может завершиться. Проверьте trace перед повторным запуском.'}</span>
            </div>
          ) : null}
          <div className="draft-generation-spinner" aria-hidden="true" />
        </section>
      ) : draftGenerationState.status === 'blocked' ? (
        <section className="card draft-start draft-generation-blocked" aria-live="polite">
          <span className="rub">{brief.rubric}</span>
          <h2>Пост остановлен до генерации</h2>
          <p>{draftGenerationState.reason}</p>
          <div className="trace-run-box">
            <span>DraftRun ID</span>
            <code>{draftGenerationState.runId}</code>
            <TraceRunLink runId={draftGenerationState.runId} />
          </div>
          <div className="facts-grid">
            <div className="fact-card">
              <span className="k">Feasibility</span>
              <strong>{draftGenerationState.feasibilityStatus}</strong>
            </div>
            {draftGenerationState.findings.slice(0, 3).map((finding, index) => (
              <div className="fact-card" key={`${finding}-${index}`}>
                <span className="k">Finding</span>
                <strong>{finding}</strong>
              </div>
            ))}
          </div>
          <div className="inline-actions">
            <button className="btn btn-sec" type="button" onClick={() => setTab('brief')}>
              Вернуться к фабуле
            </button>
          </div>
        </section>
      ) : !draft ? (
        <section className="card draft-start">
          <span className="rub">{brief.rubric}</span>
          <h2>{brief.title}</h2>
          <p>Драфт появится после утверждения фабулы. Если генерация уже запускалась, проверьте статус справа или повторите утверждение фабулы.</p>
          <button className="btn btn-sec" type="button" onClick={() => setTab('brief')}>
            Вернуться к фабуле
          </button>
        </section>
      ) : (
        <section className="doc">
          <DraftEditor
            draft={draft}
            isTextApproved={finalText?.approvalStatus === 'approved'}
            generationState={draftGenerationState}
            onApproveDraft={onApproveFinal}
            onDraftChange={onDraftChange}
            onOpenBrief={() => setTab('brief')}
            onReviseDraftWithComment={onReviseDraftWithComment}
            onSelectDraftVersion={onSelectDraftVersion}
          />
        </section>
      )}
    </section>
  );
}

function formatElapsed(startedAt: string): string {
  const seconds = Math.max(0, Math.floor((Date.now() - Date.parse(startedAt)) / 1000));
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return minutes > 0 ? `${minutes} мин ${rest} сек` : `${rest} сек`;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(value));
}

function DraftEditor({
  draft,
  isTextApproved,
  generationState,
  onApproveDraft,
  onDraftChange,
  onOpenBrief,
  onReviseDraftWithComment,
  onSelectDraftVersion
}: {
  draft: PostDraft;
  isTextApproved: boolean;
  generationState: DraftGenerationUiState;
  onApproveDraft: (versionId: string) => void | Promise<void>;
  onDraftChange: (body: string) => void;
  onOpenBrief: () => void;
  onReviseDraftWithComment: (comment: string) => Promise<void>;
  onSelectDraftVersion: (versionId: string) => void;
}) {
  const normalizedDraft = normalizePostDraftVersions(draft);
  const activeVersion = getActiveDraftVersion(normalizedDraft);
  const versions = normalizedDraft.versions ?? [activeVersion];
  const [body, setBody] = useState(activeVersion.body);
  const [editorComment, setEditorComment] = useState('');
  const [revisionError, setRevisionError] = useState('');
  const [isRevisionRunning, setRevisionRunning] = useState(false);
  const hasUnsavedChanges = body !== activeVersion.body;

  useEffect(() => {
    setBody(activeVersion.body);
    setRevisionError('');
  }, [activeVersion.body, activeVersion.id]);

  async function improveByComment() {
    const normalizedComment = editorComment.trim();
    if (!normalizedComment) return;
    setRevisionRunning(true);
    setRevisionError('');
    try {
      await onReviseDraftWithComment(normalizedComment);
      setEditorComment('');
    } catch (error) {
      setRevisionError(error instanceof Error ? error.message : 'Не удалось создать новую версию');
    } finally {
      setRevisionRunning(false);
    }
  }

  return (
    <>
      <div className="doc-head">
        <div>
          <span className="rub">Версия {activeVersion.versionNumber}</span>
          <h2>{activeVersion.title}</h2>
        </div>
        <span className={`pill ${draft.status === 'revised' ? 'pin' : 'ok'}`}>
          <i />
          {draft.status === 'revised' ? 'Отредактирован' : 'Драфт'}
        </span>
      </div>
      {isTextApproved ? (
        <div className="final-status">
          <span className="pill ok">
            <i />
            Текст утвержден
          </span>
          <span>следующий шаг: Визуал</span>
        </div>
      ) : null}
      <DraftGenerationSummary draft={draft} generationState={generationState} />
      <DraftVersionList
        activeVersionId={activeVersion.id}
        finalVersionId={normalizedDraft.finalVersionId}
        versions={versions}
        onSelect={onSelectDraftVersion}
      />
      <DraftVersionQualitySummary version={activeVersion} />
      <label className="draft-editor">
        <span className="k">Текст</span>
        <textarea
          aria-label="Текст драфта"
          value={body}
          onChange={(event) => setBody(event.target.value)}
        />
      </label>
      {hasUnsavedChanges ? <p className="muted">Есть несохраненные правки. Сохраните их как новую версию перед утверждением финала.</p> : null}
      <div className="draft-human-loop">
        <label>
          <span className="k">Комментарий редактора</span>
          <textarea
            aria-label="Комментарий к улучшению драфта"
            value={editorComment}
            onChange={(event) => setEditorComment(event.target.value)}
            placeholder="Например: усилить авторскую позицию и убрать пересказ источников"
          />
        </label>
        {revisionError ? <p className="draft-revision-error">{revisionError}</p> : null}
        <button className="btn btn-sec" type="button" disabled={!editorComment.trim() || isRevisionRunning} onClick={improveByComment}>
          Улучшить по комментарию
        </button>
      </div>
      <div className="inline-actions">
        <button className="btn btn-pri" type="button" disabled={hasUnsavedChanges} onClick={() => onApproveDraft(activeVersion.id)}>
          <Icon name="check" size={16} />
          Сделать финальной
        </button>
        <button className="btn btn-sec" type="button" disabled={!hasUnsavedChanges} onClick={() => onDraftChange(body)}>
          Сохранить как новую версию
        </button>
        <button className="btn btn-sec" type="button" onClick={onOpenBrief}>
          Вернуться к фабуле
        </button>
      </div>
    </>
  );
}

function DraftVersionList({
  activeVersionId,
  finalVersionId,
  versions,
  onSelect
}: {
  activeVersionId: string;
  finalVersionId: string | undefined;
  versions: DraftVersion[];
  onSelect: (versionId: string) => void;
}) {
  return (
    <div className="draft-version-list" aria-label="Версии драфта">
      {versions.map((version) => (
        <button
          className={`draft-version-chip${version.id === activeVersionId ? ' active' : ''}`}
          key={version.id}
          type="button"
          onClick={() => onSelect(version.id)}
        >
          <span>v{version.versionNumber}</span>
          <small>
            {versionSourceLabel(version.source)}
            {version.qualityCheck ? ` · ${qualityStatusLabel(version.qualityCheck.status)}` : ''}
            {version.id === finalVersionId ? ' · финал' : ''}
          </small>
        </button>
      ))}
    </div>
  );
}

function DraftVersionQualitySummary({ version }: { version: DraftVersion }) {
  const quality = version.qualityCheck;
  if (!quality) return null;

  const details = [
    ...quality.missedCommentIntents.map((intent) => `Не закрыто: ${intent}`),
    ...quality.regressionWarnings,
    ...quality.internalJargonLeaks.map((term) => `Внутренний термин в тексте: ${term}`)
  ].slice(0, 5);

  return (
    <div className={`draft-version-quality ${quality.status === 'passed' ? 'ok' : quality.status === 'notRun' ? 'muted' : 'warning'}`}>
      <b>{qualityStatusLabel(quality.status)}</b>
      <span>{quality.summary || 'Проверка качества версии не дала текстового вывода.'}</span>
      <div className="draft-version-quality-grid">
        <span>Комментарий: {qualityStatusLabel(quality.commentComplianceStatus)}</span>
        <span>Источники: {qualityStatusLabel(quality.sourceIntegrityStatus)}</span>
        <span>Публичная проза: {qualityStatusLabel(quality.publicProseStatus)}</span>
      </div>
      {details.length > 0 ? (
        <ul>
          {details.map((detail) => <li key={detail}>{detail}</li>)}
        </ul>
      ) : null}
    </div>
  );
}

function versionSourceLabel(source: DraftVersion['source']): string {
  if (source === 'humanCommentRevision') return 'по комментарию';
  if (source === 'manualEdit') return 'ручная правка';
  return 'машина';
}

function qualityStatusLabel(status: NonNullable<DraftVersion['qualityCheck']>['status']): string {
  if (status === 'passed') return 'прошла проверку';
  if (status === 'warning') return 'есть риски';
  if (status === 'critical') return 'критично';
  return 'проверка недоступна';
}

function DraftGenerationSummary({
  draft,
  generationState
}: {
  draft: PostDraft;
  generationState: DraftGenerationUiState;
}) {
  const generation = draft.generation;
  if (generationState.status === 'failed') {
    return (
      <div className="draft-generation-summary warning">
        <b>Backend run не записан</b>
        <span>Использован локальный fallback. Причина: {generationState.error}</span>
      </div>
    );
  }
  if (!generation) return null;

  const sourceLabel = generation.source === 'draftRun'
    ? 'DraftRun'
    : generation.source === 'openrouter'
      ? 'OpenRouter'
      : generation.source === 'backendFallback'
        ? 'Backend fallback'
        : 'Local fallback';

  return (
    <div className={`draft-generation-summary${generation.fallbackUsed ? ' warning' : ''}`}>
      <b>AI trace: {sourceLabel}</b>
      <span>
        Provider: {generation.provider ?? 'none'} · Model: {generation.model ?? 'none'} · AiRun: {generation.aiRunId ?? 'not recorded'}
      </span>
      {generation.draftRunId ? (
        <div className="trace-run-box">
          <span>DraftRun ID</span>
          <code>{generation.draftRunId}</code>
          <TraceRunLink runId={generation.draftRunId} />
        </div>
      ) : null}
      {generation.error ? <span>Ошибка: {generation.error}</span> : null}
    </div>
  );
}
