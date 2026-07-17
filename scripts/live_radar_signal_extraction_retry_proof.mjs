import { chromium } from '@playwright/test';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const runId = process.env.RADAR_LIVE_RETRY_RUN_ID?.trim();
if (!runId) throw new Error('RADAR_LIVE_RETRY_RUN_ID is required.');
const useSavedRetry = process.env.RADAR_USE_SAVED_RETRY === '1';

const rootDir = process.cwd();
const proofDir = path.join(rootDir, 'var', 'visual-proof', '2.17.4.7.0.2', 'live-retry');
const password = await readDevPassword();
const browser = await chromium.launch({ headless: true });

async function readDevPassword() {
  const source = await readFile(path.join(rootDir, '.env'), 'utf8');
  const line = source.split(/\r?\n/u).find((candidate) => candidate.startsWith('GLAVRED_DEV_AUTH_PASSWORD='));
  if (!line) return 'glavred-demo';
  return line.slice(line.indexOf('=') + 1).trim().replace(/^(['"])(.*)\1$/u, '$2');
}

async function login(page) {
  await page.goto('http://127.0.0.1:5176', { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Войти' }).waitFor();
  await page.getByLabel('Email').fill('founder@example.test');
  await page.getByLabel('Пароль').fill(password);
  const me = page.waitForResponse((response) => response.url().endsWith('/api/users/me') && response.status() === 200);
  await page.getByRole('button', { name: 'Войти' }).click();
  await me;
  await page.locator('[data-testid="project-dashboard"]').waitFor();
  await page.getByText('Backend session', { exact: true }).waitFor();
}

function acceptedSignal(payload) {
  return (payload.sourceSignals ?? []).find((signal) =>
    signal.editorialLanguage === 'ru'
      && signal.sourceLanguage === 'en'
      && signal.localizationStatus === 'localized'
  );
}

await mkdir(proofDir, { recursive: true });
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  await login(page);
  await page.goto(
    `http://127.0.0.1:5176/radar-runs?runId=${encodeURIComponent(runId)}&projectId=project-ai-design-patterns&detailId=signal-extraction`,
    { waitUntil: 'networkidle' }
  );
  await page.locator('[data-testid="radar-run-summary"]').waitFor();

  let payload;
  if (useSavedRetry) {
    payload = await page.evaluate(async ({ targetRunId }) => {
      const response = await fetch('http://127.0.0.1:8000/api/projects/project-ai-design-patterns/workspace', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error(`Workspace request failed with HTTP ${response.status}.`);
      const workspace = (await response.json()).workspace;
      const run = (workspace.radarRuns ?? []).find((candidate) => candidate.id === targetRunId);
      return {
        run,
        sourceSignals: (workspace.sourceSignals ?? []).filter((signal) => signal.radarRunId === targetRunId),
        signalExtractionReport: run?.signalExtraction
      };
    }, { targetRunId: runId });
  } else {
    const retryResponse = page.waitForResponse(
      (response) => response.url().endsWith(`/api/radar-runs/${runId}/signal-extraction`)
        && response.request().method() === 'POST',
      { timeout: 180_000 }
    );
    await page.getByRole('button', { name: 'Повторить извлечение сигналов' }).click();
    const response = await retryResponse;
    if (!response.ok()) throw new Error(`Signal extraction retry failed with HTTP ${response.status()}.`);
    payload = await response.json();
    await page.getByRole('button', { name: 'Повторить извлечение сигналов' }).waitFor();
  }
  const signal = acceptedSignal(payload);
  if (!signal) throw new Error('Retry produced no Russian editorial signal localized from an English source.');
  const evidence = (signal.evidence ?? []).find((item) =>
    /^https?:\/\//u.test(item.sourceUrl ?? '') && /[A-Za-z]/u.test(`${item.sourceTitle ?? ''} ${item.quote ?? ''}`)
  );
  if (!evidence) throw new Error('Localized signal has no original English evidence and source URL.');
  const attempts = payload.signalExtractionReport?.providerAttempts ?? [];
  if (!attempts.length || attempts.some((attempt) => attempt.status === 'blocked' || attempt.payloadBudget?.incident)) {
    throw new Error('Signal extraction retry has no clean direct budget proof.');
  }
  await page.screenshot({ path: path.join(proofDir, 'trace-after-retry.png'), fullPage: true });

  await page.goto('http://127.0.0.1:5176', { waitUntil: 'networkidle' });
  await page.locator('[data-testid="project-dashboard"]').waitFor();
  await page.getByRole('button', { name: 'Открыть кабинет' }).first().click();
  await page.getByRole('button', { name: /^Сигналы/u }).first().click();
  await page.locator('.signals-page').waitFor();
  await page.getByRole('button', { name: /Найденные сигналы/u }).click();
  const signalRow = page.locator('[data-testid="source-signal-row"]').filter({ hasText: signal.title }).first();
  await signalRow.waitFor();
  if (!(await signalRow.getByRole('link', { name: /Открыть источник/u }).count())) {
    await signalRow.locator('.signal-row-main').click();
  }
  await signalRow.getByText('Редакционная полезность не оценена').waitFor();
  await signalRow.getByText('На проверке').waitFor();
  const sourceLink = signalRow.getByRole('link', { name: /Открыть источник/u }).first();
  if ((await sourceLink.getAttribute('href')) !== evidence.sourceUrl) {
    throw new Error('Signal card source URL does not match the evidence URL.');
  }
  const traceLink = signalRow.getByRole('link', { name: 'Показать в трассе' }).first();
  const traceHref = await traceLink.getAttribute('href');
  if (!traceHref?.includes(`runId=${encodeURIComponent(runId)}`) || !traceHref.includes('detailId=signal-extraction')) {
    throw new Error('Signal card has no correct deep trace link.');
  }
  await page.screenshot({ path: path.join(proofDir, 'signal-card-after-retry.png'), fullPage: true });

  const report = {
    runId,
    extractionRevision: payload.signalExtractionReport?.revision ?? null,
    extractionStatus: payload.signalExtractionReport?.status ?? null,
    sourceSignalCount: payload.sourceSignals?.length ?? 0,
    localizedEnglishSourceSignalId: signal.id,
    editorialLanguage: signal.editorialLanguage,
    sourceLanguage: signal.sourceLanguage,
    localizationStatus: signal.localizationStatus,
    providerAttemptCount: attempts.length,
    providerAttempts: attempts.map((attempt) => ({
      attemptLabel: attempt.attemptLabel,
      status: attempt.status,
      model: attempt.model,
      providerInputCharEstimate: attempt.payloadBudget?.providerInputCharEstimate ?? null,
      messageCharCount: attempt.messageCharCount ?? null,
      repairContextCharCount: attempt.repairContextCharCount ?? null,
      providerUsageStatus: attempt.providerUsageStatus ?? null
    })),
    sourceUrlVerified: true,
    unscoredStateVerified: true,
    traceDetailVerified: true,
    persistedByUi: true,
    retryPerformedInThisInvocation: !useSavedRetry
  };
  await writeFile(path.join(proofDir, 'live-retry-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));
  await context.close();
} finally {
  await browser.close();
}
