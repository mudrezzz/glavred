import type {
  EditorialRuleGroup,
  Fabula,
  Topic,
  ValidatorResult,
  WorkspaceSection,
  WorkspaceState
} from '../domain/editorialWorkspace';

export type ContextChatScope =
  | 'memory'
  | 'sources'
  | 'importQueue'
  | 'archive'
  | 'editorialPublisher'
  | 'topics'
  | 'fabulas'
  | 'matrix'
  | 'production'
  | 'release'
  | 'analytics';

export type ContextChatActionType = 'addEditorialRule' | 'addTopic' | 'addFabula' | 'runValidation' | 'readOnly';

export type ContextChatMessageRole = 'assistant' | 'author' | 'system';

export interface ContextChatMessage {
  id: string;
  role: ContextChatMessageRole;
  text: string;
  createdAt: string;
  suggestionId?: string;
}

export interface ContextChatSuggestion {
  id: string;
  scope: ContextChatScope;
  title: string;
  body: string;
  actionType: ContextChatActionType;
  payload?: ContextChatSuggestionPayload;
  status: 'new' | 'accepted' | 'readOnly';
}

export type ContextChatSuggestionPayload =
  | AddEditorialRulePayload
  | AddTopicPayload
  | AddFabulaPayload
  | RunValidationPayload;

export interface AddEditorialRulePayload {
  group: EditorialRuleGroup;
  title: string;
  statement: string;
}

export type AddTopicPayload = Partial<
  Pick<Topic, 'title' | 'description' | 'purpose' | 'audienceValue' | 'authorStance' | 'rules' | 'forbiddenAngles'>
>;

export type AddFabulaPayload = Partial<
  Pick<Fabula, 'title' | 'description' | 'dramaturgy' | 'structure' | 'proofRequirements' | 'rules'>
>;

export interface RunValidationPayload {
  reason: string;
}

export function createContextChatSuggestions(
  workspace: WorkspaceState,
  scope: ContextChatScope
): ContextChatSuggestion[] {
  const staleValidation = Boolean(
    workspace.editorialValidationRun &&
      workspace.editorialValidationRun.revision !== (workspace.editorialSetupRevision ?? 0)
  );
  const firstWeakValidator = workspace.editorialValidationRun?.results.find((result) => result.status !== 'green');

  switch (scope) {
    case 'editorialPublisher':
      return [
        staleValidation
          ? runValidationSuggestion(scope, 'После сохраненных изменений проверка устарела.')
          : publisherRuleSuggestion(firstWeakValidator),
        {
          id: 'publisher-read-model',
          scope,
          title: 'Сверить образ автора с памятью',
          body: 'Проверьте, что правила автора не спорят с evidence из памяти: workflow, evals, trust loop и adoption должны оставаться главной оптикой.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    case 'topics':
      return [
        {
          id: 'topic-add-trust-onboarding',
          scope,
          title: 'Добавить тему про trust onboarding',
          body: 'В модели много evidence про доверие и границы уверенности. Можно завести отдельную тему для внедрения AI-фич в enterprise-среде.',
          actionType: 'addTopic',
          payload: {
            title: 'AI trust onboarding',
            description: 'Как доводить AI-фичу до доверенного использования в enterprise workflow.',
            purpose: 'Помогать AI PM проектировать доверие, rollback и evidence до масштабирования.',
            audienceValue: 'Читатель получает практическую рамку внедрения AI без demo magic.',
            authorStance: 'Доверие строится через понятные границы уверенности, доказательства и управляемый откат.',
            rules: ['Показывать, где пользователь может проверить результат', 'Не обещать автономность без rollback'],
            forbiddenAngles: ['trust через маркетинговые заявления', 'магическая точность модели']
          },
          status: 'new'
        },
        topicCoverageSuggestion(workspace, scope)
      ];
    case 'fabulas':
      return [
        {
          id: 'fabula-add-rollout-postmortem',
          scope,
          title: 'Добавить фабулу postmortem внедрения',
          body: 'Для блога AI Product Manager полезна фабула, где автор разбирает, почему пилот не стал регулярным workflow.',
          actionType: 'addFabula',
          payload: {
            title: 'Postmortem внедрения',
            description: 'Разбор перехода от AI-пилота к регулярному использованию.',
            dramaturgy: 'Сначала обещание пилота, затем friction в workflow, после этого выводы для product design.',
            structure: ['Пилот выглядел успешным', 'Где сломался adoption', 'Что нужно было проверить раньше', 'Решение для следующего запуска'],
            proofRequirements: ['факт из интервью', 'симптом adoption friction', 'вывод для PM'],
            rules: ['Не искать виноватую модель', 'Заканчивать проверяемым изменением процесса']
          },
          status: 'new'
        },
        {
          id: 'fabula-check-fit',
          scope,
          title: 'Проверить применимость фабул',
          body: 'После добавления фабулы проверьте матрицу: не каждая драматургия одинаково подходит для discovery, rollout и GTM.',
          actionType: 'runValidation',
          payload: { reason: 'Проверить coverage фабул после изменений.' },
          status: 'new'
        }
      ];
    case 'matrix':
      return [
        runValidationSuggestion(scope, 'Матрица управляет тем, какие темы и фабулы могут попадать в план.'),
        {
          id: 'matrix-read-balance',
          scope,
          title: 'Не превращать матрицу в стоп-лист',
          body: 'Отключайте только действительно несовместимые пары. Иначе контент-план быстро потеряет разнообразие.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    case 'sources':
    case 'importQueue':
    case 'archive':
      return [
        {
          id: `${scope}-archive-boundary`,
          scope,
          title: 'Не смешивать архив и evidence',
          body: 'Неразобранные и archive-only материалы не меняют позицию автора. В память стоит принимать только то, что автор действительно подтверждает.',
          actionType: 'readOnly',
          status: 'readOnly'
        },
        {
          id: `${scope}-bulk-safety`,
          scope,
          title: 'Большие пачки вести в архив',
          body: 'Для 1000 постов безопаснее использовать bulk archive, а не усиливать авторскую модель без review.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    case 'release':
      return [
        {
          id: 'release-manual-check',
          scope,
          title: 'Проверить выпуск вручную',
          body: 'Перед export убедитесь, что CTA, источники и warnings просмотрены. Автопостинга в текущем слое нет.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    case 'analytics':
      return [
        {
          id: 'analytics-learning-note',
          scope,
          title: 'Зафиксировать редакционный вывод',
          body: 'Метрики вводятся вручную. Главное здесь не dashboard, а learning note: что сработало, где голос автора был сильнее, что развивать в серию.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    case 'memory':
      return [
        {
          id: 'memory-add-raw-thought',
          scope,
          title: 'Зафиксировать сырую мысль',
          body: 'Начните с неструктурированной реакции: что вас зацепило в теме AI-B2B, где вы не согласны с рынком, что хотите не потерять.',
          actionType: 'readOnly',
          status: 'readOnly'
        },
        {
          id: 'memory-correct-position',
          scope,
          title: 'Уточнить вывод системы',
          body: 'Если карточка в "Как система поняла автора" звучит неверно, используйте корректировку прямо из assertion или evidence.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
    default:
      return [
        {
          id: `${scope}-read-current`,
          scope,
          title: 'Двигаться через HITL',
          body: 'В этом разделе помощник пока только объясняет следующий безопасный шаг. Решение и утверждение остаются за автором.',
          actionType: 'readOnly',
          status: 'readOnly'
        }
      ];
  }
}

export function createInitialContextChatMessages(scope: ContextChatScope): ContextChatMessage[] {
  return [
    {
      id: `ctx-init-${scope}`,
      role: 'assistant',
      text: 'Я синхронизирован с текущим разделом и буду предлагать только безопасные действия. Ничего не сохраняю без вашего обычного "Сохранить".',
      createdAt: new Date().toISOString()
    }
  ];
}

export function mapWorkspaceSectionToProductionScope(section: WorkspaceSection): ContextChatScope {
  if (section === 'release') return 'release';
  if (section === 'analytics') return 'analytics';
  return 'production';
}

function publisherRuleSuggestion(firstWeakValidator?: ValidatorResult): ContextChatSuggestion {
  const validatorContext = firstWeakValidator
    ? ` Последняя проверка подсветила: ${firstWeakValidator.summary}`
    : '';

  return {
    id: 'publisher-add-anti-ai-rule',
    scope: 'editorialPublisher',
    title: 'Добавить anti-AI правило',
    body: `У автора уже есть позиция против demo magic. Ее стоит закрепить как валидируемое правило стиля.${validatorContext}`,
    actionType: 'addEditorialRule',
    payload: {
      group: 'antiAiPattern',
      title: 'Не заменять позицию AI-обобщением',
      statement: 'Каждый пост должен содержать авторский trade-off, evidence или ограничение применимости, а не стерильный общий совет.'
    },
    status: 'new'
  };
}

function topicCoverageSuggestion(workspace: WorkspaceState, scope: ContextChatScope): ContextChatSuggestion {
  const hasCoverageRisk = workspace.topics.some((topic) => {
    const enabled = workspace.topicFabulaMatrix.some((entry) => entry.topicId === topic.id && entry.enabled);
    return topic.status === 'active' && !enabled;
  });

  return hasCoverageRisk
    ? runValidationSuggestion(scope, 'Есть активная тема без совместимых фабул.')
    : {
        id: 'topic-read-balance',
        scope,
        title: 'Проверить веса тем',
        body: 'Диапазоны веса должны выражать редакционное ощущение, а не жесткий календарь. Сетка вещания позже сможет подсветить конфликт.',
        actionType: 'readOnly',
        status: 'readOnly'
      };
}

function runValidationSuggestion(scope: ContextChatScope, reason: string): ContextChatSuggestion {
  return {
    id: `${scope}-run-validation`,
    scope,
    title: 'Запустить проверку',
    body: reason,
    actionType: 'runValidation',
    payload: { reason },
    status: 'new'
  };
}
