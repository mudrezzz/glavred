import type { DraftRunContextSnapshot } from '../application/draftRunContext';
import type { EditorialModel, PostBrief } from '../domain/editorialWorkspace';

export function createDraftRunRequestPayload(
  brief: PostBrief,
  editorialModel: EditorialModel,
  draftContext?: DraftRunContextSnapshot
) {
  return {
    brief: {
      id: brief.id,
      title: brief.title,
      rubric: brief.rubric,
      audience: brief.audience,
      thesis: brief.thesis,
      conflict: brief.conflict,
      authorPosition: brief.authorPosition,
      evidence: brief.evidence,
      examples: brief.examples,
      structure: brief.structure,
      cta: brief.cta,
      risks: brief.risks,
      sources: brief.sources
    },
    editorialModel: {
      audience: editorialModel.audience,
      styleRules: editorialModel.styleRules,
      forbiddenTopics: editorialModel.forbiddenTopics,
      goals: editorialModel.goals
    },
    ...(draftContext ? { draftContext } : {})
  };
}
