import type { WorkspaceState } from '../domain/editorialWorkspace';

export function createDemoWorkspace(): WorkspaceState {
  return {
    editorialModel: {
      author:
        'Анна Корн — основатель и операционный консультант, который помогает SMB внедрять AI без хайпа.',
      audience:
        'Основатели и операционные руководители малого и среднего бизнеса, которым нужна ясность, а не витрина инструментов.',
      positioning:
        'Практичный редакционный голос про AI как операционную систему бизнеса.',
      fabula:
        'AI дает пользу не тем, кто покупает больше инструментов, а тем, кто перестраивает процессы и принимает решения дисциплинированно.',
      rubrics: ['Разборы', 'Антимнения', 'Кейсы', 'Полевые заметки'],
      styleRules: [
        'Короткие фразы',
        'Спокойная уверенность',
        'Практические примеры',
        'Без пустого консалтингового тона'
      ],
      forbiddenTopics: ['Политика', 'Прогнозы курсов', 'Магическое мышление про AI'],
      goals: [
        'Усилить доверие к автору',
        'Показывать практический подход к AI',
        'Приводить предпринимателей к разговору о процессах'
      ]
    },
    sourceSignal: {
      id: 'signal-ai-pilot-failures',
      type: 'Повторяющийся паттерн',
      title: 'Провалы AI-пилотов из-за хаоса процессов',
      source: 'Telegram, LinkedIn, заметки автора',
      capturedAt: '2026-06-03',
      summary:
        'Несколько рыночных постов описывают одну проблему: команды запускают AI-пилоты, но не меняют процессы, роли и критерии результата.',
      rawNote:
        'Хороший повод для разбора: предприниматели спорят о выборе моделей, но реальная причина провалов чаще в операционном беспорядке.'
    },
    insightCard: null,
    contentPlanItem: null,
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null,
    activeSection: 'radar',
    updatedAt: new Date().toISOString()
  };
}
