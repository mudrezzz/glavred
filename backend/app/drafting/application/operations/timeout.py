"""Owner: drafting.application.operations

Used by: provider-heavy DraftRun operation services that need bounded execution.
Does not own: provider adapters, retry policy, prompt construction, persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue
from threading import Thread
from typing import Callable, Generic, TypeVar


ResultT = TypeVar("ResultT")


class OperationTimeoutError(TimeoutError):
    """Raised when a provider-heavy operation does not return in the configured envelope."""


@dataclass(frozen=True)
class TimedOperationResult(Generic[ResultT]):
    value: ResultT
    elapsed_ms: int


class TimedOperationRunner:
    """Runs a blocking callable in a daemon thread and returns control on timeout.

    Python cannot safely kill an arbitrary blocked thread. The intent here is
    containment: the DraftRun worker regains control, records a failed attempt,
    and continues to fallback instead of leaving the parent step running forever.
    """

    def run(self, operation: Callable[[], ResultT], *, timeout_seconds: float) -> TimedOperationResult[ResultT]:
        import time

        result_queue: Queue[tuple[str, object]] = Queue(maxsize=1)

        def target() -> None:
            try:
                result_queue.put(("value", operation()))
            except BaseException as exc:  # noqa: BLE001 - propagate safe operation errors to caller
                result_queue.put(("error", exc))

        start = time.perf_counter()
        thread = Thread(target=target, daemon=True)
        thread.start()
        try:
            kind, payload = result_queue.get(timeout=max(timeout_seconds, 0.001))
        except Empty as exc:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            raise OperationTimeoutError(f"Operation timed out after {timeout_seconds}s ({elapsed_ms}ms)") from exc

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if kind == "error":
            raise payload  # type: ignore[misc]
        return TimedOperationResult(value=payload, elapsed_ms=elapsed_ms)  # type: ignore[arg-type]
