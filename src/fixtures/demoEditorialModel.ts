import type { EditorialRule, Fabula, ProjectProfile, Topic } from '../domain/editorialWorkspace';

export const demoProjectProfile: ProjectProfile = {
  name: 'TG-блог AI Product Manager',
  description: 'Исследовательский блог о построении AI-B2B продуктов',
  setupStatus: 'needsReview'
};

export const demoEditorialRules: EditorialRule[] = [
  {
    id: 'rule-author-researcher',
    group: 'author',
    title: 'AI Product Manager с исследовательской оптикой',
    statement: 'Автор говорит как практик, который исследует workflow, adoption, доверие и экономику внедрения AI-B2B продуктов.',
    status: 'active',
    evidenceNoteId: 'note-workflow-risk'
  },
  {
    id: 'rule-author-no-evangelism',
    group: 'author',
    title: 'Не AI-евангелист',
    statement: 'Автор не продает магию модели, а показывает ограничения, failure modes и условия надежного rollout.',
    status: 'active',
    evidenceNoteId: 'note-demo-magic-fails'
  },
  {
    id: 'rule-audience-builders',
    group: 'audience',
    title: 'Строители AI-B2B продуктов',
    statement: 'Писать для AI PM, founders, CPO/product leaders и B2B SaaS команд, которым нужно довести AI-фичу от пилота до регулярного использования.',
    status: 'active'
  },
  {
    id: 'rule-audience-value',
    group: 'audience',
    title: 'Ценность для читателя',
    statement: 'Каждый пост должен давать читателю продуктовый критерий: что проверить, где риск, как понять, что AI-фича стала продуктом.',
    status: 'active'
  },
  {
    id: 'rule-position-demo-not-product',
    group: 'positioning',
    title: 'Демо не равно продукт',
    statement: 'AI-B2B продукт начинается не с красивого ответа модели, а с workflow improvement, evals, trust loop и adoption ritual.',
    status: 'active',
    evidenceNoteId: 'note-demo-magic-fails'
  },
  {
    id: 'rule-position-workflow-first',
    group: 'positioning',
    title: 'Workflow важнее выбора модели',
    statement: 'Если сценарий принятия решения не описан, AI ускоряет неясность вместо создания продуктовой ценности.',
    status: 'active',
    evidenceNoteId: 'note-workflow-risk'
  },
  {
    id: 'rule-style-voice-research-note',
    group: 'styleVoice',
    title: 'Голос исследовательской заметки',
    statement: 'Тон спокойный, наблюдательный, с авторской позицией до советов и чеклистов.',
    status: 'active'
  },
  {
    id: 'rule-style-language-concrete',
    group: 'styleLanguage',
    title: 'Конкретный язык продукта',
    statement: 'Использовать слова workflow, evals, rollout, adoption, trust, rollback только когда они привязаны к сцене или решению.',
    status: 'active'
  },
  {
    id: 'rule-style-rhythm',
    group: 'styleRhythm',
    title: 'Ритм: тезис -> сцена -> вывод',
    statement: 'Пост должен быстро дать конфликт, затем сцену из практики, затем критерий для читателя.',
    status: 'active'
  },
  {
    id: 'rule-anti-ai-no-generic-openers',
    group: 'antiAiPattern',
    title: 'Без стерильных AI-вводных',
    statement: 'Не начинать с фраз вроде "в современном мире AI меняет все"; сразу входить в наблюдение или конфликт.',
    status: 'active'
  },
  {
    id: 'rule-goal-build-audience',
    group: 'goal',
    title: 'Собрать аудиторию AI product builders',
    statement: 'Блог должен привлекать AI PM и founders, которым важны практические принципы AI-B2B productization.',
    status: 'active'
  },
  {
    id: 'rule-goal-research-experience',
    group: 'goal',
    title: 'Показывать исследовательский опыт',
    statement: 'Публикации должны превращать наблюдения из интервью, пилотов и архивов в ясные продуктовые принципы.',
    status: 'active'
  },
  {
    id: 'rule-forbidden-ai-hype',
    group: 'forbiddenTopic',
    title: 'Запрет: AI-хайп без механики',
    statement: 'Не публиковать тезисы о силе AI без продуктового механизма, проверки или ограничения применимости.',
    status: 'active'
  },
  {
    id: 'rule-forbidden-market-predictions',
    group: 'forbiddenTopic',
    title: 'Запрет: гарантированные прогнозы рынка',
    statement: 'Не делать уверенных рыночных прогнозов без данных и явных допущений.',
    status: 'active'
  }
];

export const demoTopics: Topic[] = [
  {
    id: 'topic-ai-product-discovery',
    title: 'AI product discovery',
    description: 'Как находить AI-B2B возможности через реальные workflow, интервью и ограничения внедрения.',
    purpose: 'Помогать AI PM выбирать не эффектные демо, а проверяемые продуктовые гипотезы.',
    audienceValue: 'Читатель получает способ понять, где AI действительно меняет рабочий процесс.',
    authorStance: 'Discovery начинается с bottleneck, риска и поведения пользователя, а не с выбора модели.',
    rules: ['Начинать с наблюдения из workflow', 'Показывать trade-off между скоростью и качеством', 'Заканчивать проверяемым критерием'],
    forbiddenAngles: ['model-first hype', 'обещания универсальной автоматизации'],
    weightRange: { min: 20, max: 30 },
    status: 'active'
  },
  {
    id: 'topic-evals-quality-loop',
    title: 'Evals & quality loop',
    description: 'Evals как продуктовая функция, а не внутренняя таблица ML-команды.',
    purpose: 'Показывать, как качество AI-фичи становится видимым для команды и пользователя.',
    audienceValue: 'Читатель понимает, какие проверки нужны до rollout и после него.',
    authorStance: 'Без evals, failure modes и ownership AI-фича остается демо.',
    rules: ['Называть критерий качества', 'Отделять product evals от offline benchmark', 'Показывать владельца проверки'],
    forbiddenAngles: ['абстрактные benchmark без связи с пользователем'],
    weightRange: { min: 20, max: 30 },
    status: 'active'
  },
  {
    id: 'topic-enterprise-trust-rollout',
    title: 'Enterprise trust & rollout',
    description: 'Доверие, rollback, explainability и границы уверенности в enterprise AI.',
    purpose: 'Разобрать, почему enterprise adoption требует доказательств и безопасного отката.',
    audienceValue: 'Читатель видит, что доверие проектируется как часть продукта.',
    authorStance: 'Enterprise users принимают AI через evidence, control и понятную ответственность.',
    rules: ['Показывать источник доверия', 'Объяснять rollback path', 'Не скрывать uncertainty'],
    forbiddenAngles: ['магическое доверие к модели', 'AI как черный ящик без ответственности'],
    weightRange: { min: 15, max: 25 },
    status: 'active'
  },
  {
    id: 'topic-gtm-adoption-economics',
    title: 'GTM/adoption economics',
    description: 'Как AI-фича проходит путь от пилота к регулярному использованию и экономике внедрения.',
    purpose: 'Связать продуктовую ценность AI с adoption, retention и операционными затратами.',
    audienceValue: 'Читатель получает язык для разговора с founders, CPO и sales без demo magic.',
    authorStance: 'Пилот ценен только если понятны adoption ritual, cost of operation и метрика результата.',
    rules: ['Отделять vanity usage от настоящего adoption', 'Показывать экономику эксплуатации', 'Не обещать headcount cuts первым тезисом'],
    forbiddenAngles: ['продажи через страх увольнений', 'ROI без операционных допущений'],
    weightRange: { min: 15, max: 25 },
    status: 'active'
  },
  {
    id: 'topic-workflow-automation-architecture',
    title: 'Workflow automation architecture',
    description: 'Архитектура AI workflow: human-in-loop, escalation, observability, ownership.',
    purpose: 'Показывать, из каких контуров состоит надежная AI-автоматизация.',
    audienceValue: 'Читатель получает практическую карту проектирования AI workflow.',
    authorStance: 'AI автоматизирует не задачу в вакууме, а контур принятия решений с проверками.',
    rules: ['Рисовать контур решения', 'Указывать человека в петле', 'Фиксировать failure mode'],
    forbiddenAngles: ['полная автономия без контроля', 'замена процесса одной кнопкой'],
    weightRange: { min: 10, max: 20 },
    status: 'active'
  }
];

export const demoFabulas: Fabula[] = [
  {
    id: 'fabula-research-note',
    title: 'Исследовательская заметка',
    description: 'Наблюдение из практики, которое превращается в аккуратный продуктовый вывод.',
    dramaturgy: 'От конкретного наблюдения к принципу, который можно проверить в своем продукте.',
    structure: ['Сцена или сигнал', 'Что в нем неочевидно', 'Продуктовый принцип', 'Как проверить у себя'],
    proofRequirements: ['Авторская заметка', 'Минимум один пример из интервью или пилота'],
    rules: ['Держать тон исследования', 'Не превращать вывод в чеклист без позиции'],
    weightRange: { min: 25, max: 35 },
    sizeIntent: 'standard',
    researchStrategy: {
      mode: 'manual',
      instructions: [
        'найти: публичные кейсы или интервью, где AI-фича ломается после демо на этапе adoption',
        'проверить: свежие наблюдения про evals, trust loop и workflow improvement',
        'не использовать: vendor blogs без независимых данных'
      ]
    },
    status: 'active'
  },
  {
    id: 'fabula-myth-breakdown',
    title: 'Разбор мифа',
    description: 'Пост, который разбирает популярное заблуждение об AI-B2B продуктах.',
    dramaturgy: 'Сначала формулируется миф, затем показывается, где он ломается в реальном workflow.',
    structure: ['Миф', 'Почему он кажется правдой', 'Где ломается', 'Более точная формулировка'],
    proofRequirements: ['Контрпример', 'Риск для продукта или GTM'],
    rules: ['Не высмеивать аудиторию', 'Давать замену мифу'],
    weightRange: { min: 15, max: 25 },
    sizeIntent: 'standard',
    researchStrategy: { mode: 'auto', instructions: [] },
    status: 'active'
  },
  {
    id: 'fabula-practical-framework',
    title: 'Практический фреймворк',
    description: 'Схема или набор вопросов для PM/founder, который проектирует AI-фичу.',
    dramaturgy: 'От проблемы к рабочему фреймворку с критериями проверки.',
    structure: ['Когда применять', '3-5 элементов фреймворка', 'Как проверить', 'Что может пойти не так'],
    proofRequirements: ['Связь с темой', 'Минимум один failure mode'],
    rules: ['Фреймворк должен быть применим за один рабочий созвон', 'Не добавлять декоративные шаги'],
    weightRange: { min: 20, max: 30 },
    sizeIntent: 'deep',
    researchStrategy: { mode: 'auto', instructions: [] },
    status: 'active'
  },
  {
    id: 'fabula-pilot-postmortem',
    title: 'Postmortem пилота',
    description: 'Разбор провала или риска AI-пилота без обвинений и задним числом.',
    dramaturgy: 'Что обещали, что произошло, какой системный урок забрать.',
    structure: ['Контекст пилота', 'Ожидание', 'Разрыв', 'Причина', 'Урок для следующего запуска'],
    proofRequirements: ['Сигнал из источника', 'Проверяемый урок'],
    rules: ['Не раскрывать приватные детали', 'Фокусироваться на системе, а не на виноватых'],
    weightRange: { min: 10, max: 20 },
    sizeIntent: 'standard',
    researchStrategy: { mode: 'auto', instructions: [] },
    status: 'active'
  },
  {
    id: 'fabula-position-manifesto',
    title: 'Позиционный манифест',
    description: 'Сильный авторский тезис о том, как надо строить AI-B2B продукты.',
    dramaturgy: 'От несогласия с рынком к ясной авторской позиции и критерию качества.',
    structure: ['С чем не согласен', 'Почему это важно', 'Моя позиция', 'Критерий для читателя'],
    proofRequirements: ['Evidence из памяти автора', 'Ограничения тезиса'],
    rules: ['Позиция должна быть острой, но не декларативной', 'Добавлять границы применимости'],
    weightRange: { min: 10, max: 20 },
    sizeIntent: 'compact',
    researchStrategy: {
      mode: 'manual',
      instructions: [
        'найти: сильные публичные позиции практиков, которые спорят с AI-first подходом',
        'проверить: внешние данные или кейсы про ограничения тезиса'
      ]
    },
    status: 'active'
  }
];
