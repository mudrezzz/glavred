"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.revision.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.drafting.application.revision.draft_editorial_revision_evaluator import DraftEditorialRevisionEvaluator
from backend.app.drafting.application.revision.draft_editorial_revision_goals import DraftEditorialRevisionGoalBuilder
from backend.app.drafting.application.revision.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.drafting.application.revision.draft_revision_acceptance_policy import RevisionAcceptancePolicy
from backend.app.drafting.application.revision.draft_revision_goal_evaluator import DraftRevisionGoalEvaluator
from backend.app.drafting.application.revision.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
from backend.app.drafting.application.revision.draft_revision_loop_cycle_runner import DraftRevisionLoopCycleRunner
from backend.app.drafting.application.revision.draft_revision_loop_policy import RevisionLoopPolicy
from backend.app.drafting.application.revision.draft_revision_rejected_moves import RevisionRejectedMovePolicy
from backend.app.drafting.application.revision.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.domain.draft_revision_loop import RevisionLoopCycle
from backend.app.drafting.application.operations.validation_runtime_budget import STOP_BUDGET_EXHAUSTED, finalize_revision_loop_stop, operation_denied_by_runtime_budget
from backend.app.drafting.application.operations.validation_revision_loop_payloads import DraftRevisionLoopResult, revision_loop_report, successful_cycle

class DraftRevisionLoopService:
    def __init__(
        self,
        *,
        ranking_service: DraftPairwiseRankingService,
        revision_service: DraftDirectedRevisionService,
        instruction_builder: DraftRevisionInstructionBuilder | None = None,
        regression_guard: DraftRevisionRegressionGuard | None = None,
        goal_evaluator: DraftRevisionGoalEvaluator | None = None,
        editorial_goal_builder: DraftEditorialRevisionGoalBuilder | None = None,
        editorial_evaluator: DraftEditorialRevisionEvaluator | None = None,
        acceptance_policy: RevisionAcceptancePolicy | None = None,
        loop_policy: RevisionLoopPolicy | None = None,
        rejected_move_policy: RevisionRejectedMovePolicy | None = None,
        max_iterations: int = 3,
    ) -> None:
        self._instruction_builder = instruction_builder or DraftRevisionInstructionBuilder()
        self._regression = regression_guard or DraftRevisionRegressionGuard()
        self._goals = goal_evaluator or DraftRevisionGoalEvaluator()
        self._editorial_goals = editorial_goal_builder or DraftEditorialRevisionGoalBuilder()
        self._editorial = editorial_evaluator or DraftEditorialRevisionEvaluator()
        self._acceptance = acceptance_policy or RevisionAcceptancePolicy()
        self._policy = loop_policy or RevisionLoopPolicy()
        self._rejected_moves = rejected_move_policy or RevisionRejectedMovePolicy()
        self._cycles = DraftRevisionLoopCycleRunner(ranking_service=ranking_service, revision_service=revision_service, regression_guard=self._regression)
        self._max_iterations = max(1, max_iterations)

    def run(
        self,
        *,
        winner: dict[str, Any] | None,
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftRevisionLoopResult:
        current = winner
        current_validation = validation_report
        constraints: list[str] = []
        cycles: list[RevisionLoopCycle] = []
        ai_run_ids: list[str] = []
        first_instruction: dict[str, Any] | None = None
        last_revision: dict[str, Any] | None = None
        last_regression: dict[str, Any] | None = None
        rejected_moves: list[dict[str, Any]] = []
        stop_reason = "validator-clean"
        detail_stop_reason: str | None = None
        guard = progress.runtime_guard if progress else None

        for cycle_number in range(1, self._max_iterations + 1):
            if operation_denied_by_runtime_budget(progress, kind="directedRevision", operation_id=f"directed-revision-cycle-{cycle_number}", detail="directed-revision-budget-denied"):
                detail_stop_reason = guard.detail_stop_reason or "runtime-budget-exhausted"
                stop_reason = STOP_BUDGET_EXHAUSTED
                break
            current_id = self._policy.candidate_id(current)
            instruction = self._instruction_builder.build(candidate_id=current_id, validation_report=current_validation).to_payload()
            if first_instruction is None:
                first_instruction = instruction
            repair_goals = self._policy.string_list(instruction.get("repairGoals"))
            editorial_goals = self._editorial_goals.build(
                candidate_id=current_id,
                repair_goals=repair_goals,
                validation_report=current_validation,
                rule_pack=rule_pack,
                material_plan=material_plan,
                previous_rejected_moves=rejected_moves,
            )
            if instruction.get("status") != "created" and not editorial_goals:
                stop_reason = "validator-clean"
                break
            instruction["status"] = "created"
            instruction["constraints"] = constraints
            instruction["editorialGoals"] = editorial_goals
            instruction["rejectedMoves"] = rejected_moves[-8:]
            revision = self._cycles.revise(
                cycle_number=cycle_number,
                candidate=current,
                instruction=instruction,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                progress=progress,
            )
            last_revision = revision
            revision_ids = self._policy.string_list(revision.get("aiRunIds"))
            ai_run_ids.extend(revision_ids)
            revised = self._policy.dict_or_empty(revision.get("revisedCandidate")) or None
            if revision.get("status") != "succeeded" or not revised:
                detail_stop_reason = str(revision.get("reason") or revision.get("error") or "directed-revision-failed")
                cycles.append(self._policy.failed_cycle(
                    cycle_number=cycle_number,
                    base_id=current_id,
                    goals=repair_goals or self._rejected_moves.goal_messages(editorial_goals),
                    editorial_goals=editorial_goals,
                    constraints=constraints,
                    revision=revision,
                    ai_run_ids=revision_ids,
                    validation_before=current_validation,
                ))
                stop_reason = "provider-failed"
                break

            regression = self._cycles.regress(
                cycle_number=cycle_number,
                current_id=current_id,
                revised=revised,
                current_validation=current_validation,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                progress=progress,
            )
            last_regression = regression.to_payload()
            validation_after = regression.validation_report or {}
            goal_result = self._goals.evaluate(
                repair_goals=repair_goals,
                validation_before=current_validation,
                validation_after=validation_after,
                base_candidate_id=current_id,
                revised_candidate_id=self._policy.candidate_id(revised),
            )
            comparison = self._cycles.compare(
                cycle_number=cycle_number,
                current=current,
                revised=revised,
                current_validation=current_validation,
                revised_validation=validation_after,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                progress=progress,
            )
            compare_ids = self._policy.string_list(comparison.get("aiRunIds"))
            ai_run_ids.extend(compare_ids)
            editorial_result = self._editorial.evaluate(
                editorial_goals=editorial_goals,
                pairwise_comparison=comparison,
                current_id=current_id,
                revised_id=self._policy.candidate_id(revised),
            )
            accepted, decision_reasons = self._acceptance.acceptance_decision(
                current_id=current_id,
                revised_id=self._policy.candidate_id(revised),
                regression_reasons=regression.reasons,
                resolved_goals=goal_result["resolved"],
                resolved_editorial_goals=editorial_result["resolvedEditorialGoals"],
                regressed_editorial_dimensions=editorial_result["regressedEditorialDimensions"],
                pairwise_winner=self._policy.pairwise_winner(comparison),
            )
            new_rejected_moves = [] if accepted else self._rejected_moves.rejected_moves_from_cycle(
                cycle_number=cycle_number,
                revised_candidate=revised,
                rejection_reasons=decision_reasons,
                unresolved_editorial_goals=editorial_result["unresolvedEditorialGoals"],
            )
            cycles.append(successful_cycle(
                cycle_number=cycle_number,
                current_id=current_id,
                repair_goals=repair_goals,
                constraints=[*constraints],
                revised=revised,
                validation_before=current_validation,
                validation_after=validation_after,
                comparison=comparison,
                goal_result=goal_result,
                editorial_goals=editorial_goals,
                editorial_result=editorial_result,
                new_rejected_moves=new_rejected_moves,
                stop_reason=self._rejected_moves.cycle_stop_reason(accepted, goal_result["unresolved"], editorial_result["unresolvedEditorialGoals"]),
                accepted=accepted,
                decision_reasons=decision_reasons,
                ai_run_ids=[*revision_ids, *compare_ids],
            ))
            if guard:
                guard.record_revision_outcome(accepted=accepted)
            if accepted:
                current = revised
                current_validation = validation_after
                constraints = [
                    *self._policy.constraints_from_unresolved(goal_result["unresolved"]),
                    *self._rejected_moves.constraints_from_editorial_goals(editorial_result["unresolvedEditorialGoals"]),
                ]
                stop_reason = "editorially-improved" if editorial_result["resolvedEditorialGoals"] else "validator-clean"
                if not constraints:
                    break
                continue
            rejected_moves.extend(new_rejected_moves)
            constraints.extend([*self._policy.constraints_from_rejection(decision_reasons, goal_result["unresolved"]), *self._rejected_moves.constraints_from_rejected_moves(new_rejected_moves)])
            stop_reason = "no-fresh-angle"

        if cycles and len(cycles) >= self._max_iterations and stop_reason not in {"provider-failed", "no-fresh-angle"} and constraints:
            stop_reason = "max-iterations"
            detail_stop_reason = detail_stop_reason or "max-iterations"

        canonical_stop_reason, detail_stop_reason, runtime_budget = finalize_revision_loop_stop(guard, stop_reason, detail_stop_reason)

        report = revision_loop_report(
            current=current,
            cycles=cycles,
            max_iterations=self._max_iterations,
            stop_reason=canonical_stop_reason,
            constraints=constraints,
            detail_stop_reason=detail_stop_reason,
            runtime_budget=runtime_budget,
        )
        return DraftRevisionLoopResult(report, current, first_instruction, last_revision, last_regression, ai_run_ids)
