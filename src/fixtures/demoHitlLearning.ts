import {
  approveFinalText,
  approvePostBrief,
  createEditorialWorkItem,
  type DraftVersion,
  type HumanCommentRevisionQualityCheck,
  type PostDraft,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import {
  createPostBrief,
  createWorkspaceInsightCard,
  inferAuthorPositionAssertions,
  upsertEditorialLearningAuthorNote
} from '../application/editorialServices';

const DEMO_TIMESTAMP = '2026-06-29T10:00:00.000Z';

export function withSeededHitlLearningScenario(workspace: WorkspaceState): WorkspaceState {
  const basePlanItem = workspace.contentPlanItems[0];
  if (!basePlanItem) return workspace;
  const planItem = {
    ...basePlanItem,
    id: 'demo-hitl-learning-slot',
    title: 'AI-B2B demo не доказывает продукт',
    approvalStatus: 'approved' as const
  };
  const insightCard = workspace.insightCard ?? createWorkspaceInsightCard(workspace);

  const postBrief = approvePostBrief(
    createPostBrief(
      planItem,
      insightCard,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix,
      {
        candidate: workspace.postCandidate ?? undefined,
        sourceSignal: workspace.sourceSignal
      }
    )
  );
  const postDraft = createSeededPostDraft(postBrief.id);
  const finalText = approveFinalText(
    { ...postDraft, activeVersionId: 'demo-hitl-draft-v2', finalVersionId: 'demo-hitl-draft-v2' },
    {
      versionId: 'demo-hitl-draft-v2',
      machineTrace: {
        draftRunId: 'demo-hitl-draft-run',
        traceStatus: 'available',
        finalQualityGate: { status: 'warning', sourceDumpRisk: 'low' },
        revisionLoop: { stopReason: 'editorially-improved' },
        alternativeAngleTournament: { status: 'succeeded', winner: 'original-pool' },
        validationSummary: { warnings: 1, critical: 0 },
        unresolvedRisks: ['v3 стала структурнее, но потеряла живую авторскую позицию']
      }
    }
  );
  const workItem = createEditorialWorkItem(planItem, { brief: postBrief, draft: postDraft, finalText });
  const upsertedNotes = upsertEditorialLearningAuthorNote(workspace.authorNotes, postDraft, finalText);
  const learningNote = upsertedNotes.find((note) => note.id === `editorial-learning-${finalText.id}`);
  const authorNotes = learningNote
    ? [...workspace.authorNotes.filter((note) => note.id !== learningNote.id), learningNote]
    : workspace.authorNotes;

  return {
    ...workspace,
    authorNotes,
    authorMemoryEvents: workspace.authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, workspace.authorMemoryEvents),
    editorialWorkItems: [...workspace.editorialWorkItems, workItem]
  };
}

function createSeededPostDraft(briefId: string): PostDraft {
  const versions = createSeededVersions();
  return {
    id: 'demo-hitl-draft',
    briefId,
    title: versions[1].title,
    body: versions[1].body,
    version: 2,
    status: 'revised',
    updatedAt: DEMO_TIMESTAMP,
    generation: {
      source: 'draftRun',
      aiRunId: 'demo-hitl-ai-run',
      draftRunId: 'demo-hitl-draft-run',
      provider: 'openrouter',
      model: 'demo-seeded',
      fallbackUsed: false,
      createdAt: DEMO_TIMESTAMP
    },
    versions,
    activeVersionId: 'demo-hitl-draft-v2',
    finalVersionId: 'demo-hitl-draft-v2'
  };
}

function createSeededVersions(): DraftVersion[] {
  return [
    {
      id: 'demo-hitl-draft-v1',
      versionNumber: 1,
      source: 'machineFinal',
      title: 'Почему AI-B2B demo еще не продукт',
      body: 'AI-B2B demo может выглядеть убедительно, но продукт начинается только там, где workflow, evals и adoption становятся регулярной практикой.',
      draftRunId: 'demo-hitl-draft-run',
      aiRunId: 'demo-hitl-ai-run',
      createdAt: '2026-06-29T09:00:00.000Z'
    },
    {
      id: 'demo-hitl-draft-v2',
      versionNumber: 2,
      source: 'humanCommentRevision',
      baseVersionId: 'demo-hitl-draft-v1',
      title: 'AI-B2B demo не доказывает продукт',
      body: 'Моя позиция простая: AI-B2B продукт нельзя оценивать по красивому demo. Его надо проверять по тому, меняет ли он рабочий процесс, выдерживает ли evals и доходит ли до регулярного использования. Поэтому хороший пилот должен показывать не магию модели, а путь от впечатления к adoption.',
      editorComment: 'усиль авторскую позицию',
      revisionSummary: 'Добавлена явная авторская позиция и конфликт demo vs adoption.',
      draftRunId: 'demo-hitl-draft-run',
      aiRunId: 'demo-hitl-revision-author-stance',
      qualityCheck: makeQualityCheck('passed', {
        matchedCommentIntents: ['author stance'],
        summary: 'Комментарий выполнен: позиция автора стала явной.'
      }),
      createdAt: '2026-06-29T09:15:00.000Z'
    },
    {
      id: 'demo-hitl-draft-v3',
      versionNumber: 3,
      source: 'humanCommentRevision',
      baseVersionId: 'demo-hitl-draft-v2',
      title: 'Три критерия AI-B2B продукта',
      body: 'Проверяйте AI-B2B пилот по трем критериям: встроился ли он в workflow, есть ли evals на качество, появляется ли регулярное использование после demo. Если один из критериев провален, перед вами не продукт, а удачный показ возможностей модели.',
      editorComment: 'добавь 3 критерия',
      revisionSummary: 'Добавлены три видимых критерия оценки пилота.',
      draftRunId: 'demo-hitl-draft-run',
      aiRunId: 'demo-hitl-revision-criteria',
      qualityCheck: makeQualityCheck('warning', {
        matchedCommentIntents: ['three criteria'],
        missedCommentIntents: ['сохранить авторскую интонацию v2'],
        regressionWarnings: ['текст стал суше и ближе к чеклисту'],
        summary: 'Три критерия добавлены, но версия потеряла часть авторского голоса.'
      }),
      createdAt: '2026-06-29T09:30:00.000Z'
    },
    {
      id: 'demo-hitl-draft-v4',
      versionNumber: 4,
      source: 'manualEdit',
      baseVersionId: 'demo-hitl-draft-v3',
      title: 'AI-B2B demo не доказывает продукт',
      body: 'AI-B2B demo легко принять за прогресс. Но мой критерий жестче: продукт начинается там, где команда видит устойчивое изменение workflow, может измерить качество через evals и понимает, почему пользователи возвращаются после пилота.',
      editorComment: 'убери сухой отчетный тон',
      revisionSummary: 'Ручная правка вернула живой тон, но редактор выбрал v2 как более точную позицию.',
      draftRunId: 'demo-hitl-draft-run',
      aiRunId: null,
      qualityCheck: makeQualityCheck('warning', {
        matchedCommentIntents: ['tone'],
        regressionWarnings: ['структурные критерии стали менее явными'],
        summary: 'Тон улучшен, но структура стала менее проверяемой.'
      }),
      createdAt: '2026-06-29T09:45:00.000Z'
    }
  ];
}

function makeQualityCheck(
  status: HumanCommentRevisionQualityCheck['status'],
  overrides: Partial<HumanCommentRevisionQualityCheck>
): HumanCommentRevisionQualityCheck {
  return {
    status,
    commentComplianceStatus: status,
    sourceIntegrityStatus: 'passed',
    publicProseStatus: status === 'passed' ? 'passed' : 'warning',
    internalJargonLeaks: [],
    regressionWarnings: [],
    matchedCommentIntents: [],
    missedCommentIntents: [],
    summary: '',
    attempts: [{ label: 'demo-seeded-quality-check', status: 'succeeded' }],
    ...overrides
  };
}
