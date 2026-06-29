import type { WorkspaceState } from '../workspace/types';

export type UserAccountStatus = 'active' | 'disabled';
export type ProjectMembershipRole = 'owner' | 'editor' | 'viewer';
export type ProjectMembershipStatus = 'active' | 'invited' | 'disabled';
export type BlogProjectStatus = 'active' | 'archived';
export type BlogProjectBenchmarkRole = 'demo' | 'privateBenchmark' | 'real';

export interface UserAccount {
  id: string;
  displayName: string;
  email?: string;
  avatarUrl?: string;
  status: UserAccountStatus;
  createdAt: string;
}

export interface ProjectMembership {
  id: string;
  userId: string;
  projectId: string;
  role: ProjectMembershipRole;
  status: ProjectMembershipStatus;
}

export interface BlogProject {
  id: string;
  ownerUserId: string;
  title: string;
  description: string;
  language: string;
  status: BlogProjectStatus;
  benchmarkRole?: BlogProjectBenchmarkRole;
  createdAt: string;
  updatedAt: string;
}

export interface PortfolioState {
  activeUserId: string;
  activeProjectId: string;
  users: UserAccount[];
  projects: BlogProject[];
  memberships: ProjectMembership[];
  workspacesByProjectId: Record<string, WorkspaceState>;
  updatedAt: string;
}

export interface PortfolioStore {
  load(): PortfolioState;
  save(portfolio: PortfolioState): void;
  reset(): PortfolioState;
}
