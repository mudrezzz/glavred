import { normalizePortfolioState } from '../application/portfolioService';
import type { PortfolioState, PortfolioStore } from '../domain/portfolio/types';
import { createDemoPortfolio, createDemoPortfolioFromWorkspace } from '../fixtures/demoPortfolio';
import { normalizeWorkspace } from './localWorkspaceStore';
import { inspectPortfolioText } from './portfolioTextIntegrity';

export const PORTFOLIO_STORAGE_KEY = 'glavred.portfolio.v1';
export const LEGACY_WORKSPACE_STORAGE_KEY = 'glavred.workspace.v1';
export const PORTFOLIO_INTEGRITY_QUARANTINE_KEY = 'glavred.portfolio.integrity.v1';

export class LocalPortfolioStore implements PortfolioStore {
  constructor(private readonly storage: Storage = window.localStorage) {}

  load(): PortfolioState {
    const rawPortfolio = this.storage.getItem(PORTFOLIO_STORAGE_KEY);

    if (rawPortfolio) {
      const diagnostic = inspectPortfolioText(rawPortfolio);
      if (diagnostic) {
        this.quarantine(diagnostic);
        this.storage.removeItem(PORTFOLIO_STORAGE_KEY);
        return createDemoPortfolio();
      }
      try {
        return normalizePortfolioState(JSON.parse(rawPortfolio) as Partial<PortfolioState>, createDemoPortfolio(), normalizeWorkspace);
      } catch {
        return createDemoPortfolio();
      }
    }

    const rawLegacyWorkspace = this.storage.getItem(LEGACY_WORKSPACE_STORAGE_KEY);
    if (rawLegacyWorkspace) {
      const diagnostic = inspectPortfolioText(rawLegacyWorkspace);
      if (diagnostic) {
        this.quarantine(diagnostic);
        this.storage.removeItem(LEGACY_WORKSPACE_STORAGE_KEY);
        return createDemoPortfolio();
      }
      try {
        return createDemoPortfolioFromWorkspace(normalizeWorkspace(JSON.parse(rawLegacyWorkspace)));
      } catch {
        return createDemoPortfolio();
      }
    }

    return createDemoPortfolio();
  }

  save(portfolio: PortfolioState): void {
    const serialized = JSON.stringify(normalizePortfolioState(portfolio, createDemoPortfolio(), normalizeWorkspace));
    const diagnostic = inspectPortfolioText(serialized);
    if (diagnostic) {
      this.quarantine(diagnostic);
      return;
    }
    this.storage.setItem(
      PORTFOLIO_STORAGE_KEY,
      serialized
    );
  }

  reset(): PortfolioState {
    const portfolio = createDemoPortfolio();
    this.storage.removeItem(LEGACY_WORKSPACE_STORAGE_KEY);
    this.save(portfolio);
    return portfolio;
  }

  private quarantine(diagnostic: { code: string; charCount: number; valueHash: string }): void {
    this.storage.setItem(
      PORTFOLIO_INTEGRITY_QUARANTINE_KEY,
      JSON.stringify({ ...diagnostic, detectedAt: new Date().toISOString() })
    );
  }
}
