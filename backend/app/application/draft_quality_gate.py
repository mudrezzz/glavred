from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_feasibility_gate import FeasibilityGate
from backend.app.application.draft_post_contract_builder import PostContractBuilder


@dataclass(frozen=True)
class DraftQualityGateResult:
    context_artifact: dict[str, Any]
    feasibility_report: dict[str, Any]
    post_contract: dict[str, Any]
    blocked: bool
    complete_payload: dict[str, Any] | None


class DraftQualityGate:
    def __init__(
        self,
        feasibility_gate: FeasibilityGate | None = None,
        post_contract_builder: PostContractBuilder | None = None,
    ) -> None:
        self._feasibility_gate = feasibility_gate or FeasibilityGate()
        self._post_contract_builder = post_contract_builder or PostContractBuilder()

    def evaluate(self, context_artifact: dict[str, Any]) -> DraftQualityGateResult:
        report = self._feasibility_gate.evaluate(context_artifact)
        feasibility_payload = report.to_payload()
        if report.blocked:
            contract_payload = self._post_contract_builder.not_created(report)
            enriched = {
                **context_artifact,
                "feasibilityReport": feasibility_payload,
                "postContract": contract_payload,
            }
            return DraftQualityGateResult(
                context_artifact=enriched,
                feasibility_report=feasibility_payload,
                post_contract=contract_payload,
                blocked=True,
                complete_payload={
                    "status": "blocked",
                    "blockedBy": "feasibility",
                    "feasibilityStatus": report.status.value,
                    "reason": report.summary,
                },
            )
        contract_payload = self._post_contract_builder.build(context_artifact, report).to_payload()
        enriched = {
            **context_artifact,
            "feasibilityReport": feasibility_payload,
            "postContract": contract_payload,
        }
        return DraftQualityGateResult(
            context_artifact=enriched,
            feasibility_report=feasibility_payload,
            post_contract=contract_payload,
            blocked=False,
            complete_payload=None,
        )
