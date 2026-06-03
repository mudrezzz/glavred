export type EditorialStageId =
  | 'source_radar'
  | 'insight_cards'
  | 'content_plan'
  | 'post_brief'
  | 'draft'
  | 'editorial_checks'
  | 'export'
  | 'learning';

export type MvpModuleId =
  | 'editorial_bible'
  | 'sources_and_insights'
  | 'content_plan'
  | 'post_brief'
  | 'draft_and_review';

export interface EditorialStage {
  id: EditorialStageId;
  label: string;
  purpose: string;
  requiresApproval: boolean;
}

export interface MvpModule {
  id: MvpModuleId;
  label: string;
  outcome: string;
}

const DEFAULT_STAGES: EditorialStage[] = [
  {
    id: 'source_radar',
    label: 'Editorial Radar',
    purpose: 'Collect signals from sources, notes, questions, and market events.',
    requiresApproval: false
  },
  {
    id: 'insight_cards',
    label: 'Insight Cards',
    purpose: 'Turn raw signals into scored editorial opportunities.',
    requiresApproval: false
  },
  {
    id: 'content_plan',
    label: 'Content Plan',
    purpose: 'Prioritize topics, formats, platforms, and publication timing.',
    requiresApproval: true
  },
  {
    id: 'post_brief',
    label: 'Post Brief',
    purpose: 'Define the thesis, conflict, evidence, structure, tone, and risks.',
    requiresApproval: true
  },
  {
    id: 'draft',
    label: 'Draft',
    purpose: 'Write the first version from an approved brief, not from a bare prompt.',
    requiresApproval: false
  },
  {
    id: 'editorial_checks',
    label: 'Editorial Checks',
    purpose: 'Run style, anti-AI, fact-checking, and policy review before release.',
    requiresApproval: true
  },
  {
    id: 'export',
    label: 'Manual Export',
    purpose: 'Prepare the final text for manual publication in the first product version.',
    requiresApproval: false
  },
  {
    id: 'learning',
    label: 'Learning Loop',
    purpose: 'Feed publication results and editorial notes back into the system.',
    requiresApproval: false
  }
];

export const MVP_MODULES: MvpModule[] = [
  {
    id: 'editorial_bible',
    label: 'Editorial Bible',
    outcome: 'Audience, positioning, fabula, rubrics, style, boundaries, and blog goals.'
  },
  {
    id: 'sources_and_insights',
    label: 'Sources and Insights',
    outcome: 'Connected materials become insight cards with relevance and banality risk.'
  },
  {
    id: 'content_plan',
    label: 'Content Plan',
    outcome: 'A weekly or monthly plan that the author can approve, edit, or reject.'
  },
  {
    id: 'post_brief',
    label: 'Post Brief',
    outcome: 'An approved editorial intention before the system writes a draft.'
  },
  {
    id: 'draft_and_review',
    label: 'Draft and Review',
    outcome: 'Draft text checked for style, factual support, policy fit, and AI markers.'
  }
];

export class EditorialWorkflow {
  private constructor(private readonly orderedStages: EditorialStage[]) {}

  static default(): EditorialWorkflow {
    return new EditorialWorkflow(DEFAULT_STAGES);
  }

  stages(): EditorialStage[] {
    return [...this.orderedStages];
  }

  approvalGates(): EditorialStage[] {
    return this.orderedStages.filter((stage) => stage.requiresApproval);
  }

  nextStage(currentStageId: EditorialStageId): EditorialStage | null {
    const index = this.orderedStages.findIndex((stage) => stage.id === currentStageId);

    if (index < 0 || index === this.orderedStages.length - 1) {
      return null;
    }

    return this.orderedStages[index + 1];
  }
}
