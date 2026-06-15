import type {
  ContentPlanItem,
  EditorialLearningNote,
  FinalText,
  ReleasePackage
} from '../domain/editorialWorkspace';

export function createEditorialLearningNote(
  releasePackage: ReleasePackage,
  finalText: FinalText,
  contentPlanItem: ContentPlanItem | null
): EditorialLearningNote {
  if (releasePackage.status !== 'exported') {
    throw new Error('Editorial learning note can be created only after manual export.');
  }

  return {
    id: `learning-${releasePackage.id}`,
    releasePackageId: releasePackage.id,
    metricSnapshot: {
      views: 0,
      reactions: 0,
      comments: 0,
      saves: 0,
      leads: 0
    },
    observedResult: '',
    audienceReaction: '',
    workingTheses: '',
    trustRubrics: contentPlanItem?.format ?? '',
    qualityAudienceTopics: '',
    strongerVoice: finalText.title,
    repeatFormats: contentPlanItem?.format ?? '',
    seriesCandidates: '',
    status: 'draft',
    updatedAt: new Date().toISOString(),
    capturedAt: null
  };
}
