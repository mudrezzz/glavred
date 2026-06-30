import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();

const APP_TSX_LIMIT = 350;
const APP_TEST_TSX_LIMIT = 300;
const LARGE_APP_DECLARATION_LIMIT = 1;
const NEAR_LIMIT_RATIO = 0.85;
const DEFAULT_EXPORT_COUNT_WARNING_LIMIT = 12;

const LARGE_SOURCE_BASELINES = [
  {
    path: "src/app/useWorkspaceController.ts",
    limit: 220,
    next: "useWorkspaceController must stay a public facade over role-owned app hooks.",
  },
  {
    path: "src/app/useWorkspacePersistence.ts",
    limit: 170,
    next: "Workspace persistence should own load/save/reset/toast and basic patch helpers only.",
  },
  {
    path: "src/app/useContextChatController.ts",
    limit: 220,
    next: "Context chat state and suggestions should stay in this app hook or split by chat/suggestions role.",
  },
  {
    path: "src/app/useSignalsWorkspaceActions.ts",
    limit: 180,
    next: "Signals workspace actions should stay app-level orchestration without feature UI or storage ownership.",
  },
  {
    path: "src/app/usePostCandidateWorkspaceActions.ts",
    limit: 80,
    next: "Post candidate workspace actions should own candidate selection and downstream reset only.",
  },
  {
    path: "src/app/useProductionFlowActions.ts",
    limit: 260,
    next: "Production flow actions should stay app-level orchestration and split by plan/release if they grow.",
  },
  {
    path: "src/app/releaseExport.ts",
    limit: 90,
    next: "Release export helpers should stay limited to browser clipboard/download edges.",
  },
  {
    path: "src/features/author-memory/AuthorMemoryView.tsx",
    limit: 320,
    next: "AuthorMemoryView must stay a feature composition root; put feed/import orchestration in feature-local hooks and views.",
  },
  {
    path: "src/features/author-memory/useMemoryFeedController.ts",
    limit: 280,
    next: "Memory feed state should stay in this hook or be split by composer/edit/correction role.",
  },
  {
    path: "src/features/author-memory/useImportReviewController.ts",
    limit: 300,
    next: "Import review state should stay in this hook or be split by queue/archive role.",
  },
  {
    path: "src/features/author-memory/MemoryFeedTab.tsx",
    limit: 260,
    next: "MemoryFeedTab should stay focused on composer, toolbar, and feed rendering.",
  },
  {
    path: "src/features/author-memory/MemorySidePanel.tsx",
    limit: 140,
    next: "MemorySidePanel should stay summary/assertion-only.",
  },
  {
    path: "src/features/author-memory/MemoryDialogs.tsx",
    limit: 120,
    next: "MemoryDialogs should stay limited to author-memory modal/confirmation surfaces.",
  },
  {
    path: "src/domain/editorialWorkspace.ts",
    limit: 170,
    next: "editorialWorkspace.ts must remain a thin compatibility barrel.",
  },
  {
    path: "src/features/editorial-model/EditorialModelView.tsx",
    limit: 220,
    next: "Editorial model internals must keep moving into feature-local tab/panel modules.",
  },
  {
    path: "src/fixtures/demoWorkspace.ts",
    limit: 120,
    next: "demoWorkspace.ts must remain the public demo factory, not the fixture owner.",
  },
  {
    path: "src/features/signals/SignalsView.tsx",
    limit: 180,
    next: "SignalsView must stay a composition root; keep radar/signal state and tab UI in feature-local modules.",
  },
  {
    path: "src/features/signals/useSignalsController.ts",
    limit: 280,
    next: "Signals tab/filter/edit state should stay in this hook or be split by radar/signal role.",
  },
  {
    path: "src/features/signals/RadarsTab.tsx",
    limit: 220,
    next: "RadarsTab should stay focused on toolbar, new radar editor, and radar list composition.",
  },
  {
    path: "src/features/signals/RadarCard.tsx",
    limit: 240,
    next: "RadarCard should stay focused on one radar row/detail/edit surface.",
  },
  {
    path: "src/features/signals/FoundSignalsTab.tsx",
    limit: 220,
    next: "FoundSignalsTab should stay focused on filter toolbar and signal list composition.",
  },
  {
    path: "src/features/signals/SourceSignalCard.tsx",
    limit: 260,
    next: "SourceSignalCard should stay focused on one found signal row/detail/edit surface.",
  },
  {
    path: "src/features/signals/SignalsHeader.tsx",
    limit: 100,
    next: "SignalsHeader should stay focused on section title and header metrics.",
  },
  {
    path: "src/features/signals/SignalsTabs.tsx",
    limit: 80,
    next: "SignalsTabs should stay focused on tab switching only.",
  },
  {
    path: "src/features/signals/PostCandidatesPreviewTab.tsx",
    limit: 120,
    next: "PostCandidatesPreviewTab should stay a composition root; keep card UI and candidate derivation in role-owned modules.",
  },
  {
    path: "src/features/signals/PostCandidateCard.tsx",
    limit: 130,
    next: "PostCandidateCard should stay focused on one compare-and-approve candidate card.",
  },
  {
    path: "src/features/signals/PostCandidateCardParts.tsx",
    limit: 40,
    next: "PostCandidateCardParts should stay limited to small candidate-card display helpers.",
  },
  {
    path: "src/features/signals/PostCandidatesToolbar.tsx",
    limit: 120,
    next: "PostCandidatesToolbar should stay focused on candidate filters, search, and list/group mode controls.",
  },
  {
    path: "src/features/signals/PostCandidateGroupList.tsx",
    limit: 110,
    next: "PostCandidateGroupList should stay focused on grouped candidate rendering.",
  },
  {
    path: "src/features/signals/PostCandidateEditForm.tsx",
    limit: 110,
    next: "PostCandidateEditForm should stay limited to inline candidate field editing.",
  },
  {
    path: "src/features/signals/PostCandidateEditContext.tsx",
    limit: 70,
    next: "PostCandidateEditContext should stay limited to source/topic/fabula edit context.",
  },
  {
    path: "src/features/signals/usePostCandidatesController.ts",
    limit: 60,
    next: "Candidate tab derivation should stay separate from useSignalsController.",
  },
  {
    path: "src/features/signals/postCandidateFilters.ts",
    limit: 80,
    next: "Candidate filters and grouping should stay local deterministic UI logic.",
  },
  {
    path: "src/application/postCandidateService.ts",
    limit: 120,
    next: "Candidate assembly should remain deterministic application logic until AI generation is introduced behind a service boundary.",
  },
  {
    path: "src/application/planningService.ts",
    limit: 180,
    next: "Planning service should keep deterministic slot assembly separate from demand and schedule helpers.",
  },
  {
    path: "src/application/planningDemandService.ts",
    limit: 70,
    next: "Planning demand summary should stay a small application helper over candidates and settings.",
  },
  {
    path: "src/application/editorialServices.ts",
    limit: 20,
    next: "editorialServices.ts must remain a compatibility barrel.",
  },
  {
    path: "src/domain/editorial-model/transitions.ts",
    limit: 20,
    next: "If editorial-model transitions grow, split them by rules, topics, fabulas, matrix, and validators.",
  },
  {
    path: "src/domain/editorial-model/rules.ts",
    limit: 50,
    next: "Editorial rule transitions should stay small and role-owned.",
  },
  {
    path: "src/domain/editorial-model/validation.ts",
    limit: 460,
    next: "If editorial validation grows, split individual validators into dedicated modules.",
  },
  {
    path: "src/domain/editorial-model/catalog.ts",
    limit: 190,
    next: "Topic/fabula/matrix transitions should stay catalog-owned.",
  },
  {
    path: "src/features/author-memory/ImportViews.tsx",
    limit: 20,
    next: "ImportViews.tsx must remain a feature-local compatibility barrel.",
  },
  {
    path: "src/features/author-memory/ExternalSourcesView.tsx",
    limit: 190,
    next: "External source UI should stay separate from memory feed and import queue logic.",
  },
  {
    path: "src/features/author-memory/ImportQueueView.tsx",
    limit: 150,
    next: "ImportQueueView should stay a composition root for queue toolbar, bulk bar, and list/group rendering.",
  },
  {
    path: "src/features/author-memory/ImportQueueToolbar.tsx",
    limit: 120,
    next: "ImportQueueToolbar should stay focused on filters and list/group mode controls.",
  },
  {
    path: "src/features/author-memory/ImportQueueBulkBar.tsx",
    limit: 130,
    next: "ImportQueueBulkBar should stay focused on selection summary and bulk actions.",
  },
  {
    path: "src/features/author-memory/ImportCandidateGroupList.tsx",
    limit: 140,
    next: "ImportCandidateGroupList should stay focused on grouped candidate rendering.",
  },
  {
    path: "src/features/author-memory/ImportCandidateList.tsx",
    limit: 120,
    next: "ImportCandidateList should stay focused on candidate list rendering.",
  },
  {
    path: "src/features/author-memory/ImportQueueEmptyState.tsx",
    limit: 60,
    next: "ImportQueueEmptyState should stay a tiny empty/resultless state component.",
  },
  {
    path: "src/features/author-memory/CandidateCard.tsx",
    limit: 170,
    next: "CandidateCard should stay focused on one imported candidate.",
  },
  {
    path: "src/features/author-memory/ArchiveView.tsx",
    limit: 150,
    next: "Archive UI should stay separate from import queue review logic.",
  },
  {
    path: "src/features/author-memory/BulkActionDialog.tsx",
    limit: 130,
    next: "Bulk action confirmation should stay a small dialog component.",
  },
  {
    path: "src/features/editorial-model/EditorialModelParts.tsx",
    limit: 20,
    next: "EditorialModelParts.tsx must remain a feature-local compatibility barrel.",
  },
  {
    path: "src/features/editorial-model/ProjectProfileHeader.tsx",
    limit: 160,
    next: "Project profile header must stay separate from rules, topics, and matrix UI.",
  },
  {
    path: "src/features/editorial-model/PublisherRulesView.tsx",
    limit: 260,
    next: "Publisher rules UI should stay focused on rules and rule editing.",
  },
  {
    path: "src/features/editorial-model/TopicsTab.tsx",
    limit: 310,
    next: "Topics tab should be split again if topic editor/list behavior grows.",
  },
  {
    path: "src/features/editorial-model/FabulasTab.tsx",
    limit: 310,
    next: "Fabulas tab should be split again if fabula editor/list behavior grows.",
  },
  {
    path: "src/features/editorial-model/MatrixTab.tsx",
    limit: 140,
    next: "Matrix UI should stay focused on compatibility editing.",
  },
  {
    path: "src/features/plan/PlanView.tsx",
    limit: 160,
    next: "PlanView must stay a composition root for grid/settings modes.",
  },
  {
    path: "src/features/plan/PlanSettingsPanel.tsx",
    limit: 220,
    next: "Plan settings UI should split field groups before adding platform-specific settings.",
  },
  {
    path: "src/features/plan/BroadcastGridList.tsx",
    limit: 100,
    next: "BroadcastGridList should stay focused on toolbar and row composition.",
  },
  {
    path: "src/features/plan/BroadcastGridRow.tsx",
    limit: 190,
    next: "BroadcastGridRow should stay focused on one slot row/detail/edit surface.",
  },
  {
    path: "src/features/plan/BroadcastGridAside.tsx",
    limit: 110,
    next: "BroadcastGridAside should stay limited to planning summary and warnings.",
  },
  {
    path: "src/features/editing/EditorialVisualStage.tsx",
    limit: 220,
    next: "EditorialVisualStage should stay focused on visual decision UI; keep real generation/search adapters outside React.",
  },
  {
    path: "src/features/editing/EditorialVisualFields.tsx",
    limit: 140,
    next: "Visual mode fields should stay presentational; keep visual generation/search logic in application/domain adapters.",
  },
  {
    path: "src/features/editing/EditorialVisualVariants.tsx",
    limit: 150,
    next: "Visual variant cards should stay presentational; keep variant generation in application services.",
  },
  {
    path: "src/features/editing/EditorialVisualMemeReferences.tsx",
    limit: 120,
    next: "Meme reference cards should stay presentational; keep reference search and remix logic in application services.",
  },
  {
    path: "src/application/visualVariantService.ts",
    limit: 130,
    next: "Visual variant service should stay deterministic until real adapters are introduced behind explicit ports.",
  },
  {
    path: "src/application/visualMemeRemixService.ts",
    limit: 120,
    next: "Meme remix placeholder service should stay deterministic until real search/remix adapters are introduced behind explicit ports.",
  },
  {
    path: "src/application/draftRunContext.ts",
    limit: 300,
    next: "DraftRun context builder should stay a pure snapshot helper; split selectors before adding retrieval or backend persistence.",
  },
  {
    path: "src/application/postCandidateLinking.ts",
    limit: 90,
    next: "Post candidate linking should stay a pure selector shared by plan approval and DraftRun context.",
  },
  {
    path: "src/infrastructure/backendDraftClient.ts",
    limit: 90,
    next: "Backend draft client should stay a thin HTTP mapper; move orchestration into app/application modules.",
  },
  {
    path: "src/infrastructure/draftRunClient.ts",
    limit: 170,
    next: "DraftRun client should stay a thin polling HTTP mapper; keep orchestration in app controllers.",
  },
  {
    path: "src/infrastructure/draftRunProgress.ts",
    limit: 70,
    next: "DraftRun progress mapper should stay a thin artifact read-model helper.",
  },
  {
    path: "src/infrastructure/draftRunBlocked.ts",
    limit: 60,
    next: "DraftRun blocked mapper should stay focused on quality-blocked response interpretation.",
  },
  {
    path: "src/infrastructure/draftRunRequestPayload.ts",
    limit: 50,
    next: "DraftRun request payload mapper should stay serialization-only.",
  },
  {
    path: "src/app/productionDraftActions.ts",
    limit: 70,
    next: "Production draft actions should stay a thin workspace patch builder for backend-generated drafts.",
  },
  {
    path: "src/app/productionVisualActions.ts",
    limit: 90,
    next: "Visual production actions should stay a thin workspace orchestration layer.",
  },
  {
    path: "src/domain/planning/settings.ts",
    limit: 120,
    next: "Planning settings normalization should stay pure and split platform policy when introduced.",
  },
  {
    path: "src/domain/planning/schedule.ts",
    limit: 80,
    next: "Planning schedule helpers should stay pure and split calendar math if it grows.",
  },
  {
    path: "src/features/signals/RadarEditor.tsx",
    limit: 270,
    next: "Radar editor should stay separate from signals list and side panel UI.",
  },
  {
    path: "src/features/signals/SignalsSidePanel.tsx",
    limit: 100,
    next: "Signals side panel should stay compact and summary-focused.",
  },
  {
    path: "src/fixtures/demoImports.ts",
    limit: 410,
    next: "If import demo data grows, split it by sources, candidates, archive, and bulk examples.",
  },
];

const TEST_FILE_BASELINES = [
  {
    path: "src/App.test.tsx",
    limit: APP_TEST_TSX_LIMIT,
    next: "App.test.tsx should cover app shell and navigation only; move feature flows into feature-owned *AppFlow.test.tsx files.",
  },
  {
    path: "src/test-support/productionFlowDriver.ts",
    limit: 120,
    next: "Production flow test helpers should stay small and avoid hidden business logic.",
  },
  {
    path: "src/test-support/signalsFlowDriver.ts",
    limit: 60,
    next: "Signals flow test helpers should stay focused on navigation shortcuts.",
  },
  {
    path: "src/features/signals/SignalsAppFlow.test.tsx",
    limit: 180,
    next: "Signals app-flow tests should split by radar/signal/candidate workflow before growing further.",
  },
  {
    path: "src/features/author-memory/AuthorMemoryAppFlow.test.tsx",
    limit: 400,
    next: "Author-memory app-flow tests should split by import queue, archive, composer, and feed workflows before growing further.",
  },
  {
    path: "src/features/context-chat/ContextChatAppFlow.test.tsx",
    limit: 140,
    next: "Context-chat app-flow tests should stay focused on assistant shell and suggestion workflows.",
  },
  {
    path: "src/features/editorial-model/EditorialModelAppFlow.test.tsx",
    limit: 180,
    next: "Editorial-model app-flow tests should split by rules/topics/fabulas/matrix when needed.",
  },
  {
    path: "src/features/plan/PlanAppFlow.test.tsx",
    limit: 120,
    next: "Plan app-flow tests should stay focused on grid/settings integration; move detailed UI tests to feature components.",
  },
  {
    path: "src/features/editing/EditorialWorkbenchAppFlow.test.tsx",
    limit: 140,
    next: "Editing app-flow tests should stay focused on queue/workbench integration.",
  },
  {
    path: "src/features/editing/EditorialWorkbenchDraftRunStatus.test.tsx",
    limit: 120,
    next: "DraftRun status UI tests should stay focused on long-running/stale generation behavior.",
  },
  {
    path: "src/features/release/ReleaseAppFlow.test.tsx",
    limit: 120,
    next: "Release app-flow tests should stay focused on release-log/manual-export integration.",
  },
  {
    path: "src/features/analytics/AnalyticsAppFlow.test.tsx",
    limit: 120,
    next: "Analytics app-flow tests should stay focused on learning-note integration.",
  },
  {
    path: "src/features/editing/EditView.test.tsx",
    limit: 720,
    next: "EditView tests should split by posts/workbench/fabula/draft/visual stage ownership before growing further.",
  },
  {
    path: "src/app/editorialWorkQueueActions.test.ts",
    limit: 420,
    next: "Editorial work queue action tests should split by planning handoff, brief/draft, and visual transitions before growing further.",
  },
  {
    path: "src/domain/editorialWorkspace.test.ts",
    limit: 850,
    next: "Editorial workspace domain tests should split by bounded domain ownership before growing further.",
  },
  {
    path: "src/infrastructure/localWorkspaceStore.test.ts",
    limit: 820,
    next: "Local workspace store tests should split migration/normalize/persistence cases before growing further.",
  },
  {
    path: "src/infrastructure/backendDraftClient.test.ts",
    limit: 90,
    next: "Backend draft client tests should stay focused on request/response mapping.",
  },
  {
    path: "src/infrastructure/draftRunClient.test.ts",
    limit: 130,
    next: "DraftRun client tests should stay focused on run start/poll/final-draft mapping.",
  },
  {
    path: "src/infrastructure/draftRunClientBlocked.test.ts",
    limit: 80,
    next: "DraftRun blocked-run tests should stay focused on quality-blocked mapping only.",
  },
  {
    path: "src/application/draftRunContext.test.ts",
    limit: 160,
    next: "DraftRun context tests should stay focused on workspace snapshot resolution.",
  },
  {
    path: "src/application/draftRunCandidateRecovery.test.ts",
    limit: 120,
    next: "DraftRun candidate recovery tests should stay focused on candidate link fallback cases.",
  },
  {
    path: "src/app/productionDraftActions.test.ts",
    limit: 70,
    next: "Production draft action tests should stay focused on generated-draft workspace sync.",
  },
];

const BACKEND_SOURCE_BASELINES = [
  {
    path: "backend/app/main.py",
    limit: 60,
    next: "FastAPI app factory should stay a thin composition root.",
  },
  {
    path: "backend/app/settings.py",
    limit: 100,
    next: "Backend settings should stay focused on typed environment configuration.",
  },
  {
    path: "backend/app/api/dependencies.py",
    limit: 60,
    next: "API dependencies should stay limited to request-time service wiring.",
  },
  {
    path: "backend/app/api/health.py",
    limit: 60,
    next: "Health routes should stay thin and delegate behavior to application services.",
  },
  {
    path: "backend/app/api/ai_runs.py",
    limit: 120,
    next: "AI run routes should stay thin and delegate orchestration to AiRunService.",
  },
  {
    path: "backend/app/api/drafts.py",
    limit: 130,
    next: "Draft routes should stay thin and delegate generation to DraftGenerationService.",
  },
  {
    path: "backend/app/api/draft_generation_contracts.py",
    limit: 100,
    next: "Draft request/response contracts should stay mapping-only and framework-light.",
  },
  {
    path: "backend/app/api/draft_runs.py",
    limit: 120,
    next: "DraftRun routes should stay thin and delegate orchestration to DraftRunService.",
  },
  {
    path: "backend/app/api/portfolio.py",
    limit: 130,
    next: "Portfolio routes should stay thin and delegate auth/project logic to PortfolioService.",
  },
  {
    path: "backend/app/api/portfolio_contracts.py",
    limit: 140,
    next: "Portfolio API contracts should stay HTTP-shape mapping only.",
  },
  {
    path: "backend/app/application/health_service.py",
    limit: 90,
    next: "Health service should stay focused on liveness/readiness orchestration.",
  },
  {
    path: "backend/app/application/ai_run_service.py",
    limit: 100,
    next: "AI run service should own audit orchestration only; provider execution belongs in later services.",
  },
  {
    path: "backend/app/application/draft_generation_service.py",
    limit: 130,
    next: "Draft generation service should stay orchestration-only; split provider policy if it grows.",
  },
  {
    path: "backend/app/application/deterministic_draft_service.py",
    limit: 80,
    next: "Deterministic draft fallback should stay a small fallback service.",
  },
  {
    path: "backend/app/application/draft_run_payloads.py",
    limit: 100,
    next: "DraftRun payload mapping should stay serialization-only.",
  },
  {
    path: "backend/app/application/draft_run_context_payloads.py",
    limit: 70,
    next: "DraftRun context payload mapping should stay serialization-only.",
  },
  {
    path: "backend/app/application/draft_run_context_builder.py",
    limit: 160,
    next: "DraftRun context builder should stay pure summary normalization; split per entity before adding rule compilation.",
  },
  {
    path: "backend/app/application/draft_source_ledger_builder.py",
    limit: 70,
    next: "Draft SourceLedger builder should stay orchestration-only; source sections own claim extraction.",
  },
  {
    path: "backend/app/application/draft_source_ledger_sections.py",
    limit: 270,
    next: "Draft SourceLedger sections should split by brief/candidate/signal/topic source before validators consume it.",
  },
  {
    path: "backend/app/application/draft_feasibility_gate.py",
    limit: 120,
    next: "Draft feasibility gate should stay deterministic policy only; split status rules before adding validators.",
  },
  {
    path: "backend/app/application/draft_feasibility_policy.py",
    limit: 120,
    next: "Draft feasibility policy should stay deterministic status decision logic; split validator checks before adding scoring.",
  },
  {
    path: "backend/app/application/draft_post_contract_builder.py",
    limit: 130,
    next: "Draft post contract builder should stay contract assembly only; split obligation mappers before growing.",
  },
  {
    path: "backend/app/application/publication_size_contract_resolver.py",
    limit: 120,
    next: "Publication size resolution should stay isolated from post contract and rule registry compilation.",
  },
  {
    path: "backend/app/application/draft_quality_gate.py",
    limit: 70,
    next: "Draft quality gate should stay orchestration-only between feasibility and contract.",
  },
  {
    path: "backend/app/application/draft_rule_pack_compiler.py",
    limit: 80,
    next: "Draft rule-pack compiler should stay orchestration-only; section builders own category mapping.",
  },
  {
    path: "backend/app/application/draft_rule_pack_sections.py",
    limit: 210,
    next: "Draft rule-pack sections should split by category before validator or scoring logic is added.",
  },
  {
    path: "backend/app/application/draft_rule_pack_from_registry.py",
    limit: 60,
    next: "Draft RulePack-from-registry mapper should stay conversion-only.",
  },
  {
    path: "backend/app/application/draft_rule_registry_compiler.py",
    limit: 80,
    next: "Draft rule-registry compiler should stay orchestration-only; section mappers own rule extraction.",
  },
  {
    path: "backend/app/application/draft_rule_registry_contract.py",
    limit: 120,
    next: "Draft rule-registry contract mapper should stay focused on PostContract rules.",
  },
  {
    path: "backend/app/application/draft_rule_registry_size.py",
    limit: 110,
    next: "Publication-size registry rules should stay deterministic and contract-owned.",
  },
  {
    path: "backend/app/application/draft_rule_registry_sections.py",
    limit: 320,
    next: "Draft rule-registry sections should split by source family before validator execution is added.",
  },
  {
    path: "backend/app/application/draft_material_plan_service.py",
    limit: 190,
    next: "Draft material planning service should stay step orchestration only; split provider policy before adding retrieval.",
  },
  {
    path: "backend/app/application/material_plan_evidence_projection.py",
    limit: 120,
    next: "Material-plan evidence projection should stay deterministic and ledger-owned.",
  },
  {
    path: "backend/app/application/material_plan_accountability.py",
    limit: 100,
    next: "Material-plan accountability should stay validation-only; split repair policy if it grows.",
  },
  {
    path: "backend/app/application/material_plan_retry_policy.py",
    limit: 60,
    next: "Material-plan retry policy should stay declarative.",
  },
  {
    path: "backend/app/application/material_plan_retry_orchestrator.py",
    limit: 380,
    next: "Material-plan retry orchestration should split provider execution from fallback recording before adding more retry modes.",
  },
  {
    path: "backend/app/application/draft_strategy_service.py",
    limit: 190,
    next: "Draft strategy service should stay step orchestration only; split prompt policy before candidate generation.",
  },
  {
    path: "backend/app/application/source_intent_normalizer.py",
    limit: 90,
    next: "Source intent normalizer should stay deterministic classification only.",
  },
  {
    path: "backend/app/application/source_research_plan_service.py",
    limit: 160,
    next: "Source research planning service should stay one-step orchestration only; split provider policy before retrieval.",
  },
  {
    path: "backend/app/application/source_research_plan_sanitizer.py",
    limit: 70,
    next: "Source research plan sanitizer should stay deterministic source-intent cleanup only.",
  },
  {
    path: "backend/app/application/source_research_prompts.py",
    limit: 80,
    next: "Source research prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/source_research_audit.py",
    limit: 80,
    next: "Source research audit helpers should stay sanitized trace builders only.",
  },
  {
    path: "backend/app/application/public_evidence_retrieval_service.py",
    limit: 210,
    next: "Public evidence retrieval service should stay orchestration-only; split retrieval operation progress before adding more adapters.",
  },
  {
    path: "backend/app/application/public_evidence_query_builder.py",
    limit: 110,
    next: "Public evidence query building should stay deterministic and provider-free.",
  },
  {
    path: "backend/app/application/public_evidence_relevance.py",
    limit: 90,
    next: "Public evidence relevance guard should stay deterministic; split scoring before adding provider logic.",
  },
  {
    path: "backend/app/application/draft_public_evidence_step_service.py",
    limit: 90,
    next: "Public evidence step service should stay a narrow orchestration boundary for retrieval, synthesis, and merge.",
  },
  {
    path: "backend/app/application/deterministic_external_evidence_synthesis.py",
    limit: 90,
    next: "Deterministic external evidence synthesis should stay fallback-only and provider-free.",
  },
  {
    path: "backend/app/application/deterministic_external_evidence_synthesis_step_service.py",
    limit: 40,
    next: "Deterministic external evidence synthesis step adapter should stay compatibility-only.",
  },
  {
    path: "backend/app/application/external_evidence_synthesis_prompts.py",
    limit: 80,
    next: "External evidence synthesis prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/external_evidence_synthesis_service.py",
    limit: 190,
    next: "External evidence synthesis service should stay one-step orchestration only; split audit mapping before growing.",
  },
  {
    path: "backend/app/application/source_ledger_external_evidence_merger.py",
    limit: 140,
    next: "SourceLedger external evidence merger should stay deterministic merge policy only.",
  },
  {
    path: "backend/app/application/openrouter_public_search_service.py",
    limit: 210,
    next: "OpenRouter public search service should stay search-task orchestration only; split audit/prompt mapping before growing.",
  },
  {
    path: "backend/app/application/public_evidence_ports.py",
    limit: 60,
    next: "Public evidence ports should stay tiny protocol/result contracts.",
  },
  {
    path: "backend/app/application/disabled_public_search_adapter.py",
    limit: 50,
    next: "Disabled public search adapter should stay a simple not-configured fallback.",
  },
  {
    path: "backend/app/application/deterministic_source_research_plan_service.py",
    limit: 90,
    next: "Deterministic source research planning should stay fallback-only and provider-free.",
  },
  {
    path: "backend/app/application/deterministic_source_research_step_service.py",
    limit: 50,
    next: "Deterministic source research step adapter should stay compatibility-only.",
  },
  {
    path: "backend/app/application/draft_rhetorical_plan_service.py",
    limit: 180,
    next: "Draft rhetorical planning service should stay one-step orchestration only; split provider policy before validators.",
  },
  {
    path: "backend/app/application/draft_rhetorical_plan_retry.py",
    limit: 230,
    next: "Rhetorical plan retry orchestration should stay limited to JSON attempts and fallback discipline.",
  },
  {
    path: "backend/app/application/json_step_retry_policy.py",
    limit: 40,
    next: "JSON step retry policy should stay a tiny attempt-sequence helper.",
  },
  {
    path: "backend/app/application/draft_rhetorical_plan_prompts.py",
    limit: 80,
    next: "Draft rhetorical planning prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_rhetorical_plan_audit.py",
    limit: 70,
    next: "Draft rhetorical planning audit helpers should stay sanitized trace builders only.",
  },
  {
    path: "backend/app/application/deterministic_rhetorical_plan_service.py",
    limit: 140,
    next: "Deterministic rhetorical planning should stay fallback-only and provider-free.",
  },
  {
    path: "backend/app/application/deterministic_rhetorical_plan_step_service.py",
    limit: 50,
    next: "Deterministic rhetorical planning step adapter should stay compatibility-only.",
  },
  {
    path: "backend/app/application/draft_candidate_direction_service.py",
    limit: 70,
    next: "Draft candidate directions should stay deterministic direction policy only.",
  },
  {
    path: "backend/app/application/draft_candidate_generation_service.py",
    limit: 240,
    next: "Draft candidate generation should stay step orchestration only; split provider policy or scoring before growing.",
  },
  {
    path: "backend/app/application/draft_candidate_selection_service.py",
    limit: 70,
    next: "Draft candidate selection should stay deterministic v1 scoring only.",
  },
  {
    path: "backend/app/application/draft_candidate_publishability.py",
    limit: 100,
    next: "Draft candidate publishability should stay a provider-free selection guard.",
  },
  {
    path: "backend/app/application/draft_candidate_prompts.py",
    limit: 80,
    next: "Draft candidate prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_candidate_audit.py",
    limit: 90,
    next: "Draft candidate audit helpers should stay sanitized trace builders only.",
  },
  {
    path: "backend/app/application/deterministic_draft_candidate_service.py",
    limit: 90,
    next: "Deterministic draft candidate fallback should stay small and provider-free.",
  },
  {
    path: "backend/app/application/draft_candidate_result.py",
    limit: 30,
    next: "Draft candidate result should stay a tiny application DTO.",
  },
  {
    path: "backend/app/application/draft_candidate_selection_block.py",
    limit: 40,
    next: "Draft candidate selection blocked payload should stay a tiny mapper.",
  },
  {
    path: "backend/app/application/draft_run_pipeline_ports.py",
    limit: 50,
    next: "DraftRun pipeline ports should stay limited to pipeline repository protocols.",
  },
  {
    path: "backend/app/application/draft_run_progress.py",
    limit: 80,
    next: "DraftRun progress helper should stay limited to step status and AiRun id persistence.",
  },
  {
    path: "backend/app/application/draft_run_step_progress.py",
    limit: 160,
    next: "DraftRun step progress sink should stay limited to artifact-level operation trace updates.",
  },
  {
    path: "backend/app/application/draft_run_step_progress_payload.py",
    limit: 40,
    next: "DraftRun step progress payload helpers should stay tiny artifact merge utilities.",
  },
  {
    path: "backend/app/application/draft_run_staleness.py",
    limit: 60,
    next: "DraftRun staleness helper should stay a pure timestamp inspector.",
  },
  {
    path: "backend/app/application/draft_run_draft_step_service.py",
    limit: 50,
    next: "DraftRun legacy draft step service should stay a compatibility fallback only.",
  },
  {
    path: "backend/app/application/draft_validation_linter.py",
    limit: 240,
    next: "Draft validation linter should split into size/evidence/contract/publishability validators before growing.",
  },
  {
    path: "backend/app/application/draft_attribution_markers.py",
    limit: 120,
    next: "Draft attribution marker extraction should stay deterministic and provider-free.",
  },
  {
    path: "backend/app/application/draft_attribution_requirements.py",
    limit: 120,
    next: "Draft attribution requirement normalization should stay provider-free and validator-owned.",
  },
  {
    path: "backend/app/application/draft_validation_evidence.py",
    limit: 120,
    next: "Draft validation evidence checks should stay deterministic and attribution-focused.",
  },
  {
    path: "backend/app/application/draft_validator_orchestrator.py",
    limit: 110,
    next: "Draft validator orchestrator should stay report assembly only; split validator routing if it grows.",
  },
  {
    path: "backend/app/application/draft_llm_validation_service.py",
    limit: 260,
    next: "Draft LLM validation service should stay one provider-backed report-only validator orchestration.",
  },
  {
    path: "backend/app/application/draft_llm_validation_prompts.py",
    limit: 90,
    next: "Draft LLM validation prompts should stay prompt-shape builders only.",
  },
  {
    path: "backend/app/application/draft_llm_validation_audit.py",
    limit: 60,
    next: "Draft LLM validation audit helpers should stay sanitized trace builders only.",
  },
  {
    path: "backend/app/application/draft_llm_validation_parser.py",
    limit: 80,
    next: "Draft LLM validation parser should stay payload normalization only.",
  },
  {
    path: "backend/app/application/draft_llm_validation_observations.py",
    limit: 80,
    next: "Draft LLM validation observations should stay pass/positive normalization only.",
  },
  {
    path: "backend/app/application/draft_validation_step_service.py",
    limit: 90,
    next: "Draft validation step service should stay composition-only between deterministic and LLM reports.",
  },
  {
    path: "backend/app/application/draft_validation_alternative_flow.py",
    limit: 110,
    next: "Draft validation alternative flow should stay focused on challenger merge and validation reuse.",
  },
  {
    path: "backend/app/application/draft_validation_step.py",
    limit: 40,
    next: "Draft validation step adapter should stay a thin pipeline bridge.",
  },
  {
    path: "backend/app/application/draft_validation_operation_safety.py",
    limit: 70,
    next: "Draft validation operation safety should stay focused on safe provider-heavy operation failure mapping.",
  },
  {
    path: "backend/app/application/deterministic_pairwise_ranking.py",
    limit: 110,
    next: "Deterministic pairwise ranking should stay fallback-only and validator-report driven.",
  },
  {
    path: "backend/app/application/draft_pairwise_ranking_prompts.py",
    limit: 60,
    next: "Pairwise ranking prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_pairwise_ranking_service.py",
    limit: 190,
    next: "Pairwise ranking service should stay one-step orchestration only; split parser or audit mapping before growing.",
  },
  {
    path: "backend/app/application/draft_pairwise_ranking_payloads.py",
    limit: 80,
    next: "Pairwise ranking payload helpers should stay parser/attempt-record only.",
  },
  {
    path: "backend/app/application/draft_directed_revision_prompts.py",
    limit: 50,
    next: "Directed revision prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_directed_revision_service.py",
    limit: 160,
    next: "Directed revision service should stay one-shot provider orchestration only; split retry plumbing before adding loops.",
  },
  {
    path: "backend/app/application/draft_revision_instruction_builder.py",
    limit: 70,
    next: "Draft revision instruction builder should stay limited to actionable finding projection.",
  },
  {
    path: "backend/app/application/draft_revision_regression.py",
    limit: 110,
    next: "Draft revision regression guard should stay deterministic and validation-report based.",
  },
  {
    path: "backend/app/application/draft_final_quality_assessment.py",
    limit: 150,
    next: "Final quality assessment should stay deterministic public-prose heuristics only.",
  },
  {
    path: "backend/app/application/draft_final_quality_attribution.py",
    limit: 80,
    next: "Final quality attribution split should stay deterministic and handoff-focused.",
  },
  {
    path: "backend/app/application/draft_final_quality_contract.py",
    limit: 130,
    next: "Final quality contract builder should stay provider-free and contract-assembly only.",
  },
  {
    path: "backend/app/application/draft_final_quality_gate.py",
    limit: 140,
    next: "Final quality gate should stay thin orchestration between contract, evaluator, and repair loop.",
  },
  {
    path: "backend/app/application/draft_final_quality_gate_evaluator.py",
    limit: 110,
    next: "Final quality gate evaluator should own deterministic plus independent-review report assembly only.",
  },
  {
    path: "backend/app/application/draft_final_quality_gate_payloads.py",
    limit: 80,
    next: "Final quality gate payload helpers should stay serialization and status utilities only.",
  },
  {
    path: "backend/app/application/draft_final_quality_repair_loop.py",
    limit: 180,
    next: "Final quality repair loop should stay bounded repair-cycle orchestration only.",
  },
  {
    path: "backend/app/application/draft_final_quality_review_parser.py",
    limit: 90,
    next: "Final quality review parser should stay payload normalization only.",
  },
  {
    path: "backend/app/application/draft_final_quality_review_prompts.py",
    limit: 90,
    next: "Final quality review prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_final_quality_review_service.py",
    limit: 190,
    next: "Final quality review service should stay one provider-backed JSON review orchestration.",
  },
  {
    path: "backend/app/application/draft_revision_loop_config.py",
    limit: 20,
    next: "Draft revision loop config should stay a tiny settings normalization helper.",
  },
  {
    path: "backend/app/application/draft_revision_goal_evaluator.py",
    limit: 90,
    next: "Draft revision goal evaluator should stay deterministic and validation-report based.",
  },
  {
    path: "backend/app/application/draft_editorial_revision_goals.py",
    limit: 160,
    next: "Editorial revision goals should stay deterministic and artifact-projection only.",
  },
  {
    path: "backend/app/application/draft_editorial_revision_evaluator.py",
    limit: 100,
    next: "Editorial revision evaluator should stay deterministic and pairwise-report based.",
  },
  {
    path: "backend/app/application/draft_revision_rejected_moves.py",
    limit: 80,
    next: "Revision rejected-move helpers should stay trace/policy projection only.",
  },
  {
    path: "backend/app/application/draft_revision_loop_policy.py",
    limit: 100,
    next: "Draft revision loop policy helpers should stay deterministic and provider-free.",
  },
  {
    path: "backend/app/application/draft_revision_loop_cycle_runner.py",
    limit: 110,
    next: "Draft revision loop cycle runner should stay a thin operation executor.",
  },
  {
    path: "backend/app/application/draft_revision_loop_service.py",
    limit: 220,
    next: "Draft revision loop service should stay bounded orchestration; split cycle policies before adding more checks.",
  },
  {
    path: "backend/app/application/draft_ranking_revision_result.py",
    limit: 20,
    next: "Draft ranking revision result should stay a tiny application DTO.",
  },
  {
    path: "backend/app/application/draft_ranking_revision_mapping.py",
    limit: 60,
    next: "Draft ranking revision mapping should stay DTO conversion and formatting only.",
  },
  {
    path: "backend/app/application/draft_ranking_revision_service.py",
    limit: 140,
    next: "Draft ranking revision service should stay orchestration-only between ranking, revision, and regression guard.",
  },
  {
    path: "backend/app/application/draft_validation_ranking_bridge.py",
    limit: 50,
    next: "Draft validation ranking bridge should stay a narrow adapter from validation step to ranking revision.",
  },
  {
    path: "backend/app/application/draft_model_role_resolver.py",
    limit: 90,
    next: "Draft model role resolver should stay configuration policy only; prompt behavior belongs to role-owned services.",
  },
  {
    path: "backend/app/application/draft_generation_params.py",
    limit: 90,
    next: "Draft generation params should stay numeric config normalization and provider payload mapping only.",
  },
  {
    path: "backend/app/application/draft_provider_error_utils.py",
    limit: 40,
    next: "Draft provider error utilities should stay limited to safe error and raw excerpt extraction.",
  },
  {
    path: "backend/app/application/draft_article_dossier_builder.py",
    limit: 230,
    next: "Article dossier builder should stay deterministic card extraction; split artifact sections if it grows.",
  },
  {
    path: "backend/app/application/draft_context_pack_builder.py",
    limit: 90,
    next: "Context pack builder should stay role-selection policy only.",
  },
  {
    path: "backend/app/application/draft_article_memory_service.py",
    limit: 50,
    next: "Article memory service should stay a thin wrapper over dossier and context-pack builders.",
  },
  {
    path: "backend/app/application/draft_planning_prompts.py",
    limit: 80,
    next: "Draft planning prompts should stay prompt-message builders only.",
  },
  {
    path: "backend/app/application/draft_planning_audit.py",
    limit: 90,
    next: "Draft planning audit helpers should stay sanitized trace builders only.",
  },
  {
    path: "backend/app/application/deterministic_draft_planning_service.py",
    limit: 120,
    next: "Deterministic draft planning should stay fallback-only and split by step before growing.",
  },
  {
    path: "backend/app/application/deterministic_draft_planning_step_services.py",
    limit: 80,
    next: "Deterministic planning step adapters should stay compatibility-only.",
  },
  {
    path: "backend/app/application/draft_planning_result.py",
    limit: 30,
    next: "Draft planning step result should stay a tiny application DTO.",
  },
  {
    path: "backend/app/application/draft_run_pipeline.py",
    limit: 160,
    next: "DraftRun pipeline should stay high-level orchestration; split long step executors before adding more provider-heavy stages.",
  },
  {
    path: "backend/app/application/draft_run_service.py",
    limit: 80,
    next: "DraftRun service should stay queue/audit orchestration only.",
  },
  {
    path: "backend/app/application/portfolio_service.py",
    limit: 90,
    next: "Portfolio service should own auth/session/access use cases only.",
  },
  {
    path: "backend/app/domain/health.py",
    limit: 60,
    next: "Health domain objects should stay provider-free and framework-free.",
  },
  {
    path: "backend/app/domain/ai_run.py",
    limit: 80,
    next: "AI run domain objects should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_generation.py",
    limit: 70,
    next: "Draft generation domain contracts should stay provider-free and framework-free.",
  },
  {
    path: "backend/app/domain/draft_run.py",
    limit: 120,
    next: "DraftRun domain objects should stay provider-free and infrastructure-free.",
  },
  {
    path: "backend/app/domain/portfolio.py",
    limit: 70,
    next: "Portfolio DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_run_steps.py",
    limit: 80,
    next: "DraftRun step keys should stay provider-free and contain only ordering/title metadata.",
  },
  {
    path: "backend/app/domain/draft_run_context.py",
    limit: 70,
    next: "DraftRun context DTOs should stay provider-free and infrastructure-free.",
  },
  {
    path: "backend/app/domain/draft_source_ledger.py",
    limit: 140,
    next: "Draft SourceLedger DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_source_intent.py",
    limit: 160,
    next: "Draft SourceIntent DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_public_evidence.py",
    limit: 140,
    next: "Draft public evidence DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_evidence_synthesis.py",
    limit: 90,
    next: "Draft evidence synthesis DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_feasibility.py",
    limit: 80,
    next: "Draft feasibility DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_post_contract.py",
    limit: 100,
    next: "Draft post contract DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/publication_size.py",
    limit: 60,
    next: "Publication size contract DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_rule_pack.py",
    limit: 100,
    next: "Draft RulePack DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_rule_registry.py",
    limit: 120,
    next: "Draft RuleRegistry DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_planning.py",
    limit: 100,
    next: "Draft planning DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_candidates.py",
    limit: 140,
    next: "Draft candidate DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_validation.py",
    limit: 120,
    next: "Draft validation DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_llm_validation.py",
    limit: 100,
    next: "Draft LLM validation DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_ranking_revision.py",
    limit: 110,
    next: "Draft ranking/revision DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_revision_loop.py",
    limit: 90,
    next: "Draft revision loop DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_model_roles.py",
    limit: 60,
    next: "Draft model role DTOs should stay provider-free and settings-free.",
  },
  {
    path: "backend/app/domain/draft_article_memory.py",
    limit: 120,
    next: "Draft article memory DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/domain/draft_rhetorical_plan.py",
    limit: 120,
    next: "Draft rhetorical plan DTOs should stay provider-free and persistence-free.",
  },
  {
    path: "backend/app/infrastructure/openrouter_config.py",
    limit: 80,
    next: "OpenRouter config validator must not perform provider calls.",
  },
  {
    path: "backend/app/infrastructure/openrouter_draft_adapter.py",
    limit: 140,
    next: "OpenRouter draft adapter should stay provider-call-only; prompt policy belongs in application contracts.",
  },
  {
    path: "backend/app/infrastructure/openrouter_json_adapter.py",
    limit: 100,
    next: "OpenRouter JSON adapter should stay generic provider-call-only.",
  },
  {
    path: "backend/app/infrastructure/openrouter_web_search_adapter.py",
    limit: 130,
    next: "OpenRouter web search adapter should stay provider-call and citation parsing only.",
  },
  {
    path: "backend/app/infrastructure/public_url_reader.py",
    limit: 100,
    next: "Public URL reader should stay one-URL HTTP extraction only; split crawler/search adapters separately.",
  },
  {
    path: "backend/app/infrastructure/sqlite_ai_run_repository.py",
    limit: 130,
    next: "SQLite AI run repository should stay audit-storage-only; split schema/mappers before adding more tables.",
  },
  {
    path: "backend/app/infrastructure/celery_app.py",
    limit: 60,
    next: "Celery app wiring should stay infrastructure-only and config-only.",
  },
  {
    path: "backend/app/infrastructure/celery_draft_run_dispatcher.py",
    limit: 40,
    next: "Celery dispatcher should stay a tiny task submission adapter.",
  },
  {
    path: "backend/app/infrastructure/draft_run_tasks.py",
    limit: 70,
    next: "Celery task body should stay a thin infrastructure entrypoint over DraftRunPipeline.",
  },
  {
    path: "backend/app/infrastructure/draft_run_pipeline_factory.py",
    limit: 80,
    next: "DraftRun pipeline factory should stay infrastructure wiring only.",
  },
  {
    path: "backend/app/infrastructure/draft_run_pipeline_provider_services.py",
    limit: 60,
    next: "DraftRun provider-service wiring should stay limited to provider-backed pipeline dependencies.",
  },
  {
    path: "backend/app/infrastructure/draft_run_pipeline_validation_services.py",
    limit: 60,
    next: "DraftRun validation/ranking wiring should stay limited to validation pipeline dependencies.",
  },
  {
    path: "backend/app/infrastructure/sqlite_draft_run_repository.py",
    limit: 230,
    next: "SQLite DraftRun repository should own storage only; split mappers/schema before adding more tables.",
  },
  {
    path: "backend/app/infrastructure/sqlite_portfolio_repository.py",
    limit: 340,
    next: "SQLite portfolio repository should own storage/schema only; split seed/mappers before growing.",
  },
  {
    path: "backend/tests/test_settings.py",
    limit: 100,
    next: "Backend settings tests should split when provider config coverage grows.",
  },
  {
    path: "backend/tests/test_settings_draft_models.py",
    limit: 50,
    next: "Draft model settings tests should stay focused on role-model env mapping.",
  },
  {
    path: "backend/tests/test_public_evidence_retrieval.py",
    limit: 130,
    next: "Public evidence retrieval tests should stay focused on batch assembly and adapter merge behavior.",
  },
  {
    path: "backend/tests/test_openrouter_public_search_service.py",
    limit: 120,
    next: "OpenRouter public search tests should split provider success/error from integration wiring before growing.",
  },
  {
    path: "backend/tests/test_openrouter_public_search_relevance.py",
    limit: 80,
    next: "OpenRouter public search relevance tests should stay focused on citation filtering behavior.",
  },
  {
    path: "backend/tests/test_health_api.py",
    limit: 120,
    next: "Backend API tests should split by route group when more APIs are added.",
  },
  {
    path: "backend/tests/test_ai_run_api.py",
    limit: 130,
    next: "AI run API tests should split by create/read/list behavior before growing further.",
  },
  {
    path: "backend/tests/test_ai_run_repository.py",
    limit: 110,
    next: "AI run repository tests should split by schema/write/query behavior before growing further.",
  },
  {
    path: "backend/tests/test_draft_generation_api.py",
    limit: 170,
    next: "Draft generation API tests should split by success/fallback/provider errors before growing further.",
  },
  {
    path: "backend/tests/test_draft_run_api.py",
    limit: 130,
    next: "DraftRun API tests should split by create/read/worker handoff before growing further.",
  },
  {
    path: "backend/tests/test_portfolio_api.py",
    limit: 140,
    next: "Portfolio API tests should split auth/session and project snapshot cases before growing further.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline.py",
    limit: 100,
    next: "DraftRun pipeline tests should split by step execution when real reasoning is added.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_article_memory.py",
    limit: 70,
    next: "DraftRun article-memory pipeline tests should stay focused on stored dossier/context-pack artifacts.",
  },
  {
    path: "backend/tests/test_draft_run_context_builder.py",
    limit: 160,
    next: "DraftRun context builder tests should stay focused on context normalization.",
  },
  {
    path: "backend/tests/test_draft_source_ledger_builder.py",
    limit: 120,
    next: "Draft SourceLedger builder tests should split by claim source before growing further.",
  },
  {
    path: "backend/tests/test_draft_feasibility_and_contract.py",
    limit: 120,
    next: "Draft feasibility and contract tests should split by policy and contract mapping before growing.",
  },
  {
    path: "backend/tests/test_publication_size_contract.py",
    limit: 110,
    next: "Publication size contract tests should stay focused on resolver and deterministic registry rules.",
  },
  {
    path: "backend/tests/test_draft_rule_pack_compiler.py",
    limit: 100,
    next: "Draft RulePack compiler tests should split by source category before growing.",
  },
  {
    path: "backend/tests/test_draft_rule_registry_compiler.py",
    limit: 90,
    next: "Draft RuleRegistry compiler tests should split by source family before validator coverage grows.",
  },
  {
    path: "backend/tests/test_draft_planning_services.py",
    limit: 180,
    next: "Draft planning service tests should split by material/strategy before growing.",
  },
  {
    path: "backend/tests/test_draft_material_plan_service.py",
    limit: 240,
    next: "Material-plan service tests should split retry/accountability fixtures before growing.",
  },
  {
    path: "backend/tests/test_source_intent_and_research_plan.py",
    limit: 150,
    next: "Source intent and research-plan tests should split normalizer and provider service cases before growing.",
  },
  {
    path: "backend/tests/test_source_research_plan_sanitizer.py",
    limit: 60,
    next: "Source research plan sanitizer tests should stay focused on deterministic cleanup cases.",
  },
  {
    path: "backend/tests/test_external_evidence_synthesis_and_merge.py",
    limit: 120,
    next: "External evidence synthesis and merge tests should stay focused on evidence-to-ledger mapping.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_external_evidence.py",
    limit: 90,
    next: "DraftRun external evidence pipeline tests should stay separate from source-ledger seed tests.",
  },
  {
    path: "backend/tests/test_draft_candidate_services.py",
    limit: 180,
    next: "Draft candidate service tests should stay focused on direction and generation wiring.",
  },
  {
    path: "backend/tests/test_draft_candidate_selection_guard.py",
    limit: 110,
    next: "Draft candidate selection guard tests should stay focused on publishability decisions.",
  },
  {
    path: "backend/tests/test_draft_rhetorical_plan_service.py",
    limit: 120,
    next: "Draft rhetorical plan tests should split provider/fallback and pipeline wiring before growing.",
  },
  {
    path: "backend/tests/test_draft_rhetorical_plan_retry.py",
    limit: 100,
    next: "Draft rhetorical retry tests should stay focused on JSON retry policy behavior.",
  },
  {
    path: "backend/tests/test_draft_llm_validation_service.py",
    limit: 130,
    next: "Draft LLM validation service tests should stay focused on provider success/retry/unavailable behavior.",
  },
  {
    path: "backend/tests/test_draft_model_role_resolver.py",
    limit: 80,
    next: "Draft model role resolver tests should stay focused on role/default/unconfigured selection.",
  },
  {
    path: "backend/tests/test_draft_article_memory.py",
    limit: 90,
    next: "Article memory tests should stay focused on dossier and context-pack extraction.",
  },
  {
    path: "backend/tests/test_draft_llm_validation_parser.py",
    limit: 80,
    next: "Draft LLM validation parser tests should stay focused on findings/observations normalization.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_validation_step.py",
    limit: 90,
    next: "DraftRun validation pipeline tests should stay focused on validation step wiring.",
  },
  {
    path: "backend/tests/test_draft_validation_alternative_flow.py",
    limit: 70,
    next: "Draft validation alternative flow tests should stay focused on challenger-only final validation.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_candidates.py",
    limit: 80,
    next: "DraftRun candidate pipeline tests should stay separate from context/rule/planning tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_candidate_block.py",
    limit: 80,
    next: "DraftRun candidate block tests should stay separate from successful candidate pipeline tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_planning_steps.py",
    limit: 80,
    next: "DraftRun planning-step pipeline tests should stay separate from context/rule-pack tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_rule_pack.py",
    limit: 60,
    next: "DraftRun pipeline rule-pack failure tests should stay separate from happy-path step tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_source_ledger.py",
    limit: 70,
    next: "DraftRun SourceLedger pipeline tests should stay separate from context/rule-pack tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_quality_gate.py",
    limit: 90,
    next: "DraftRun quality-gate pipeline tests should stay separate from context/rule-pack tests.",
  },
  {
    path: "backend/tests/test_draft_run_pipeline_progress.py",
    limit: 120,
    next: "DraftRun progress pipeline tests should stay focused on step status and child AiRun id persistence.",
  },
  {
    path: "backend/tests/test_draft_run_step_progress.py",
    limit: 60,
    next: "DraftRun operation progress tests should stay focused on artifact persistence and stale timestamp behavior.",
  },
  {
    path: "backend/tests/test_draft_revision_operation_repair.py",
    limit: 90,
    next: "Draft revision operation repair tests should stay focused on failed-cycle finalization behavior.",
  },
  {
    path: "backend/tests/test_draft_run_staleness_api.py",
    limit: 100,
    next: "DraftRun staleness API tests should stay focused on computed stale fields.",
  },
  {
    path: "backend/tests/test_draft_run_repository.py",
    limit: 100,
    next: "DraftRun repository tests should split by schema/write/query behavior before growing further.",
  },
];

const ADR_PATH =
  "docs/adr/2026-06-15-react-ui-uses-feature-modules-not-app-god-file.md";
const MODULE_GUARDRAILS_ADR_PATH =
  "docs/adr/2026-06-15-domain-feature-modules-have-size-boundary-guardrails.md";
const FEATURE_INTERNALS_ADR_PATH =
  "docs/adr/2026-06-15-feature-entrypoints-stay-thin-and-domain-transitions-are-role-owned.md";
const ARCHITECTURE_DRIFT_ADR_PATH =
  "docs/adr/2026-06-16-architecture-drift-is-prevented-by-agent-and-smoke-guardrails.md";
const TEST_OWNERSHIP_ADR_PATH =
  "docs/adr/2026-06-18-app-flow-tests-follow-feature-ownership.md";
const BACKEND_AI_EXECUTION_ADR_PATH =
  "docs/adr/2026-06-18-backend-starts-as-openrouter-ai-execution-layer.md";
const SAO_PATH = "docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md";
const ENV_EXAMPLE_PATH = ".env.example";

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
const warnings = [];

function warn(message) {
  warnings.push(message);
}

function assert(condition, message) {
  if (!condition) {
    failures.push(message);
  }
}

function countExportedSymbols(source) {
  const namedDeclarationCount = [
    ...source.matchAll(
      /^export\s+(?:async\s+)?(?:function|class|const|let|var|interface|type|enum)\s+([A-Za-z_$][\w$]*)/gm
    ),
  ].length;

  const namedExportCount = [...source.matchAll(/^export\s+\{([^}]+)\}/gm)].reduce(
    (total, match) =>
      total +
      match[1]
        .split(",")
        .map((entry) => entry.trim())
        .filter(Boolean).length,
    0
  );

  return namedDeclarationCount + namedExportCount;
}

function resolveModuleReference(sourceFile, importPath) {
  if (!importPath.startsWith(".")) {
    return importPath;
  }

  return path
    .relative(ROOT, path.resolve(ROOT, path.dirname(sourceFile), importPath))
    .replaceAll(path.sep, "/");
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
assert(
  fileExists(FEATURE_INTERNALS_ADR_PATH),
  `Missing ADR: ${FEATURE_INTERNALS_ADR_PATH}`
);
assert(
  fileExists(ARCHITECTURE_DRIFT_ADR_PATH),
  `Missing ADR: ${ARCHITECTURE_DRIFT_ADR_PATH}`
);
assert(
  fileExists(TEST_OWNERSHIP_ADR_PATH),
  `Missing ADR: ${TEST_OWNERSHIP_ADR_PATH}`
);
assert(
  fileExists(BACKEND_AI_EXECUTION_ADR_PATH),
  `Missing ADR: ${BACKEND_AI_EXECUTION_ADR_PATH}`
);
assert(fileExists(ENV_EXAMPLE_PATH), `Missing environment contract: ${ENV_EXAMPLE_PATH}`);

const envExampleSource = fileExists(ENV_EXAMPLE_PATH) ? readText(ENV_EXAMPLE_PATH) : "";
const requiredEnvFragments = [
  "VITE_API_BASE_URL=",
  "GLAVRED_ENV=",
  "GLAVRED_API_HOST=",
  "GLAVRED_API_PORT=",
  "GLAVRED_CORS_ORIGINS=",
  "DATABASE_URL=",
  "REDIS_URL=",
  "AI_RUN_AUDIT_DB_PATH=",
  "DRAFT_RUN_DB_PATH=",
  "OPENROUTER_API_KEY=",
  "OPENROUTER_BASE_URL=",
  "OPENROUTER_DEFAULT_MODEL=",
  "OPENROUTER_BACKUP_MODEL=",
  "OPENROUTER_APP_NAME=",
  "OPENROUTER_HTTP_REFERER=",
  "LANGGRAPH_DOCUMENT_AI_PLATFORM_MODE=",
  "LANGGRAPH_DOCUMENT_AI_PLATFORM_CONFIG=",
];

for (const fragment of requiredEnvFragments) {
  assert(
    envExampleSource.includes(fragment),
    `.env.example is missing required backend/OpenRouter variable: ${fragment}`
  );
}

const gitignoreSource = fileExists(".gitignore") ? readText(".gitignore") : "";
assert(gitignoreSource.includes(".env"), ".gitignore must ignore local .env files.");
assert(
  gitignoreSource.includes("!.env.example"),
  ".gitignore must keep .env.example commit-ready."
);

const requiredDockerFiles = [
  ".dockerignore",
  "compose.yaml",
  "docker/backend.Dockerfile",
  "docker/frontend.Dockerfile",
];

for (const requiredFile of requiredDockerFiles) {
  assert(fileExists(requiredFile), `Missing Docker local-stack file: ${requiredFile}`);
}

const composeSource = fileExists("compose.yaml") ? readText("compose.yaml") : "";
for (const fragment of ["redis:", "worker:", "REDIS_URL: redis://redis:6379/0"]) {
  assert(composeSource.includes(fragment), `compose.yaml is missing queued-run fragment: ${fragment}`);
}

const requiredSourceFiles = [
  "src/app/AppShell.tsx",
  "src/app/Sidebar.tsx",
  "src/app/Topbar.tsx",
  "src/app/navigation.ts",
  "src/app/useWorkspaceController.ts",
  "src/app/useWorkspacePersistence.ts",
  "src/app/useContextChatController.ts",
  "src/app/useSignalsWorkspaceActions.ts",
  "src/app/useProductionFlowActions.ts",
  "src/app/releaseExport.ts",
  "src/app/contextChatScope.ts",
  "src/shared/ui/Icon.tsx",
  "src/features/author-memory/AuthorMemoryView.tsx",
  "src/features/author-memory/useMemoryFeedController.ts",
  "src/features/author-memory/useImportReviewController.ts",
  "src/features/author-memory/MemoryFeedTab.tsx",
  "src/features/author-memory/MemorySidePanel.tsx",
  "src/features/author-memory/MemoryDialogs.tsx",
  "src/features/author-memory/ImportViews.tsx",
  "src/features/author-memory/ExternalSourcesView.tsx",
  "src/features/author-memory/ImportQueueView.tsx",
  "src/features/author-memory/ImportQueueToolbar.tsx",
  "src/features/author-memory/ImportQueueBulkBar.tsx",
  "src/features/author-memory/ImportCandidateGroupList.tsx",
  "src/features/author-memory/ImportCandidateList.tsx",
  "src/features/author-memory/ImportQueueEmptyState.tsx",
  "src/features/author-memory/CandidateCard.tsx",
  "src/features/author-memory/ArchiveView.tsx",
  "src/features/author-memory/BulkActionDialog.tsx",
  "src/features/author-memory/components.tsx",
  "src/features/author-memory/helpers.ts",
  "src/features/editorial-model/EditorialModelView.tsx",
  "src/features/editorial-model/EditorialModelParts.tsx",
  "src/features/editorial-model/ProjectProfileHeader.tsx",
  "src/features/editorial-model/PublisherRulesView.tsx",
  "src/features/editorial-model/TopicsTab.tsx",
  "src/features/editorial-model/FabulasTab.tsx",
  "src/features/editorial-model/MatrixTab.tsx",
  "src/features/editorial-model/ValidationPanel.tsx",
  "src/features/editorial-model/helpers.ts",
  "src/features/signals/SignalsView.tsx",
  "src/features/signals/useSignalsController.ts",
  "src/features/signals/SignalsHeader.tsx",
  "src/features/signals/SignalsTabs.tsx",
  "src/features/signals/RadarsTab.tsx",
  "src/features/signals/RadarCard.tsx",
  "src/features/signals/FoundSignalsTab.tsx",
  "src/features/signals/SourceSignalCard.tsx",
  "src/features/signals/PostCandidatesPreviewTab.tsx",
  "src/features/signals/PostCandidateCard.tsx",
  "src/features/signals/PostCandidateCardParts.tsx",
  "src/features/signals/PostCandidatesToolbar.tsx",
  "src/features/signals/PostCandidateGroupList.tsx",
  "src/features/signals/PostCandidateEditForm.tsx",
  "src/features/signals/PostCandidateEditContext.tsx",
  "src/features/signals/usePostCandidatesController.ts",
  "src/features/signals/postCandidateFilters.ts",
  "src/features/signals/RadarEditor.tsx",
  "src/features/signals/SignalsSidePanel.tsx",
  "src/features/signals/helpers.tsx",
  "src/features/plan/PlanView.tsx",
  "src/features/plan/PlanSettingsPanel.tsx",
  "src/features/plan/BroadcastGridList.tsx",
  "src/features/plan/BroadcastGridRow.tsx",
  "src/features/plan/BroadcastGridAside.tsx",
  "src/features/briefing/BriefView.tsx",
  "src/features/editing/EditView.tsx",
  "src/features/editing/EditorialVisualStage.tsx",
  "src/features/editing/EditorialVisualFields.tsx",
  "src/features/editing/EditorialVisualVariants.tsx",
  "src/features/editing/EditorialVisualMemeReferences.tsx",
  "src/features/release/ReleaseView.tsx",
  "src/features/analytics/AnalyticsView.tsx",
  "src/application/visualVariantService.ts",
  "src/application/visualMemeRemixService.ts",
  "src/application/draftRunContext.ts",
  "src/application/postCandidateLinking.ts",
  "src/infrastructure/backendDraftClient.ts",
  "src/infrastructure/draftRunClient.ts",
  "src/infrastructure/draftRunRequestPayload.ts",
  "src/app/productionDraftActions.ts",
  "src/app/productionVisualActions.ts",
];

for (const requiredFile of requiredSourceFiles) {
  assert(fileExists(requiredFile), `Missing React architecture source file: ${requiredFile}`);
}

const largeSourceStats = [];
const testFileStats = [];
const backendSourceStats = [];
const nearLimitStats = [];
const exportCountStats = [];

for (const baseline of LARGE_SOURCE_BASELINES) {
  assert(fileExists(baseline.path), `Missing large-file baseline target: ${baseline.path}`);

  if (fileExists(baseline.path)) {
    const source = readText(baseline.path);
    const lines = lineCount(source);
    const exportCount = countExportedSymbols(source);
    largeSourceStats.push({ ...baseline, lines });
    exportCountStats.push({ ...baseline, exportCount });

    if (lines >= Math.ceil(baseline.limit * NEAR_LIMIT_RATIO)) {
      nearLimitStats.push({ ...baseline, lines });
      warn(
        `${baseline.path} is near its architecture limit: ${lines}/${baseline.limit} lines. ${baseline.next}`
      );
    }

    if (exportCount > DEFAULT_EXPORT_COUNT_WARNING_LIMIT) {
      warn(
        `${baseline.path} exports ${exportCount} symbols; review whether the public surface should be split or kept behind a role-owned facade.`
      );
    }

    assert(
      lines <= baseline.limit,
      [
        `${baseline.path} has ${lines} lines; temporary limit is ${baseline.limit}.`,
        baseline.next,
      ].join("\n")
    );
  }
}

for (const baseline of TEST_FILE_BASELINES) {
  assert(fileExists(baseline.path), `Missing test architecture baseline target: ${baseline.path}`);

  if (fileExists(baseline.path)) {
    const source = readText(baseline.path);
    const lines = lineCount(source);
    testFileStats.push({ ...baseline, lines });

    if (lines >= Math.ceil(baseline.limit * NEAR_LIMIT_RATIO)) {
      nearLimitStats.push({ ...baseline, lines });
      warn(
        `${baseline.path} is near its test architecture limit: ${lines}/${baseline.limit} lines. ${baseline.next}`
      );
    }

    assert(
      lines <= baseline.limit,
      [
        `${baseline.path} has ${lines} lines; temporary test limit is ${baseline.limit}.`,
        baseline.next,
      ].join("\n")
    );
  }
}

if (fileExists("backend")) {
  const requiredBackendFiles = [
    "pyproject.toml",
    "backend/app/__main__.py",
    "backend/app/main.py",
    "backend/app/settings.py",
    "backend/app/api/dependencies.py",
    "backend/app/api/health.py",
    "backend/app/api/ai_runs.py",
    "backend/app/api/drafts.py",
    "backend/app/api/draft_generation_contracts.py",
    "backend/app/api/draft_runs.py",
    "backend/app/application/health_service.py",
    "backend/app/application/ai_run_service.py",
    "backend/app/application/draft_generation_service.py",
    "backend/app/application/deterministic_draft_service.py",
    "backend/app/application/draft_run_payloads.py",
    "backend/app/application/draft_run_context_payloads.py",
    "backend/app/application/draft_run_context_builder.py",
    "backend/app/application/draft_source_ledger_builder.py",
    "backend/app/application/draft_source_ledger_sections.py",
    "backend/app/application/draft_feasibility_gate.py",
    "backend/app/application/draft_feasibility_policy.py",
    "backend/app/application/draft_post_contract_builder.py",
    "backend/app/application/publication_size_contract_resolver.py",
    "backend/app/application/draft_quality_gate.py",
    "backend/app/application/draft_rule_pack_compiler.py",
    "backend/app/application/draft_rule_pack_sections.py",
    "backend/app/application/draft_rule_pack_from_registry.py",
    "backend/app/application/draft_rule_registry_compiler.py",
    "backend/app/application/draft_rule_registry_contract.py",
    "backend/app/application/draft_rule_registry_size.py",
    "backend/app/application/draft_rule_registry_sections.py",
    "backend/app/application/draft_material_plan_service.py",
    "backend/app/application/material_plan_evidence_projection.py",
    "backend/app/application/material_plan_accountability.py",
    "backend/app/application/material_plan_retry_policy.py",
    "backend/app/application/material_plan_retry_orchestrator.py",
    "backend/app/application/draft_strategy_service.py",
    "backend/app/application/source_intent_normalizer.py",
    "backend/app/application/source_research_plan_service.py",
    "backend/app/application/source_research_plan_sanitizer.py",
    "backend/app/application/source_research_prompts.py",
    "backend/app/application/source_research_audit.py",
    "backend/app/application/public_evidence_retrieval_service.py",
    "backend/app/application/public_evidence_query_builder.py",
    "backend/app/application/public_evidence_relevance.py",
    "backend/app/application/draft_public_evidence_step_service.py",
    "backend/app/application/deterministic_external_evidence_synthesis.py",
    "backend/app/application/deterministic_external_evidence_synthesis_step_service.py",
    "backend/app/application/external_evidence_synthesis_prompts.py",
    "backend/app/application/external_evidence_synthesis_service.py",
    "backend/app/application/source_ledger_external_evidence_merger.py",
    "backend/app/application/openrouter_public_search_service.py",
    "backend/app/application/public_evidence_ports.py",
    "backend/app/application/disabled_public_search_adapter.py",
    "backend/app/application/deterministic_source_research_plan_service.py",
    "backend/app/application/deterministic_source_research_step_service.py",
    "backend/app/application/draft_rhetorical_plan_service.py",
    "backend/app/application/draft_rhetorical_plan_retry.py",
    "backend/app/application/json_step_retry_policy.py",
    "backend/app/application/draft_rhetorical_plan_prompts.py",
    "backend/app/application/draft_rhetorical_plan_audit.py",
    "backend/app/application/deterministic_rhetorical_plan_service.py",
    "backend/app/application/deterministic_rhetorical_plan_step_service.py",
    "backend/app/application/draft_candidate_direction_service.py",
    "backend/app/application/draft_candidate_generation_service.py",
    "backend/app/application/draft_candidate_selection_service.py",
    "backend/app/application/draft_candidate_publishability.py",
    "backend/app/application/draft_candidate_prompts.py",
    "backend/app/application/draft_candidate_audit.py",
    "backend/app/application/deterministic_draft_candidate_service.py",
    "backend/app/application/draft_candidate_result.py",
    "backend/app/application/draft_candidate_selection_block.py",
    "backend/app/application/draft_run_pipeline_ports.py",
    "backend/app/application/draft_run_progress.py",
    "backend/app/application/draft_run_step_progress.py",
    "backend/app/application/draft_run_step_progress_payload.py",
    "backend/app/application/draft_run_staleness.py",
    "backend/app/application/draft_run_draft_step_service.py",
    "backend/app/application/draft_validation_linter.py",
    "backend/app/application/draft_attribution_markers.py",
    "backend/app/application/draft_attribution_requirements.py",
    "backend/app/application/draft_validation_evidence.py",
    "backend/app/application/draft_validator_orchestrator.py",
    "backend/app/application/draft_llm_validation_service.py",
    "backend/app/application/draft_llm_validation_prompts.py",
    "backend/app/application/draft_llm_validation_audit.py",
    "backend/app/application/draft_llm_validation_parser.py",
    "backend/app/application/draft_llm_validation_observations.py",
    "backend/app/application/draft_validation_step_service.py",
    "backend/app/application/draft_validation_step.py",
    "backend/app/application/draft_validation_operation_safety.py",
    "backend/app/application/deterministic_pairwise_ranking.py",
    "backend/app/application/draft_pairwise_ranking_prompts.py",
    "backend/app/application/draft_pairwise_ranking_service.py",
    "backend/app/application/draft_pairwise_ranking_payloads.py",
    "backend/app/application/draft_directed_revision_prompts.py",
    "backend/app/application/draft_directed_revision_service.py",
    "backend/app/application/draft_revision_instruction_builder.py",
    "backend/app/application/draft_revision_regression.py",
    "backend/app/application/draft_final_quality_assessment.py",
    "backend/app/application/draft_final_quality_attribution.py",
    "backend/app/application/draft_final_quality_contract.py",
    "backend/app/application/draft_final_quality_gate.py",
    "backend/app/application/draft_final_quality_gate_evaluator.py",
    "backend/app/application/draft_final_quality_gate_payloads.py",
    "backend/app/application/draft_final_quality_repair_loop.py",
    "backend/app/application/draft_final_quality_review_parser.py",
    "backend/app/application/draft_final_quality_review_prompts.py",
    "backend/app/application/draft_final_quality_review_service.py",
    "backend/app/application/draft_revision_loop_config.py",
    "backend/app/application/draft_revision_goal_evaluator.py",
    "backend/app/application/draft_editorial_revision_goals.py",
    "backend/app/application/draft_editorial_revision_evaluator.py",
    "backend/app/application/draft_revision_rejected_moves.py",
    "backend/app/application/draft_revision_loop_policy.py",
    "backend/app/application/draft_revision_loop_cycle_runner.py",
    "backend/app/application/draft_revision_loop_service.py",
    "backend/app/application/draft_ranking_revision_result.py",
    "backend/app/application/draft_ranking_revision_mapping.py",
    "backend/app/application/draft_ranking_revision_service.py",
    "backend/app/application/draft_validation_ranking_bridge.py",
    "backend/app/application/draft_model_role_resolver.py",
    "backend/app/application/draft_generation_params.py",
    "backend/app/application/draft_provider_error_utils.py",
    "backend/app/application/draft_article_dossier_builder.py",
    "backend/app/application/draft_context_pack_builder.py",
    "backend/app/application/draft_article_memory_service.py",
    "backend/app/application/draft_planning_prompts.py",
    "backend/app/application/draft_planning_audit.py",
    "backend/app/application/deterministic_draft_planning_service.py",
    "backend/app/application/deterministic_draft_planning_step_services.py",
    "backend/app/application/draft_planning_result.py",
    "backend/app/application/draft_run_pipeline.py",
    "backend/app/application/draft_run_service.py",
    "backend/app/domain/health.py",
    "backend/app/domain/ai_run.py",
    "backend/app/domain/draft_generation.py",
    "backend/app/domain/draft_run.py",
    "backend/app/domain/draft_run_steps.py",
    "backend/app/domain/draft_run_context.py",
    "backend/app/domain/draft_source_ledger.py",
    "backend/app/domain/draft_source_intent.py",
    "backend/app/domain/draft_public_evidence.py",
    "backend/app/domain/draft_evidence_synthesis.py",
    "backend/app/domain/draft_feasibility.py",
    "backend/app/domain/draft_post_contract.py",
    "backend/app/domain/publication_size.py",
    "backend/app/domain/draft_rule_pack.py",
    "backend/app/domain/draft_rule_registry.py",
    "backend/app/domain/draft_planning.py",
    "backend/app/domain/draft_rhetorical_plan.py",
    "backend/app/domain/draft_candidates.py",
    "backend/app/domain/draft_validation.py",
    "backend/app/domain/draft_llm_validation.py",
    "backend/app/domain/draft_ranking_revision.py",
    "backend/app/domain/draft_model_roles.py",
    "backend/app/domain/draft_article_memory.py",
    "backend/app/infrastructure/openrouter_config.py",
    "backend/app/infrastructure/openrouter_draft_adapter.py",
    "backend/app/infrastructure/openrouter_json_adapter.py",
    "backend/app/infrastructure/openrouter_web_search_adapter.py",
    "backend/app/infrastructure/public_url_reader.py",
    "backend/app/infrastructure/sqlite_ai_run_repository.py",
    "backend/app/infrastructure/celery_app.py",
    "backend/app/infrastructure/celery_draft_run_dispatcher.py",
    "backend/app/infrastructure/draft_run_tasks.py",
    "backend/app/infrastructure/draft_run_pipeline_factory.py",
    "backend/app/infrastructure/draft_run_pipeline_provider_services.py",
    "backend/app/infrastructure/draft_run_pipeline_validation_services.py",
    "backend/app/infrastructure/sqlite_draft_run_repository.py",
    "backend/tests/test_settings.py",
    "backend/tests/test_settings_draft_models.py",
    "backend/tests/test_health_api.py",
    "backend/tests/test_ai_run_api.py",
    "backend/tests/test_ai_run_repository.py",
    "backend/tests/test_draft_generation_api.py",
    "backend/tests/test_draft_run_api.py",
    "backend/tests/test_draft_run_pipeline.py",
    "backend/tests/test_draft_run_pipeline_article_memory.py",
    "backend/tests/test_draft_run_context_builder.py",
    "backend/tests/test_draft_source_ledger_builder.py",
    "backend/tests/test_draft_feasibility_and_contract.py",
    "backend/tests/test_publication_size_contract.py",
    "backend/tests/test_draft_rule_pack_compiler.py",
    "backend/tests/test_draft_rule_registry_compiler.py",
    "backend/tests/test_draft_planning_services.py",
    "backend/tests/test_draft_material_plan_service.py",
    "backend/tests/test_source_intent_and_research_plan.py",
    "backend/tests/test_source_research_plan_sanitizer.py",
    "backend/tests/test_public_evidence_retrieval.py",
    "backend/tests/test_external_evidence_synthesis_and_merge.py",
    "backend/tests/test_openrouter_public_search_service.py",
    "backend/tests/test_openrouter_public_search_relevance.py",
    "backend/tests/test_draft_candidate_services.py",
    "backend/tests/test_draft_candidate_selection_guard.py",
    "backend/tests/test_draft_validation.py",
    "backend/tests/test_draft_llm_validation_service.py",
    "backend/tests/test_draft_model_role_resolver.py",
    "backend/tests/test_draft_article_memory.py",
    "backend/tests/test_draft_llm_validation_parser.py",
    "backend/tests/test_draft_ranking_revision.py",
    "backend/tests/test_draft_rhetorical_plan_service.py",
    "backend/tests/test_draft_rhetorical_plan_retry.py",
    "backend/tests/test_draft_run_pipeline_validation_step.py",
    "backend/tests/test_draft_run_pipeline_candidates.py",
    "backend/tests/test_draft_run_pipeline_candidate_block.py",
    "backend/tests/test_draft_run_pipeline_planning_steps.py",
    "backend/tests/test_draft_run_pipeline_rule_pack.py",
    "backend/tests/test_draft_run_pipeline_source_ledger.py",
    "backend/tests/test_draft_run_pipeline_external_evidence.py",
    "backend/tests/test_draft_run_pipeline_quality_gate.py",
    "backend/tests/test_draft_run_pipeline_progress.py",
    "backend/tests/test_draft_run_staleness_api.py",
    "backend/tests/test_draft_run_repository.py",
  ];

  for (const requiredFile of requiredBackendFiles) {
    assert(fileExists(requiredFile), `Missing backend architecture source file: ${requiredFile}`);
  }

  for (const baseline of BACKEND_SOURCE_BASELINES) {
    assert(fileExists(baseline.path), `Missing backend baseline target: ${baseline.path}`);

    if (fileExists(baseline.path)) {
      const source = readText(baseline.path);
      const lines = lineCount(source);
      backendSourceStats.push({ ...baseline, lines });

      if (lines >= Math.ceil(baseline.limit * NEAR_LIMIT_RATIO)) {
        nearLimitStats.push({ ...baseline, lines });
        warn(
          `${baseline.path} is near its backend architecture limit: ${lines}/${baseline.limit} lines. ${baseline.next}`
        );
      }

      assert(
        lines <= baseline.limit,
        [
          `${baseline.path} has ${lines} lines; temporary backend limit is ${baseline.limit}.`,
          baseline.next,
        ].join("\n")
      );
    }
  }
}

const forbiddenAppTestSymbols = [
  "goToSignals",
  "createApprovedBrief",
  "createApprovedFinalText",
  "createExportedRelease",
  "getByLabelText",
];

for (const symbol of forbiddenAppTestSymbols) {
  assert(
    !appTestSource.includes(symbol),
    `src/App.test.tsx must not contain feature-flow test internals: ${symbol}. Move the scenario into a feature-owned *AppFlow.test.tsx file.`
  );
}

assert(
  !appSource.includes("LocalWorkspaceStore"),
  "src/App.tsx must not import or instantiate LocalWorkspaceStore; use src/app/useWorkspaceController.ts."
);

const workspaceControllerSource = readText("src/app/useWorkspaceController.ts");
const forbiddenWorkspaceControllerSymbols = [
  "sendContextChatMessage",
  "acceptContextChatSuggestion",
  "approveSourceSignal",
  "saveRadar",
  "createDraftFromBrief",
  "downloadMarkdown",
];

for (const symbol of forbiddenWorkspaceControllerSymbols) {
  assert(
    !workspaceControllerSource.includes(symbol),
    `src/app/useWorkspaceController.ts must not contain app action internals: ${symbol}. Use role-owned app hooks.`
  );
}

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

const signalsViewSource = readText("src/features/signals/SignalsView.tsx");
const forbiddenSignalsViewSymbols = [
  "function openNewRadar",
  "function saveRadarDraft",
  "filteredSignals",
  "function startSignalEdit",
  "function patchRadarRule",
  "function patchRadarSource",
];

for (const symbol of forbiddenSignalsViewSymbols) {
  assert(
    !signalsViewSource.includes(symbol),
    `src/features/signals/SignalsView.tsx must not contain signals internals: ${symbol}. Use useSignalsController or feature-local tab/entity modules.`
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

const authorMemoryViewSource = readText("src/features/author-memory/AuthorMemoryView.tsx");
const forbiddenAuthorMemoryEntrypointSymbols = [
  "function submitNote",
  "function saveEdit",
  "function performBulkAction",
  "function acceptArchiveRecordToMemory",
  "function restoreArchiveRecordToQueue",
  "function deleteArchiveRecord",
];

for (const symbol of forbiddenAuthorMemoryEntrypointSymbols) {
  assert(
    !authorMemoryViewSource.includes(symbol),
    `AuthorMemoryView.tsx must not contain author-memory orchestration internals: ${symbol}. Use feature-local hooks.`
  );
}

const importQueueViewSource = readText("src/features/author-memory/ImportQueueView.tsx");
const forbiddenImportQueueViewSymbols = [
  "function patchFilters",
  "import-filter-grid",
  "bulk-bar",
  "view-toggle",
  "groups.map",
  "filteredCandidates.map",
];

for (const symbol of forbiddenImportQueueViewSymbols) {
  assert(
    !importQueueViewSource.includes(symbol),
    `ImportQueueView.tsx must not contain import queue internals: ${symbol}. Use feature-local queue modules.`
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
const moduleReferencePattern =
  /(?:from\s+|import\s*\(\s*|import\s+)["']([^"']+)["']/g;

for (const featureFile of featureFiles) {
  const [, featureName] = featureFile.match(/^src\/features\/([^/]+)\//) ?? [];
  if (!featureName) {
    continue;
  }

  const source = readText(featureFile);
  for (const match of source.matchAll(moduleReferencePattern)) {
    const importPath = match[1];
    const resolvedImport = resolveModuleReference(featureFile, importPath);

    assert(
      !["src/features", "@/features", "~features"].includes(importPath) &&
        resolvedImport !== "src/features" &&
        !resolvedImport.startsWith("src/features/index"),
      `${featureFile} imports a root features barrel (${importPath}); use app wiring, shared/ui, application, or domain instead.`
    );

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

const featureBarrelFiles = featureFiles.filter((featureFile) =>
  /^src\/features\/(?:index|[^/]+\/index)\.(?:ts|tsx)$/.test(featureFile)
);

assert(
  featureBarrelFiles.length === 0,
  `Feature barrel files can bypass dependency hygiene and are forbidden: ${featureBarrelFiles.join(", ")}`
);

const backendPythonFiles = fileExists("backend/app") ? listFiles("backend/app", [".py"]) : [];
const pythonImportPattern = /^\s*(?:from\s+([A-Za-z_][\w.]+)\s+import|import\s+([A-Za-z_][\w.]+))/gm;

function pythonImports(source) {
  return [...source.matchAll(pythonImportPattern)].map((match) => match[1] ?? match[2]);
}

function importsForbiddenModule(importPath, forbiddenModule) {
  return importPath === forbiddenModule || importPath.startsWith(`${forbiddenModule}.`);
}

const backendDomainForbiddenImports = [
  "fastapi",
  "httpx",
  "requests",
  "celery",
  "redis",
  "sqlite3",
  "sqlalchemy",
  "pydantic_settings",
  "uvicorn",
  "openai",
  "langgraph_document_ai_platform",
  "langgraph",
];

const backendApiForbiddenImports = [
  "httpx",
  "requests",
  "celery",
  "redis",
  "sqlite3",
  "openai",
  "langgraph_document_ai_platform",
  "langgraph",
];

for (const backendFile of backendPythonFiles) {
  const imports = pythonImports(readText(backendFile));
  const forbiddenImports = backendFile.startsWith("backend/app/domain/")
    ? backendDomainForbiddenImports
    : backendFile.startsWith("backend/app/api/")
      ? backendApiForbiddenImports
      : [];

  for (const importPath of imports) {
    for (const forbiddenImport of forbiddenImports) {
      assert(
        !importsForbiddenModule(importPath, forbiddenImport),
        `${backendFile} imports ${importPath}; backend layer forbids ${forbiddenImport} here.`
      );
    }
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
  "Feature entrypoints stay thin",
  "Domain transitions are role-owned",
  "domain/application/fixtures/feature files must shrink through the 1.5.x refactoring chain",
  "Architecture drift prevention",
  "Test ownership guardrails",
  "src/test-support",
  "*AppFlow.test.tsx",
  "near-limit",
  "agent workflow",
  "## Backend AI Execution Architecture",
  "OpenRouter is the default LLM provider target",
  "langgraph-document-ai-platform",
  "no 2-3k line backend files",
  "no provider calls from API handlers",
  "backend/app/api/health.py",
  "backend/app/api/ai_runs.py",
  "backend/app/api/drafts.py",
  "backend/app/api/draft_runs.py",
  "backend/app/api/portfolio.py",
  "backend/app/api/portfolio_contracts.py",
  "backend/app/application/health_service.py",
  "backend/app/application/ai_run_service.py",
  "backend/app/application/draft_generation_service.py",
  "backend/app/application/portfolio_service.py",
  "backend/app/application/draft_run_service.py",
  "backend/app/application/draft_run_pipeline.py",
  "backend/app/application/draft_validation_linter.py",
  "backend/app/application/draft_attribution_markers.py",
  "backend/app/application/draft_attribution_requirements.py",
  "backend/app/application/draft_validation_evidence.py",
  "backend/app/application/draft_validator_orchestrator.py",
  "backend/app/application/draft_llm_validation_service.py",
  "backend/app/application/draft_llm_validation_prompts.py",
  "backend/app/application/draft_llm_validation_audit.py",
  "backend/app/application/draft_llm_validation_parser.py",
  "backend/app/application/draft_llm_validation_observations.py",
  "backend/app/application/draft_validation_step_service.py",
  "backend/app/application/draft_validation_step.py",
  "backend/app/application/deterministic_pairwise_ranking.py",
  "backend/app/application/draft_pairwise_ranking_prompts.py",
  "backend/app/application/draft_pairwise_ranking_service.py",
  "backend/app/application/draft_pairwise_ranking_payloads.py",
  "backend/app/application/draft_directed_revision_prompts.py",
  "backend/app/application/draft_directed_revision_service.py",
  "backend/app/application/draft_revision_instruction_builder.py",
  "backend/app/application/draft_revision_regression.py",
  "backend/app/application/draft_final_quality_assessment.py",
  "backend/app/application/draft_final_quality_attribution.py",
  "backend/app/application/draft_final_quality_contract.py",
  "backend/app/application/draft_final_quality_gate.py",
  "backend/app/application/draft_final_quality_gate_evaluator.py",
  "backend/app/application/draft_final_quality_gate_payloads.py",
  "backend/app/application/draft_final_quality_repair_loop.py",
  "backend/app/application/draft_final_quality_review_parser.py",
  "backend/app/application/draft_final_quality_review_prompts.py",
  "backend/app/application/draft_final_quality_review_service.py",
  "backend/app/application/draft_revision_loop_config.py",
  "backend/app/application/draft_revision_goal_evaluator.py",
  "backend/app/application/draft_editorial_revision_goals.py",
  "backend/app/application/draft_editorial_revision_evaluator.py",
  "backend/app/application/draft_revision_rejected_moves.py",
  "backend/app/application/draft_revision_loop_policy.py",
  "backend/app/application/draft_revision_loop_cycle_runner.py",
  "backend/app/application/draft_revision_loop_service.py",
  "backend/app/application/draft_ranking_revision_result.py",
  "backend/app/application/draft_ranking_revision_mapping.py",
  "backend/app/application/draft_ranking_revision_service.py",
  "backend/app/application/draft_validation_ranking_bridge.py",
  "backend/app/application/draft_validation_operation_safety.py",
  "backend/app/application/draft_model_role_resolver.py",
  "backend/app/application/draft_generation_params.py",
  "backend/app/application/draft_provider_error_utils.py",
  "backend/app/application/draft_article_dossier_builder.py",
  "backend/app/application/draft_context_pack_builder.py",
  "backend/app/application/draft_article_memory_service.py",
  "backend/app/application/draft_run_context_builder.py",
  "backend/app/application/draft_source_ledger_builder.py",
  "backend/app/application/draft_source_ledger_sections.py",
  "backend/app/application/draft_feasibility_gate.py",
  "backend/app/application/draft_feasibility_policy.py",
  "backend/app/application/draft_post_contract_builder.py",
  "backend/app/application/draft_quality_gate.py",
  "backend/app/application/draft_rule_pack_compiler.py",
  "backend/app/application/draft_rule_pack_sections.py",
  "backend/app/application/draft_rule_pack_from_registry.py",
  "backend/app/application/draft_rule_registry_compiler.py",
  "backend/app/application/draft_rule_registry_contract.py",
  "backend/app/application/draft_rule_registry_sections.py",
  "backend/app/application/draft_material_plan_service.py",
  "backend/app/application/material_plan_evidence_projection.py",
  "backend/app/application/material_plan_accountability.py",
  "backend/app/application/material_plan_retry_policy.py",
  "backend/app/application/material_plan_retry_orchestrator.py",
  "backend/app/application/draft_strategy_service.py",
  "backend/app/application/source_intent_normalizer.py",
  "backend/app/application/source_research_plan_service.py",
  "backend/app/application/source_research_plan_sanitizer.py",
  "backend/app/application/source_research_prompts.py",
  "backend/app/application/source_research_audit.py",
    "backend/app/application/public_evidence_retrieval_service.py",
    "backend/app/application/public_evidence_query_builder.py",
    "backend/app/application/public_evidence_relevance.py",
    "backend/app/application/draft_public_evidence_step_service.py",
    "backend/app/application/deterministic_external_evidence_synthesis.py",
    "backend/app/application/deterministic_external_evidence_synthesis_step_service.py",
    "backend/app/application/external_evidence_synthesis_prompts.py",
    "backend/app/application/external_evidence_synthesis_service.py",
    "backend/app/application/source_ledger_external_evidence_merger.py",
    "backend/app/application/openrouter_public_search_service.py",
  "backend/app/application/public_evidence_ports.py",
  "backend/app/application/disabled_public_search_adapter.py",
  "backend/app/application/deterministic_source_research_plan_service.py",
  "backend/app/application/draft_rhetorical_plan_service.py",
  "backend/app/application/draft_rhetorical_plan_retry.py",
  "backend/app/application/json_step_retry_policy.py",
  "backend/app/application/draft_rhetorical_plan_prompts.py",
  "backend/app/application/draft_rhetorical_plan_audit.py",
  "backend/app/application/deterministic_rhetorical_plan_service.py",
  "backend/app/application/deterministic_rhetorical_plan_step_service.py",
  "backend/app/application/draft_candidate_generation_service.py",
  "backend/app/application/draft_candidate_direction_service.py",
  "backend/app/application/draft_candidate_selection_service.py",
  "backend/app/application/draft_run_draft_step_service.py",
  "backend/app/application/draft_run_step_progress.py",
  "backend/app/application/draft_run_step_progress_payload.py",
  "backend/app/infrastructure/openrouter_config.py",
  "backend/app/infrastructure/openrouter_draft_adapter.py",
  "backend/app/infrastructure/openrouter_json_adapter.py",
  "backend/app/infrastructure/openrouter_web_search_adapter.py",
  "backend/app/infrastructure/public_url_reader.py",
  "backend/app/infrastructure/sqlite_ai_run_repository.py",
  "backend/app/infrastructure/sqlite_draft_run_repository.py",
  "backend/app/infrastructure/sqlite_portfolio_repository.py",
  "backend/app/infrastructure/celery_app.py",
  "backend/app/infrastructure/draft_run_tasks.py",
  "backend/app/infrastructure/draft_run_pipeline_factory.py",
  "backend/app/infrastructure/draft_run_pipeline_provider_services.py",
  "backend/app/infrastructure/draft_run_pipeline_validation_services.py",
  "backend/app/domain/portfolio.py",
  "backend/app/domain/draft_run_steps.py",
  "backend/app/domain/draft_run_context.py",
  "backend/app/domain/draft_source_ledger.py",
    "backend/app/domain/draft_source_intent.py",
    "backend/app/domain/draft_public_evidence.py",
    "backend/app/domain/draft_evidence_synthesis.py",
    "backend/app/domain/draft_feasibility.py",
  "backend/app/domain/draft_post_contract.py",
  "backend/app/domain/draft_rule_pack.py",
  "backend/app/domain/draft_rule_registry.py",
  "backend/app/domain/draft_planning.py",
  "backend/app/domain/draft_rhetorical_plan.py",
    "backend/app/domain/draft_candidates.py",
  "backend/app/domain/draft_llm_validation.py",
  "backend/app/domain/draft_ranking_revision.py",
  "backend/app/domain/draft_revision_loop.py",
  "backend/app/domain/draft_model_roles.py",
  "backend/app/domain/draft_article_memory.py",
    "backend/app/domain/draft_revision_loop.py",
  "src/application/draftRunContext.ts",
  "Dockerized local stack",
  "Redis",
  "Celery",
  "compose.yaml",
  "docker/backend.Dockerfile",
  "docker/frontend.Dockerfile",
];

for (const fragment of requiredSaoFragments) {
  assert(
    saoSource.includes(fragment),
    `SAO is missing required React architecture fragment: ${fragment}`
  );
}

if (failures.length > 0) {
  if (warnings.length > 0) {
    console.warn("Architecture smoke warnings:");
    for (const warning of warnings) {
      console.warn(`- ${warning}`);
    }
  }

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
for (const stat of testFileStats) {
  console.log(`- ${stat.path}: ${stat.lines}/${stat.limit} test lines`);
}
for (const stat of backendSourceStats) {
  console.log(`- ${stat.path}: ${stat.lines}/${stat.limit} backend lines`);
}

if (nearLimitStats.length > 0) {
  console.log(
    `- Near-limit files (>= ${Math.round(NEAR_LIMIT_RATIO * 100)}% of limit):`
  );
  for (const stat of nearLimitStats) {
    console.log(`  - ${stat.path}: ${stat.lines}/${stat.limit} lines`);
  }
} else {
  console.log(`- Near-limit files (>= ${Math.round(NEAR_LIMIT_RATIO * 100)}% of limit): none`);
}

const exportWarnings = exportCountStats.filter(
  (stat) => stat.exportCount > DEFAULT_EXPORT_COUNT_WARNING_LIMIT
);

if (exportWarnings.length > 0) {
  console.log(`- Export-count warnings (> ${DEFAULT_EXPORT_COUNT_WARNING_LIMIT} exports):`);
  for (const stat of exportWarnings) {
    console.log(`  - ${stat.path}: ${stat.exportCount} exports`);
  }
} else {
  console.log(`- Export-count warnings (> ${DEFAULT_EXPORT_COUNT_WARNING_LIMIT} exports): none`);
}
