import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();

const APP_TSX_LIMIT = 350;
const APP_TEST_TSX_LIMIT = 850;
const LARGE_APP_DECLARATION_LIMIT = 1;

const LARGE_SOURCE_BASELINES = [
  {
    path: "src/features/author-memory/AuthorMemoryView.tsx",
    limit: 1460,
    next: "Author memory internals must keep moving into feature-local components before new UI is added.",
  },
  {
    path: "src/domain/editorialWorkspace.ts",
    limit: 170,
    next: "editorialWorkspace.ts must remain a thin compatibility barrel.",
  },
  {
    path: "src/features/editorial-model/EditorialModelView.tsx",
    limit: 1090,
    next: "Editorial model internals must keep moving into feature-local tab/panel modules.",
  },
  {
    path: "src/fixtures/demoWorkspace.ts",
    limit: 120,
    next: "demoWorkspace.ts must remain the public demo factory, not the fixture owner.",
  },
  {
    path: "src/features/signals/SignalsView.tsx",
    limit: 950,
    next: "Signals internals must keep moving into radar/signal component modules.",
  },
  {
    path: "src/application/editorialServices.ts",
    limit: 20,
    next: "editorialServices.ts must remain a compatibility barrel.",
  },
  {
    path: "src/domain/editorial-model/transitions.ts",
    limit: 640,
    next: "If editorial-model transitions grow, split them by rules, topics, fabulas, matrix, and validators.",
  },
  {
    path: "src/fixtures/demoImports.ts",
    limit: 410,
    next: "If import demo data grows, split it by sources, candidates, archive, and bulk examples.",
  },
];

const ADR_PATH =
  "docs/adr/2026-06-15-react-ui-uses-feature-modules-not-app-god-file.md";
const MODULE_GUARDRAILS_ADR_PATH =
  "docs/adr/2026-06-15-domain-feature-modules-have-size-boundary-guardrails.md";
const SAO_PATH = "docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md";

function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), "utf8");
}

function lineCount(text) {
  return text.split(/\r?\n/).length;
}

function fileExists(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function listFiles(dir, extensions) {
  const absoluteDir = path.join(ROOT, dir);
  if (!fs.existsSync(absoluteDir)) {
    return [];
  }

  const entries = fs.readdirSync(absoluteDir, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const fullPath = path.join(absoluteDir, entry.name);
    const relativePath = path.relative(ROOT, fullPath).replaceAll(path.sep, "/");

    if (entry.isDirectory()) {
      return listFiles(relativePath, extensions);
    }

    return extensions.some((extension) => entry.name.endsWith(extension)) ? [relativePath] : [];
  });
}

const failures = [];

function assert(condition, message) {
  if (!condition) {
    failures.push(message);
  }
}

const appSource = readText("src/App.tsx");
const appTestSource = readText("src/App.test.tsx");
const appLines = lineCount(appSource);
const appTestLines = lineCount(appTestSource);

assert(
  appLines <= APP_TSX_LIMIT,
  `src/App.tsx has ${appLines} lines; temporary limit is ${APP_TSX_LIMIT}. Extract UI before adding more.`
);

assert(
  appTestLines <= APP_TEST_TSX_LIMIT,
  `src/App.test.tsx has ${appTestLines} lines; temporary limit is ${APP_TEST_TSX_LIMIT}. Split tests before adding more.`
);

const largeDeclarationPattern =
  /^(?:export\s+)?function\s+([A-Z][A-Za-z0-9]*(?:View|Editor|Panel|Overlay|Card|Header|Sidebar|Topbar))\b/gm;
const largeDeclarations = [...appSource.matchAll(largeDeclarationPattern)].map(
  (match) => match[1]
);

assert(
  largeDeclarations.length <= LARGE_APP_DECLARATION_LIMIT,
  [
    `src/App.tsx has ${largeDeclarations.length} large UI declarations; temporary limit is ${LARGE_APP_DECLARATION_LIMIT}.`,
    `New declarations: ${largeDeclarations.join(", ")}`,
  ].join("\n")
);

assert(fileExists(ADR_PATH), `Missing ADR: ${ADR_PATH}`);
assert(
  fileExists(MODULE_GUARDRAILS_ADR_PATH),
  `Missing ADR: ${MODULE_GUARDRAILS_ADR_PATH}`
);

const requiredSourceFiles = [
  "src/app/AppShell.tsx",
  "src/app/Sidebar.tsx",
  "src/app/Topbar.tsx",
  "src/app/navigation.ts",
  "src/app/useWorkspaceController.ts",
  "src/app/contextChatScope.ts",
  "src/shared/ui/Icon.tsx",
  "src/features/author-memory/AuthorMemoryView.tsx",
  "src/features/author-memory/components.tsx",
  "src/features/author-memory/helpers.ts",
  "src/features/editorial-model/EditorialModelView.tsx",
  "src/features/editorial-model/ValidationPanel.tsx",
  "src/features/editorial-model/helpers.ts",
  "src/features/signals/SignalsView.tsx",
  "src/features/signals/helpers.tsx",
  "src/features/plan/PlanView.tsx",
  "src/features/briefing/BriefView.tsx",
  "src/features/editing/EditView.tsx",
  "src/features/release/ReleaseView.tsx",
  "src/features/analytics/AnalyticsView.tsx",
];

for (const requiredFile of requiredSourceFiles) {
  assert(fileExists(requiredFile), `Missing React architecture source file: ${requiredFile}`);
}

const largeSourceStats = [];

for (const baseline of LARGE_SOURCE_BASELINES) {
  assert(fileExists(baseline.path), `Missing large-file baseline target: ${baseline.path}`);

  if (fileExists(baseline.path)) {
    const lines = lineCount(readText(baseline.path));
    largeSourceStats.push({ ...baseline, lines });
    assert(
      lines <= baseline.limit,
      [
        `${baseline.path} has ${lines} lines; temporary limit is ${baseline.limit}.`,
        baseline.next,
      ].join("\n")
    );
  }
}

assert(
  !appSource.includes("LocalWorkspaceStore"),
  "src/App.tsx must not import or instantiate LocalWorkspaceStore; use src/app/useWorkspaceController.ts."
);

const forbiddenAppSignalsSymbols = [
  "function SignalsViewV2",
  "function RadarEditor",
  "function SignalsSidePanel",
  "function RadarView",
  "createRadarDraft",
  "isRadarSourceConfigurationValid",
  "radarSourceTypeLabel",
  "signalReviewStatusLabel",
];

for (const symbol of forbiddenAppSignalsSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain signals feature internals: ${symbol}. Use src/features/signals.`
  );
}

const forbiddenAppEditorialModelSymbols = [
  "function EditorialModelView",
  "function TopicEditor",
  "function FabulaEditor",
  "function TopicFabulaMatrixView",
  "function EditorialValidationPanel",
  "createEditorialRule",
  "createTopicDraft",
  "createFabulaDraft",
];

for (const symbol of forbiddenAppEditorialModelSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain editorial-model feature internals: ${symbol}. Use src/features/editorial-model.`
  );
}

const forbiddenAppAuthorMemorySymbols = [
  "function AuthorMemoryView",
  "function AuthorNoteCard",
  "function AssertionCard",
  "function ExternalSourcesView",
  "function ImportQueueView",
  "function ArchiveView",
  "function BulkActionDialog",
  "createAuthorMemoryEvent",
  "filterAuthorNotes",
  "getImportSummary",
  "sourceTypeLabel",
  "reviewStatusLabel",
];

for (const symbol of forbiddenAppAuthorMemorySymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain author-memory feature internals: ${symbol}. Use src/features/author-memory.`
  );
}

const forbiddenAppProductionSymbols = [
  "function PlanView",
  "function BriefView",
  "function EditView",
  "function ReleaseView",
  "function AnalyticsView",
  "function HitlGate",
  "function FieldInput",
  "function CheckCard",
  "function FinalTextView",
];

for (const symbol of forbiddenAppProductionSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain production-flow feature internals: ${symbol}. Use src/features/* and src/shared/* modules.`
  );
}

const featureFiles = listFiles("src/features", [".ts", ".tsx"]);
const importPattern = /from\s+["']([^"']+)["']/g;

for (const featureFile of featureFiles) {
  const [, featureName] = featureFile.match(/^src\/features\/([^/]+)\//) ?? [];
  if (!featureName) {
    continue;
  }

  const source = readText(featureFile);
  for (const match of source.matchAll(importPattern)) {
    const importPath = match[1];
    let resolvedImport = importPath;

    if (importPath.startsWith(".")) {
      resolvedImport = path
        .relative(ROOT, path.resolve(ROOT, path.dirname(featureFile), importPath))
        .replaceAll(path.sep, "/");
    }

    const [, importedFeature] =
      resolvedImport.match(/^src\/features\/([^/]+)/) ??
      importPath.match(/^src\/features\/([^/]+)/) ??
      [];

    if (!importedFeature) {
      continue;
    }

    assert(
      importedFeature === featureName,
      `${featureFile} imports another feature (${importedFeature}); feature -> feature imports are forbidden.`
    );
  }
}

const saoSource = readText(SAO_PATH);
const requiredSaoFragments = [
  "## React UI Architecture",
  "src/app/",
  "src/features/author-memory",
  "src/features/editorial-model",
  "src/features/signals",
  "src/features/plan",
  "src/features/briefing",
  "src/features/editing",
  "src/features/release",
  "src/features/analytics",
  "src/features/context-chat",
  "src/shared/ui",
  "src/shared/format",
  "features -> shared/application/domain",
  "no feature -> feature",
  "Large-file guardrails",
  "domain/application/fixtures/feature files must shrink through the 1.5.x refactoring chain",
];

for (const fragment of requiredSaoFragments) {
  assert(
    saoSource.includes(fragment),
    `SAO is missing required React architecture fragment: ${fragment}`
  );
}

if (failures.length > 0) {
  console.error("Architecture smoke failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("Architecture smoke passed.");
console.log(`- src/App.tsx: ${appLines}/${APP_TSX_LIMIT} lines`);
console.log(`- src/App.test.tsx: ${appTestLines}/${APP_TEST_TSX_LIMIT} lines`);
console.log(
  `- Large App.tsx UI declarations: ${largeDeclarations.length}/${LARGE_APP_DECLARATION_LIMIT}`
);
for (const stat of largeSourceStats) {
  console.log(`- ${stat.path}: ${stat.lines}/${stat.limit} lines`);
}
