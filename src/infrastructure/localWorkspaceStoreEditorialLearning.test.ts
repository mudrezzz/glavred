import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { normalizeWorkspace } from './localWorkspaceStore';

describe('local workspace store editorial learning notes', () => {
  it('normalizes legacy editorial learning notes without metadata as pending review', () => {
    const workspace = createDemoWorkspace();
    const loaded = normalizeWorkspace({
      ...workspace,
      authorNotes: [
        {
          ...workspace.authorNotes[0],
          id: 'editorial-learning-legacy',
          type: 'editorialLearning',
          title: 'Редакторское наблюдение',
          body: 'Автор выбрал раннюю версию после машинной правки.',
          tags: [],
          attachments: undefined as never,
          editorialLearning: undefined
        },
        ...workspace.authorNotes
      ]
    });

    expect(loaded.authorNotes[0]).toMatchObject({
      id: 'editorial-learning-legacy',
      type: 'editorialLearning',
      attachments: [],
      tags: expect.arrayContaining(['editorial-learning']),
      editorialLearning: {
        status: 'pendingReview',
        suggestedMemoryTakeaway: 'Автор выбрал раннюю версию после машинной правки.'
      }
    });
  });
});
