import { describe, expect, it } from 'vitest';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from './authorMemoryService';
import {
  updateEditorialLearningStatus,
  upsertEditorialLearningAuthorNote
} from './editorialLearningMemoryService';
import type { AuthorNote, FinalText, PostDraft } from '../domain/editorialWorkspace';

describe('editorial learning memory service', () => {
  it('creates one pending editorial learning note from a final editor decision', () => {
    const postDraft = makeDraft();
    const finalText = makeFinalText();

    const notes = upsertEditorialLearningAuthorNote([], postDraft, finalText);
    const secondPass = upsertEditorialLearningAuthorNote(notes, postDraft, finalText);

    expect(secondPass).toHaveLength(1);
    expect(secondPass[0]).toMatchObject({
      id: 'editorial-learning-final-draft-1',
      type: 'editorialLearning',
      tags: expect.arrayContaining(['editorial-learning', 'hitl', 'draft-version', 'author-stance'])
    });
    expect(secondPass[0].editorialLearning).toMatchObject({
      status: 'pendingReview',
      selectedVersionId: 'draft-1-v1',
      rejectedVersionIds: ['draft-1-v2'],
      humanRevisionCount: 1,
      manualEditCount: 0,
      comments: ['усиль авторскую позицию']
    });
    expect(secondPass[0].body).toContain('Что запомнить');
  });

  it('keeps pending learning notes out of author-position inference until accepted', () => {
    const [pendingNote] = upsertEditorialLearningAuthorNote([], makeDraft(), makeFinalText());
    const acceptedNote = updateEditorialLearningStatus([pendingNote], pendingNote.id, 'accepted')[0];

    const pendingAssertions = inferAuthorPositionAssertions([pendingNote], [createAuthorMemoryEvent(pendingNote)]);
    const acceptedAssertions = inferAuthorPositionAssertions([acceptedNote], [createAuthorMemoryEvent(acceptedNote)]);

    const pendingEvidenceCount = pendingAssertions.reduce((count, assertion) => count + assertion.evidence.length, 0);
    const acceptedEvidenceCount = acceptedAssertions.reduce((count, assertion) => count + assertion.evidence.length, 0);

    expect(pendingEvidenceCount).toBe(0);
    expect(acceptedEvidenceCount).toBeGreaterThan(0);
  });
});

function makeDraft(): PostDraft {
  return {
    id: 'draft-1',
    briefId: 'brief-1',
    title: 'Machine draft',
    body: 'Base body',
    version: 2,
    status: 'revised',
    updatedAt: '2026-06-29T09:00:00.000Z',
    generation: {
      source: 'draftRun',
      aiRunId: 'ai-run-1',
      draftRunId: 'draft-run-1',
      provider: 'openrouter',
      model: 'writer',
      fallbackUsed: false,
      createdAt: '2026-06-29T09:00:00.000Z'
    },
    versions: [
      {
        id: 'draft-1-v1',
        versionNumber: 1,
        source: 'machineFinal',
        title: 'Machine draft',
        body: 'Base body',
        draftRunId: 'draft-run-1',
        aiRunId: 'ai-run-1',
        createdAt: '2026-06-29T09:00:00.000Z'
      },
      {
        id: 'draft-1-v2',
        versionNumber: 2,
        source: 'humanCommentRevision',
        baseVersionId: 'draft-1-v1',
        title: 'Revision',
        body: 'Revision body',
        editorComment: 'усиль авторскую позицию',
        draftRunId: 'draft-run-1',
        aiRunId: 'ai-run-2',
        qualityCheck: {
          status: 'warning',
          commentComplianceStatus: 'passed',
          sourceIntegrityStatus: 'warning',
          publicProseStatus: 'passed',
          internalJargonLeaks: [],
          regressionWarnings: ['lost source marker'],
          matchedCommentIntents: ['author stance'],
          missedCommentIntents: [],
          summary: 'Авторская позиция усилена, но есть риск source marker.',
          attempts: []
        },
        createdAt: '2026-06-29T09:10:00.000Z'
      }
    ],
    activeVersionId: 'draft-1-v1'
  };
}

function makeFinalText(): FinalText {
  return {
    id: 'final-draft-1',
    draftId: 'draft-1',
    draftVersionId: 'draft-1-v1',
    versionNumber: 1,
    title: 'Machine draft',
    body: 'Base body',
    approvalStatus: 'approved',
    approvedAt: '2026-06-29T09:20:00.000Z',
    editorDecisionSnapshot: {
      id: 'editor-decision-draft-1-v1',
      draftId: 'draft-1',
      selectedVersionId: 'draft-1-v1',
      selectedVersionNumber: 1,
      selectedVersionSource: 'machineFinal',
      machineFinalVersionId: 'draft-1-v1',
      humanRevisionCount: 1,
      manualEditCount: 0,
      comments: [{ versionId: 'draft-1-v2', versionNumber: 2, comment: 'усиль авторскую позицию' }],
      machineTrace: {
        draftRunId: 'draft-run-1',
        traceStatus: 'available',
        unresolvedRisks: ['source marker risk']
      },
      createdAt: '2026-06-29T09:20:00.000Z'
    }
  };
}
