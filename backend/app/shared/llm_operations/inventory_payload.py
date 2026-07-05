"""Owner: shared.llm_operations

Used by: Diagnostics and architecture smoke to serialize operation inventory data.
Does not own: Provider execution, prompt text, operation routing, or roadmap status changes.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.shared.llm_operations.drafting_inventory_data import CURRENT_LLM_OPERATION_INVENTORY


class LlmOperationInventoryPayloadExporter:
    def payload(self) -> list[dict[str, object]]:
        return [entry.to_payload() for entry in CURRENT_LLM_OPERATION_INVENTORY]

operation_inventory_payload = LlmOperationInventoryPayloadExporter().payload
