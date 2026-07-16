import { chromium } from '@playwright/test';
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const rootDir = process.cwd();
const apiPort = process.env.CONNECTED_SIGNALS_API_PORT ?? '8199';
const uiPort = process.env.CONNECTED_SIGNALS_UI_PORT ?? '4183';
const apiUrl = `http://127.0.0.1:${apiPort}`;
const uiUrl = `http://127.0.0.1:${uiPort}`;
const password = 'connected-signals-smoke';
const workDir = await mkdtemp(path.join(tmpdir(), 'glavred-signals-'));
const proofDir = path.join(rootDir, 'var', 'visual-proof', '2.17.4.7.0.1');
const logs = { backend: '', frontend: '' };

function startProcess(command, args, env, logKey, shell = false) {
  const child = spawn(command, args, {
    cwd: rootDir,
    env: { ...process.env, ...env },
    shell,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  child.stdout.on('data', (chunk) => {
    logs[logKey] += chunk.toString();
  });
  child.stderr.on('data', (chunk) => {
    logs[logKey] += chunk.toString();
  });
  return child;
}

function stopProcess(child) {
  if (!child || child.exitCode !== null) return;
  if (process.platform === 'win32' && child.pid) {
    spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' });
  } else {
    child.kill('SIGTERM');
  }
}

async function waitFor(url, label) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 45_000) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {
      // The process is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 400));
  }
  throw new Error(`${label} did not start.\n${logs.backend.slice(-1500)}\n${logs.frontend.slice(-1500)}`);
}

async function openProject(page) {
  const button = page.getByRole('button', { name: 'Открыть кабинет' }).first();
  if (await button.count()) await button.click();
  await page.getByRole('button', { name: /^Сигналы/i }).first().waitFor();
  const switcher = page.locator('[data-testid="portfolio-switcher"] .sidebar-portfolio-trigger');
  await switcher.click();
  await page.getByText('backend session', { exact: true }).waitFor();
  await switcher.click();
}

async function putHostileButValidWorkspace(page) {
  const result = await page.evaluate(async ({ apiBase }) => {
    const response = await fetch(`${apiBase}/api/projects/project-ai-design-patterns/workspace`, {
      credentials: 'include'
    });
    if (!response.ok) return { status: response.status, step: 'get' };
    const payload = await response.json();
    const workspace = payload.workspace;
    const continuous = 'длиннаякорректнаястрокабезпробелов'.repeat(28);
    const paragraph = 'Система должна сохранять русский текст, доказательства и ограничения без перекодирования. ';
    workspace.insightCard = {
      ...(workspace.insightCard ?? {}),
      title: `Проверка устойчивого интерфейса: ${continuous.slice(0, 520)}`,
      whyItMatters: `${paragraph.repeat(42)}${continuous}`
    };
    if (workspace.radars?.[0]?.rules?.[0]) {
      workspace.radars[0].rules[0].statement = `${paragraph.repeat(46)}${continuous}`;
    }
    if (workspace.sourceSignals?.[0]) {
      workspace.sourceSignals[0].summary = `${paragraph.repeat(36)}${continuous}`;
      workspace.sourceSignals[0].sourceUrl = `https://example.test/${continuous}`;
    }
    const saved = await fetch(`${apiBase}/api/projects/project-ai-design-patterns/workspace`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace })
    });
    return { status: saved.status, step: 'put' };
  }, { apiBase: apiUrl });
  if (result.status !== 200) throw new Error(`Connected workspace ${result.step} failed with ${result.status}.`);
}

async function assertCorruptSaveIsRejected(page) {
  const result = await page.evaluate(async ({ apiBase }) => {
    const response = await fetch(`${apiBase}/api/projects/project-ai-design-patterns/workspace`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workspace: { title: 'РџСЂРёРІРµС‚ РџСЂРёРІРµС‚ РџСЂРёРІРµС‚' } })
    });
    const payload = await response.json();
    return { status: response.status, code: payload?.detail?.code };
  }, { apiBase: apiUrl });
  if (result.status !== 422 || result.code !== 'workspace-text-integrity-failed') {
    throw new Error(`Corrupt workspace was not rejected: ${JSON.stringify(result)}`);
  }
}

async function assertSignalsLayout(page, viewport, name) {
  await page.setViewportSize(viewport);
  const nav = page.getByRole('button', { name: /^Сигналы/i }).first();
  if (await nav.count()) await nav.click();
  await page.locator('.signals-page').waitFor();
  const firstRadar = page.locator('[data-testid="radar-row"]').first();
  if (await firstRadar.count()) {
    const main = firstRadar.locator('.radar-row-main');
    if (!(await firstRadar.evaluate((element) => element.classList.contains('expanded')))) await main.click();
  }
  const metrics = await page.evaluate(() => {
    const pageWidth = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    const grids = Array.from(document.querySelectorAll('.signals-workspace-grid'));
    const gridOverflow = Math.max(0, ...grids.map((item) => item.scrollWidth - item.clientWidth));
    const editors = Array.from(document.querySelectorAll('.radar-object, .insight-mini, .signal-card'));
    const contentOverflow = Math.max(0, ...editors.map((item) => item.scrollWidth - item.clientWidth));
    const buttons = Array.from(document.querySelectorAll('.signals-page button'));
    return {
      pageWidth,
      gridOverflow,
      contentOverflow,
      hasLocalFallback: document.body.textContent?.toLowerCase().includes('local fallback') ?? false,
      hasInsightPreview: Boolean(document.querySelector('.insight-mini-preview')),
      hasFullDisclosure: Boolean(document.querySelector('.insight-mini-details summary')),
      buttonCount: buttons.length
    };
  });
  const failures = [];
  if (metrics.pageWidth > 2) failures.push(`page overflow ${metrics.pageWidth}px`);
  if (metrics.gridOverflow > 2) failures.push(`grid overflow ${metrics.gridOverflow}px`);
  if (metrics.contentOverflow > 2) failures.push(`content overflow ${metrics.contentOverflow}px`);
  if (metrics.hasLocalFallback) failures.push('local fallback is active');
  if (!metrics.hasInsightPreview || !metrics.hasFullDisclosure) failures.push('bounded insight preview is missing');
  if (metrics.buttonCount < 5) failures.push('signals actions are not reachable');
  if (failures.length) throw new Error(`${name}: ${failures.join('; ')}`);
  await page.screenshot({ path: path.join(proofDir, `signals-${name}.png`), fullPage: true });
}

await mkdir(proofDir, { recursive: true });
const backend = startProcess(
  'python',
  ['-m', 'backend.app'],
  {
    GLAVRED_API_HOST: '127.0.0.1',
    GLAVRED_API_PORT: apiPort,
    GLAVRED_CORS_ORIGINS: uiUrl,
    GLAVRED_DEV_AUTH_PASSWORD: password,
    PORTFOLIO_DB_PATH: path.join(workDir, 'portfolio.sqlite3'),
    AI_RUN_AUDIT_DB_PATH: path.join(workDir, 'ai-runs.sqlite3'),
    DRAFT_RUN_DB_PATH: path.join(workDir, 'draft-runs.sqlite3')
  },
  'backend'
);
const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const frontend = startProcess(
  npmCommand,
  ['run', 'dev', '--', '--host', '127.0.0.1', '--port', uiPort, '--strictPort'],
  { VITE_API_BASE_URL: apiUrl, BROWSER: 'none' },
  'frontend',
  process.platform === 'win32'
);

let browser;
try {
  await waitFor(`${apiUrl}/health`, 'FastAPI');
  await waitFor(uiUrl, 'Vite');
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(uiUrl, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'Войти' }).waitFor();
  await page.getByLabel('Email').fill('founder@example.test');
  await page.getByLabel('Пароль').fill(password);
  const authenticatedMe = page.waitForResponse(
    (response) => response.url().endsWith('/api/users/me') && response.status() === 200
  );
  await page.getByRole('button', { name: 'Войти' }).click();
  await authenticatedMe;
  await page.locator('[data-testid="project-dashboard"]').waitFor();
  await page.getByText('Backend session', { exact: true }).waitFor();
  await openProject(page);
  await putHostileButValidWorkspace(page);
  await assertCorruptSaveIsRejected(page);
  await page.reload({ waitUntil: 'networkidle' });
  await openProject(page);

  const viewports = [
    [{ width: 390, height: 844 }, 'mobile'],
    [{ width: 1180, height: 820 }, 'laptop'],
    [{ width: 1440, height: 1000 }, 'desktop'],
    [{ width: 1904, height: 1080 }, 'wide'],
    [{ width: 2048, height: 1152 }, 'ultrawide']
  ];
  for (const [viewport, name] of viewports) {
    await assertSignalsLayout(page, viewport, name);
  }
  console.log(`Connected Signals smoke passed at ${viewports.map(([, name]) => name).join(', ')}.`);
} catch (error) {
  console.error(error);
  console.error(logs.backend.slice(-2000));
  console.error(logs.frontend.slice(-2000));
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  stopProcess(frontend);
  stopProcess(backend);
  await rm(workDir, { recursive: true, force: true });
}
