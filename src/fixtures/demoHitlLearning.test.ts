import { describe, expect, it } from 'vitest';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import { createDemoWorkspace } from './demoWorkspace';

describe('seeded HITL learning demo scenario', () => {
  it('seeds versioned draft, final decision, quality checks and a pending learning note', () => {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: true });
    const workItem = workspace.editorialWorkItems.find((item) => item.draft?.id === 'demo-hitl-draft');
    const versions = workItem?.draft?.versions ?? [];
    const learningNote = workspace.authorNotes.find((note) => note.type === 'editorialLearning');

    expect(versions.map((version) => version.versionNumber)).toEqual([1, 2, 3, 4]);
    expect(versions[1]).toMatchObject({
      source: 'humanCommentRevision',
      editorComment: 'усиль авторскую позицию',
      qualityCheck: expect.objectContaining({
        status: 'passed',
        matchedCommentIntents: ['author stance']
      })
    });
    expect(versions[2]).toMatchObject({
      editorComment: 'добавь 3 критерия',
      qualityCheck: expect.objectContaining({
        status: 'warning',
        matchedCommentIntents: ['three criteria']
      })
    });
    expect(versions[3]).toMatchObject({
      source: 'manualEdit',
      editorComment: 'убери сухой отчетный тон'
    });
    expect(workItem?.finalText).toMatchObject({
      draftVersionId: 'demo-hitl-draft-v2',
      versionNumber: 2
    });
    expect(learningNote).toMatchObject({
      editorialLearning: expect.objectContaining({
        status: 'pendingReview',
        selectedVersionId: 'demo-hitl-draft-v2',
        rejectedVersionIds: ['demo-hitl-draft-v3', 'demo-hitl-draft-v4']
      })
    });
    expect(learningNote?.tags).toEqual(expect.arrayContaining([
      'author-stance',
      'tone',
      'structure',
      'comment-compliance'
    ]));
  });

  it('does not use the pending seeded learning note for inference until it is accepted', () => {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: true });
    const pendingAssertions = inferAuthorPositionAssertions(workspace.authorNotes, workspace.authorMemoryEvents);
    const acceptedNotes = workspace.authorNotes.map((note) =>
      note.type === 'editorialLearning' && note.editorialLearning
        ? { ...note, editorialLearning: { ...note.editorialLearning, status: 'accepted' as const } }
        : note
    );
    const acceptedAssertions = inferAuthorPositionAssertions(
      acceptedNotes,
      acceptedNotes.map((note) => createAuthorMemoryEvent(note))
    );

    expect(pendingAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.includes('editorial-learning'))).toBe(false);
    expect(acceptedAssertions.flatMap((assertion) => assertion.evidence).some((item) => item.noteId.includes('editorial-learning'))).toBe(true);
  });
});
