import type { WorkspaceSection } from '../domain/editorialWorkspace';

export type NavigationItem = {
  id: WorkspaceSection;
  icon: string;
  label: string;
  count?: string;
  disabled?: boolean;
};

export const NAV: NavigationItem[] = [
  { id: 'memory', icon: 'memory', label: 'Память автора' },
  { id: 'editorialModel', icon: 'model', label: 'Редакционная модель' },
  { id: 'signals', icon: 'radar', label: 'Сигналы' },
  { id: 'plan', icon: 'plan', label: 'План', count: '1' },
  { id: 'edit', icon: 'edit', label: 'Редактура' },
  { id: 'release', icon: 'release', label: 'Выпуск' },
  { id: 'analytics', icon: 'analytics', label: 'Аналитика' }
];

export const TITLES: Record<WorkspaceSection, [string, string]> = {
  memory: ['Память автора', 'Заметки -> позиция автора'],
  editorialModel: ['Редакционная модель', 'Правила и контекст блога'],
  signals: ['Сигналы', 'Радары -> сигналы -> кандидаты'],
  plan: ['План', 'HITL · Gate 1'],
  brief: ['Фабула поста', 'HITL · Gate 2'],
  edit: ['Редактура', 'HITL · Gate 3'],
  release: ['Выпуск', 'Manual export'],
  analytics: ['Аналитика', 'Редакционные выводы']
};
