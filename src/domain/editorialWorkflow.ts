export type EditorialStageId =
  | 'sources'
  | 'insights'
  | 'plan'
  | 'brief'
  | 'draft'
  | 'editing'
  | 'release'
  | 'analytics';

export interface EditorialStage {
  id: EditorialStageId;
  label: string;
  requiresApproval: boolean;
}

const DEFAULT_STAGES: EditorialStage[] = [
  { id: 'sources', label: 'Sources', requiresApproval: false },
  { id: 'insights', label: 'Insights', requiresApproval: false },
  { id: 'plan', label: 'Plan', requiresApproval: true },
  { id: 'brief', label: 'Brief', requiresApproval: true },
  { id: 'draft', label: 'Draft', requiresApproval: false },
  { id: 'editing', label: 'Editing', requiresApproval: true },
  { id: 'release', label: 'Release', requiresApproval: false },
  { id: 'analytics', label: 'Analytics', requiresApproval: false }
];

export class EditorialWorkflow {
  private constructor(private readonly orderedStages: EditorialStage[]) {}

  static default(): EditorialWorkflow {
    return new EditorialWorkflow(DEFAULT_STAGES);
  }

  stages(): EditorialStage[] {
    return [...this.orderedStages];
  }

  nextStage(currentStageId: EditorialStageId): EditorialStage | null {
    const index = this.orderedStages.findIndex((stage) => stage.id === currentStageId);

    if (index < 0 || index === this.orderedStages.length - 1) {
      return null;
    }

    return this.orderedStages[index + 1];
  }
}
