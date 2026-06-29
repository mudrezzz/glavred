import { normalizePortfolioState } from '../application/portfolioService';
import type { PortfolioState, PortfolioStore } from '../domain/portfolio/types';
import { createDemoPortfolio, createDemoPortfolioFromWorkspace } from '../fixtures/demoPortfolio';
import { normalizeWorkspace } from './localWorkspaceStore';

export const PORTFOLIO_STORAGE_KEY = 'glavred.portfolio.v1';
export const LEGACY_WORKSPACE_STORAGE_KEY = 'glavred.workspace.v1';

export class LocalPortfolioStore implements PortfolioStore {
  constructor(private readonly storage: Storage = window.localStorage) {}

  load(): PortfolioState {
    const rawPortfolio = this.storage.getItem(PORTFOLIO_STORAGE_KEY);

    if (rawPortfolio) {
      try {
        return normalizePortfolioState(JSON.parse(rawPortfolio) as Partial<PortfolioState>, createDemoPortfolio(), normalizeWorkspace);
      } catch {
        return createDemoPortfolio();
      }
    }

    const rawLegacyWorkspace = this.storage.getItem(LEGACY_WORKSPACE_STORAGE_KEY);
    if (rawLegacyWorkspace) {
      try {
        return createDemoPortfolioFromWorkspace(normalizeWorkspace(JSON.parse(rawLegacyWorkspace)));
      } catch {
        return createDemoPortfolio();
      }
    }

    return createDemoPortfolio();
  }

  save(portfolio: PortfolioState): void {
    this.storage.setItem(
      PORTFOLIO_STORAGE_KEY,
      JSON.stringify(normalizePortfolioState(portfolio, createDemoPortfolio(), normalizeWorkspace))
    );
  }

  reset(): PortfolioState {
    const portfolio = createDemoPortfolio();
    this.storage.removeItem(LEGACY_WORKSPACE_STORAGE_KEY);
    this.save(portfolio);
    return portfolio;
  }
}
