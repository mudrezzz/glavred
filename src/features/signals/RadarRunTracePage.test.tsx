import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { setRadarRunTracePortfolioLoadersForTests } from '../../infrastructure/radarRunTraceClient';
import { createRadarTracePortfolio } from './radarRunTraceTestFixtures';
import { RadarRunTracePage } from './RadarRunTracePage';

describe('RadarRunTracePage', () => {
  afterEach(() => {
    setRadarRunTracePortfolioLoadersForTests(null, null);
    window.history.pushState({}, '', '/');
  });

  it('loads an enriched RadarRun by id and switches trace details', async () => {
    setRadarRunTracePortfolioLoadersForTests(() => createRadarTracePortfolio(), null);

    const { container } = render(<RadarRunTracePage />);

    fireEvent.change(screen.getByLabelText('RadarRun ID'), { target: { value: 'radar-run-industrial-1' } });
    fireEvent.click(container.querySelector('.ai-run-search button') as HTMLButtonElement);

    expect(await screen.findByText('Industrial AI cases')).toBeInTheDocument();
    expect(screen.getByTestId('radar-run-summary')).toHaveTextContent('1');
    expect(screen.getByTestId('radar-run-timeline')).toHaveTextContent('search-plan');

    fireEvent.click(within(screen.getByTestId('radar-run-timeline')).getByText('search-plan'));
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('Industrial case examples');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('industrial AI maintenance case study');

    fireEvent.click(within(screen.getByTestId('radar-run-timeline')).getByText('read-selection'));
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('best-diverse-result');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('vendor-pricing-noise');
  });

  it('renders legacy/minimal runs without empty external-search sections', async () => {
    setRadarRunTracePortfolioLoadersForTests(
      () => createRadarTracePortfolio({
        searchPlan: undefined,
        rawResults: undefined,
        selectedForRead: undefined,
        rejectedBeforeRead: undefined
      }),
      null
    );

    const { container } = render(<RadarRunTracePage />);

    fireEvent.change(screen.getByLabelText('RadarRun ID'), { target: { value: 'radar-run-industrial-1' } });
    fireEvent.click(container.querySelector('.ai-run-search button') as HTMLButtonElement);

    expect(await screen.findByText('Industrial AI cases')).toBeInTheDocument();
    expect(screen.getByTestId('radar-run-timeline')).not.toHaveTextContent('Search plan unavailable');
    expect(screen.getByTestId('radar-run-timeline')).not.toHaveTextContent('Benchmark verdict');
    expect(screen.getByTestId('radar-run-timeline')).not.toHaveTextContent('raw results');
  });

  it('renders live benchmark verdict payload when present', async () => {
    setRadarRunTracePortfolioLoadersForTests(
      () => createRadarTracePortfolio({
        benchmarkReport: {
          status: 'inconclusive',
          scenarioId: 'benchmark-industrial-ai-maintenance-cases',
          evaluationMode: 'live',
          providerHealth: 'unavailable',
          coverage: { traceComplete: false },
          plannedCoverage: {
            queryFamilies: { expected: ['limitationCritique'], covered: ['limitationCritique'], missing: [] },
            evidenceTypes: { expected: ['limitationCritique'], covered: ['limitationCritique'], missing: [] }
          },
          executedCoverage: {
            queryFamilies: { expected: ['limitationCritique'], covered: [], missing: ['limitationCritique'] },
            evidenceTypes: { expected: ['limitationCritique'], covered: [], missing: ['limitationCritique'] }
          },
          skippedRequiredCoverage: [
            {
              kind: 'queryFamily',
              value: 'limitationCritique',
              reason: 'budget-max-external-queries',
              intentId: 'intent-limits'
            }
          ],
          inconclusiveReasons: ['openrouter-not-configured'],
          traceComplete: false
        }
      }),
      null
    );

    const { container } = render(<RadarRunTracePage />);

    fireEvent.change(screen.getByLabelText('RadarRun ID'), { target: { value: 'radar-run-industrial-1' } });
    fireEvent.click(container.querySelector('.ai-run-search button') as HTMLButtonElement);
    fireEvent.click(await screen.findByText('Benchmark verdict'));

    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('inconclusive');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('unavailable');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('openrouter-not-configured');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('limitationCritique');
    expect(screen.getByTestId('radar-run-detail-panel')).toHaveTextContent('budget-max-external-queries');
  });

  it('reports missing run ids clearly', async () => {
    setRadarRunTracePortfolioLoadersForTests(() => createRadarTracePortfolio(), () => createRadarTracePortfolio());

    const { container } = render(<RadarRunTracePage />);

    fireEvent.change(screen.getByLabelText('RadarRun ID'), { target: { value: 'missing-run' } });
    fireEvent.click(container.querySelector('.ai-run-search button') as HTMLButtonElement);

    expect(await screen.findByText(/RadarRun not found/i)).toBeInTheDocument();
  });

  it('opens as a standalone app route and auto-loads from URL', async () => {
    window.history.pushState({}, '', '/radar-runs?runId=radar-run-industrial-1');
    setRadarRunTracePortfolioLoadersForTests(() => createRadarTracePortfolio(), null);

    render(<App />);

    await waitFor(() => expect(screen.getByText('Industrial AI cases')).toBeInTheDocument());
    expect(screen.getByTestId('radar-run-summary')).toBeInTheDocument();
    expect(screen.queryByText('Главред')).not.toBeInTheDocument();
  });
});
