import { describe, expect, it } from 'vitest';
import {
  getActiveWorkspace,
  selectPortfolioProject,
  selectPortfolioUser,
  updateActiveProjectWorkspace
} from '../application/portfolioService';
import type { AuthorNote } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { LEGACY_WORKSPACE_STORAGE_KEY, LocalPortfolioStore, PORTFOLIO_STORAGE_KEY } from './localPortfolioStore';

function createMemoryStorage(): Storage {
  const values = new Map<string, string>();

  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key: string) => values.get(key) ?? null,
    key: (index: number) => Array.from(values.keys())[index] ?? null,
    removeItem: (key: string) => {
      values.delete(key);
    },
    setItem: (key: string, value: string) => {
      values.set(key, value);
    }
  };
}

describe('LocalPortfolioStore', () => {
  it('loads a local demo portfolio with two users and three projects', () => {
    const store = new LocalPortfolioStore(createMemoryStorage());
    const portfolio = store.load();

    expect(portfolio.users).toHaveLength(2);
    expect(portfolio.projects.map((project) => project.title)).toEqual([
      'Опытный цех «Сборочная»',
      'Северная стена',
      'Главред: быть интересным'
    ]);
    expect(portfolio.activeUserId).toBe('user-founder-editor');
    expect(portfolio.activeProjectId).toBe('project-ai-design-patterns');
    expect(getActiveWorkspace(portfolio).projectProfile.name).toBe('Опытный цех «Сборочная»');
  });

  it('migrates a legacy singleton workspace into one project', () => {
    const storage = createMemoryStorage();
    const legacyWorkspace = {
      ...createDemoWorkspace(),
      projectProfile: { ...createDemoWorkspace().projectProfile, name: 'Legacy blog' }
    };
    storage.setItem(LEGACY_WORKSPACE_STORAGE_KEY, JSON.stringify(legacyWorkspace));
    const store = new LocalPortfolioStore(storage);
    const portfolio = store.load();

    expect(portfolio.users).toHaveLength(1);
    expect(portfolio.projects).toHaveLength(1);
    expect(portfolio.projects[0].title).toBe('Legacy blog');
    expect(getActiveWorkspace(portfolio).projectProfile.name).toBe('Legacy blog');
  });

  it('persists project workspace state without leaking it to another project', () => {
    const storage = createMemoryStorage();
    const store = new LocalPortfolioStore(storage);
    const note: AuthorNote = {
      id: 'note-project-isolation',
      type: 'thought',
      title: '',
      body: 'Only Sborochnaya should see this note.',
      sourceUrl: '',
      tags: ['isolation'],
      attachments: [],
      capturedAt: '2026-06-29T10:00:00.000Z'
    };
    const changed = updateActiveProjectWorkspace(store.load(), (workspace) => ({
      ...workspace,
      authorNotes: [note, ...workspace.authorNotes],
      updatedAt: '2026-06-29T10:00:00.000Z'
    }));

    store.save(changed);
    const kasha = selectPortfolioProject(store.load(), 'project-kasha-iz-topora');
    const aiDesign = selectPortfolioProject(store.load(), 'project-ai-design-patterns');

    expect(getActiveWorkspace(kasha).authorNotes.some((candidate) => candidate.id === note.id)).toBe(false);
    expect(getActiveWorkspace(aiDesign).authorNotes.some((candidate) => candidate.id === note.id)).toBe(true);
    expect(storage.getItem(PORTFOLIO_STORAGE_KEY)).toContain('project-ai-design-patterns');
  });

  it('switches users to an accessible project', () => {
    const store = new LocalPortfolioStore(createMemoryStorage());
    const switched = selectPortfolioUser(store.load(), 'user-product-editor');

    expect(switched.activeUserId).toBe('user-product-editor');
    expect(switched.activeProjectId).toBe('project-glavred-blog');
    expect(getActiveWorkspace(switched).projectProfile.name).toBe('Главред: быть интересным');
  });
});
