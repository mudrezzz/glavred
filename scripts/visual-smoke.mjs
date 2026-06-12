import { chromium } from '@playwright/test';
import { spawn, spawnSync } from 'node:child_process';

const rootDir = process.cwd();
const port = process.env.VISUAL_SMOKE_PORT ?? '4181';
const baseUrl = `http://127.0.0.1:${port}`;

function runDevServer() {
  const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  return spawn(
    npmCommand,
    ['run', 'dev', '--', '--host', '127.0.0.1', '--port', port, '--strictPort'],
    {
      cwd: rootDir,
      env: { ...process.env, BROWSER: 'none' },
      shell: process.platform === 'win32',
      stdio: ['ignore', 'pipe', 'pipe']
    }
  );
}

function stopDevServer(server) {
  if (process.platform === 'win32' && server.pid) {
    spawnSync('taskkill', ['/pid', String(server.pid), '/T', '/F'], { stdio: 'ignore' });
    return;
  }

  server.kill();
}

async function waitForServer() {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 30000) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) return;
    } catch {
      // Vite is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Vite did not start at ${baseUrl}`);
}

function assertLayout(result) {
  const failures = [];

  if (result.initialToastVisible) failures.push('Initial autosave toast is visible before any user action.');
  if (!result.rowCount) failures.push('No source rows were rendered.');
  if (!result.hasMetaBar) failures.push('Source row metadata bar is missing.');
  if (result.rowOverflow > 2) failures.push(`Source row overflows horizontally by ${result.rowOverflow}px.`);
  if (result.titleHeight > 78) failures.push(`Source title is too tall (${result.titleHeight}px); likely broken into narrow columns.`);
  if (result.titleWidth < 160) failures.push(`Source title is too narrow (${result.titleWidth}px); row columns are collapsing.`);
  if (result.actionsOverflow) failures.push('Source action buttons overflow outside the row.');

  if (failures.length) {
    throw new Error(`Visual smoke failed:\n- ${failures.join('\n- ')}`);
  }
}

function assertChatLayout(result) {
  const failures = [];

  if (!result.toggleVisible) failures.push(`${result.viewport}: context chat toggle is not visible.`);
  if (!result.drawerVisible) failures.push(`${result.viewport}: context chat drawer did not open.`);
  if (result.drawerOverflow > 2) failures.push(`${result.viewport}: context chat drawer overflows horizontally by ${result.drawerOverflow}px.`);
  if (result.drawerWidth < result.minWidth || result.drawerWidth > result.maxWidth) {
    failures.push(`${result.viewport}: context chat drawer width ${result.drawerWidth}px is outside ${result.minWidth}-${result.maxWidth}px.`);
  }
  if (result.pageOverflow > 2) failures.push(`${result.viewport}: page overflows horizontally by ${result.pageOverflow}px.`);

  if (failures.length) {
    throw new Error(`Context chat visual smoke failed:\n- ${failures.join('\n- ')}`);
  }
}

async function assertContextChatAtViewport(page, viewport, options) {
  await page.setViewportSize(viewport);
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.locator('[data-testid="context-chat-toggle"]').waitFor();

  const toggleVisible = await page.locator('[data-testid="context-chat-toggle"]').isVisible();
  await page.locator('[data-testid="context-chat-toggle"]').click();
  await page.locator('[data-testid="context-chat-drawer"]').waitFor();

  const result = await page.evaluate(
    ({ viewportName, minWidth, maxWidth }) => {
      const drawer = document.querySelector('[data-testid="context-chat-drawer"]');
      const rect = drawer?.getBoundingClientRect();
      return {
        viewport: viewportName,
        toggleVisible: Boolean(document.querySelector('[data-testid="context-chat-toggle"]')) || true,
        drawerVisible: Boolean(drawer),
        drawerWidth: rect?.width ?? 0,
        drawerOverflow: drawer ? drawer.scrollWidth - drawer.clientWidth : 0,
        pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        minWidth,
        maxWidth
      };
    },
    { viewportName: options.name, minWidth: options.minWidth, maxWidth: options.maxWidth }
  );

  assertChatLayout({ ...result, toggleVisible });
}

async function main() {
  const server = runDevServer();
  let stderr = '';
  server.stderr.on('data', (chunk) => {
    stderr += chunk.toString();
  });

  try {
    await waitForServer();
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1440, height: 1024 }, locale: 'ru-RU' });

    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page.evaluate(() => window.localStorage.clear());
    await page.reload({ waitUntil: 'networkidle' });
    await page.locator('[role="tab"]').nth(1).click();
    await page.locator('[data-testid="source-row"]').first().waitFor();

    const result = await page.evaluate(() => {
      const toast = document.querySelector('.toast');
      const firstRow = document.querySelector('[data-testid="source-row"]');
      const title = firstRow?.querySelector('.source-title-button');
      const metaBar = firstRow?.querySelector('.source-row-meta-bar');
      const actionButtons = Array.from(firstRow?.querySelectorAll('.source-row-actions button') ?? []);
      const rowRect = firstRow?.getBoundingClientRect();
      const titleRect = title?.getBoundingClientRect();

      return {
        initialToastVisible: Boolean(toast),
        rowCount: document.querySelectorAll('[data-testid="source-row"]').length,
        hasMetaBar: Boolean(metaBar),
        rowOverflow: firstRow ? firstRow.scrollWidth - firstRow.clientWidth : 0,
        titleHeight: titleRect?.height ?? 0,
        titleWidth: titleRect?.width ?? 0,
        actionsOverflow: Boolean(
          rowRect &&
            actionButtons.some((button) => {
              const rect = button.getBoundingClientRect();
              return rect.left < rowRect.left - 1 || rect.right > rowRect.right + 1;
            })
        )
      };
    });

    assertLayout(result);

    await page.locator('.source-row-actions button').filter({ hasText: /Проверить вручную/i }).first().click();
    await page.locator('.toast').waitFor({ state: 'visible', timeout: 5000 });
    await page.waitForFunction(() => !document.querySelector('.toast'), undefined, { timeout: 6000 });

    await assertContextChatAtViewport(page, { width: 1440, height: 1024 }, { name: 'desktop', minWidth: 340, maxWidth: 500 });
    await assertContextChatAtViewport(page, { width: 1180, height: 820 }, { name: 'laptop', minWidth: 340, maxWidth: 500 });
    await assertContextChatAtViewport(page, { width: 390, height: 760 }, { name: 'mobile', minWidth: 360, maxWidth: 390 });

    await browser.close();
  } catch (error) {
    console.error(stderr);
    throw error;
  } finally {
    stopDevServer(server);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
