"""Unit tests for ApiGatekeeper."""

import contextlib
import threading
import time

import pytest

from shared.gatekeeper import ApiGatekeeper, QueueStatus


def test_execute_success(gatekeeper):
    result = gatekeeper.execute(lambda: 42)
    assert result == 42


def test_execute_passes_args(gatekeeper):
    result = gatekeeper.execute(lambda x, y: x + y, 3, 4)
    assert result == 7


def test_execute_passes_kwargs(gatekeeper):
    result = gatekeeper.execute(lambda x=0: x * 2, x=5)
    assert result == 10


def test_queue_status_increments(gatekeeper):
    gatekeeper.execute(lambda: None)
    gatekeeper.execute(lambda: None)
    status = gatekeeper.get_queue_status()
    assert status.processed_total == 2
    assert status.failed_total == 0


def test_retry_on_transient_failure(rate_limit_config):
    """Call should succeed on second attempt after one failure."""
    call_count = {"n": 0}

    def flaky():
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise ConnectionError("transient")
        return "ok"

    gk = ApiGatekeeper(rate_limit_config)
    result = gk.execute(flaky)
    assert result == "ok"
    assert call_count["n"] == 2


def test_exhausted_retries_raises(rate_limit_config):
    """RuntimeError after all retries fail."""

    def always_fail():
        raise ConnectionError("permanent")

    gk = ApiGatekeeper(rate_limit_config)
    with pytest.raises(RuntimeError, match="retries"):
        gk.execute(always_fail)


def test_failed_counter_increments(rate_limit_config):
    gk = ApiGatekeeper(rate_limit_config)
    with contextlib.suppress(RuntimeError):
        gk.execute(lambda: (_ for _ in ()).throw(OSError("x")))
    assert gk.get_queue_status().failed_total == 1


def test_queue_status_type(gatekeeper):
    status = gatekeeper.get_queue_status()
    assert isinstance(status, QueueStatus)
    assert isinstance(status.depth, int)


def test_purge_window_removes_old_entries(rate_limit_config):
    """_purge_window should evict timestamps outside the span."""
    from collections import deque

    window = deque([0.0, 0.5, 1.0])
    ApiGatekeeper._purge_window(window, now=100.0, span=60)
    assert len(window) == 0


def test_purge_window_keeps_recent_entries(rate_limit_config):
    import time
    from collections import deque

    now = time.monotonic()
    window = deque([now - 5, now - 2, now])
    ApiGatekeeper._purge_window(window, now=now, span=60)
    assert len(window) == 3


def test_requests_execute_in_fifo_order(rate_limit_config):
    rate_limit_config.concurrent_max = 1
    gate = ApiGatekeeper(rate_limit_config)
    release = threading.Event()
    started = threading.Event()
    order = []

    def first():
        started.set()
        release.wait(timeout=2)
        order.append("first")

    def run(name):
        gate.execute(lambda: order.append(name))

    threads = [threading.Thread(target=lambda: gate.execute(first))]
    threads[0].start()
    assert started.wait(timeout=2)
    for name in ("second", "third"):
        thread = threading.Thread(target=run, args=(name,))
        threads.append(thread)
        thread.start()
        time.sleep(0.02)
    assert gate.get_queue_status().depth == 2
    release.set()
    for thread in threads:
        thread.join(timeout=2)
    assert order == ["first", "second", "third"]
    assert gate.get_queue_status().depth == 0
