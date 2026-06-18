import type {
  AuthorExternalSource,
  AuthorMemoryEvent,
  AuthorNote,
  AuthorPositionAssertion,
  ImportedMemoryCandidate,
} from '../author-memory/types';
import type {
  EditorialModel,
  EditorialRule,
  EditorialValidationRun,
  Fabula,
  ProjectProfile,
  Topic,
  TopicFabulaMatrixEntry,
} from '../editorial-model/types';
import type { ArchiveRecord, BulkImportAction } from '../imports/types';
import type {
  ContentPlanItem,
  ContentPlanSettings,
  InsightCard,
  PlanWeightWarning,
} from '../planning/types';
import type { PostCandidate } from '../post-candidates/types';
import type {
  EditorialCheck,
  EditorialLearningNote,
  EditorialWorkItem,
  EditorNote,
  FinalText,
  PostBrief,
  PostDraft,
  PostVisual,
  ReleasePackage,
} from '../production/types';
import type { RadarDefinition, SourceSignal } from '../signals/types';

// WorkspaceState is the local-first aggregate persisted by the browser store.
export interface WorkspaceState {
  authorNotes: AuthorNote[];
  authorMemoryEvents: AuthorMemoryEvent[];
  authorPositionAssertions: AuthorPositionAssertion[];
  editorialModel: EditorialModel;
  projectProfile: ProjectProfile;
  editorialRules: EditorialRule[];
  editorialSetupRevision: number;
  editorialValidationRun: EditorialValidationRun | null;
  topics: Topic[];
  fabulas: Fabula[];
  topicFabulaMatrix: TopicFabulaMatrixEntry[];
  radars: RadarDefinition[];
  sourceSignal: SourceSignal;
  sourceSignals: SourceSignal[];
  postCandidates: PostCandidate[];
  postCandidate: PostCandidate | null;
  insightCard: InsightCard | null;
  contentPlanItem: ContentPlanItem | null;
  contentPlanItems: ContentPlanItem[];
  contentPlanSettings: ContentPlanSettings;
  planWeightWarnings: PlanWeightWarning[];
  editorialWorkItems: EditorialWorkItem[];
  selectedEditorialWorkItemId: string | null;
  postBrief: PostBrief | null;
  postDraft: PostDraft | null;
  editorialChecks: EditorialCheck[];
  editorNotes: EditorNote[];
  finalText: FinalText | null;
  postVisual: PostVisual | null;
  releasePackage: ReleasePackage | null;
  editorialLearningNote: EditorialLearningNote | null;
  externalSources: AuthorExternalSource[];
  importCandidates: ImportedMemoryCandidate[];
  archiveRecords: ArchiveRecord[];
  bulkImportActions: BulkImportAction[];
  activeSection: WorkspaceSection;
  updatedAt: string;
}

export type WorkspaceSection =
  | 'memory'
  | 'editorialModel'
  | 'signals'
  | 'plan'
  | 'brief'
  | 'edit'
  | 'release'
  | 'analytics';

export interface WorkspaceStore {
  load(): WorkspaceState;
  save(workspace: WorkspaceState): void;
  reset(): WorkspaceState;
}
