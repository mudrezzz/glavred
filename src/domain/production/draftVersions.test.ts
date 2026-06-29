import { describe, expect, it } from 'vitest';
import type { PostDraft } from './types';
import {
  addHumanCommentRevisionVersion,
  approveFinalText,
  normalizePostDraftVersions,
  reviseDraft,
  selectDraftVersion
} from './transitions';

describe('draft version transitions', () => {
  it('normalizes a legacy draft into machine v1', () => {
    const draft = normalizePostDraftVersions(makeDraft());

    expect(draft.version).toBe(1);
    expect(draft.activeVersionId).toBe('draft-1-v1');
    expect(draft.versions).toMatchObject([
      {
        id: 'draft-1-v1',
        versionNumber: 1,
        source: 'machineFinal',
        title: 'Machine title',
        body: 'Machine body'
      }
    ]);
  });

  it('creates immutable human and manual versions', () => {
    const draft = addHumanCommentRevisionVersion(makeDraft(), {
      title: 'Human title',
      body: 'Human body',
      editorComment: 'Make it sharper',
      revisionSummary: 'Strengthened the opening.',
      aiRunId: 'ai-human-1'
    });
    const edited = reviseDraft(draft, 'Manual body');

    expect(edited.versions?.map((version) => version.source)).toEqual([
      'machineFinal',
      'humanCommentRevision',
      'manualEdit'
    ]);
    expect(edited.versions?.[0].body).toBe('Machine body');
    expect(edited.versions?.[1]).toMatchObject({
      baseVersionId: 'draft-1-v1',
      editorComment: 'Make it sharper',
      aiRunId: 'ai-human-1'
    });
    expect(edited.body).toBe('Manual body');
  });

  it('can approve an earlier version and snapshot the human loop', () => {
    const human = addHumanCommentRevisionVersion(makeDraft(), {
      title: 'Human title',
      body: 'Human body',
      editorComment: 'Make it sharper'
    });
    const selected = selectDraftVersion(human, 'draft-1-v1');
    const final = approveFinalText(selected, {
      versionId: 'draft-1-v1',
      machineTrace: {
        draftRunId: 'run-1',
        traceStatus: 'available',
        finalQualityGate: { status: 'passed' },
        unresolvedRisks: ['minor tone risk']
      }
    });

    expect(final.draftVersionId).toBe('draft-1-v1');
    expect(final.versionNumber).toBe(1);
    expect(final.body).toBe('Machine body');
    expect(final.editorDecisionSnapshot).toMatchObject({
      selectedVersionId: 'draft-1-v1',
      selectedVersionNumber: 1,
      selectedVersionSource: 'machineFinal',
      machineFinalVersionId: 'draft-1-v1',
      humanRevisionCount: 1,
      manualEditCount: 0,
      machineTrace: {
        draftRunId: 'run-1',
        traceStatus: 'available'
      }
    });
    expect(final.editorDecisionSnapshot?.comments).toEqual([
      {
        versionId: 'draft-1-v2',
        versionNumber: 2,
        comment: 'Make it sharper'
      }
    ]);
  });
});

function makeDraft(): PostDraft {
  return {
    id: 'draft-1',
    briefId: 'brief-1',
    title: 'Machine title',
    body: 'Machine body',
    version: 1,
    status: 'draft',
    updatedAt: '2026-06-28T00:00:00.000Z',
    generation: {
      source: 'draftRun',
      aiRunId: 'ai-machine-1',
      draftRunId: 'run-1',
      provider: 'openrouter',
      model: 'writer-model',
      fallbackUsed: false,
      createdAt: '2026-06-28T00:00:00.000Z'
    }
  };
}
