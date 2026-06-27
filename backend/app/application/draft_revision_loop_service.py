from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_editorial_revision_evaluator import DraftEditorialRevisionEvaluator
from backend.app.application.draft_editorial_revision_goals import DraftEditorialRevisionGoalBuilder
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_revision_acceptance_policy import acceptance_decision
from backend.app.application.draft_revision_goal_evaluator import DraftRevisionGoalEvaluator
from backend.app.application.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
from backend.app.application.draft_revision_loop_cycle_runner import DraftRevisionLoopCycleRunner
from backend.app.application.draft_revision_loop_policy import candidate_id, constraints_from_rejection, constraints_from_unresolved, dict_or_empty, failed_cycle, pairwise_winner, string_list
from backend.app.application.draft_revision_rejected_moves import constraints_from_editorial_goals, constraints_from_rejected_moves, cycle_stop_reason, goal_messages, rejected_moves_from_cycle
from backend.app.application.draft_revision_regression import DraftRevisionRegressionGuard
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.domain.draft_revision_loop import RevisionLoopCycle, RevisionLoopReport

@dataclass(frozen=True)
class DraftRevisionLoopResult:
    report: RevisionLoopReport
    final_candidate: dict[str, Any] | None
    first_instruction: dict[str, Any] | None
    last_revision: dict[str, Any] | None
    last_regression: dict[str, Any] | None
    ai_run_ids: list[str]
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
        max_iterations: int = 3,
    ) -> None:
        self._instruction_builder = instruction_builder or DraftRevisionInstructionBuilder()
        self._regression = regression_guard or DraftRevisionRegressionGuard()
        self._goals = goal_evaluator or DraftRevisionGoalEvaluator()
        self._editorial_goals = editorial_goal_builder or DraftEditorialRevisionGoalBuilder()
        self._editorial = editorial_evaluator or DraftEditorialRevisionEvaluator()
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

        for cycle_number in range(1, self._max_iterations + 1):
            current_id = candidate_id(current)
            instruction = self._instruction_builder.build(candidate_id=current_id, validation_report=current_validation).to_payload()
            if first_instruction is None:
                first_instruction = instruction
            repair_goals = string_list(instruction.get("repairGoals"))
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
            revision_ids = string_list(revision.get("aiRunIds"))
            ai_run_ids.extend(revision_ids)
            revised = dict_or_empty(revision.get("revisedCandidate")) or None
            if revision.get("status") != "succeeded" or not revised:
                cycles.append(failed_cycle(
                    cycle_number=cycle_number,
                    base_id=current_id,
                    goals=repair_goals or goal_messages(editorial_goals),
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
                revised_candidate_id=candidate_id(revised),
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
            compare_ids = string_list(comparison.get("aiRunIds"))
            ai_run_ids.extend(compare_ids)
            editorial_result = self._editorial.evaluate(
                editorial_goals=editorial_goals,
                pairwise_comparison=comparison,
                current_id=current_id,
                revised_id=candidate_id(revised),
            )
            accepted, decision_reasons = acceptance_decision(
                current_id=current_id,
                revised_id=candidate_id(revised),
                regression_reasons=regression.reasons,
                resolved_goals=goal_result["resolved"],
                resolved_editorial_goals=editorial_result["resolvedEditorialGoals"],
                regressed_editorial_dimensions=editorial_result["regressedEditorialDimensions"],
                pairwise_winner=pairwise_winner(comparison),
            )
            new_rejected_moves = [] if accepted else rejected_moves_from_cycle(
                cycle_number=cycle_number,
                revised_candidate=revised,
                rejection_reasons=decision_reasons,
                unresolved_editorial_goals=editorial_result["unresolvedEditorialGoals"],
            )
            cycles.append(RevisionLoopCycle(
                cycle_number=cycle_number,
                base_candidate_id=current_id,
                repair_goals=repair_goals,
                constraints=[*constraints],
                revised_candidate=revised,
                validation_before=current_validation,
                validation_after=validation_after,
                pairwise_comparison=comparison,
                resolved_goals=goal_result["resolved"],
                unresolved_goals=goal_result["unresolved"],
                editorial_goals=editorial_goals,
                editorial_dimension_scores=editorial_result["editorialDimensionScores"],
                resolved_editorial_goals=editorial_result["resolvedEditorialGoals"],
                unresolved_editorial_goals=editorial_result["unresolvedEditorialGoals"],
                new_rejected_moves=new_rejected_moves,
                acceptance_decision={"accepted": accepted, "reasons": decision_reasons},
                stop_reason=cycle_stop_reason(accepted, goal_result["unresolved"], editorial_result["unresolvedEditorialGoals"]),
                accepted=accepted,
                rejection_reasons=[] if accepted else decision_reasons,
                ai_run_ids=[*revision_ids, *compare_ids],
            ))
            if accepted:
                current = revised
                current_validation = validation_after
                constraints = [
                    *constraints_from_unresolved(goal_result["unresolved"]),
                    *constraints_from_editorial_goals(editorial_result["unresolvedEditorialGoals"]),
                ]
                stop_reason = "editorially-improved" if editorial_result["resolvedEditorialGoals"] else "validator-clean"
                if not constraints:
                    break
                continue
            rejected_moves.extend(new_rejected_moves)
            constraints.extend([*constraints_from_rejection(decision_reasons, goal_result["unresolved"]), *constraints_from_rejected_moves(new_rejected_moves)])
            stop_reason = "no-fresh-angle"

        if cycles and len(cycles) >= self._max_iterations and stop_reason not in {"provider-failed", "no-fresh-angle"} and constraints:
            stop_reason = "max-iterations"

        report = RevisionLoopReport(
            status="succeeded" if current else "blocked",
            max_iterations=self._max_iterations,
            cycles=cycles,
            final_candidate_id=candidate_id(current),
            final_source="revisionLoop" if any(cycle.accepted for cycle in cycles) else "originalCandidate",
            stop_reason=stop_reason,
            unresolved_goals=[*cycles[-1].unresolved_goals, *goal_messages(cycles[-1].unresolved_editorial_goals)] if cycles else [],
            constraints=constraints,
        )
        return DraftRevisionLoopResult(report, current, first_instruction, last_revision, last_regression, ai_run_ids)
