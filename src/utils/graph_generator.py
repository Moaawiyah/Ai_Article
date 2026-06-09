"""Matplotlib performance graph generator for the article pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

_FILENAME = "benchmark.png"


def generate_performance_graph(topic: str, output_dir: Path) -> str | None:
    """Generate a performance comparison PNG and save it to output_dir.

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

    load = np.linspace(0, 100, 50)
    # HULA: sustains high throughput, graceful degradation above 80 % load
    hula = np.where(
        load <= 80,
        9.5 * (1 - 0.0005 * load**2),
        9.5 * (1 - 0.0005 * 64**2) - 0.04 * (load - 80),
    )
    hula = np.clip(hula, 0, 10)
    # ECMP: lower peak, earlier drop under congestion
    ecmp = np.where(
        load <= 60,
        7.0 * (1 - 0.0012 * load**2) + 4,
        7.0 * (1 - 0.0012 * 36**2) + 4 - 0.07 * (load - 60),
    )
    ecmp = np.clip(ecmp, 0, 10)

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(load, hula, label="HULA",  linewidth=2,   color="#1f77b4")
    ax.plot(load, ecmp, label="ECMP",  linewidth=2,   color="#ff7f0e", linestyle="--")

    ax.set_xlabel("Network Load (%)",   fontname=font, fontsize=11)
    ax.set_ylabel("Throughput (Gbps)",  fontname=font, fontsize=11)
    short_topic = (topic[:55] + "…") if len(topic) > 55 else topic
    ax.set_title(f"Load Balancing Performance\n{short_topic}", fontname=font, fontsize=10)
    ax.legend(framealpha=0.9, prop={"family": font, "size": 10})
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 11)
    fig.tight_layout()

    out_path = output_dir / _FILENAME
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    log.info("Graph saved → %s", out_path)
    return _FILENAME
