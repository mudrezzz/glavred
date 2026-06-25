from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_revision_goal_evaluator import DraftRevisionGoalEvaluator
from backend.app.application.draft_revision_instruction_builder import DraftRevisionInstructionBuilder
from backend.app.application.draft_revision_loop_policy import acceptance_decision, candidate_id, combined_validation, constraints_from_rejection, constraints_from_unresolved, dict_or_empty, failed_cycle, last_value, pairwise_winner, string_list
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
        max_iterations: int = 3,
    ) -> None:
        self._ranking = ranking_service
        self._revision = revision_service
        self._instruction_builder = instruction_builder or DraftRevisionInstructionBuilder()
        self._regression = regression_guard or DraftRevisionRegressionGuard()
        self._goals = goal_evaluator or DraftRevisionGoalEvaluator()
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
        stop_reason = "quality-threshold"

        for cycle_number in range(1, self._max_iterations + 1):
            current_id = candidate_id(current)
            instruction = self._instruction_builder.build(candidate_id=current_id, validation_report=current_validation).to_payload()
            if first_instruction is None:
                first_instruction = instruction
            repair_goals = string_list(instruction.get("repairGoals"))
            if instruction.get("status") != "created" or not repair_goals:
                stop_reason = "quality-threshold"
                break
            instruction["constraints"] = constraints
            revision = self._revise_cycle(cycle_number, current, instruction, context_artifact, rule_pack, material_plan, progress)
            last_revision = revision
            revision_ids = string_list(revision.get("aiRunIds"))
            ai_run_ids.extend(revision_ids)
            revised = dict_or_empty(revision.get("revisedCandidate")) or None
            if revision.get("status") != "succeeded" or not revised:
                cycles.append(failed_cycle(
                    cycle_number=cycle_number,
                    base_id=current_id,
                    goals=repair_goals,
                    constraints=constraints,
                    revision=revision,
                    ai_run_ids=revision_ids,
                    validation_before=current_validation,
                ))
                stop_reason = "provider-failed"
                break

            regression = self._regress_cycle(cycle_number, current_id, revised, current_validation, context_artifact, rule_pack, material_plan, progress)
            last_regression = regression.to_payload()
            validation_after = regression.validation_report or {}
            goal_result = self._goals.evaluate(
                repair_goals=repair_goals,
                validation_before=current_validation,
                validation_after=validation_after,
                base_candidate_id=current_id,
                revised_candidate_id=candidate_id(revised),
            )
            comparison = self._compare_cycle(cycle_number, current, revised, current_validation, validation_after, context_artifact, rule_pack, material_plan, progress)
            compare_ids = string_list(comparison.get("aiRunIds"))
            ai_run_ids.extend(compare_ids)
            accepted, reasons = acceptance_decision(
                current_id=current_id,
                revised_id=candidate_id(revised),
                regression_reasons=regression.reasons,
                resolved_goals=goal_result["resolved"],
                pairwise_winner=pairwise_winner(comparison),
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
                accepted=accepted,
                rejection_reasons=reasons,
                ai_run_ids=[*revision_ids, *compare_ids],
            ))
            if accepted:
                current = revised
                current_validation = validation_after
                constraints = constraints_from_unresolved(goal_result["unresolved"])
                stop_reason = "quality-threshold" if not constraints else "max-iterations"
                if not constraints:
                    break
                continue
            constraints.extend(constraints_from_rejection(reasons, goal_result["unresolved"]))
            stop_reason = "no-improvement"

        report = RevisionLoopReport(
            status="succeeded" if current else "blocked",
            max_iterations=self._max_iterations,
            cycles=cycles,
            final_candidate_id=candidate_id(current),
            final_source="revisionLoop" if any(cycle.accepted for cycle in cycles) else "originalCandidate",
            stop_reason=stop_reason,
            unresolved_goals=cycles[-1].unresolved_goals if cycles else [],
            constraints=constraints,
        )
        return DraftRevisionLoopResult(report, current, first_instruction, last_revision, last_regression, ai_run_ids)

    def _revise_cycle(
        self,
        cycle_number: int,
        candidate: dict[str, Any] | None,
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        operation_id = f"directed-revision-cycle-{cycle_number}"
        if progress:
            progress.start_operation(operation_id, kind="directedRevision", label=f"Revision cycle {cycle_number}", target=candidate_id(candidate) or "none")
        revision = self._revision.revise(candidate=candidate, instruction=instruction, context_artifact=context_artifact, rule_pack=rule_pack, material_plan=material_plan)
        if progress:
            progress.complete_operation(operation_id, ai_run_id=last_value(string_list(revision.get("aiRunIds"))), notes=[f"status={revision.get('status')}"])
        return revision

    def _regress_cycle(
        self,
        cycle_number: int,
        current_id: str | None,
        revised: dict[str, Any],
        current_validation: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ):
        operation_id = f"revision-regression-cycle-{cycle_number}"
        if progress:
            progress.start_operation(operation_id, kind="revisionRegression", label=f"Regression guard cycle {cycle_number}")
        regression = self._regression.evaluate(
            original_candidate_id=str(current_id or ""),
            revised_candidate=revised,
            validation_report=current_validation,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        if progress:
            progress.complete_operation(operation_id, notes=[f"accepted={regression.accepted}"])
        return regression

    def _compare_cycle(
        self,
        cycle_number: int,
        current: dict[str, Any] | None,
        revised: dict[str, Any],
        current_validation: dict[str, Any],
        revised_validation: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        operation_id = f"revision-pairwise-cycle-{cycle_number}"
        if progress:
            progress.start_operation(operation_id, kind="pairwiseRanking", label=f"Compare revision cycle {cycle_number}")
        report = self._ranking.rank(
            draft_artifact={"candidates": [item for item in [current, revised] if item], "selection": {"scorecard": []}},
            validation_report=combined_validation(current_validation, revised_validation),
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        )
        if progress:
            progress.complete_operation(operation_id, ai_run_id=last_value(report.ai_run_ids), notes=[f"winner={report.decision.winner_candidate_id}"])
        return report.to_payload()
