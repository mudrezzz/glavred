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

const projectId: DemoBenchmarkProjectId = 'project-kasha-iz-topora';

const severnayaStenaTopicFabulaCompatibility: Pick<TopicFabulaMatrixEntry, 'topicId' | 'fabulaId'>[] = [
  { topicId: 'stena-topic-client-relief', fabulaId: 'stena-fabula-fog-removal' },
  { topicId: 'stena-topic-deal-route', fabulaId: 'stena-fabula-fog-removal' },
  { topicId: 'stena-topic-rope-team', fabulaId: 'stena-fabula-fog-removal' },
  { topicId: 'stena-topic-lost-route', fabulaId: 'stena-fabula-failure-analysis' },
  { topicId: 'stena-topic-deal-route', fabulaId: 'stena-fabula-failure-analysis' },
  { topicId: 'stena-topic-belay', fabulaId: 'stena-fabula-failure-analysis' },
  { topicId: 'stena-topic-gear', fabulaId: 'stena-fabula-gear-check' },
  { topicId: 'stena-topic-belay', fabulaId: 'stena-fabula-gear-check' },
  { topicId: 'stena-topic-rope-team', fabulaId: 'stena-fabula-gear-check' },
  { topicId: 'stena-topic-client-relief', fabulaId: 'stena-fabula-route-note' },
  { topicId: 'stena-topic-deal-route', fabulaId: 'stena-fabula-route-note' },
  { topicId: 'stena-topic-lost-route', fabulaId: 'stena-fabula-route-note' },
  { topicId: 'stena-topic-belay', fabulaId: 'stena-fabula-checkpoint' },
  { topicId: 'stena-topic-client-relief', fabulaId: 'stena-fabula-checkpoint' },
  { topicId: 'stena-topic-gear', fabulaId: 'stena-fabula-checkpoint' },
  { topicId: 'stena-topic-deal-route', fabulaId: 'stena-fabula-climb-plan' },
  { topicId: 'stena-topic-rope-team', fabulaId: 'stena-fabula-climb-plan' },
  { topicId: 'stena-topic-belay', fabulaId: 'stena-fabula-climb-plan' }
];

export const severnayaStenaBenchmarkSeed: BenchmarkWorkspaceSeed = {
  projectProfile: {
    name: 'Северная стена',
    description:
      'Telegram blog about complex B2B deals as commercial climbs: route, rope team, gear, belay, CRM, RevOps and ABM.',
    setupStatus: 'needsReview'
  },
  editorialModel: {
    author:
      'Практик коммерциализации сложных технических B2B-продуктов на стыке продукта, продаж, product marketing, пресейла, внедрения и CRM-дисциплины. Пишет как участник небольшой быстрой команды, которая заходит в коммерческий туман, читает рельеф клиента, собирает маршрут, снаряжение и страховку. Не sales coach и не большой консалтинг, а спокойный и острый руководитель маршрута.',
    audience:
      'Фаундеры B2B-компаний, коммерческие директора, heads of sales, RevOps, product marketing и продуктовые команды, у которых сделки вязнут в ЛПР, закупках, CRM-хаосе и внутренней политике клиента.',
    positioning:
      'Северная стена показывает, как проводить сложные B2B-сделки через туман, закупки, ЛПР, CRM-хаос и внутреннюю политику клиента без консалтингового пафоса и без веры в героизм одного продавца. AI здесь - легкое снаряжение для account research, call review, CRM hygiene, материалов и аналитики, но не главный герой и не замена коммерческого суждения.',
    fabula:
      'Сложная продажа - это не воронка и не скрипт, а коммерческий маршрут. Побеждает не самый громкий продавец, а связка продаж, маркетинга и продукта, которая понимает рельеф клиента, несет правильное снаряжение и держит страховку на каждом этапе.',
    rubrics: [
      'Маршрут сделки',
      'Рельеф клиента',
      'Снаряжение',
      'Страховка',
      'Связка',
      'Потерянный маршрут'
    ],
    styleRules: [
      'Писать как полевые записки с восхождения: сцена, риск, рельеф, решение, вывод.',
      'Держать одну альпинистскую метафору: маршрут, связка, снаряжение, страховка, туман, срыв, базовый лагерь, штурм.',
      'Показывать боль сделки через конкретную ситуацию, а не через определение RevOps.',
      'Для полевой записки и практического разбора начинать с узнаваемой сцены сделки: зависшая сделка, мертвое КП, CRM-прогноз, закупочная развилка, уставший внутренний чемпион или потерянный ЛПР.',
      'Сохранять экспертность без McKinsey-тона: живо, иронично, жестко, но с рабочим инструментом на выходе.'
    ],
    forbiddenTopics: [
      'Пилотский жаргон и смешение метафор',
      'Консалтинговая методичка для студентов',
      'Мотивация сейлзов и разговоры о харизме вместо системы',
      'ИИ как магия вместо ускорителя уже понятной коммерческой дисциплины'
    ],
    goals: [
      'Привлекать клиентов, которым нужна управляемая система сложных B2B-продаж, а не очередной тренинг продаж.',
      'Объяснять, почему рынок дозрел до RevOps и когда компания уже переросла героические продажи на таланте отдельных сейлзов.',
      'Показывать, что сильная сложная продажа проектируется через процесс, доказательства, CRM, материалы, ABM, product marketing и связку продукта, продаж и маркетинга.',
      'Демонстрировать практическую экспертизу без образа тяжелого и дорогого консалтинга.',
      'Сделать блог местом, где читатель узнает свою боль и думает: эти люди уже были на моей стене.'
    ]
  },
  authorNotes: [
    note(
      'stena-note-route-not-funnel',
      'thought',
      'Сделка не зависает, она теряет маршрут',
      'Статус "КП отправлено" часто прячет срыв маршрута: закупка не понимает процедуру, финансы не видели экономики, ЛПР не берет риск, а внутренний чемпион устал тащить объяснение наверх.',
      ['route', 'complex-b2b', 'deal-risk'],
      '2026-07-02T11:00:00.000Z'
    ),
    note(
      'stena-note-rope-team',
      'thought',
      'Сложный B2B идет связкой',
      'Продажи, маркетинг, продукт и внедрение должны идти в одной связке. Если маркетинг создает лиды без доверия, продукт говорит функциями, а продажи одни несут риск сделки, группа дергает веревку в разные стороны.',
      ['rope-team', 'revops', 'product-marketing'],
      '2026-07-02T11:15:00.000Z'
    ),
    note(
      'stena-note-gear',
      'manualCorrection',
      'Материалы продаж - это снаряжение, а не красота',
      'КП, one-pager, демо, battlecard и account brief нужны не для презентабельности. Они должны помогать пройти рельеф клиента: инженерный риск, закупку, финансы, роли, следующий шаг и критерии внедрения.',
      ['sales-enablement', 'gear', 'materials'],
      '2026-07-02T11:30:00.000Z'
    ),
    note(
      'stena-note-belay',
      'thought',
      'CRM должна быть страховкой маршрута',
      'CRM полезна только тогда, когда фиксирует критерии этапа, следующий шаг, риск, владельца и доказательство движения. Иначе это журнал восхождения, который заполняют после того, как группа уже сорвалась.',
      ['crm', 'belay', 'forecast'],
      '2026-07-02T11:45:00.000Z'
    ),
    note(
      'stena-note-ai-light-gear',
      'linkReaction',
      'ИИ - легкое снаряжение, а не автопилот',
      'ИИ ускоряет разбор звонков, account brief, подготовку материалов, CRM hygiene и аналитику. Но если маршрута нет, он просто быстрее производит коммерческий хаос.',
      ['ai', 'revops', 'light-gear'],
      '2026-07-02T12:00:00.000Z',
      'https://t.me/minqly'
    )
  ],
  editorialRules: [
    rule(
      'stena-rule-author-field-practitioner',
      'author',
      'Автор как руководитель маршрута',
      'Автор пишет как практик коммерциализации сложных технических B2B-продуктов на стыке продукта, продаж, product marketing, пресейла, внедрения и CRM-дисциплины. Он не sales coach и не большой консалтинг, а спокойный и острый руководитель маршрута, который уже ходил по таким стенам.'
    ),
    rule(
      'stena-rule-audience-commercial-fog',
      'audience',
      'Писать для тех, кто живет в коммерческом тумане',
      'Основная аудитория: B2B-фундеры, коммерческие директора, heads of sales, RevOps, product marketing и продуктовые команды, у которых сделки вязнут в ЛПР, закупках, CRM-хаосе, экономике внедрения и внутренней политике клиента.'
    ),
    rule(
      'stena-rule-goal-client-attraction',
      'goal',
      'Привлекать клиентов через видимую экспертизу',
      'Каждый материал должен показывать, что команда умеет превращать сложную B2B-продажу в управляемый маршрут: с ролями клиента, экономикой, материалами, CRM, ABM, продуктовой ценностью и страховкой на каждом участке.'
    ),
    rule(
      'stena-rule-goal-revops-maturity',
      'goal',
      'Объяснять зрелость рынка для RevOps',
      'Посты должны показывать, когда компания уже переросла героические продажи на таланте отдельных сейлзов и ей нужна повторяемая коммерческая система на стыке продаж, маркетинга и продукта.'
    ),
    rule(
      'stena-rule-goal-sales-engineering',
      'goal',
      'Продвигать инженерию сложных продаж',
      'Материалы должны показывать продажи как проектируемую систему: маршрут, роли клиента, доказательства, материалы, CRM, ABM, продуктовую ценность и связь с внедрением.'
    ),
    rule(
      'stena-rule-goal-practical-team',
      'goal',
      'Создавать доверие к небольшой практичной команде',
      'Посты должны демонстрировать опытную, быструю и адекватную по стоимости команду, которая умеет входить в коммерческий туман без театра большого консалтинга.'
    ),
    rule(
      'stena-rule-single-metaphor',
      'styleLanguage',
      'Одна метафора: восхождение',
      'Использовать альпинистскую лексику как объяснительный инструмент, не смешивать ее с авиацией, военным жаргоном или generic business speak.'
    ),
    rule(
      'stena-rule-reader-pain',
      'styleVoice',
      'Начинать с узнаваемой боли',
      'Пост должен начинаться с ситуации, в которой founder, коммерческий директор или RevOps узнает свой туман: зависшая сделка, мертвое КП, CRM-прогноз, закупочная развилка.'
    ),
    rule(
      'stena-rule-system-not-hero',
      'positioning',
      'Система важнее героизма',
      'Главная позиция: сложные B2B-продажи надо проектировать как повторяемую систему, а не оставлять на харизме отдельных продавцов.'
    ),
    rule(
      'stena-rule-ai-light-gear',
      'positioning',
      'AI как легкое снаряжение',
      'AI допустим как ускоритель коммерческой операционки: account research, call review, CRM hygiene, материалы и аналитика. Но он не должен становиться главным героем и не заменяет коммерческое суждение команды.'
    ),
    rule(
      'stena-rule-no-student-handbook',
      'forbiddenTopic',
      'Не методичка',
      'Не писать учебные определения RevOps, ABM или CRM без сцены, ставки и практического вывода.'
    )
  ],
  topics: [
    topic(
      'stena-topic-deal-route',
      'Маршрут сделки',
      'Как сделка проходит через рынок, аккаунт, ЛПР, экономику, закупку, внедрение и обратную связь.',
      'Показать, что сделкой нужно управлять как маршрутом, а не как стадиями в CRM.',
      'Читатель видит, где конкретно его сделка теряет высоту: нет владельца риска, нет процедуры, нет экономики, нет следующего шага.',
      'Сделка не зависает сама: она остается без маршрута, снаряжения или страховки.'
    ),
    topic(
      'stena-topic-client-relief',
      'Рельеф клиента',
      'ЛПР, ЛВПР, закупки, финансы, инженерные риски, внутренняя политика и роли внутри корпоративного клиента.',
      'Учить смотреть на клиента как на рельеф, а не как на один контакт в CRM.',
      'Читатель получает карту препятствий и понимает, почему хороший демо-звонок не гарантирует движение сделки.',
      'В сложном B2B продают не контакту, а внутренней системе принятия решения.'
    ),
    topic(
      'stena-topic-gear',
      'Снаряжение продаж',
      'КП, one-pager, battlecards, discovery scripts, account brief, демо и материалы для разных ролей клиента.',
      'Показать, какие материалы реально помогают команде идти по маршруту.',
      'Читатель понимает, чем рабочее КП отличается от красивого PDF и почему материалы должны вести клиента к следующему шагу.',
      'Материалы продаж должны работать как снаряжение: снижать риск, помогать двигаться и держать смысл в связке.'
    ),
    topic(
      'stena-topic-belay',
      'Страховка RevOps',
      'CRM-дисциплина, BANT+, критерии этапов, forecast, pipeline hygiene, контроль обещаний и next step.',
      'Объяснить RevOps как страховочную систему сложных сделок.',
      'Читатель получает не модный термин, а проверочные вопросы: где у нас нет страховки и почему прогноз врет.',
      'RevOps нужен там, где продажи, маркетинг и продукт перестали держать общий коммерческий маршрут.'
    ),
    topic(
      'stena-topic-rope-team',
      'Связка продаж, маркетинга и продукта',
      'ABM, Power Web, product marketing, продуктовая ценность, пресейл, внедрение и обратная связь как единая коммерческая связка.',
      'Показать, почему сложная продажа срывается, когда продажи, маркетинг и продукт идут разными маршрутами.',
      'Читатель видит, какие материалы, сигналы и роли должны соединять отделы, чтобы клиент двигался дальше.',
      'Коммерческий маршрут держится не на одном сейлзе, а на связке функций, которые несут одну карту ценности.'
    ),
    topic(
      'stena-topic-lost-route',
      'Потерянный маршрут',
      'Зависшие сделки, мертвые КП, неверный forecast, забытые next steps и postmortem после потерь.',
      'Разбирать срывы без охоты на виноватых: где маршрут потеряли, какую страховку не поставили и что менять в системе.',
      'Читатель получает язык для честного разбора провалов и превращает loss review в следующий рабочий маршрут.',
      'Проигранная сделка полезна, если из нее достали рельеф, снаряжение и контрольные точки для следующего восхождения.'
    )
  ],
  fabulas: [
    fabula(
      'stena-fabula-fog-removal',
      'Разогнать туман',
      'Пост, который начинается с узнаваемой коммерческой неясности и превращает ее в карту рельефа и следующий шаг.',
      'Боль -> скрытый рельеф -> карта -> контрольная точка -> следующий шаг.',
      ['Узнаваемая боль', 'Что на самом деле скрыто в тумане', 'Карта рельефа', 'Что проверить завтра'],
      ['Сцена из сделки или публичный кейс', 'Один проверочный критерий'],
      'standard',
      'standard',
      'manual',
      [
        'начать с узнаваемой боли сделки, а не с определения термина',
        'держать альпинистскую метафору без декоративности',
        'не уходить в generic sales advice',
        'обязательно показать ставку сделки и следующий шаг'
      ]
    ),
    fabula(
      'stena-fabula-failure-analysis',
      'Разбор сорвавшегося восхождения',
      'Разбор зависшей или проигранной сделки без поиска виноватых: где команда потеряла маршрут и какую страховку надо было поставить.',
      'Сбой -> ошибка маршрута -> недостающее снаряжение или страховка -> исправление системы.',
      ['Сцена срыва', 'Где потеряли маршрут', 'Чего не было в системе', 'Какую страховку поставить', 'Что не повторять'],
      ['Sanitized case, loss review or author memory', 'Конкретная причина срыва'],
      'standard',
      'standard',
      'manual',
      [
        'не обвинять сейлзов в слабости',
        'показывать системную причину срыва',
        'заканчивать поправкой к маршруту, CRM, материалам или ролям'
      ]
    ),
    fabula(
      'stena-fabula-gear-check',
      'Проверка снаряжения',
      'Разбор одного инструмента, материала, процесса или AI-ускорителя под нагрузкой сложной сделки.',
      'Инструмент -> нагрузка маршрута -> где помогает -> где не поможет -> критерий применения.',
      ['Что проверяем', 'Какая нагрузка сделки', 'Где выдерживает', 'Где не спасает', 'Правило применения'],
      ['Пример из сложной сделки', 'Критерий применимости', 'Ограничение инструмента'],
      'standard',
      'light',
      'manual'
    ),
    fabula(
      'stena-fabula-route-note',
      'Полевая записка с маршрута',
      'Живая заметка из одной сцены: что увидели на маршруте, какой принцип достали и какой практический ход стоит забрать.',
      'Сцена -> наблюдение -> принцип -> практический ход.',
      ['Сцена', 'Наблюдение', 'Что это значит для маршрута', 'Что сделать команде'],
      ['Авторская память или sanitized case', 'Один практический критерий'],
      'standard',
      'standard',
      'manual',
      [
        'сохранять живой голос',
        'не превращать сцену в учебник',
        'оставлять читателю один рабочий ход'
      ]
    ),
    fabula(
      'stena-fabula-checkpoint',
      'Контрольная точка',
      'Диагностический пост: по каким признакам понять, что маршрут, рельеф, снаряжение или страховка не готовы.',
      'Чеклист -> признаки риска -> вопросы -> действие.',
      ['Что проверяем', 'Три-пять признаков риска', 'Вопросы команде', 'Какой следующий шаг'],
      ['Практические критерии', 'Связь с CRM/материалами/ролями'],
      'deep',
      'standard',
      'manual'
    ),
    fabula(
      'stena-fabula-climb-plan',
      'План восхождения',
      'Большой разбор коммерческого маршрута: роли, материалы, рельеф клиента, RevOps-контроли и риски внедрения.',
      'Базовый лагерь -> рельеф -> связка -> снаряжение -> страховка -> штурм -> урок.',
      ['Контекст рынка', 'Карта маршрута', 'Роли и риски', 'Материалы', 'CRM/RevOps', 'Что брать в следующий маршрут'],
      ['Несколько источников или sanitized case', 'Явные риски переноса'],
      'deep',
      'marketResearch',
      'manual',
      ['использовать для больших разборов рынка, ABM или сложных B2B-кейсов']
    )
  ],
  radars: [
    radar(
      'stena-radar-author-memory',
      'Память автора: коммерческие маршруты',
      'Искать повторяющиеся мысли про сложные сделки, ЛПР, закупки, CRM, материалы, RevOps, ABM и потери маршрута.',
      'Author memory and sanitized project materials.'
    ),
    radar(
      'stena-radar-practice-cases',
      'Полевые кейсы сложных B2B-продаж',
      'Искать практические кейсы, где видно, как сделка идет через роли, закупку, экономику, внедрение и CRM-дисциплину.',
      'Public RevOps, ABM, enterprise sales and product marketing cases.'
    ),
    radar(
      'stena-radar-ai-revops',
      'AI как легкое снаряжение RevOps',
      'Искать примеры, где AI ускоряет account research, call review, CRM hygiene, sales materials or pipeline analytics without replacing commercial judgment.',
      'Public AI-for-sales/RevOps examples and author-validated notes.'
    )
  ],
  sourceSignals: [
    signal(
      'stena-signal-lost-route',
      'Route failure',
      'Сделка не зависла. Она потеряла маршрут',
      'Sanitized complex B2B sales support deck',
      'Сложная продажа проходит через проблему, экономику, ЛПР, процесс, ТКП, закупку и внедрение. Если команда видит только "КП отправлено", она не видит рельеф сделки.',
      'Первый benchmark-пост должен начинаться со сцены: в CRM стоит "КП отправлено", а внутри клиента уже идут закупка, финансы, инженерный риск и усталый чемпион.',
      'stena-topic-lost-route',
      'stena-fabula-failure-analysis'
    ),
    signal(
      'stena-signal-five-questions',
      'Route map',
      'Пять вопросов, которые превращают продукт в коммерческий маршрут',
      'Sanitized RevOps and product commercialization materials',
      'Клиент, ценность, сделка, материалы и измерение дают карту того, где коммерческая система проседает.',
      'Использовать как практичный пост без учебника: пять вопросов как контрольные точки маршрута, а не как чеклист ради чеклиста.',
      'stena-topic-belay',
      'stena-fabula-checkpoint'
    ),
    signal(
      'stena-signal-gear',
      'Sales gear',
      'КП как снаряжение, а не красивый PDF',
      'Sanitized team materials and sales enablement notes',
      'Материалы должны помогать разным ролям клиента пройти следующий участок: инженерный риск, экономику, закупку, внедрение и внутреннее согласование.',
      'Сделать пост о том, почему КП без закупочной развилки и карты ролей оставляет сделку без страховки.',
      'stena-topic-gear',
      'stena-fabula-gear-check'
    ),
    signal(
      'stena-signal-ai-light-gear',
      'AI accelerator',
      'AI как легкое снаряжение RevOps',
      'Author-validated Minqly-style memory and sanitized team practice',
      'AI полезен для account brief, разбора звонков, CRM hygiene, материалов и аналитики, но только если маршрут уже описан.',
      'Пост должен не уходить в AI-хайп: показать, что AI облегчает рюкзак, но не выбирает маршрут за группу.',
      'stena-topic-belay',
      'stena-fabula-gear-check'
    )
  ],
  externalSources: [
    externalSource(
      'stena-source-b2b-sales-deck',
      'Sanitized complex B2B sales support deck',
      'document',
      'Private user-provided team material paraphrased into public-safe fixture notes about market, value, sales process, CRM, education and analytics.'
    ),
    externalSource(
      'stena-source-author-channel',
      'Author-validated Minqly channel',
      'blogSite',
      'Public Telegram channel used for author-memory inspiration and tone validation, not as copied post source: https://t.me/minqly'
    ),
    externalSource(
      'stena-source-revops-public-cases',
      'Public RevOps and ABM case queue',
      'blogSite',
      'Future reviewed queue for RevOps, ABM, enterprise sales, CRM discipline and product marketing cases.'
    )
  ],
  topicFabulaCompatibility: severnayaStenaTopicFabulaCompatibility,
  defaultPlatform: 'Telegram',
  defaultPublicationSizeProfileId: 'telegram-post',
  postsPerWeek: 3,
  readyScenario: {
    planId: 'stena-plan-lost-route',
    title: 'Сделка не зависла. Она потеряла маршрут',
    expectedEffect:
      'Написать живой Telegram-разбор сорвавшегося восхождения: показать, как статус "КП отправлено" скрывает потерянный маршрут через ЛПР, закупку, экономику и CRM-хаос, и какую RevOps-страховку надо поставить перед следующим подходом.',
    topicId: 'stena-topic-lost-route',
    fabulaId: 'stena-fabula-failure-analysis',
    sourceSignalId: 'stena-signal-lost-route',
    format: 'Telegram failure analysis'
  }
};

export function createSevernayaStenaPublicationChannels(): PublicationChannel[] {
  return [
    createPublicationChannel({
      id: 'channel-stena-telegram',
      projectId,
      platform: 'telegram',
      title: 'Telegram',
      handleOrUrl: '@north_wall_b2b',
      language: 'ru',
      role: 'primary',
      defaultPublicationSizeProfileId: 'telegram-post'
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
    rules: ['Начинать со сцены на маршруте', 'Показывать рельеф клиента', 'Заканчивать рабочей страховкой'],
    forbiddenAngles: ['generic sales advice', 'пилотский жаргон', 'консалтинговая методичка'],
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
    rules: ['Не терять альпинистскую метафору', 'Не превращать пост в учебник', 'Показывать ставку сделки'],
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
    sourceType: id.includes('practice') ? 'externalSource' : 'authorMemory',
    scope,
    rules: [{ id: `${id}-rule`, operator: 'and', negate: false, statement: ruleStatement, status: 'active' }],
    sources: [
      {
        id: `${id}-source`,
        type: id.includes('practice') ? 'openWeb' : 'manualSource',
        title: `${title} source`,
        value: scope,
        notes: 'Sanitized benchmark seed; private source documents are not committed.',
        status: 'active'
      }
    ],
    filters: [
      {
        id: `${id}-filter-route`,
        dimension: 'topics',
        enabled: true,
        mode: 'mustMatch',
        instruction:
          'Signal must help explain a complex B2B route, client relief, RevOps belay, sales gear, ABM or CRM discipline.'
      }
    ],
    sourceDiscoveryMode: 'specifiedAndAdditional',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-07-02T12:00:00.000Z',
    notes: 'Benchmark radar for Северная стена project rework.'
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
    capturedAt: '2026-07-02',
    summary,
    rawNote,
    radarId: 'stena-radar-author-memory',
    reviewStatus: 'approved',
    suggestedTopicId: topicId,
    suggestedFabulaId: fabulaId,
    suggestedValue: rawNote,
    duplicateRisk: 'low',
    searchNote: 'Sanitized benchmark signal from user-provided materials and project concept discussion.'
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
    lastCheckedAt: '2026-07-02',
    lastImportedAt: '',
    notes
  };
}
