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

  if (!result.triggerVisible) failures.push(`${result.viewport}: context chat topbar trigger is not visible.`);
  if (!result.drawerVisible) failures.push(`${result.viewport}: context chat drawer did not open.`);
  if (result.drawerOverflow > 2) failures.push(`${result.viewport}: context chat drawer overflows horizontally by ${result.drawerOverflow}px.`);
  if (result.drawerWidth < result.minWidth || result.drawerWidth > result.maxWidth) {
    failures.push(`${result.viewport}: context chat drawer width ${result.drawerWidth}px is outside ${result.minWidth}-${result.maxWidth}px.`);
  }
  if (!result.hasDrawerShadow) failures.push(`${result.viewport}: context chat drawer has no visual shadow.`);
  if (!result.hasLeftSeparation) failures.push(`${result.viewport}: context chat drawer has no left separation edge.`);
  if (Math.abs(result.viewportRight - result.drawerRight) > result.maxRightGap) {
    failures.push(`${result.viewport}: drawer right gap is ${Math.round(result.viewportRight - result.drawerRight)}px.`);
  }
  if (result.suggestionButtonHeight > 64) {
    failures.push(`${result.viewport}: suggestion action button is too tall (${result.suggestionButtonHeight}px).`);
  }
  if (result.firstSuggestionHeight > 360) {
    failures.push(`${result.viewport}: first suggestion card is too tall (${result.firstSuggestionHeight}px).`);
  }
  if (result.pageOverflow > 2) failures.push(`${result.viewport}: page overflows horizontally by ${result.pageOverflow}px.`);

  if (failures.length) {
    throw new Error(`Context chat visual smoke failed:\n- ${failures.join('\n- ')}`);
  }
}

function assertSignalsLayout(result) {
  const failures = [];

  if (!result.sectionHeaderExists) failures.push(`${result.viewport}: signals section header is missing.`);
  if (!result.radarRowCount) failures.push(`${result.viewport}: no radar rows rendered.`);
  if (!result.signalRowCount) failures.push(`${result.viewport}: no signal rows rendered.`);
  if (result.pageOverflow > 2) failures.push(`${result.viewport}: signals page overflows horizontally by ${result.pageOverflow}px.`);
  if (result.radarOverflow > 2) failures.push(`${result.viewport}: radar row overflows by ${result.radarOverflow}px.`);
  if (result.signalOverflow > 2) failures.push(`${result.viewport}: signal row overflows by ${result.signalOverflow}px.`);
  if (result.workspaceGap !== null && result.workspaceGap < 16) failures.push(`${result.viewport}: signals main/side columns overlap or have too little gap (${result.workspaceGap}px).`);
  if (!result.radarHasFrame) failures.push(`${result.viewport}: radar row has no visible frame/background.`);
  if (!result.signalHasFrame) failures.push(`${result.viewport}: signal row has no visible frame/background.`);
  if (result.radarStatusHeight > 44) failures.push(`${result.viewport}: radar status chip is too tall (${result.radarStatusHeight}px).`);
  if (result.signalStatusHeight > 44) failures.push(`${result.viewport}: signal status chip is too tall (${result.signalStatusHeight}px).`);
  if (!result.radarStatusNoWrap) failures.push(`${result.viewport}: radar status chip can wrap.`);
  if (!result.signalStatusNoWrap) failures.push(`${result.viewport}: signal status chip can wrap.`);
  if (!result.filterToolbarHasFrame) failures.push(`${result.viewport}: signal filter toolbar has no frame.`);
  if (result.expandedSignalEscapesCard) failures.push(`${result.viewport}: expanded signal details escape the signal card.`);
  if (result.radarActionMinGap !== null && result.radarActionMinGap < 8) failures.push(`${result.viewport}: radar action buttons are too close (${result.radarActionMinGap}px).`);
  if (result.signalActionMinGap !== null && result.signalActionMinGap < 8) failures.push(`${result.viewport}: signal action buttons are too close (${result.signalActionMinGap}px).`);
  if (result.sideActionGap !== null && result.sideActionGap < 12) failures.push(`${result.viewport}: signal side action has too little top spacing (${result.sideActionGap}px).`);
  if (result.radarEditorOverflow > 2) failures.push(`${result.viewport}: radar editor content overflows by ${result.radarEditorOverflow}px.`);
  if (result.radarEditorSectionGap !== null && result.radarEditorSectionGap < 12) failures.push(`${result.viewport}: radar editor sections are too cramped (${result.radarEditorSectionGap}px).`);
  if (result.signalTitleWidth !== null && result.signalTitleWidth < 180 && result.viewport !== 'mobile') failures.push(`${result.viewport}: signal title column is too narrow (${result.signalTitleWidth}px).`);

  if (failures.length) {
    throw new Error(`Signals visual smoke failed:\n- ${failures.join('\n- ')}`);
  }
}

async function assertSignalsAtViewport(page, viewport, viewportName) {
  await page.setViewportSize(viewport);
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Сигналы/i }).click();
  await page.locator('[data-testid="radar-row"]').first().waitFor();

  const radarResult = await page.evaluate((name) => {
    const radarRow = document.querySelector('[data-testid="radar-row"]');
    const radarStatus = radarRow?.querySelector('.radar-status');
    const radarActions = Array.from(radarRow?.querySelectorAll('.radar-actions .btn') ?? []);
    const sidePanel = document.querySelector('.signal-side-panel');
    const sideSummary = sidePanel?.querySelector('.signal-summary-grid');
    const sideAction = sidePanel?.querySelector('.btn.wide');
    const main = document.querySelector('.signals-workspace-grid .memory-main');
    const side = document.querySelector('.signals-workspace-grid .memory-side');
    const radarStyle = radarRow ? window.getComputedStyle(radarRow) : null;
    const radarStatusStyle = radarStatus ? window.getComputedStyle(radarStatus) : null;
    const sideSummaryRect = sideSummary?.getBoundingClientRect();
    const sideActionRect = sideAction?.getBoundingClientRect();
    const mainRect = main?.getBoundingClientRect();
    const sideRect = side?.getBoundingClientRect();
    const actionRects = radarActions.map((element) => element.getBoundingClientRect()).sort((a, b) => a.top - b.top || a.left - b.left);
    const sameLineGaps = actionRects
      .slice(1)
      .map((rect, index) => ({ rect, prev: actionRects[index] }))
      .filter(({ rect, prev }) => Math.abs(rect.top - prev.top) < 8)
      .map(({ rect, prev }) => Math.round(rect.left - prev.right));
    const radarActionMinGap = sameLineGaps.length ? Math.min(...sameLineGaps) : null;
    const workspaceGap =
      mainRect && sideRect && Math.abs(mainRect.top - sideRect.top) < 80 ? Math.round(sideRect.left - mainRect.right) : null;

    return {
      viewport: name,
      sectionHeaderExists: Boolean(document.querySelector('[data-testid="signals-section-header"]')),
      radarRowCount: document.querySelectorAll('[data-testid="radar-row"]').length,
      pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      radarOverflow: radarRow ? radarRow.scrollWidth - radarRow.clientWidth : 0,
      workspaceGap,
      radarHasFrame: Boolean(
        radarStyle &&
          radarStyle.borderStyle !== 'none' &&
          Number.parseFloat(radarStyle.borderWidth || '0') >= 1 &&
          radarStyle.backgroundColor !== 'rgba(0, 0, 0, 0)'
      ),
      radarStatusHeight: radarStatus?.getBoundingClientRect().height ?? 0,
      radarStatusNoWrap: radarStatusStyle?.whiteSpace === 'nowrap',
      radarActionMinGap,
      sideActionGap: sideSummaryRect && sideActionRect ? Math.round(sideActionRect.top - sideSummaryRect.bottom) : null
    };
  }, viewportName);

  await page.locator('[data-testid="radar-row"]').first().getByRole('button', { name: /Редактировать/i }).click();
  await page.locator('.radar-editor').waitFor();
  const radarEditorResult = await page.evaluate((name) => {
    const editor = document.querySelector('.radar-editor');
    const sections = Array.from(editor?.querySelectorAll('.radar-config-section') ?? []);
    const sectionRects = sections.map((section) => section.getBoundingClientRect()).sort((a, b) => a.top - b.top);
    const sectionGap =
      sectionRects.length > 1
        ? Math.min(...sectionRects.slice(1).map((rect, index) => Math.round(rect.top - sectionRects[index].bottom)))
        : null;

    return {
      viewport: name,
      radarEditorOverflow: editor ? editor.scrollWidth - editor.clientWidth : 0,
      radarEditorSectionGap: sectionGap
    };
  }, viewportName);

  await page.getByRole('button', { name: /Найденные сигналы/i }).click();
  await page.locator('[data-testid="source-signal-row"]').first().waitFor();
  await page.locator('[data-testid="source-signal-row"]').first().locator('.signal-row-main').click();

  const signalResult = await page.evaluate((name) => {
    const signalRow = document.querySelector('[data-testid="source-signal-row"]');
    const signalStatus = signalRow?.querySelector('.signal-status');
    const signalTitle = signalRow?.querySelector('.signal-title');
    const signalActions = Array.from(signalRow?.querySelectorAll('.signal-actions .btn') ?? []);
    const filterToolbar = document.querySelector('[data-testid="signal-filter-toolbar"]');
    const signalDetails = signalRow?.querySelector('.radar-details');
    const signalStyle = signalRow ? window.getComputedStyle(signalRow) : null;
    const filterStyle = filterToolbar ? window.getComputedStyle(filterToolbar) : null;
    const signalStatusStyle = signalStatus ? window.getComputedStyle(signalStatus) : null;
    const signalRowRect = signalRow?.getBoundingClientRect();
    const detailRect = signalDetails?.getBoundingClientRect();
    const actionRects = signalActions.map((element) => element.getBoundingClientRect()).sort((a, b) => a.top - b.top || a.left - b.left);
    const sameLineGaps = actionRects
      .slice(1)
      .map((rect, index) => ({ rect, prev: actionRects[index] }))
      .filter(({ rect, prev }) => Math.abs(rect.top - prev.top) < 8)
      .map(({ rect, prev }) => Math.round(rect.left - prev.right));
    const signalActionMinGap = sameLineGaps.length ? Math.min(...sameLineGaps) : null;

    return {
      viewport: name,
      signalRowCount: document.querySelectorAll('[data-testid="source-signal-row"]').length,
      pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      signalOverflow: signalRow ? signalRow.scrollWidth - signalRow.clientWidth : 0,
      signalHasFrame: Boolean(
        signalStyle &&
          signalStyle.borderStyle !== 'none' &&
          Number.parseFloat(signalStyle.borderWidth || '0') >= 1 &&
          signalStyle.backgroundColor !== 'rgba(0, 0, 0, 0)'
      ),
      signalStatusHeight: signalStatus?.getBoundingClientRect().height ?? 0,
      signalStatusNoWrap: signalStatusStyle?.whiteSpace === 'nowrap',
      signalTitleWidth: signalTitle ? Math.round(signalTitle.getBoundingClientRect().width) : null,
      signalActionMinGap,
      filterToolbarHasFrame: Boolean(
        filterStyle &&
          filterStyle.borderStyle !== 'none' &&
          Number.parseFloat(filterStyle.borderWidth || '0') >= 1 &&
          filterStyle.backgroundColor !== 'rgba(0, 0, 0, 0)'
      ),
      expandedSignalEscapesCard: Boolean(
        signalRowRect &&
          detailRect &&
          (detailRect.left < signalRowRect.left - 1 ||
            detailRect.right > signalRowRect.right + 1 ||
            detailRect.bottom > signalRowRect.bottom + 1)
      )
    };
  }, viewportName);

  assertSignalsLayout({
    ...radarResult,
    ...radarEditorResult,
    ...signalResult,
    pageOverflow: Math.max(radarResult.pageOverflow, signalResult.pageOverflow),
    radarRowCount: radarResult.radarRowCount,
    signalRowCount: signalResult.signalRowCount
  });
}

async function assertContextChatAtViewport(page, viewport, options) {
  await page.setViewportSize(viewport);
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.evaluate(() => window.localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  await page.getByRole('button', { name: /Редакционная модель/i }).click();
  await page.locator('.validation-panel').waitFor();
  await page.locator('[data-testid="context-chat-topbar-trigger"]').waitFor();

  const triggerVisible = await page.locator('[data-testid="context-chat-topbar-trigger"]').isVisible();
  await page.locator('[data-testid="context-chat-topbar-trigger"]').click();
  await page.locator('[data-testid="context-chat-drawer"]').waitFor();
  await page.getByRole('tab', { name: /Подсказки/i }).click();
  await page.locator('.context-suggestion').first().waitFor();

  const result = await page.evaluate(
    ({ viewportName, minWidth, maxWidth, maxRightGap }) => {
      const drawer = document.querySelector('[data-testid="context-chat-drawer"]');
      const firstSuggestion = document.querySelector('.context-suggestion');
      const suggestionButton = firstSuggestion?.querySelector('.btn');
      const rect = drawer?.getBoundingClientRect();
      const drawerStyle = drawer ? window.getComputedStyle(drawer) : null;
      const suggestionRect = firstSuggestion?.getBoundingClientRect();
      const suggestionButtonRect = suggestionButton?.getBoundingClientRect();
      return {
        viewport: viewportName,
        triggerVisible: Boolean(document.querySelector('[data-testid="context-chat-topbar-trigger"]')),
        drawerVisible: Boolean(drawer),
        drawerWidth: rect?.width ?? 0,
        drawerLeft: rect?.left ?? 0,
        drawerRight: rect?.right ?? 0,
        viewportRight: window.innerWidth,
        hasDrawerShadow: Boolean(drawerStyle && drawerStyle.boxShadow !== 'none'),
        hasLeftSeparation: Boolean(
          drawerStyle &&
            drawerStyle.borderLeftStyle !== 'none' &&
            Number.parseFloat(drawerStyle.borderLeftWidth || '0') >= 1
        ),
        firstSuggestionHeight: suggestionRect?.height ?? 0,
        suggestionButtonHeight: suggestionButtonRect?.height ?? 0,
        drawerOverflow: drawer ? drawer.scrollWidth - drawer.clientWidth : 0,
        pageOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        maxRightGap,
        minWidth,
        maxWidth
      };
    },
    {
      viewportName: options.name,
      minWidth: options.minWidth,
      maxWidth: options.maxWidth,
      maxRightGap: options.maxRightGap
    }
  );

  assertChatLayout({ ...result, triggerVisible });
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

    await assertContextChatAtViewport(page, { width: 1440, height: 1024 }, { name: 'desktop', minWidth: 340, maxWidth: 390, maxRightGap: 24 });
    await assertContextChatAtViewport(page, { width: 1180, height: 820 }, { name: 'laptop', minWidth: 340, maxWidth: 390, maxRightGap: 24 });
    await assertContextChatAtViewport(page, { width: 390, height: 760 }, { name: 'mobile', minWidth: 360, maxWidth: 390, maxRightGap: 2 });
    await assertSignalsAtViewport(page, { width: 1440, height: 1024 }, 'desktop');
    await assertSignalsAtViewport(page, { width: 1180, height: 820 }, 'laptop');
    await assertSignalsAtViewport(page, { width: 390, height: 760 }, 'mobile');

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
