import { createAuthorMemoryEvent, createBroadcastPlan, inferAuthorPositionAssertions } from '../application/editorialServices';
import { createDefaultTopicFabulaMatrix } from '../domain/editorialWorkspace';
import type { WorkspaceState } from '../domain/editorialWorkspace';
import { demoAuthorNotes } from './demoAuthorMemory';
import { demoArchiveRecords, demoExternalSources, demoImportCandidates } from './demoImports';
import { demoEditorialRules, demoFabulas, demoProjectProfile, demoTopics } from './demoEditorialModel';
import { createEvaluatedDemoSourceSignals, demoRadarsWithFilters } from './demoSignals';

export function createDemoWorkspace(): WorkspaceState {
  const authorMemoryEvents = demoAuthorNotes.map(createAuthorMemoryEvent);
  const authorPositionAssertions = inferAuthorPositionAssertions(demoAuthorNotes, authorMemoryEvents);
  const evaluatedSourceSignals = createEvaluatedDemoSourceSignals(demoTopics);

  const workspace: WorkspaceState = {
    authorNotes: demoAuthorNotes,
    authorMemoryEvents,
    authorPositionAssertions,
    editorialModel: {
      author:
        'AI Product Manager, ведущий Telegram-блог о исследовательском построении AI-B2B продуктов.',
      audience:
        'AI PM, founders, CPO/product leaders и B2B SaaS команды, которым нужно доводить AI-функции от пилота до регулярного использования.',
      positioning:
        'Исследовательский голос про AI product management: меньше демо-магии, больше workflow, evals, trust loop, adoption и экономики внедрения.',
      fabula:
        'AI-B2B продукт выигрывает не тем, что красиво отвечает в демо, а тем, что помогает пользователю надежно менять рабочий процесс и доверять границам системы.',
      rubrics: ['Product research notes', 'AI adoption', 'Evals & quality', 'Trust loop'],
      styleRules: [
        'Писать как исследователь продукта, а не как AI-евангелист',
        'Фиксировать авторскую позицию до советов',
        'Показывать workflow и trade-offs',
        'Убирать стерильные AI-обобщения'
      ],
      forbiddenTopics: ['AI-хайп без продуктовой механики', 'Гарантированные прогнозы рынка', 'Магическое мышление про модели'],
      goals: [
        'Собрать аудиторию AI PM и founders вокруг практики AI-B2B productization',
        'Показывать исследовательский опыт построения AI-функций',
        'Превращать наблюдения из интервью и пилотов в ясные продуктовые принципы'
      ]
    },
    projectProfile: demoProjectProfile,
    editorialRules: demoEditorialRules,
    editorialSetupRevision: 0,
    editorialValidationRun: null,
    topics: demoTopics,
    fabulas: demoFabulas,
    topicFabulaMatrix: createDefaultTopicFabulaMatrix(demoTopics, demoFabulas),
    radars: demoRadarsWithFilters,
    sourceSignal: {
      id: 'signal-ai-demo-to-adoption-gap',
      type: 'Повторяющийся паттерн',
      title: 'AI-B2B пилоты не переходят из demo magic в adoption',
      source: 'Telegram, customer interviews, заметки автора',
      capturedAt: '2026-06-10',
      summary:
        'Несколько команд показывают сильные AI demo, но после пилота usage не становится регулярным. В заметках повторяются причины: не встроен workflow, нет evals, непонятны границы уверенности и нет rollback path.',
      rawNote:
        'Хороший материал для TG-поста: не спорить про модели, а показать разрыв между демо и продуктом. Это лучше относится к GTM/adoption, чем к support automation.'
    },
    sourceSignals: evaluatedSourceSignals,
    postCandidates: [],
    postCandidate: null,
    insightCard: null,
    contentPlanItem: null,
    contentPlanItems: [],
    contentPlanSettings: {
      period: 'month',
      postsPerWeek: 3,
      planningHorizonDays: 30,
      publishingDays: [1, 3, 5],
      publishingTimes: ['10:00'],
      publishSlots: [
        { date: '2026-06-17', time: '10:00' },
        { date: '2026-06-19', time: '10:00' },
        { date: '2026-06-22', time: '10:00' },
        { date: '2026-06-24', time: '10:00' },
        { date: '2026-06-26', time: '10:00' },
        { date: '2026-06-29', time: '10:00' }
      ],
      minCandidatesPerSlot: 1,
      maxCandidatesPerSlot: 2,
      defaultPlatform: 'Telegram',
      signalSelectionPolicy: 'hitl-only'
    },
    planWeightWarnings: [],
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null,
    externalSources: demoExternalSources,
    importCandidates: demoImportCandidates,
    archiveRecords: demoArchiveRecords,
    bulkImportActions: [],
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };

  const selectedSourceSignal = evaluatedSourceSignals[0];
  const workspaceWithSelectedSignal = {
    ...workspace,
    sourceSignal: selectedSourceSignal
  };

  return {
    ...workspaceWithSelectedSignal,
    contentPlanItems: createBroadcastPlan(workspaceWithSelectedSignal)
  };
}
