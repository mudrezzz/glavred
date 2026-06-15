// Shared domain primitives used by multiple bounded contexts.
export type ApprovalStatus = 'draft' | 'approved' | 'rejected';
export type DraftStatus = 'draft' | 'revised';
export type EditorialEntityStatus = 'active' | 'paused';

export interface WeightRange {
  min: number;
  max: number;
}
