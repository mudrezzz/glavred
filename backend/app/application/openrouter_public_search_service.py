from backend.app.application.ai_run_service import AiRunService
from backend.app.application.public_evidence_ports import PublicEvidenceSearchResult, PublicEvidenceSearchTask
from backend.app.application.public_evidence_relevance import filter_relevant_citations
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_public_evidence import (
    PublicEvidenceAllowedUse,
    PublicEvidenceAttempt,
    PublicEvidenceAttemptStatus,
    PublicEvidenceItem,
    PublicEvidenceWarning,
)
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.settings import BackendSettings


class OpenRouterPublicSearchService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        web_search_adapter: OpenRouterWebSearchAdapter,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._web_search_adapter = web_search_adapter

    def search(self, task: PublicEvidenceSearchTask) -> PublicEvidenceSearchResult:
        if not self._settings.openrouter_web_tools_enabled:
            return self._not_configured(task, "OpenRouter web tools are disabled.")
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return self._not_configured(task, "OpenRouter is not configured.")
        attempt_id = _attempt_id("search", task.task_id, task.source_intent_item_id)
        messages = _search_messages(task.query)
        request_payload = _request_trace(
            task=task,
            model=self._settings.openrouter_web_search_model_or_default,
            max_results=self._settings.openrouter_web_search_max_results,
            messages=messages,
        )
        try:
            result = self._web_search_adapter.search(settings=self._settings, query=task.query, messages=messages)
            relevance = filter_relevant_citations(result.citations, task=task)
            items = [
                PublicEvidenceItem(
                    id=f"public-evidence-{attempt_id}-{index + 1}",
                    attempt_id=attempt_id,
                    source_url=citation.url,
                    source_title=citation.title,
                    snippet=_truncate(citation.snippet or result.content, 700),
                    text_summary=_truncate(citation.snippet or result.content, 1200),
                    provenance="openrouterWebSearch",
                    confidence="medium",
                    allowed_use=PublicEvidenceAllowedUse.NEEDS_QUALIFICATION,
                    extraction_notes=["Search citation from OpenRouter web_search; ledger merge and validation are still required."],
                )
                for index, citation in enumerate(relevance.accepted)
            ]
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=self._settings.openrouter_web_search_model_or_default,
                request_payload=request_payload,
                result_payload={
                    "draftRunStep": "publicEvidenceSearch",
                    "content": result.content,
                    "citations": [citation.__dict__ for citation in result.citations],
                    "acceptedCitations": [citation.__dict__ for citation in relevance.accepted],
                    "rejectedCitations": relevance.rejected,
                    "evidenceItems": [item.to_payload() for item in items],
                    "providerResponse": result.raw_response,
                },
                fallback_used=False,
            )
            warnings = []
            if not result.citations:
                warnings.append(PublicEvidenceWarning(code="search-no-citations", message="OpenRouter search returned no citations.", target=task.query))
            elif not items:
                warnings.append(PublicEvidenceWarning(code="search-no-relevant-evidence", message="OpenRouter search citations did not match the research task.", target=task.query))
            return PublicEvidenceSearchResult(
                attempts=[PublicEvidenceAttempt(
                    id=attempt_id,
                    task_id=task.task_id,
                    source_intent_item_id=task.source_intent_item_id,
                    kind="search",
                    target=task.technical_target or task.query,
                    status=PublicEvidenceAttemptStatus.SUCCEEDED,
                    notes=["OpenRouter web_search executed; citations became evidence candidates."],
                    metadata={**_task_metadata(task), "rejectedCitations": relevance.rejected},
                )],
                items=items,
                warnings=warnings,
                ai_run_ids=[run.id],
                metadata={"searchProvider": "openrouter:web_search", "model": self._settings.openrouter_web_search_model_or_default, "aiRunId": run.id, "rejectedCitationCount": len(relevance.rejected)},
            )
        except Exception as exc:
            error = self._safe_error(exc)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=self._settings.openrouter_web_search_model_or_default,
                request_payload=request_payload,
                result_payload={"draftRunStep": "publicEvidenceSearch", "error": error, "fallback": "noSearchEvidence"},
                fallback_used=True,
                error=error,
            )
            return PublicEvidenceSearchResult(
                attempts=[PublicEvidenceAttempt(
                    id=attempt_id,
                    task_id=task.task_id,
                    source_intent_item_id=task.source_intent_item_id,
                    kind="search",
                    target=task.technical_target or task.query,
                    status=PublicEvidenceAttemptStatus.FAILED,
                    notes=["OpenRouter web_search failed; no evidence item was created."],
                    error=error,
                    metadata=_task_metadata(task),
                )],
                warnings=[PublicEvidenceWarning(code="openrouter-search-failed", message=error, target=task.query)],
                ai_run_ids=[run.id],
                metadata={"searchProvider": "openrouter:web_search", "model": self._settings.openrouter_web_search_model_or_default, "aiRunId": run.id},
            )

    def _not_configured(self, task: PublicEvidenceSearchTask, reason: str) -> PublicEvidenceSearchResult:
        return PublicEvidenceSearchResult(
            attempts=[PublicEvidenceAttempt(
                id=_attempt_id("search", task.task_id, task.source_intent_item_id),
                task_id=task.task_id,
                source_intent_item_id=task.source_intent_item_id,
                kind="search",
                target=task.technical_target or task.query,
                status=PublicEvidenceAttemptStatus.NOT_CONFIGURED,
                notes=[reason],
                metadata=_task_metadata(task),
            )],
            metadata={"searchProvider": "notConfigured"},
        )

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _search_messages(target: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "Use web search to find public evidence. Return a concise grounded answer with citations. Do not invent facts."},
        {"role": "user", "content": f"Find credible public sources for this research task:\n{target}"},
    ]


def _request_trace(
    *,
    task: PublicEvidenceSearchTask,
    model: str,
    max_results: int,
    messages: list[dict[str, str]],
) -> dict:
    return {
        "draftRunStep": "publicEvidenceSearch",
        "taskId": task.task_id,
        "sourceIntentItemId": task.source_intent_item_id,
        "target": task.technical_target,
        "builtQuery": task.query,
        "originalTask": task.original_task,
        "sourceTarget": task.source_target,
        "exclusions": task.exclusions,
        "providerRequest": {
            "model": model,
            "messages": messages,
            "tools": [{"type": "openrouter:web_search", "parameters": {"max_results": max_results}}],
        },
    }


def _attempt_id(prefix: str, task_id: str | None, source_intent_item_id: str | None) -> str:
    suffix = task_id or source_intent_item_id or "unlinked"
    return f"{prefix}-{suffix}"


def _task_metadata(task: PublicEvidenceSearchTask) -> dict:
    return {
        "builtQuery": task.query,
        "originalTask": task.original_task,
        "sourceTarget": task.source_target,
        "exclusions": task.exclusions,
    }


def _truncate(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit].rstrip()
