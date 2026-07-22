import { chromium } from '@playwright/test';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const rootDir = process.cwd();
const proofDir = path.join(rootDir, 'var', 'visual-proof', '2.17.4.7.0.2', 'live');
const password = await readDevPassword();
const browser = await chromium.launch({ headless: true });

async function readDevPassword() {
  const source = await readFile(path.join(rootDir, '.env'), 'utf8');
  const line = source.split(/\r?\n/u).find((candidate) => candidate.startsWith('GLAVRED_DEV_AUTH_PASSWORD='));
  if (!line) return 'glavred-demo';
  return line.slice(line.indexOf('=') + 1).trim().replace(/^(['"])(.*)\1$/u, '$2');
}

async function login(page, baseUrl) {
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Войти' }).waitFor();
  await page.getByLabel('Email').fill('founder@example.test');
  await page.getByLabel('Пароль').fill(password);
  const me = page.waitForResponse((response) => response.url().endsWith('/api/users/me') && response.status() === 200);
  await page.getByRole('button', { name: 'Войти' }).click();
  await me;
  await page.locator('[data-testid="project-dashboard"]').waitFor();
  await page.getByText('Backend session', { exact: true }).waitFor();
}

async function openIndustrialRadar(page) {
  await page.getByRole('button', { name: 'Открыть кабинет' }).first().click();
  await page.getByRole('button', { name: /^Сигналы/i }).first().click();
  await page.locator('.signals-page').waitFor();
  const radar = page.locator('[data-testid="radar-row"]').filter({ hasText: /Кейсы промышленного ИИ|Industrial AI cases/u }).first();
  await radar.waitFor();
  if (!(await radar.locator('[data-testid="radar-settings-panel"]').count())) {
    await radar.locator('.radar-row-main').click();
  }
  await radar.locator('[data-testid="radar-settings-panel"]').waitFor();
  await radar.getByRole('button', { name: 'Запустить радар' }).waitFor();
  return radar;
}

async function waitUntilSaved(page, runId) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 90_000) {
    const found = await page.evaluate(async ({ targetRunId }) => {
      const response = await fetch('http://127.0.0.1:8000/api/projects/project-ai-design-patterns/workspace', {
        credentials: 'include'
      });
      if (!response.ok) return false;
      const payload = await response.json();
      return (payload.workspace?.radarRuns ?? []).some((run) => run.id === targetRunId);
    }, { targetRunId: runId });
    if (found) return;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error(`RadarRun ${runId} was not persisted by the UI.`);
}

await mkdir(proofDir, { recursive: true });
let report;
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  await login(page, 'http://127.0.0.1:5176');
  const radar = await openIndustrialRadar(page);
  const responsePromise = page.waitForResponse(
    (response) => response.url().endsWith('/api/radar-runs/external') && response.request().method() === 'POST',
    { timeout: 600_000 }
  );
  await radar.getByRole('button', { name: 'Запустить радар' }).click();
  const response = await responsePromise;
  if (!response.ok()) throw new Error(`UI RadarRun failed with HTTP ${response.status()}.`);
  const payload = await response.json();
  const runId = payload.run?.id;
  if (!runId) throw new Error('UI RadarRun response has no run id.');
  if ((payload.sourceSignals ?? []).length < 1) throw new Error('UI RadarRun produced no source signal candidates.');
  if ((payload.foundMaterials ?? []).length < 1) throw new Error('UI RadarRun produced no found materials.');
  const languageContext = payload.run?.languageContext ?? payload.run?.searchPlan?.languageContext;
  if (languageContext?.editorialLanguage !== 'ru') throw new Error('RadarRun did not use BlogProject.language=ru.');
  if (languageContext?.sourceLanguagePolicy !== 'editorialAndEnglish') {
    throw new Error('RadarRun did not use editorialAndEnglish source policy.');
  }
  const localizedSignal = payload.sourceSignals.find((signal) =>
    signal.editorialLanguage === 'ru' && signal.sourceLanguage === 'en' && signal.localizationStatus === 'localized'
  );
  if (!localizedSignal) throw new Error('No Russian editorial signal was localized from an English source.');
  const editorialText = [
    localizedSignal.title,
    localizedSignal.summary,
    localizedSignal.uncertainty,
    localizedSignal.mechanism,
    localizedSignal.outcome,
    ...(localizedSignal.limitations ?? [])
  ].join(' ');
  if (!/[А-Яа-яЁё]/u.test(editorialText)) throw new Error('Localized signal has no Russian editorial text.');
  const originalEvidence = (localizedSignal.evidence ?? []).find((item) =>
    /^https?:\/\//u.test(item.sourceUrl ?? '') && /[A-Za-z]/u.test(`${item.sourceTitle ?? ''} ${item.quote ?? ''}`)
  );
  if (!originalEvidence) throw new Error('Localized signal has no original English evidence with a safe source URL.');
  const attempts = payload.signalExtractionReport?.providerAttempts ?? [];
  if (attempts.length < 1) throw new Error('Signal extraction has no provider attempt trace.');
  if (attempts.some((attempt) => attempt.status === 'blocked' || attempt.payloadBudget?.incident)) {
    throw new Error('Signal extraction exceeded its existing provider-input/message budget.');
  }
  await waitUntilSaved(page, runId);
  await page.getByRole('button', { name: /Найденные сигналы/u }).click();
  const signalRow = page.locator('[data-testid="source-signal-row"]').filter({ hasText: localizedSignal.title }).first();
  await signalRow.waitFor();
  await signalRow.locator('.signal-row-main').click();
  await signalRow.getByText('Редакционная полезность не оценена').waitFor();
  await signalRow.getByText('На проверке').waitFor();
  const sourceLink = signalRow.getByRole('link', { name: /Открыть источник/u }).first();
  if ((await sourceLink.getAttribute('href')) !== originalEvidence.sourceUrl) {
    throw new Error('Signal card source URL does not match the original evidence URL.');
  }
  await page.screenshot({ path: path.join(proofDir, 'signals-desktop.png'), fullPage: true });

  await signalRow.getByRole('link', { name: 'Показать в трассе' }).first().click();
  await page.waitForURL(/\/radar-runs\?.*detailId=signal-extraction/u);
  await page.locator('[data-testid="radar-run-summary"]').waitFor({ timeout: 30_000 });
  const traceText = await page.locator('body').innerText();
  if (!traceText.includes(runId)) throw new Error('Technical trace does not show the fresh run id.');
  await page.screenshot({ path: path.join(proofDir, 'trace-desktop.png'), fullPage: true });

  report = {
    runId,
    runStatus: payload.run.status,
    foundMaterialCount: payload.foundMaterials.length,
    sourceSignalCount: payload.sourceSignals.length,
    localizedEnglishSourceSignalId: localizedSignal.id,
    editorialLanguage: languageContext.editorialLanguage,
    sourceLanguagePolicy: languageContext.sourceLanguagePolicy,
    queryLanguages: [...new Set((payload.run?.searchPlan?.queries ?? []).map((query) => query.queryLanguage))],
    sourceUrlVerified: true,
    traceDetailVerified: true,
    extractionAttempts: attempts.length,
    extractionBudgetRespected: true,
    extractionStatus: payload.signalExtractionReport?.status ?? null,
    benchmarkStatus: payload.run.benchmarkReport?.status ?? null,
    operationCount: payload.run.operations?.length ?? 0,
    persistedByUi: true,
    traceOpened: true,
    hosts: { '127.0.0.1': 'authenticated' }
  };
  await context.close();

  const localhostContext = await browser.newContext({ viewport: { width: 1180, height: 820 } });
  const localhostPage = await localhostContext.newPage();
  await login(localhostPage, 'http://localhost:5176');
  report.hosts.localhost = 'authenticated';
  await localhostContext.close();
  await writeFile(path.join(proofDir, 'live-radar-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
