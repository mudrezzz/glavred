import { chromium } from '@playwright/test';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

const rootDir = process.cwd();
const proofDir = path.join(rootDir, 'var', 'visual-proof', '2.17.4.7.1', 'live');
const projectId = 'project-ai-design-patterns';
const replayRunId = 'radar-run-ai-pattern-radar-industrial-cases-7';
const reuseExistingRun = process.env.GLAVRED_LIVE_PROOF_REUSE === '1';
const skipReplay = process.env.GLAVRED_LIVE_PROOF_SKIP_REPLAY === '1';
const password = await readDevPassword();
const browser = await chromium.launch({ headless: true });

async function readDevPassword() {
  if (process.env.GLAVRED_DEV_AUTH_PASSWORD) return process.env.GLAVRED_DEV_AUTH_PASSWORD;
  if (process.env.GLAVRED_DEV_AUTH_PASSWORD_FILE) {
    const secret = (await readFile(process.env.GLAVRED_DEV_AUTH_PASSWORD_FILE, 'utf8')).trim();
    if (secret) return secret;
  }
  try {
    const source = await readFile(path.join(rootDir, '.env'), 'utf8');
    const line = source.split(/\r?\n/u).find((candidate) => candidate.startsWith('GLAVRED_DEV_AUTH_PASSWORD='));
    if (line) return line.slice(line.indexOf('=') + 1).trim().replace(/^(['"])(.*)\1$/u, '$2');
  } catch {
    // Remote QA intentionally excludes the complete local .env file.
  }
  return 'glavred-demo';
}

async function login(page, baseUrl) {
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Войти' }).waitFor();
  await page.getByLabel('Email').fill('founder@example.test');
  await page.getByLabel('Пароль').fill(password);
  const me = page.waitForResponse((response) => response.url().endsWith('/api/users/me') && response.status() === 200);
  await page.getByRole('button', { name: 'Войти' }).click();
  await me;
  await page.locator('[data-testid="project-dashboard"]').waitFor({ timeout: 90_000 });
  const owner = page.locator('[data-testid="project-dashboard-owner"]');
  await owner.waitFor({ state: 'attached', timeout: 90_000 });
  const startedAt = Date.now();
  let ownerText = '';
  while (Date.now() - startedAt < 120_000) {
    ownerText = ((await owner.textContent()) ?? '').replace(/\s+/gu, ' ').trim();
    if (ownerText.includes('Backend session')) return;
    await page.waitForTimeout(500);
  }
  throw new Error(`Authenticated dashboard did not expose the backend session state: ${ownerText.slice(0, 240)}`);
}

async function openIndustrialRadar(page) {
  await page.getByRole('button', { name: 'Открыть кабинет' }).first().click();
  await page.getByRole('button', { name: /^Сигналы/i }).first().click();
  await page.locator('.signals-page').waitFor();
  const radar = page.locator('[data-testid="radar-row"]').filter({ hasText: /Промышленные AI-кейсы|Кейсы промышленного ИИ/u }).first();
  await radar.waitFor();
  if (!(await radar.locator('[data-testid="radar-settings-panel"]').count())) {
    await radar.locator('.radar-row-main').click();
  }
  await radar.locator('[data-testid="radar-settings-panel"]').waitFor();
  return radar;
}

async function waitUntilSaved(page, runId, predicate) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 120_000) {
    const found = await page.evaluate(async ({ targetRunId }) => {
      const response = await fetch('http://127.0.0.1:8000/api/projects/project-ai-design-patterns/workspace', { credentials: 'include' });
      if (!response.ok) return null;
      const payload = await response.json();
      const run = (payload.workspace?.radarRuns ?? []).find((item) => item.id === targetRunId);
      return run ? { run, signals: (payload.workspace?.sourceSignals ?? []).filter((item) => item.radarRunId === targetRunId) } : null;
    }, { targetRunId: runId });
    if (found && predicate(found)) return found;
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error(`RadarRun ${runId} did not reach the expected persisted state.`);
}

function assertScoring(payload, label) {
  const signals = payload.sourceSignals ?? [];
  const report = payload.signalScoringReport ?? payload.run?.signalScoring ?? {};
  if (signals.length < 1) throw new Error(`${label}: no source signals.`);
  if (report.status !== 'succeeded') throw new Error(`${label}: scoring status is ${report.status}.`);
  if (signals.some((signal) => !signal.utilityReport?.recommendation)) throw new Error(`${label}: signal without terminal recommendation.`);
  if (signals.some((signal) => signal.utilityReport?.version !== 2)) throw new Error(`${label}: legacy utility report remains.`);
  if (signals.some((signal) => !Array.isArray(signal.utilityReport?.radarCriteria) || !Array.isArray(signal.utilityReport?.projectCriteria))) {
    throw new Error(`${label}: explainable criterion groups are missing.`);
  }
  if (signals.some((signal) => !Array.isArray(signal.utilityReport?.qualityChecks) || !signal.relationshipReport)) {
    throw new Error(`${label}: quality or relationship report is missing.`);
  }
  const criteria = signals.flatMap((signal) => [
    ...(signal.utilityReport.radarCriteria ?? []),
    ...(signal.utilityReport.projectCriteria ?? [])
  ]);
  if (criteria.some((item) => !item.criterionId || !item.title || !item.statement || !item.mode || !item.verdict || !item.summary)) {
    throw new Error(`${label}: criterion explainability contract is incomplete.`);
  }
  if (signals.every((signal) => ['notRecommended', 'inconclusive'].includes(signal.utilityReport.recommendation))) {
    throw new Error(`${label}: all signals are rejected or inconclusive.`);
  }
  const unresolved = (report.unresolvedSettingRefCount ?? 0) + (report.unresolvedEvidenceRefCount ?? 0);
  if (unresolved !== 0) throw new Error(`${label}: unresolved setting/evidence refs.`);
  const attempts = report.providerAttempts ?? [];
  if (attempts.length < 1) throw new Error(`${label}: no provider attempt trace.`);
  if (attempts.some((attempt) => attempt.status === 'blocked' || attempt.payloadBudget?.incident || attempt.messageCharCount > 22000)) {
    throw new Error(`${label}: scoring budget was exceeded.`);
  }
  const signalIds = new Set(signals.map((signal) => signal.id));
  const unresolvedRelationships = signals.flatMap((signal) => signal.relationshipReport?.relations ?? [])
    .filter((item) => !signalIds.has(item.otherSignalId));
  if (unresolvedRelationships.length) throw new Error(`${label}: unresolved relationship signal refs.`);
  return { signals, report, attempts };
}

function assertDigitalAdvisorReplay(proof) {
  const advisors = proof.signals.filter((signal) => /цифров.*советчик|советчик.*ТОиР/iu.test(`${signal.title} ${signal.summary}`));
  if (advisors.length !== 1) throw new Error(`Replay expected one extracted digital-advisor signal, got ${advisors.length}.`);
  const advisor = advisors[0];
  const topic = (advisor.utilityReport.radarCriteria ?? []).find((item) => item.dimension === 'topicAffinity');
  if (topic?.verdict !== 'СОВПАДАЕТ') throw new Error(`Digital advisor topic verdict is ${topic?.verdict ?? 'missing'}.`);
  const checks = Object.fromEntries((advisor.utilityReport.qualityChecks ?? []).map((item) => [item.checkId, item]));
  if (!['capabilityOnly', 'missing'].includes(checks['outcome-support']?.classification)) {
    throw new Error(`Digital advisor result support is ${checks['outcome-support']?.classification ?? 'missing'}.`);
  }
  if (['independent', 'corroborated'].includes(checks['source-posture']?.classification)) {
    throw new Error('Digital advisor source was treated as independently proven.');
  }
  if (advisor.utilityReport.recommendation !== 'reviewWithCaution') {
    throw new Error(`Digital advisor recommendation is ${advisor.utilityReport.recommendation}.`);
  }
  const risk = proof.signals.find((signal) => /риск/iu.test(`${signal.title} ${signal.summary}`));
  if (!risk) throw new Error('Replay has no automated-risk signal from the shared source.');
  const relatedSameSource = (advisor.relationshipReport?.relations ?? []).some(
    (item) => item.otherSignalId === risk.id && item.kind === 'relatedSameSource'
  );
  if (!relatedSameSource) {
    throw new Error('Risk and digital-advisor signals were not classified as relatedSameSource.');
  }
  return { advisor, relatedSameSource, risk };
}

async function assertNoOverflow(page, width) {
  const geometry = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth
  }));
  if (geometry.scrollWidth > geometry.clientWidth + 2) {
    throw new Error(`Signals UI overflows at ${width}px: ${geometry.scrollWidth}/${geometry.clientWidth}.`);
  }
}

await mkdir(proofDir, { recursive: true });
let report;
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  await login(page, 'http://127.0.0.1:5176');

  const persistedWorkspace = await page.evaluate(async () => {
    const response = await fetch('http://127.0.0.1:8000/api/projects/project-ai-design-patterns/workspace', { credentials: 'include' });
    if (!response.ok) throw new Error(`Workspace load failed with HTTP ${response.status}.`);
    return (await response.json()).workspace;
  });
  let replayProof = null;
  let replayResult = null;
  if (!skipReplay) {
    const replayResponse = await page.evaluate(async ({ replayId, project }) => {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${project}/radar-runs/${replayId}/signal-scoring`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      return { status: response.status, payload: await response.json() };
    }, { replayId: replayRunId, project: projectId });
    if (replayResponse.status !== 200) throw new Error(`Replay scoring failed with HTTP ${replayResponse.status}.`);
    replayProof = assertScoring(replayResponse.payload, 'digital-advisor-replay');
    replayResult = assertDigitalAdvisorReplay(replayProof);
  }
  const reusableRun = reuseExistingRun ? [...persistedWorkspace.radarRuns]
    .sort((left, right) => String(right.startedAt).localeCompare(String(left.startedAt)))
    .find((run) =>
    run.id !== replayRunId && run.radarId === 'ai-pattern-radar-industrial-cases' && run.signalScoring?.status === 'succeeded'
    ) : null;
  let payload = reusableRun ? {
    run: reusableRun,
    sourceSignals: persistedWorkspace.sourceSignals.filter((signal) => signal.radarRunId === reusableRun.id),
    signalScoringReport: reusableRun.signalScoring
  } : null;
  await page.goto('http://127.0.0.1:5176', { waitUntil: 'networkidle' });
  const radar = await openIndustrialRadar(page);
  if (!payload) {
    const runResponsePromise = page.waitForResponse(
      (response) => response.url().endsWith('/api/radar-runs/external') && response.request().method() === 'POST',
      { timeout: 600_000 }
    );
    await radar.getByRole('button', { name: 'Запустить радар' }).click();
    const runResponse = await runResponsePromise;
    if (!runResponse.ok()) throw new Error(`Fresh UI RadarRun failed with HTTP ${runResponse.status()}.`);
    payload = await runResponse.json();
    await writeFile(path.join(proofDir, 'fresh-ui-response.json'), `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  }
  const runId = payload.run?.id;
  if (!runId) throw new Error('Fresh UI RadarRun has no run id.');
  const freshProof = assertScoring(payload, 'fresh-live-run');
  if (!reuseExistingRun) {
    await waitUntilSaved(page, runId, ({ run, signals }) => run.signalScoring?.revision >= 1 && signals.length >= 1);
  }

  await page.getByRole('button', { name: /Найденные сигналы/u }).click();
  const selectedSignal = freshProof.signals.find((signal) =>
    ['candidate', 'new', 'corrected'].includes(signal.reviewStatus) && signal.utilityReport.recommendation !== 'notRecommended'
  ) ?? freshProof.signals.find((signal) => signal.utilityReport.recommendation !== 'notRecommended') ?? freshProof.signals[0];
  const signalRow = page.locator('[data-testid="source-signal-row"]').filter({ hasText: selectedSignal.title }).first();
  await signalRow.waitFor();
  if (!(await signalRow.locator('[data-testid="signal-utility-report"]').isVisible())) {
    await signalRow.locator('.signal-row-main').click();
  }
  await signalRow.locator('[data-testid="signal-utility-report"]').waitFor();
  await signalRow.getByRole('heading', { name: 'Соответствие радару', exact: true }).waitFor();
  await signalRow.getByRole('heading', { name: 'Соответствие редакционной модели', exact: true }).waitFor();
  await signalRow.getByRole('heading', { name: 'Качество и риски', exact: true }).waitFor();
  await signalRow.getByRole('heading', { name: 'Связанные сигналы', exact: true }).waitFor();
  await signalRow.getByRole('link', { name: /Открыть источник/u }).first().waitFor();
  const visibleSignalText = await signalRow.innerText();
  const rawHandle = (selectedSignal.evidenceRefs ?? [])[0];
  if (rawHandle && (visibleSignalText.includes(rawHandle.materialId) || visibleSignalText.includes(rawHandle.fragmentId))) {
    throw new Error('Product UI exposes a raw evidence handle.');
  }

  await signalRow.getByRole('button', { name: 'Корректировать' }).click();
  await signalRow.locator('[data-testid="signal-edit-form"]').waitFor();
  const editContextText = await signalRow.locator('.signal-facts').innerText();
  const mechanismApplicable = selectedSignal.utilityReport?.qualityChecks
    ?.find((item) => item.checkId === 'mechanism-support')?.applicable
    ?? ['case', 'practice', 'change', 'problemFailureMode', 'recurringPattern'].includes(selectedSignal.type);
  const requiredEditContext = [
    selectedSignal.source,
    selectedSignal.uncertainty,
    ...(selectedSignal.limitations ?? []),
    mechanismApplicable ? selectedSignal.mechanism : null
  ].filter(Boolean);
  for (const value of requiredEditContext) {
    if (!editContextText.includes(value)) {
      throw new Error(`Signal edit mode lost applicable read-only context: ${String(value).slice(0, 80)}`);
    }
  }
  await signalRow.getByRole('heading', { name: 'Доказательства', exact: true }).waitFor();
  await signalRow.getByRole('button', { name: 'Отменить' }).click();

  const rescorePromise = page.waitForResponse(
    (response) => response.url().includes(`/api/projects/${projectId}/radar-runs/${runId}/signal-scoring`) && response.request().method() === 'POST',
    { timeout: 600_000 }
  );
  await signalRow.getByRole('button', { name: 'Пересчитать полезность' }).click();
  const rescoreResponse = await rescorePromise;
  if (!rescoreResponse.ok()) throw new Error(`Manual rescore failed with HTTP ${rescoreResponse.status()}.`);
  const rescorePayload = await rescoreResponse.json();
  const rescoreProof = assertScoring(rescorePayload, 'manual-rescore');
  const expectedRevision = Number(freshProof.report.revision ?? 0) + 1;
  await waitUntilSaved(page, runId, ({ run }) => run.signalScoring?.revision >= expectedRevision);

  const rescoredSelectedSignal = rescoreProof.signals.find((signal) => signal.id === selectedSignal.id) ?? selectedSignal;
  let reviewPayload = { sourceSignal: rescoredSelectedSignal };
  if (rescoredSelectedSignal.reviewStatus !== 'approved') {
    const reviewPromise = page.waitForResponse(
      (response) => response.url().includes(`/api/projects/${projectId}/source-signals/${selectedSignal.id}/review`) && response.request().method() === 'POST',
      { timeout: 60_000 }
    );
    await signalRow.getByRole('button', { name: 'Утвердить' }).click();
    const reviewResponse = await reviewPromise;
    if (!reviewResponse.ok()) throw new Error(`Human review failed with HTTP ${reviewResponse.status()}.`);
    reviewPayload = await reviewResponse.json();
  }

  const refreshedRow = page
    .locator('[data-testid="source-signal-row"]')
    .filter({ hasText: reviewPayload.sourceSignal.title })
    .first();
  if (reviewPayload.sourceSignal.reviewStatus !== 'approved' || reviewPayload.sourceSignal.reviewHistory?.length < 1) {
    throw new Error('Human review event was not recorded.');
  }
  if (!(await refreshedRow.getByText('История решений').isVisible())) {
    await refreshedRow.locator('.signal-row-main').click();
  }
  await refreshedRow.getByText('История решений').waitFor();

  const widths = [390, 1180, 1440, 1904, 2048];
  for (const width of widths) {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 1000 });
    await assertNoOverflow(page, width);
    await page.screenshot({ path: path.join(proofDir, `signals-${width}.png`), fullPage: true });
  }

  const sourceLink = refreshedRow.getByRole('link', { name: /Открыть источник/u }).first();
  const sourceUrl = await sourceLink.getAttribute('href');
  if (!sourceUrl || !/^https?:\/\//u.test(sourceUrl)) throw new Error('Signal has no safe source URL.');
  await refreshedRow.getByRole('link', { name: 'Показать в трассе' }).first().click();
  await page.waitForURL(/\/radar-runs\?.*detailId=signal-extraction/u);
  try {
    await page.locator('[data-testid="radar-run-summary"]').waitFor({ timeout: 60_000 });
  } catch (error) {
    const pageText = (await page.locator('body').innerText()).slice(0, 3000);
    throw new Error(`Trace page did not load for ${page.url()}: ${pageText}`, { cause: error });
  }
  const scoringTraceButton = page
    .locator('[data-testid="radar-run-timeline"] button')
    .filter({ hasText: 'Редакционная полезность' });
  await scoringTraceButton.waitFor({ timeout: 15_000 });
  await scoringTraceButton.click();
  await page.locator('[data-testid="radar-run-detail-panel"]').getByText('Редакционная полезность', { exact: true }).waitFor();
  await page.screenshot({ path: path.join(proofDir, 'trace-desktop.png'), fullPage: true });

  report = {
    replayRunId: replayProof ? replayRunId : null,
    replaySignalCount: replayProof?.signals.length ?? 0,
    digitalAdvisorSignalId: replayResult?.advisor.id ?? null,
    digitalAdvisorRecommendation: replayResult?.advisor.utilityReport.recommendation ?? null,
    digitalAdvisorResultSupport: replayResult?.advisor.utilityReport.qualityChecks.find((item) => item.checkId === 'outcome-support')?.classification ?? null,
    digitalAdvisorSourcePosture: replayResult?.advisor.utilityReport.qualityChecks.find((item) => item.checkId === 'source-posture')?.classification ?? null,
    digitalAdvisorRelatedSameSource: replayResult?.relatedSameSource ?? null,
    relatedRiskSignalId: replayResult?.risk?.id ?? null,
    runId,
    runStatus: payload.run.status,
    signalCount: freshProof.signals.length,
    recommendations: freshProof.signals.map((signal) => ({ id: signal.id, recommendation: signal.utilityReport.recommendation })),
    scoringStatus: freshProof.report.status,
    scoringAttempts: freshProof.attempts.length,
    scoringUsage: freshProof.attempts.map((attempt) => attempt.providerUsage ?? null),
    scoringBudgetRespected: true,
    unresolvedSettingRefCount: freshProof.report.unresolvedSettingRefCount,
    unresolvedEvidenceRefCount: freshProof.report.unresolvedEvidenceRefCount,
    explainableCriteriaVerified: true,
    relationshipReportVerified: true,
    rawEvidenceHandlesHidden: true,
    manualRescoreRevision: rescoreProof.report.revision,
    reviewedSignalId: reviewPayload.sourceSignal.id,
    reviewStatus: reviewPayload.sourceSignal.reviewStatus,
    reviewRevision: reviewPayload.sourceSignal.reviewRevision,
    reviewEventCount: reviewPayload.sourceSignal.reviewHistory.length,
    sourceUrlVerified: true,
    traceOpened: true,
    scoringTraceOpened: true,
    viewportOverflowChecks: widths,
    hosts: { '127.0.0.1': 'authenticated' }
  };
  await context.close();

  const localhostContext = await browser.newContext({ viewport: { width: 1180, height: 820 } });
  const localhostPage = await localhostContext.newPage();
  await login(localhostPage, 'http://localhost:5176');
  report.hosts.localhost = 'authenticated';
  await localhostContext.close();
  await writeFile(path.join(proofDir, 'live-radar-utility-report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
