import { mapWorkspaceSectionToProductionScope } from '../application/contextChat';
import type {
  ContextChatActionType,
  ContextChatIntent,
  ContextChatMessage,
  ContextChatScope
} from '../application/contextChat';
import type { WorkspaceSection } from '../domain/editorialWorkspace';
import type { MemoryInternalTab } from '../features/author-memory/types';
import type { EditorialModelTab } from '../features/editorial-model/types';

export type ContextChatTab = 'chat' | 'suggestions';

export function getContextChatScope(
  active: WorkspaceSection,
  memoryTab: MemoryInternalTab,
  editorialTab: EditorialModelTab
): ContextChatScope {
  if (active === 'memory') {
    if (memoryTab === 'sources') return 'sources';
    if (memoryTab === 'queue') return 'importQueue';
    if (memoryTab === 'archive') return 'archive';
    return 'memory';
  }

  if (active === 'editorialModel') {
    if (editorialTab === 'topics') return 'topics';
    if (editorialTab === 'fabulas') return 'fabulas';
    if (editorialTab === 'matrix') return 'matrix';
    return 'editorialPublisher';
  }

  return mapWorkspaceSectionToProductionScope(active);
}

export function contextChatScopeLabel(scope: ContextChatScope): string {
  const labels: Record<ContextChatScope, string> = {
    memory: 'Память автора · мысли и корректировки',
    sources: 'Память автора · источники',
    importQueue: 'Память автора · очередь разбора',
    archive: 'Память автора · архив',
    editorialPublisher: 'Редакционная модель · издательство',
    topics: 'Редакционная модель · темы',
    fabulas: 'Редакционная модель · фабулы',
    matrix: 'Редакционная модель · матрица',
    production: 'Производство поста · HITL flow',
    release: 'Выпуск · manual export',
    analytics: 'Аналитика · learning note'
  };
  return labels[scope];
}

export function contextChatRoleLabel(role: ContextChatMessage['role']): string {
  if (role === 'author') return 'Вы';
  if (role === 'system') return 'Система';
  return 'Помощник';
}

export function contextChatActionLabel(actionType: ContextChatActionType): string {
  const labels: Record<ContextChatActionType, string> = {
    addEditorialRule: 'Добавить правило',
    addTopic: 'Создать черновик темы',
    addFabula: 'Создать черновик фабулы',
    runValidation: 'Проверить',
    readOnly: 'Принять к сведению'
  };
  return labels[actionType];
}
