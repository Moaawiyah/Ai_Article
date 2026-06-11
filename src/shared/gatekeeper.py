"""API Gatekeeper — centralised rate-limiting, queuing, and retry for all API calls."""

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate-limit settings loaded from config (never hard-coded)."""

    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    retry_after_seconds: int
    max_retries: int
    queue_max_depth: int
    minute_window_seconds: int
    hour_window_seconds: int


@dataclass
class QueueStatus:
    """Snapshot of the gatekeeper queue."""

    depth: int
    processed_total: int
    failed_total: int


class ApiGatekeeper:
    """Centralized API call manager.

    All external API calls must pass through this gatekeeper.
    Enforces rate limits, queues overflow requests (FIFO), and retries
    on transient failures.
    """

    def __init__(self, config: RateLimitConfig) -> None:
        """Initialize with rate-limit config."""
        self._cfg = config
        self._minute_window: deque = deque()
        self._hour_window: deque = deque()
        self._semaphore = threading.Semaphore(config.concurrent_max)
        self._request_queue: deque[object] = deque()
        self._processed = 0
        self._failed = 0
        self._condition = threading.Condition()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, api_call: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute *api_call* through the gatekeeper.

        - Checks rate limits before execution
        - Queues request if limit is reached (backpressure)
        - Retries on transient failures up to max_retries times
        - Logs every call
        """
        ticket = object()
        self._enqueue(ticket)
        self._wait_for_turn(ticket)
        try:
            return self._execute_with_retry(api_call, *args, **kwargs)
        finally:
            with self._condition:
                self._semaphore.release()
                self._condition.notify_all()

    def get_queue_status(self) -> QueueStatus:
        """Return current queue depth and cumulative stats."""
        return QueueStatus(
            depth=len(self._request_queue),
            processed_total=self._processed,
            failed_total=self._failed,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _enqueue(self, ticket: object) -> None:
        """Append a request to the bounded FIFO queue, applying backpressure."""
        with self._condition:
            while len(self._request_queue) >= self._cfg.queue_max_depth:
                self._condition.wait()
            self._request_queue.append(ticket)
            self._condition.notify_all()

    def _wait_for_turn(self, ticket: object) -> None:
        """Wait until *ticket* is first in FIFO order and a rate slot is free."""
        while True:
            now = time.monotonic()
            with self._condition:
                self._purge_window(
                    self._minute_window, now, self._cfg.minute_window_seconds
                )
                self._purge_window(
                    self._hour_window, now, self._cfg.hour_window_seconds
                )
                is_head = bool(self._request_queue) and self._request_queue[0] is ticket
                within_limits = (
                    len(self._minute_window) < self._cfg.requests_per_minute
                    and len(self._hour_window) < self._cfg.requests_per_hour
                )
                if is_head and within_limits and self._semaphore.acquire(blocking=False):
                    self._minute_window.append(now)
                    self._hour_window.append(now)
                    self._request_queue.popleft()
                    self._condition.notify_all()
                    return
                logger.debug("Request queued; waiting %ss", self._cfg.retry_after_seconds)
                self._condition.wait(timeout=self._cfg.retry_after_seconds)

    @staticmethod
    def _purge_window(window: deque, now: float, span: int) -> None:
        """Remove timestamps older than *span* seconds from *window*."""
        cutoff = now - span
        while window and window[0] < cutoff:
            window.popleft()

    def _execute_with_retry(self, api_call: Callable, *args: Any, **kwargs: Any) -> Any:
        """Run *api_call*, retrying on Exception up to max_retries times."""
        last_exc: Exception | None = None
        for attempt in range(1, self._cfg.max_retries + 1):
            try:
                result = api_call(*args, **kwargs)
                with self._condition:
                    self._processed += 1
                logger.info("API call succeeded on attempt %d", attempt)
                return result
            except Exception as exc:
                last_exc = exc
                logger.warning("API call failed (attempt %d/%d): %s", attempt, self._cfg.max_retries, exc)
                if attempt < self._cfg.max_retries:
                    time.sleep(self._cfg.retry_after_seconds)
        with self._condition:
            self._failed += 1
        raise RuntimeError(f"API call failed after {self._cfg.max_retries} retries") from last_exc
