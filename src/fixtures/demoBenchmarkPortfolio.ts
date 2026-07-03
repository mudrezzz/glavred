import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import {
  createDefaultTopicFabulaMatrix,
  DEFAULT_CONTENT_PLAN_SETTINGS,
  type AuthorExternalSource,
  type AuthorNote,
  type ContentPlanItem,
  type EditorialModel,
  type EditorialRule,
  type Fabula,
  type InsightCard,
  type ProjectProfile,
  type RadarDefinition,
  type SourceSignal,
  type Topic,
  type TopicFabulaMatrixEntry,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { runLocalRadar } from '../application/upstreamRadarRunService';
import type { PublicationChannel } from '../domain/publication-channels/types';
import {
  aiDesignPatternsBenchmarkSeed,
  createAiDesignPatternsPublicationChannels
} from './demoAiDesignPatternsProject';
import {
  createGlavredBlogPublicationChannels,
  glavredBlogBenchmarkSeed
} from './demoGlavredBlogProject';
import { createDemoWorkspace } from './demoWorkspace';
import {
  createSevernayaStenaPublicationChannels,
  severnayaStenaBenchmarkSeed
} from './demoSevernayaStenaProject';

export type DemoBenchmarkProjectId =
  | 'project-ai-design-patterns'
  | 'project-kasha-iz-topora'
  | 'project-glavred-blog';

export interface DemoPortfolioBenchmarkExpectation {
  projectId: DemoBenchmarkProjectId;
  language: string;
  defaultPlatform: string;
  benchmarkSignals: string[];
  mustAvoid: string[];
  readyScenarioId: string;
}

type TopicFabulaCompatibility = {
  topicId: string;
  fabulaId: string;
};

export const demoPortfolioBenchmarkExpectations: Record<DemoBenchmarkProjectId, DemoPortfolioBenchmarkExpectation> = {
  'project-ai-design-patterns': {
    projectId: 'project-ai-design-patterns',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'ai-patterns-plan-decision-workbench',
    benchmarkSignals: ['industrial AI scope', 'pattern naming', 'ТОиР evidence', 'community pattern book'],
    mustAvoid: ['generic AI news', 'model leaderboard without industrial context', 'autonomous AI promises without HITL']
  },
  'project-kasha-iz-topora': {
    projectId: 'project-kasha-iz-topora',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'stena-plan-lost-route',
    benchmarkSignals: ['alpinist metaphor', 'complex B2B route', 'RevOps belay', 'field-tested deal pain'],
    mustAvoid: ['student handbook tone', 'mixed pilot metaphor', 'generic sales motivation', 'AI hype as main topic']
  },
  'project-glavred-blog': {
    projectId: 'project-glavred-blog',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'glavred-plan-flat-ai-draft',
    benchmarkSignals: ['being interesting', 'author voice', 'practical editorial method', 'Telegram/Dzen readiness'],
    mustAvoid: ['generic product marketing', 'opaque AI magic', 'internal trace dump as public prose', 'autoposting promise']
  }
};

export type BenchmarkWorkspaceSeed = {
  projectProfile: ProjectProfile;
  editorialModel: EditorialModel;
  authorNotes: AuthorNote[];
  editorialRules: EditorialRule[];
  topics: Topic[];
  fabulas: Fabula[];
  radars: RadarDefinition[];
  sourceSignals: SourceSignal[];
  externalSources: AuthorExternalSource[];
  topicFabulaCompatibility?: TopicFabulaCompatibility[];
  defaultPlatform: string;
  defaultPublicationSizeProfileId: string;
  postsPerWeek: number;
  readyScenario: {
    planId: string;
    title: string;
    expectedEffect: string;
    topicId: string;
    fabulaId: string;
    sourceSignalId: string;
    format: string;
  };
};

export function createBenchmarkProjectWorkspace(projectId: DemoBenchmarkProjectId): WorkspaceState {
  const seed = benchmarkWorkspaceSeeds[projectId];
  if (projectId === 'project-ai-design-patterns') return createAiDesignPatternsWorkspace(seed);

  const base = createDemoWorkspace({ includeSeededHitlLearning: false });
  const authorMemoryEvents = seed.authorNotes.map(createAuthorMemoryEvent);
  const topicFabulaMatrix = createBenchmarkTopicFabulaMatrix(seed);
  const sourceSignals = seed.sourceSignals.map(withSignalEvidence);
  const sourceSignal = sourceSignals.find((signal) => signal.id === seed.readyScenario.sourceSignalId) ?? sourceSignals[0];
  const topic = seed.topics.find((item) => item.id === seed.readyScenario.topicId) ?? seed.topics[0];
  const fabula = seed.fabulas.find((item) => item.id === seed.readyScenario.fabulaId) ?? seed.fabulas[0];
  const insightCard = createBenchmarkInsight(seed, sourceSignal, topic, fabula);
  const publicationChannels = createBenchmarkPublicationChannels(projectId);
  const defaultChannel = publicationChannels.find((channel) => channel.status === 'active') ?? publicationChannels[0];
  const contentPlanItems = createBenchmarkPlanItems(seed, defaultChannel);

  const workspace: WorkspaceState = {
    ...base,
    authorNotes: seed.authorNotes,
    authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(seed.authorNotes, authorMemoryEvents),
    editorialModel: seed.editorialModel,
    projectProfile: seed.projectProfile,
    editorialRules: seed.editorialRules,
    editorialValidationRun: null,
    topics: seed.topics,
    fabulas: seed.fabulas,
    topicFabulaMatrix,
    sourceRegistry: { id: 'source-registry-project', handles: [], updatedAt: '2026-07-01T09:00:00.000Z' },
    radarRuns: [],
    foundMaterials: [],
    radars: seed.radars,
    sourceSignal,
    sourceSignals,
    insightCard,
    contentPlanItem: contentPlanItems[0],
    contentPlanItems,
    contentPlanSettings: {
      ...DEFAULT_CONTENT_PLAN_SETTINGS,
      period: 'month',
      postsPerWeek: seed.postsPerWeek,
      defaultPlatform: defaultChannel?.title ?? seed.defaultPlatform,
      defaultChannelId: defaultChannel?.id,
      defaultPublicationSizeProfileId: seed.defaultPublicationSizeProfileId,
      publishSlots: [
        { date: '2026-07-01', time: '10:00' },
        { date: '2026-07-03', time: '10:00' },
        { date: '2026-07-06', time: '10:00' }
      ]
    },
    publicationChannels,
    postCandidates: [],
    postCandidate: null,
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    postVisual: null,
    releasePackage: null,
    editorialLearningNote: null,
    externalSources: seed.externalSources,
    importCandidates: [],
    archiveRecords: [],
    bulkImportActions: [],
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };

  return runLocalRadar(workspace, selectSeededRadarId(workspace), '2026-07-01T09:00:00.000Z');
}

function createAiDesignPatternsWorkspace(seed: BenchmarkWorkspaceSeed): WorkspaceState {
  const base = createDemoWorkspace({ includeSeededHitlLearning: true });
  const learningNotes = base.authorNotes.filter((note) => note.type === 'editorialLearning');
  const authorNotes = [...seed.authorNotes, ...learningNotes];
  const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
  const topics = seed.topics;
  const fabulas = seed.fabulas;
  const topicFabulaMatrix = createBenchmarkTopicFabulaMatrix(seed);
  const sourceSignals = seed.sourceSignals.map(withSignalEvidence);
  const sourceSignal = sourceSignals.find((signal) => signal.id === seed.readyScenario.sourceSignalId) ?? sourceSignals[0];
  const topic = topics.find((item) => item.id === seed.readyScenario.topicId) ?? topics[0];
  const fabula = fabulas.find((item) => item.id === seed.readyScenario.fabulaId) ?? fabulas[0];
  const insightCard = createBenchmarkInsight(seed, sourceSignal, topic, fabula);
  const publicationChannels = createBenchmarkPublicationChannels('project-ai-design-patterns');
  const defaultChannel = publicationChannels.find((channel) => channel.status === 'active') ?? publicationChannels[0];
  const contentPlanItems = createBenchmarkPlanItems(seed, defaultChannel);

  const workspace: WorkspaceState = {
    ...base,
    projectProfile: seed.projectProfile,
    editorialModel: seed.editorialModel,
    authorNotes,
    authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
    editorialRules: seed.editorialRules,
    editorialValidationRun: null,
    topics,
    fabulas,
    topicFabulaMatrix,
    sourceRegistry: { id: 'source-registry-project', handles: [], updatedAt: '2026-07-01T09:00:00.000Z' },
    radarRuns: [],
    foundMaterials: [],
    radars: seed.radars,
    sourceSignals,
    sourceSignal,
    insightCard,
    contentPlanItem: contentPlanItems[0],
    contentPlanItems,
    contentPlanSettings: {
      ...DEFAULT_CONTENT_PLAN_SETTINGS,
      period: 'month',
      postsPerWeek: seed.postsPerWeek,
      defaultPlatform: defaultChannel?.title ?? seed.defaultPlatform,
      defaultChannelId: defaultChannel?.id,
      defaultPublicationSizeProfileId: seed.defaultPublicationSizeProfileId,
      maxCandidatesPerSlot: 2,
      publishSlots: [
        { date: '2026-07-01', time: '10:00' },
        { date: '2026-07-08', time: '10:00' }
      ]
    },
    publicationChannels,
    postCandidates: base.postCandidates,
    postCandidate: base.postCandidate,
    postBrief: base.postBrief,
    postDraft: base.postDraft,
    editorialChecks: base.editorialChecks,
    editorNotes: base.editorNotes,
    finalText: base.finalText,
    postVisual: base.postVisual,
    releasePackage: base.releasePackage,
    editorialLearningNote: base.editorialLearningNote,
    externalSources: [...seed.externalSources, ...base.externalSources],
    importCandidates: base.importCandidates,
    archiveRecords: base.archiveRecords,
    bulkImportActions: base.bulkImportActions,
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };

  return runLocalRadar(workspace, selectSeededRadarId(workspace), '2026-07-01T09:00:00.000Z');
}

function selectSeededRadarId(workspace: WorkspaceState): string {
  return workspace.radars.find((radar) => radar.sourceType === 'authorMemory' || radar.sourceType === 'archive')?.id
    ?? workspace.radars[0]?.id
    ?? '';
}

function createBenchmarkInsight(
  seed: BenchmarkWorkspaceSeed,
  signal: SourceSignal,
  topic: Topic,
  fabula: Fabula
): InsightCard {
  return {
    id: `insight-${seed.readyScenario.planId}`,
    signalId: signal.id,
    title: seed.readyScenario.title,
    whyItMatters: signal.summary,
    audienceRelevance: seed.editorialModel.audience,
    authorPosition: topic.authorStance,
    rubric: topic.title,
    urgency: 'Benchmark scenario: ready to test portfolio-specific drafting quality.',
    score: 0.9,
    banalityRisk: 0.16,
    factGaps: fabula.proofRequirements,
    topicId: topic.id,
    topicTitle: topic.title,
    fabulaId: fabula.id,
    fabulaTitle: fabula.title
  };
}

function createBenchmarkPlanItems(seed: BenchmarkWorkspaceSeed, defaultChannel?: PublicationChannel): ContentPlanItem[] {
  const first = seed.readyScenario;
  return [
    createPlanItem(seed, first, 'Высокий', '2026-07-01', defaultChannel),
    createPlanItem(seed, {
      ...first,
      planId: `${first.planId}-followup`,
      title: `${first.title}: follow-up angle`
    }, 'Нормальный', '2026-07-03', defaultChannel)
  ];
}

function createPlanItem(
  seed: BenchmarkWorkspaceSeed,
  scenario: BenchmarkWorkspaceSeed['readyScenario'],
  priority: string,
  date: string,
  defaultChannel?: PublicationChannel
): ContentPlanItem {
  const topic = seed.topics.find((item) => item.id === scenario.topicId);
  const fabula = seed.fabulas.find((item) => item.id === scenario.fabulaId);
  return {
    id: scenario.planId,
    insightId: `insight-${seed.readyScenario.planId}`,
    title: scenario.title,
    platform: defaultChannel?.title ?? seed.defaultPlatform,
    channelId: defaultChannel?.id,
    date,
    time: '10:00',
    priority,
    format: scenario.format,
    expectedEffect: scenario.expectedEffect,
    approvalStatus: 'draft',
    topicId: scenario.topicId,
    topicTitle: topic?.title,
    fabulaId: scenario.fabulaId,
    fabulaTitle: fabula?.title,
    sourceSignalId: scenario.sourceSignalId,
    publicationSizeProfileId: defaultChannel?.defaultPublicationSizeProfileId ?? seed.defaultPublicationSizeProfileId,
    manualOverride: false,
    weightWarningIds: []
  };
}

function createBenchmarkPublicationChannels(projectId: DemoBenchmarkProjectId): PublicationChannel[] {
  if (projectId === 'project-ai-design-patterns') {
    return createAiDesignPatternsPublicationChannels();
  }

  if (projectId === 'project-glavred-blog') {
    return createGlavredBlogPublicationChannels();
  }

  return createSevernayaStenaPublicationChannels();
}

function createBenchmarkTopicFabulaMatrix(seed: BenchmarkWorkspaceSeed): TopicFabulaMatrixEntry[] {
  if (!seed.topicFabulaCompatibility?.length) {
    return createDefaultTopicFabulaMatrix(seed.topics, seed.fabulas);
  }

  const enabled = new Set(seed.topicFabulaCompatibility.map((entry) => `${entry.topicId}:${entry.fabulaId}`));
  return seed.topics.flatMap((topic) =>
    seed.fabulas.map((fabula) => ({
      topicId: topic.id,
      fabulaId: fabula.id,
      enabled: enabled.has(`${topic.id}:${fabula.id}`)
    }))
  );
}

function withSignalEvidence(signal: SourceSignal): SourceSignal {
  return {
    ...signal,
    evidence: signal.evidence ?? [
      {
        id: `evidence-${signal.id}`,
        sourceTitle: signal.source,
        sourceUrl: '',
        quote: signal.summary,
        summary: signal.rawNote
      }
    ],
    searchNote: signal.searchNote ?? 'Benchmark seed: sanitized source context, not a live ingestion result.'
  };
}

const benchmarkWorkspaceSeeds: Record<DemoBenchmarkProjectId, BenchmarkWorkspaceSeed> = {
  'project-ai-design-patterns': aiDesignPatternsBenchmarkSeed,
  'project-kasha-iz-topora': severnayaStenaBenchmarkSeed,
  'project-glavred-blog': glavredBlogBenchmarkSeed

};
