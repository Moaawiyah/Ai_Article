"""Matplotlib graph generator — 2-panel PNG for the article pipeline.

Panel 1 (left):  CDF of bottleneck queue length (packets)
Panel 2 (right): Average FCT (ms) vs Network Load (%)
"""

from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

_FILENAME = "benchmark.png"

_COLORS     = ["#1f77b4", "#ff7f0e", "#2ca02c"]
_LINESTYLES = ["-",        "--",       "-."]

_FALLBACK_SERIES = [
    {"name": "Main",           "median_queue": 12,  "p95_queue": 45,
     "base_fct_ms": 1.2, "fct_slope": 0.015},
    {"name": "Architecture A", "median_queue": 60,  "p95_queue": 200,
     "base_fct_ms": 4.0, "fct_slope": 0.080},
    {"name": "Architecture B", "median_queue": 120, "p95_queue": 380,
     "base_fct_ms": 8.0, "fct_slope": 0.160},
]


def _lognormal_params(median: float, p95: float) -> tuple[float, float]:
    """Fit lognormal mu and sigma from median and 95th-percentile."""
    import numpy as np
    mu    = float(np.log(max(median, 1)))
    sigma = (float(np.log(max(p95, median + 1))) - mu) / 1.645
    return mu, max(sigma, 0.01)


def _fct_curve(load, base_fct: float, slope: float):
    """Average FCT (ms) as a function of network load (%).

    Stays flat at base_fct until ~40% load, then grows with an exponential
    kick above 80% to mimic queuing-theory blow-up near saturation.
    """
    import numpy as np
    linear = base_fct + slope * load
    # Extra blow-up near saturation
    blowup = np.where(load > 80, base_fct * 0.5 * ((load - 80) / 20) ** 2, 0)
    return linear + blowup


def generate_performance_graph(
    topic: str,
    output_dir: Path,
    spec: dict | None = None,
) -> str | None:
    """Generate a 2-panel PNG (CDF queue + FCT vs Load) and save to output_dir.

    spec: dict from graph_spec.generate_graph_spec() with keys main/arch_a/arch_b.
    Returns the bare filename on success, or None if matplotlib is unavailable.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
        import numpy as np
    except ImportError:
        log.warning("matplotlib not installed — skipping graph generation")
        return None

    available = {f.name for f in font_manager.fontManager.ttflist}
    font = "Times New Roman" if "Times New Roman" in available else "DejaVu Serif"

    series = [spec["main"], spec["arch_a"], spec["arch_b"]] if spec else _FALLBACK_SERIES

    rng  = np.random.default_rng(42)
    load = np.linspace(0, 100, 200)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    short_topic = (topic[:50] + "…") if len(topic) > 50 else topic
    fig.suptitle(short_topic, fontname=font, fontsize=10, y=1.01)

    # ── Panel 1: CDF of bottleneck queue length ──────────────────────────────
    x_max = max(float(s["p95_queue"]) for s in series) * 1.15
    x_cdf = np.linspace(0, x_max, 500)

    for s, color, ls in zip(series, _COLORS, _LINESTYLES):
        mu, sigma = _lognormal_params(float(s["median_queue"]), float(s["p95_queue"]))
        samples   = rng.lognormal(mu, sigma, size=20_000)
        cdf       = np.searchsorted(np.sort(samples), x_cdf, side="right") / len(samples)
        ax1.plot(x_cdf, cdf, label=s["name"], linewidth=2, color=color, linestyle=ls)

    for pct, label in ((0.50, "p50"), (0.95, "p95")):
        ax1.axhline(pct, color="grey", linewidth=0.7, linestyle=":", alpha=0.6)
        ax1.text(x_max * 0.02, pct + 0.01, label, fontsize=8, color="grey", fontname=font)

    ax1.set_xlabel("Bottleneck Queue Length (packets)", fontname=font, fontsize=11)
    ax1.set_ylabel("CDF",                               fontname=font, fontsize=11)
    ax1.set_title("Bottleneck Queue CDF",               fontname=font, fontsize=11)
    ax1.legend(framealpha=0.9, prop={"family": font, "size": 9})
    ax1.set_xlim(0, x_max)
    ax1.set_ylim(0, 1.05)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(True, linestyle="--", alpha=0.4)

    # ── Panel 2: Average FCT vs Network Load ─────────────────────────────────
    for s, color, ls in zip(series, _COLORS, _LINESTYLES):
        fct = _fct_curve(load, float(s["base_fct_ms"]), float(s["fct_slope"]))
        ax2.plot(load, fct, label=s["name"], linewidth=2, color=color, linestyle=ls)

    ax2.set_xlabel("Network Load (%)",      fontname=font, fontsize=11)
    ax2.set_ylabel("Average FCT (ms)",      fontname=font, fontsize=11)
    ax2.set_title("Avg. Flow Completion Time vs. Load", fontname=font, fontsize=11)
    ax2.legend(framealpha=0.9, prop={"family": font, "size": 9})
    ax2.set_xlim(0, 100)
    ax2.set_ylim(bottom=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(True, linestyle="--", alpha=0.4)

    fig.tight_layout()

    out_path = output_dir / _FILENAME
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info("2-panel graph saved → %s", out_path)
    return _FILENAME
