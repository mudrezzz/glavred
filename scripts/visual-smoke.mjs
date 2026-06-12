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
