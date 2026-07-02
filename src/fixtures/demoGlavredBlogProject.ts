import type {
  AuthorExternalSource,
  AuthorNote,
  EditorialRule,
  Fabula,
  RadarDefinition,
  SourceSignal,
  Topic,
  TopicFabulaMatrixEntry
} from '../domain/editorialWorkspace';
import type { PublicationChannel } from '../domain/publication-channels/types';
import { createPublicationChannel } from '../domain/publication-channels/transitions';
import type { BenchmarkWorkspaceSeed, DemoBenchmarkProjectId } from './demoBenchmarkPortfolio';

const projectId: DemoBenchmarkProjectId = 'project-glavred-blog';

const glavredBlogTopicFabulaCompatibility: Pick<TopicFabulaMatrixEntry, 'topicId' | 'fabulaId'>[] = [
  { topicId: 'glavred-topic-be-interesting', fabulaId: 'glavred-fabula-flat-draft' },
  { topicId: 'glavred-topic-before-after', fabulaId: 'glavred-fabula-flat-draft' },
  { topicId: 'glavred-topic-ai-without-flattening', fabulaId: 'glavred-fabula-flat-draft' },
  { topicId: 'glavred-topic-be-interesting', fabulaId: 'glavred-fabula-editorial-method' },
  { topicId: 'glavred-topic-editorial-system', fabulaId: 'glavred-fabula-editorial-method' },
  { topicId: 'glavred-topic-template-library', fabulaId: 'glavred-fabula-editorial-method' },
  { topicId: 'glavred-topic-editorial-system', fabulaId: 'glavred-fabula-inside-mechanism' },
  { topicId: 'glavred-topic-ai-without-flattening', fabulaId: 'glavred-fabula-inside-mechanism' },
  { topicId: 'glavred-topic-adoption-practice', fabulaId: 'glavred-fabula-inside-mechanism' },
  { topicId: 'glavred-topic-template-library', fabulaId: 'glavred-fabula-role-template' },
  { topicId: 'glavred-topic-adoption-practice', fabulaId: 'glavred-fabula-role-template' },
  { topicId: 'glavred-topic-be-interesting', fabulaId: 'glavred-fabula-role-template' },
  { topicId: 'glavred-topic-before-after', fabulaId: 'glavred-fabula-before-after' },
  { topicId: 'glavred-topic-ai-without-flattening', fabulaId: 'glavred-fabula-before-after' },
  { topicId: 'glavred-topic-editorial-system', fabulaId: 'glavred-fabula-before-after' },
  { topicId: 'glavred-topic-be-interesting', fabulaId: 'glavred-fabula-anti-pattern' },
  { topicId: 'glavred-topic-template-library', fabulaId: 'glavred-fabula-anti-pattern' },
  { topicId: 'glavred-topic-adoption-practice', fabulaId: 'glavred-fabula-anti-pattern' }
];

export const glavredBlogBenchmarkSeed: BenchmarkWorkspaceSeed = {
  projectProfile: {
    name: 'Главред: быть интересным',
    description: 'Telegram-first product philosophy blog about keeping author voice, thought and usefulness in AI-assisted content.',
    setupStatus: 'needsReview'
  },
  editorialModel: {
    author:
      'Создатель и продуктовый главред AI-native редакционной системы. Пишет не как продавец генератора постов, а как практик, который собирает редакционный цех: память автора, фабулы, источники, проверки, версии и человеческое решение.',
    audience:
      'Эксперты, консультанты, founders, маркетологи, дизайнеры, product marketing команды и небольшие B2B-команды, которым нужно регулярно звучать интересно, но которые не хотят превращать свой голос в усредненный AI-контент.',
    positioning:
      'Главред - это быть интересным. Продукт не обещает волшебную кнопку автопостинга: он снимает рутину, подносит материал, держит контекст и проверки, но оставляет автору позицию, вкус и финальное решение.',
    fabula:
      'Интересный AI-assisted текст рождается из редакционной системы: авторская память, тема, фабула, источники, роли моделей, quality gate, HITL-версии и наблюдения, которые потом возвращаются в память автора.',
    rubrics: [
      'Быть интересным',
      'Редакционная машина',
      'AI без обезличивания',
      'Библиотеки и шаблоны',
      'Разборы до/после',
      'Практика внедрения'
    ],
    styleRules: [
      'Писать как создатель продукта, который сам устал от плоского AI-контента и показывает рабочую редакционную альтернативу.',
      'Объяснять внутренние механики через человеческую боль: скучный черновик, потерянный голос, бесконечные правки, ручной поиск материала.',
      'Давать читателю готовый прием, шаблон, критерий или способ диагностики, а не только размышление о продукте.',
      'Технические термины Главреда переводить в редакционную пользу: зачем это автору, редактору или команде.'
    ],
    forbiddenTopics: [
      'Generic AI copywriting tips',
      'Обещание автопостинга без работы автора',
      'Релизные заметки о фичах без редакционной боли',
      'Внутренний trace dump вместо публичного объяснения',
      'Шаблон ради шаблона без ситуации применения'
    ],
    goals: [
      'Показывать философию Главреда: AI помогает быть интересным, а не просто писать быстрее.',
      'Привлекать авторов, экспертов и команды, которым нужен управляемый AI-assisted editorial workflow.',
      'Доказывать, что харизма автора сохраняется через память, фабулы, HITL и финальное человеческое решение.',
      'Создавать регулярные библиотеки и шаблоны для маркетолога, дизайнера, консультанта, founder и других авторских ролей.',
      'Готовить будущую Telegram + Dzen адаптацию одной идеи без потери авторской позиции.'
    ]
  },
  authorNotes: [
    note(
      'glavred-note-be-interesting',
      'thought',
      'Главред - это быть интересным',
      'Смысл продукта не в том, чтобы быстрее производить больше текстов. Смысл в том, чтобы автор с AI под рукой не стал плоским: сохранил нерв, позицию, опыт, примеры и право сказать "нет" последней машинной версии.',
      ['be-interesting', 'product-philosophy', 'author-voice'],
      '2026-07-03T09:00:00.000Z'
    ),
    note(
      'glavred-note-ai-routine',
      'thought',
      'AI должен подносить снаряды, а не командовать автором',
      'AI полезен, когда снимает рутину: поиск материала, сбор вариантов, проверку источников, черновые структуры, диагностику слабых мест. Но интересность текста остается редакционной задачей автора и системы.',
      ['ai-assisted', 'editorial-system', 'routine'],
      '2026-07-03T09:15:00.000Z'
    ),
    note(
      'glavred-note-not-prompt-game',
      'manualCorrection',
      'Промпты не заменяют редакционную систему',
      'Проблема не в том, что пользователь плохо написал промпт. Проблема в том, что без памяти автора, фабулы, источников, проверок и HITL даже хороший промпт быстро возвращает усредненный текст.',
      ['prompting', 'workflow', 'anti-pattern'],
      '2026-07-03T09:30:00.000Z'
    ),
    note(
      'glavred-note-template-library',
      'thought',
      'Библиотеки нужны как рабочие заготовки, не как мертвые шаблоны',
      'Шаблон полезен, если помогает автору быстрее собрать живой материал под свою ситуацию: консультант объясняет кейс, маркетолог формулирует позицию, дизайнер показывает решение, founder спорит с рынком.',
      ['templates', 'roles', 'practical-library'],
      '2026-07-03T09:45:00.000Z'
    ),
    note(
      'glavred-note-final-choice',
      'thought',
      'Последняя версия не обязана быть лучшей',
      'Редактор должен видеть версии, комментарии, проверки и риски, а потом выбрать любую версию как финальную. Иногда v1 честнее и сильнее, чем аккуратная v3.',
      ['hitl', 'versions', 'editorial-decision'],
      '2026-07-03T10:00:00.000Z'
    )
  ],
  editorialRules: [
    rule(
      'glavred-rule-author-product-editor',
      'author',
      'Автор как создатель редакционного цеха',
      'Автор пишет из позиции практика, который строит Главред как AI-native редакционную систему: показывает решения, сомнения, ограничения, ошибки и рабочие приемы, а не продает "генератор постов".'
    ),
    rule(
      'glavred-rule-audience-authors-teams',
      'audience',
      'Писать для тех, кому надо звучать интересно регулярно',
      'Основная аудитория: эксперты, консультанты, founders, маркетологи, дизайнеры и B2B-команды, у которых есть экспертиза, но регулярное превращение ее в сильный контент слишком дорого по времени.'
    ),
    rule(
      'glavred-rule-goal-interesting-content',
      'goal',
      'Доказывать, что AI может помогать быть интересным',
      'Каждый выпуск должен поддерживать центральную философию: Главред сохраняет голос автора и силу AI через управляемый редакционный контур.'
    ),
    rule(
      'glavred-rule-goal-practical-templates',
      'goal',
      'Создавать прикладные библиотеки и шаблоны',
      'Посты должны постепенно складываться в библиотеку приемов, шаблонов и разборов для разных авторских ролей: маркетолог, дизайнер, консультант, founder, эксперт.'
    ),
    rule(
      'glavred-rule-positioning-not-autoposter',
      'positioning',
      'Не обещать волшебную кнопку',
      'Главред - не простенький автопостер. Это работа с контекстом, памятью, источниками, фабулой и человеческим выбором, где система снимает рутину и делает качество управляемым.'
    ),
    rule(
      'glavred-rule-style-pain-first',
      'styleVoice',
      'Начинать с узнаваемой редакционной боли',
      'Пост должен входить через ситуацию: AI написал гладкий, но мертвый текст; автор устал от промптов; команда потеряла голос; шаблон не ложится на реальный опыт.'
    ),
    rule(
      'glavred-rule-style-jargon-to-benefit',
      'styleLanguage',
      'Внутренние термины переводить в пользу автора',
      'SourceLedger, finalQualityGate, HITL, revisionLoop и context pack можно упоминать только тогда, когда рядом объяснено, какую редакционную боль это снимает.'
    ),
    rule(
      'glavred-rule-anti-pattern-feature-marketing',
      'antiAiPattern',
      'Не превращать блог в релизные заметки',
      'Фича Главреда появляется в тексте только через боль и рабочий сценарий. Нельзя писать "мы добавили X" без ответа, почему это помогает автору быть интереснее.'
    )
  ],
  topics: [
    topic(
      'glavred-topic-be-interesting',
      'Быть интересным',
      'Почему AI-тексты становятся гладкими, безопасными и скучными, и как вернуть им нерв, конфликт, позицию и человеческую пользу.',
      'Сформулировать главную философию продукта.',
      'Читатель понимает, почему его проблема не в одном плохом промпте, а в отсутствии редакционной системы.',
      'Интересность - это не украшение текста, а управляемая редакционная задача.'
    ),
    topic(
      'glavred-topic-editorial-system',
      'Редакционная машина',
      'Как работают память автора, фабулы, источники, validation, final gate, версии и editor decision snapshot.',
      'Показывать устройство Главреда через пользу, а не через техдок.',
      'Читатель видит, какие части процесса снимают рутину и где остается человеческое решение.',
      'Качество появляется из контура, где каждый шаг оставляет артефакт и проверку.'
    ),
    topic(
      'glavred-topic-ai-without-flattening',
      'AI без обезличивания',
      'Как использовать модели так, чтобы они не усредняли голос автора и не превращали эксперта в корпоративный шум.',
      'Показать роль модели как помощника, а не автора вместо автора.',
      'Читатель получает критерии, где AI усиливает, а где начинает стирать голос.',
      'AI должен приносить материал и варианты, но не забирать позицию и вкус.'
    ),
    topic(
      'glavred-topic-template-library',
      'Библиотеки и шаблоны',
      'Готовые редакционные схемы для маркетолога, дизайнера, консультанта, founder и эксперта.',
      'Создавать reusable library, которую можно взять и адаптировать.',
      'Читатель уходит с практической заготовкой, а не с общей идеей.',
      'Шаблон хорош только тогда, когда оставляет место для живого материала автора.'
    ),
    topic(
      'glavred-topic-before-after',
      'Разборы до/после',
      'Публичные разборы слабого AI-черновика, редакционной правки и итогового решения.',
      'Учить видеть, что именно делает текст живым.',
      'Читатель получает язык диагностики: где плоскость, где позиция, где доказательство, где польза.',
      'Хороший разбор показывает механизм улучшения, а не просто "стало лучше".'
    ),
    topic(
      'glavred-topic-adoption-practice',
      'Практика внедрения',
      'Кому, когда и как помогает Главред: индивидуальному автору, небольшой команде, редактору, агентству или B2B-команде.',
      'Показывать реальные сценарии работы, ограничения и настройку процесса.',
      'Читатель понимает, как встроить систему в свою работу без обещания магии.',
      'Внедрение начинается с редакционной дисциплины, а не с кнопки генерации.'
    )
  ],
  fabulas: [
    fabula(
      'glavred-fabula-flat-draft',
      'Плоский черновик',
      'Разбор типичного AI-текста, который формально правильный, но неинтересный.',
      'Скучный AI-черновик -> где умер автор -> какая редакционная операция нужна -> обновленная версия -> принцип.',
      ['Черновик', 'Почему он мертвый', 'Что возвращает автора', 'Как меняется текст', 'Правило для следующего раза'],
      ['Фрагмент черновика или публично-безопасный пример', 'Явный критерий улучшения'],
      'standard',
      'light',
      'manual'
    ),
    fabula(
      'glavred-fabula-editorial-method',
      'Редакционный прием',
      'Один конкретный прием: позиция, контраст, сцена, напряжение, критерий, полезный шаблон.',
      'Боль -> прием -> пример -> как применить -> где не сработает.',
      ['Боль', 'Прием', 'Мини-пример', 'Инструкция применения', 'Ограничение'],
      ['Один практический пример', 'Явное ограничение приема'],
      'standard',
      'standard',
      'manual'
    ),
    fabula(
      'glavred-fabula-inside-mechanism',
      'Как устроено внутри',
      'Объяснить механику Главреда через редакционную проблему: память, фабула, источники, validation, gate, HITL.',
      'Проблема автора -> почему простой AI-подход ломается -> механизм Главреда -> что видит редактор -> что становится лучше.',
      ['Проблема', 'Почему один prompt не решает', 'Механизм', 'Польза для редактора', 'Ограничение'],
      ['Связь с реальным artifact/trace', 'Польза без internal dump'],
      'deep',
      'standard',
      'auto'
    ),
    fabula(
      'glavred-fabula-role-template',
      'Шаблон для роли',
      'Готовая заготовка для конкретного автора: маркетолог, дизайнер, консультант, founder, эксперт.',
      'Роль -> типовая боль -> шаблон -> как адаптировать -> пример первого выпуска.',
      ['Для кого', 'В какой ситуации', 'Шаблон', 'Как адаптировать под себя', 'Первый пример'],
      ['Четкая роль', 'Минимум один заполненный пример'],
      'standard',
      'light',
      'manual'
    ),
    fabula(
      'glavred-fabula-before-after',
      'До / после',
      'Показать путь от сырого материала или AI-черновика к сильному публичному тексту.',
      'Исходный материал -> машинная версия -> редакторское решение -> итог -> чему научились.',
      ['Исходник', 'Что сделал AI', 'Что поправил редактор', 'Итоговая версия', 'Урок'],
      ['Сравнимые фрагменты', 'Явное объяснение редакторского решения'],
      'standard',
      'standard',
      'manual'
    ),
    fabula(
      'glavred-fabula-anti-pattern',
      'Анти-паттерн',
      'Разобрать соблазнительный, но слабый способ работать с AI-контентом.',
      'Соблазн -> почему кажется разумным -> где ломается -> замена -> проверочный вопрос.',
      ['Соблазн', 'Почему так делают', 'Как ломается', 'Что делать вместо', 'Проверка'],
      ['Контрпример', 'Безопасная альтернатива'],
      'standard',
      'standard',
      'manual'
    )
  ],
  radars: [
    radar(
      'glavred-radar-product-philosophy',
      'Философия Главреда',
      'Искать сигналы о том, почему AI-контент становится плоским и как редакционная система возвращает интересность.',
      'Product notes, roadmap decisions, HITL diagnostics and final quality gate examples.'
    ),
    radar(
      'glavred-radar-template-library',
      'Библиотека шаблонов',
      'Искать повторяемые авторские роли и ситуации, где нужен практический шаблон: маркетолог, дизайнер, консультант, founder, эксперт.',
      'Author memory, product docs, user situations and demo feedback.'
    ),
    radar(
      'glavred-radar-before-after',
      'До/после и разборы',
      'Искать примеры, где AI-черновик формально правильный, но теряет голос, позицию или пользу.',
      'Demo DraftRun traces, HITL revisions and sanitized editorial examples.'
    )
  ],
  sourceSignals: [
    signal(
      'glavred-signal-flat-ai-content',
      'Product philosophy',
      'AI пишет быстро, но слишком часто получается гладко и неинтересно',
      'Product philosophy notes',
      'Главная боль автора: AI умеет писать текст, но без памяти автора, фабулы и human decision текст становится усредненным. Главред должен объяснять, как оставаться интересным, не возвращаясь к полностью ручному письму.',
      'Первый benchmark-пост должен показать, почему проблема не в плохом промпте, а в отсутствии редакционного контура.',
      'glavred-topic-be-interesting',
      'glavred-fabula-flat-draft'
    ),
    signal(
      'glavred-signal-author-memory',
      'Workflow principle',
      'Память автора нужна, чтобы модель не каждый раз начинала с нуля',
      'Author memory implementation notes',
      'Авторская память хранит не только факты, но и повторяющиеся решения: что автор считает важным, какие ходы отвергает, где голос должен звучать жестче или живее.',
      'Подходит для объяснения внутренней механики через пользу автора.',
      'glavred-topic-editorial-system',
      'glavred-fabula-inside-mechanism'
    ),
    signal(
      'glavred-signal-template-library',
      'Template library',
      'Маркетологу, дизайнеру и консультанту нужны разные редакционные заготовки',
      'Template library backlog',
      'Один и тот же AI-подход не подходит всем: консультанту нужен кейс и вывод, дизайнеру - решение и аргументация, маркетологу - позиция и доказательство.',
      'Можно сделать пост-библиотеку с первым набором шаблонов.',
      'glavred-topic-template-library',
      'glavred-fabula-role-template'
    ),
    signal(
      'glavred-signal-final-choice',
      'HITL principle',
      'Редактор может выбрать не последнюю версию',
      'HITL versioning notes',
      'Человеческий выбор важнее линейной веры в "еще одну итерацию". Иногда автор возвращается к v1, потому что она живее, а система должна сохранить этот сигнал.',
      'Подходит для поста о версиях, final decision и learning notes.',
      'glavred-topic-adoption-practice',
      'glavred-fabula-inside-mechanism'
    )
  ],
  externalSources: [
    externalSource(
      'glavred-source-product-docs',
      'Glavred product docs and roadmap',
      'document',
      'Current public-safe product docs, roadmap decisions and architecture notes about author memory, context packs, final quality gate and HITL.'
    ),
    externalSource(
      'glavred-source-demo-trace',
      'Demo DraftRun and HITL traces',
      'manualUpload',
      'Sanitized examples of validation, revision loop, final gate and human-comment quality checks.'
    ),
    externalSource(
      'glavred-source-template-backlog',
      'Role template backlog',
      'manualUpload',
      'Future library ideas for marketers, designers, consultants, founders and expert authors.'
    )
  ],
  topicFabulaCompatibility: glavredBlogTopicFabulaCompatibility,
  defaultPlatform: 'Telegram',
  defaultPublicationSizeProfileId: 'telegram-post',
  postsPerWeek: 2,
  readyScenario: {
    planId: 'glavred-plan-flat-ai-draft',
    title: 'Почему AI пишет гладко, но неинтересно',
    expectedEffect:
      'Написать Telegram-пост о философии Главреда: почему один prompt не спасает авторский голос, как редакционная система возвращает интересность, и какую работу все равно делает человек.',
    topicId: 'glavred-topic-be-interesting',
    fabulaId: 'glavred-fabula-flat-draft',
    sourceSignalId: 'glavred-signal-flat-ai-content',
    format: 'Telegram product philosophy note'
  }
};

export function createGlavredBlogPublicationChannels(): PublicationChannel[] {
  return [
    createPublicationChannel({
      id: 'channel-glavred-telegram',
      projectId,
      platform: 'telegram',
      title: 'Telegram',
      handleOrUrl: '@glavred_product',
      language: 'ru',
      role: 'primary',
      defaultPublicationSizeProfileId: 'telegram-post'
    }),
    createPublicationChannel({
      id: 'channel-glavred-dzen',
      projectId,
      platform: 'dzen',
      title: 'Дзен',
      handleOrUrl: 'dzen.ru/glavred',
      language: 'ru',
      role: 'experiment',
      defaultPublicationSizeProfileId: 'linkedin-article'
    })
  ];
}

function note(
  id: string,
  type: AuthorNote['type'],
  title: string,
  body: string,
  tags: string[],
  capturedAt: string,
  sourceUrl = ''
): AuthorNote {
  return { id, type, title, body, sourceUrl, tags, attachments: [], capturedAt };
}

function rule(id: string, group: EditorialRule['group'], title: string, statement: string): EditorialRule {
  return { id, group, title, statement, status: 'active' };
}

function topic(
  id: string,
  title: string,
  description: string,
  purpose: string,
  audienceValue: string,
  authorStance: string
): Topic {
  return {
    id,
    title,
    description,
    purpose,
    audienceValue,
    authorStance,
    rules: ['Начинать с редакционной боли', 'Показывать авторскую позицию', 'Давать применимый прием или критерий'],
    forbiddenAngles: ['generic AI advice', 'feature release note', 'internal jargon dump'],
    weightRange: { min: 20, max: 35 },
    status: 'active'
  };
}

function fabula(
  id: string,
  title: string,
  description: string,
  dramaturgy: string,
  structure: string[],
  proofRequirements: string[],
  sizeIntent: Fabula['sizeIntent'],
  researchDepth: Fabula['researchDepth'],
  researchMode: Fabula['researchStrategy']['mode'],
  instructions: string[] = []
): Fabula {
  return {
    id,
    title,
    description,
    dramaturgy,
    structure,
    proofRequirements,
    rules: ['Не терять боль автора', 'Не подменять вывод списком фич', 'Показывать человеческое решение'],
    weightRange: { min: 20, max: 35 },
    sizeIntent,
    researchDepth,
    researchStrategy: { mode: researchMode, instructions },
    status: 'active'
  };
}

function radar(id: string, title: string, ruleStatement: string, scope: string): RadarDefinition {
  return {
    id,
    title,
    sourceType: 'authorMemory',
    scope,
    rules: [{ id: `${id}-rule`, operator: 'and', negate: false, statement: ruleStatement, status: 'active' }],
    sources: [
      {
        id: `${id}-source`,
        type: 'manualSource',
        title: `${title} source`,
        value: scope,
        notes: 'Sanitized product benchmark seed; private product notes are not committed.',
        status: 'active'
      }
    ],
    filters: [
      {
        id: `${id}-filter-editorial-value`,
        dimension: 'topics',
        enabled: true,
        mode: 'mustMatch',
        instruction:
          'Signal must help explain how Glavred keeps author voice, editorial method, templates, HITL, or multi-platform readiness.'
      }
    ],
    sourceDiscoveryMode: 'specifiedAndAdditional',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-07-03T10:00:00.000Z',
    notes: 'Benchmark radar for the Glavred product philosophy blog.'
  };
}

function signal(
  id: string,
  type: string,
  title: string,
  source: string,
  summary: string,
  rawNote: string,
  topicId: string,
  fabulaId: string
): SourceSignal {
  return {
    id,
    type,
    title,
    source,
    capturedAt: '2026-07-03',
    summary,
    rawNote,
    radarId: 'glavred-radar-product-philosophy',
    reviewStatus: 'approved',
    suggestedTopicId: topicId,
    suggestedFabulaId: fabulaId,
    suggestedValue: rawNote,
    duplicateRisk: 'low',
    searchNote: 'Sanitized benchmark signal from product philosophy discussion and roadmap context.'
  };
}

function externalSource(
  id: string,
  title: string,
  type: AuthorExternalSource['type'],
  notes: string
): AuthorExternalSource {
  return {
    id,
    type,
    title,
    url: '',
    fileReference: '',
    status: 'needsReview',
    importMode: 'reviewedQueue',
    lastCheckedAt: '2026-07-03',
    lastImportedAt: '',
    notes
  };
}
