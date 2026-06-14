import { chromium } from '@playwright/test';
import { spawn, spawnSync } from 'node:child_process';

const rootDir = process.cwd();
const port = process.env.DESIGN_SMOKE_PORT ?? '4182';
const baseUrl = `http://127.0.0.1:${port}`;

function runDevServer() {
  const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  return spawn(npmCommand, ['run', 'dev', '--', '--host', '127.0.0.1', '--port', port, '--strictPort'], {
    cwd: rootDir,
    env: { ...process.env, BROWSER: 'none' },
    shell: process.platform === 'win32',
    stdio: ['ignore', 'pipe', 'pipe']
  });
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

function failIfAny(title, failures) {
  if (failures.length) {
    throw new Error(`${title} failed:\n- ${failures.join('\n- ')}`);
  }
}

function sharedDesignChecks() {
  function numberFromPx(value) {
    return Number.parseFloat(value || '0') || 0;
  }

  function minSameLineGap(elements) {
    const rects = Array.from(elements)
      .map((element) => element.getBoundingClientRect())
      .filter((rect) => rect.width > 0 && rect.height > 0)
      .sort((a, b) => a.top - b.top || a.left - b.left);
    const gaps = rects
      .slice(1)
      .map((rect, index) => ({ rect, prev: rects[index] }))
      .filter(({ rect, prev }) => Math.abs(rect.top - prev.top) < 8)
      .map(({ rect, prev }) => Math.round(rect.left - prev.right));
    return gaps.length ? Math.min(...gaps) : null;
  }

  function cardPaddingFailures() {
    const failures = [];
    const selectors = ['.project-profile-header', '.signals-section-header', '.panel', '.card:not(.signal-card):not(.radar-card)'];
    document.querySelectorAll(selectors.join(',')).forEach((element) => {
      const rect = element.getBoundingClientRect();
      if (rect.width < 80 || rect.height < 40) return;
      const style = window.getComputedStyle(element);
      const left = numberFromPx(style.paddingLeft);
      const right = numberFromPx(style.paddingRight);
      const top = numberFromPx(style.paddingTop);
      const bottom = numberFromPx(style.paddingBottom);
      if (Math.min(left, right, top, bottom) < 14) {
        failures.push(`${element.className || element.tagName}: padding is too small (${top}/${right}/${bottom}/${left}).`);
      }
    });
    return failures;
  }

  function columnGapFailures() {
    const failures = [];
    document.querySelectorAll('.memory-grid, .editorial-workspace, .signals-workspace-grid').forEach((grid) => {
      const children = Array.from(grid.children).filter((child) => {
        const rect = child.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
      if (children.length < 2) return;
      const [first, second] = children;
      const firstRect = first.getBoundingClientRect();
      const secondRect = second.getBoundingClientRect();
      const verticalOverlap = firstRect.bottom > secondRect.top && secondRect.bottom > firstRect.top;
      const sameRow = verticalOverlap || Math.abs(firstRect.top - secondRect.top) < 80;
      if (!sameRow) return;
      const gap = Math.round(secondRect.left - firstRect.right);
      const requiredGap = grid.classList.contains('signals-workspace-grid') ? 28 : 16;
      if (gap < requiredGap) {
        failures.push(`${grid.className}: main/side gap is too small (${gap}px).`);
      }
    });
    return failures;
  }

  function mainContentOverflowFailures() {
    const failures = [];
    document.querySelectorAll('.signals-workspace-grid').forEach((grid) => {
      const main = grid.querySelector('.memory-main');
      const side = grid.querySelector('.memory-side');
      if (!main || !side) return;
      const mainRect = main.getBoundingClientRect();
      const sideRect = side.getBoundingClientRect();
      const sameRow = mainRect.bottom > sideRect.top && sideRect.bottom > mainRect.top;
      const allowedRight = sameRow ? Math.min(mainRect.right, sideRect.left - 28) : mainRect.right;

      main.querySelectorAll(':scope > *').forEach((child) => {
        const rect = child.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 20) return;
        if (rect.right > allowedRight + 1) {
          failures.push(
            `${child.className || child.tagName}: overflows Signals main column by ${Math.round(rect.right - allowedRight)}px.`
          );
        }
      });
    });
    return failures;
  }

  function actionGapFailures() {
    const failures = [];
    document
      .querySelectorAll('.row-actions, .inline-actions, .composer-actions, .entity-actions-footer, .source-row-actions')
      .forEach((group) => {
        const buttons = group.querySelectorAll('button, .btn');
        if (buttons.length < 2) return;
        const minGap = minSameLineGap(buttons);
        if (minGap !== null && minGap < 8) {
          failures.push(`${group.className}: action gap is too small (${minGap}px).`);
        }
      });
    return failures;
  }

  function pageOverflowFailure() {
    const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    return overflow > 2 ? [`page overflows horizontally by ${overflow}px.`] : [];
  }

  return [
    ...pageOverflowFailure(),
    ...cardPaddingFailures(),
    ...columnGapFailures(),
    ...mainContentOverflowFailures(),
    ...actionGapFailures()
  ];
}

async function assertCommonDesign(page, label) {
  const failures = await page.evaluate(sharedDesignChecks);
  failIfAny(`${label} design contract`, failures);
}

async function assertSignalsDesign(page, viewportName) {
  await page.locator('[data-testid="signals-section-header"]').waitFor();
  const baseFailures = await page.evaluate(sharedDesignChecks);
  const specificFailures = await page.evaluate(() => {
    const failures = [];
    const header = document.querySelector('[data-testid="signals-section-header"]');
    const tabs = document.querySelector('.signal-tabs');
    const tabCount = tabs?.querySelector('.tab-count');
    const headerStats = header?.querySelector('.signals-header-stats');
    const radarEditor = document.querySelector('.radar-editor');
    const firstFormInput = radarEditor?.querySelector('.signal-edit-form input, .signal-edit-form textarea, .signal-edit-form select');
    const firstConfigSection = radarEditor?.querySelector('.radar-config-section');

    if (!header?.classList.contains('project-profile-header')) {
      failures.push('signals header does not reuse project-profile-header pattern.');
    }

    if (header && headerStats) {
      const headerRect = header.getBoundingClientRect();
      const statsRect = headerStats.getBoundingClientRect();
      const rightGap = Math.round(headerRect.right - statsRect.right);
      if (rightGap < 12 || rightGap > 32) {
        failures.push(`signals header metrics are not aligned to the right edge (${rightGap}px).`);
      }
    }

    if (!tabCount) {
      failures.push('signals tab count badge is missing.');
    } else {
      const rect = tabCount.getBoundingClientRect();
      const style = window.getComputedStyle(tabCount);
      const marginLeft = Number.parseFloat(style.marginLeft || '0') || 0;
      if (rect.width < 22 || rect.height < 22 || marginLeft < 6) {
        failures.push(`signals tab count badge is malformed (${Math.round(rect.width)}x${Math.round(rect.height)}, margin ${marginLeft}px).`);
      }
    }

    if (radarEditor && firstFormInput && firstConfigSection) {
      const inputRect = firstFormInput.getBoundingClientRect();
      const sectionRect = firstConfigSection.getBoundingClientRect();
      if (Math.abs(inputRect.left - sectionRect.left) > 2 || Math.abs(inputRect.right - sectionRect.right) > 2) {
        failures.push('radar editor grouped sections are not aligned with base fields.');
      }
    }

    return failures;
  });

  failIfAny(`${viewportName} signals design`, [...baseFailures, ...specificFailures]);
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
    const page = await browser.newPage({ viewport: { width: 1440, height: 1024 } });
    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page.evaluate(() => window.localStorage.clear());
    await page.reload({ waitUntil: 'networkidle' });

    await page.locator('.nav-item').nth(1).click();
    await page.locator('.project-profile-header').waitFor();
    await assertCommonDesign(page, 'editorial model');

    await page.locator('.nav-item').nth(2).click();
    await page.locator('[data-testid="radar-row"]').first().waitFor();
    await assertSignalsDesign(page, 'desktop');

    await page.locator('[data-testid="radar-row"]').first().locator('.radar-actions .btn').first().click();
    await page.locator('.radar-editor').waitFor();
    await assertSignalsDesign(page, 'desktop radar editor');

    await page.locator('.signal-tabs .tab').nth(1).click();
    await page.locator('[data-testid="source-signal-row"]').first().waitFor();
    await assertSignalsDesign(page, 'desktop found signals');

    await page.setViewportSize({ width: 1180, height: 820 });
    await page.reload({ waitUntil: 'networkidle' });
    await page.locator('.nav-item').nth(2).click();
    await page.locator('[data-testid="radar-row"]').first().waitFor();
    await assertSignalsDesign(page, 'laptop');

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
