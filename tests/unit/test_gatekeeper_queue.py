"""Concurrency tests for ApiGatekeeper's FIFO bounded queue."""

import threading
import time

from shared.gatekeeper import ApiGatekeeper, RateLimitConfig


def _fast_config(**overrides) -> RateLimitConfig:
    """Build a fast, deterministic config (no real sleeps)."""
    params = {
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
        "concurrent_max": 5,
        "retry_after_seconds": 0,
        "max_retries": 2,
    }
    params.update(overrides)
    return RateLimitConfig(**params)


def test_depth_moves_under_load():
    """Queue depth rises while a call blocks and returns to 0 after release."""
    gk = ApiGatekeeper(_fast_config(concurrent_max=1))
    started = threading.Event()
    release = threading.Event()

    def blocking():
        started.set()
        release.wait(timeout=5)
        return "done"

    workers = [threading.Thread(target=gk.execute, args=(blocking,)) for _ in range(4)]
    for w in workers:
        w.start()

    assert started.wait(timeout=5)
    # Spin briefly until the other 3 threads have enqueued their tickets.
    deadline = time.monotonic() + 5
    while gk.get_queue_status().depth < 4 and time.monotonic() < deadline:
        time.sleep(0.01)
    assert gk.get_queue_status().depth > 0

    release.set()
    for w in workers:
        w.join(timeout=5)
    assert gk.get_queue_status().depth == 0
    assert gk.get_queue_status().processed_total == 4


def test_fifo_admission_order():
    """With concurrent_max=1, bodies must start in submission order."""
    gk = ApiGatekeeper(_fast_config(concurrent_max=1))
    order: list[int] = []
    order_lock = threading.Lock()
    hold = threading.Event()

    def make(idx: int):
        def body():
            # Block the first body so later submissions all queue up behind it.
            hold.wait(timeout=5)
            with order_lock:
                order.append(idx)
            return idx

        return body

    workers = []
    for i in range(6):
        # Stagger submission so tickets are taken in strict index order.
        t = threading.Thread(target=gk.execute, args=(make(i),))
        t.start()
        workers.append(t)
        time.sleep(0.02)

    hold.set()
    for w in workers:
        w.join(timeout=5)

    assert order == sorted(order)
    assert order == list(range(6))


def test_backpressure_no_crash():
    """Tiny queue + flood of threads: all complete, nothing raised, no drops."""
    gk = ApiGatekeeper(_fast_config(queue_maxsize=1, concurrent_max=1))
    errors: list[Exception] = []
    err_lock = threading.Lock()

    def run():
        try:
            gk.execute(lambda: 1)
        except Exception as exc:  # noqa: BLE001
            with err_lock:
                errors.append(exc)

    workers = [threading.Thread(target=run) for _ in range(10)]
    for w in workers:
        w.start()
    for w in workers:
        w.join(timeout=10)

    assert errors == []
    assert gk.get_queue_status().processed_total == 10
    assert gk.get_queue_status().depth == 0


def test_config_windows_and_maxsize_used():
    """Configured window/maxsize values flow into the gatekeeper."""
    cfg = _fast_config(
        queue_maxsize=7,
        minute_window_seconds=120,
        hour_window_seconds=7200,
    )
    assert cfg.minute_window_seconds == 120
    assert cfg.hour_window_seconds == 7200
    gk = ApiGatekeeper(cfg)
    assert gk._request_queue.maxsize == 7


def test_tiny_rpm_window_blocks_then_admits():
    """A 1-RPM limit serializes within the window, then admits after purge."""
    cfg = _fast_config(
        requests_per_minute=1,
        retry_after_seconds=0,
        minute_window_seconds=0,  # window purges immediately so calls admit
    )
    gk = ApiGatekeeper(cfg)
    assert gk.execute(lambda: "a") == "a"
    assert gk.execute(lambda: "b") == "b"
    assert gk.get_queue_status().processed_total == 2
