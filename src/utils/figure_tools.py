"""CrewAI tools for generating article figures at agent runtime.

The Writer agent calls these tools to produce figures whose content is
derived from what the agent is actually writing, not pre-determined.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from crewai.tools import tool

_ASSETS = Path("outputs/assets")


@tool("generate_architecture_diagram")
def generate_architecture_diagram(agents_json: str) -> str:
    """Generate an architecture diagram PNG for a multi-agent system.

    Args:
        agents_json: JSON array of objects, each with keys:
            "name"  — agent role label (keep short, <=20 chars)
            "color" — hex color string, e.g. "#2E86AB"
            "desc"  — one-line description (<=30 chars)
            "output" — output filename this agent produces
        Example:
            [
              {"name":"Researcher","color":"#2E86AB","desc":"Finds sources","output":"research_brief.md"},
              {"name":"Writer","color":"#4CAF72","desc":"Drafts article","output":"draft.md"}
            ]

    Returns a confirmation message with the saved file path.
    """
    try:
        agents = json.loads(agents_json)
    except Exception as exc:
        return f"ERROR: could not parse agents_json — {exc}"

    n = len(agents)
    fig_w = max(10, n * 2.6 + 1)
    fig, ax = plt.subplots(figsize=(fig_w, 5.5))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    fig.patch.set_facecolor("#f8f9fa")

    box_w, box_h = 2.0, 1.6
    y_center = 3.0
    spacing = (fig_w - 1.0) / n
    xs = [0.5 + spacing * (i + 0.5) for i in range(n)]

    for agent, x in zip(agents, xs):
        shadow = mpatches.FancyBboxPatch(
            (x - box_w / 2 + 0.06, y_center - box_h / 2 - 0.06),
            box_w, box_h, boxstyle="round,pad=0.12",
            linewidth=0, facecolor="#bbbbbb", alpha=0.45, zorder=2,
        )
        ax.add_patch(shadow)
        box = mpatches.FancyBboxPatch(
            (x - box_w / 2, y_center - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.12", linewidth=1.6,
            edgecolor="#222", facecolor=agent.get("color", "#888"), alpha=0.90, zorder=3,
        )
        ax.add_patch(box)
        ax.text(x, y_center + 0.26, agent["name"],
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="white", zorder=4)
        ax.text(x, y_center - 0.35, agent.get("desc", ""),
                ha="center", va="center", fontsize=7.5, color="white", zorder=4)
        ax.text(x, y_center - box_h / 2 - 0.28, agent.get("output", ""),
                ha="center", va="top", fontsize=7, color="#444", style="italic")

    for i in range(len(xs) - 1):
        ax.annotate(
            "", xy=(xs[i + 1] - box_w / 2, y_center),
            xytext=(xs[i] + box_w / 2, y_center),
            arrowprops=dict(arrowstyle="-|>", color="#444", lw=1.9), zorder=2,
        )

    ax.text(fig_w / 2, 5.1,
            "Multi-Agent Collaboration Architecture",
            ha="center", fontsize=12, fontweight="bold", color="#111")

    _ASSETS.mkdir(parents=True, exist_ok=True)
    out = _ASSETS / "architecture_diagram.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return f"Architecture diagram saved to {out}"


@tool("generate_performance_graph")
def generate_performance_graph(data_json: str) -> str:
    """Generate a performance bar chart PNG for agent or system metrics.

    Args:
        data_json: JSON object with keys:
            "title"   — chart title string
            "xlabel"  — x-axis label
            "ylabel"  — y-axis label
            "labels"  — list of category labels (bars)
            "values"  — list of numeric values (same length as labels)
            "colors"  — optional list of hex color strings
        Example:
            {
              "title": "Agent Task Completion Rate",
              "xlabel": "Agent Role",
              "ylabel": "Completion Rate (%)",
              "labels": ["Researcher","Writer","Reviewer","LaTeX Formatter","PDF Validator"],
              "values": [92, 85, 88, 80, 94],
              "colors": ["#2E86AB","#4CAF72","#E8A838","#D9534F","#7B2D8B"]
            }

    Returns a confirmation message with the saved file path.
    """
    try:
        d = json.loads(data_json)
    except Exception as exc:
        return f"ERROR: could not parse data_json — {exc}"

    labels = d.get("labels", [])
    values = d.get("values", [])
    if not labels or not values or len(labels) != len(values):
        return "ERROR: labels and values must be non-empty lists of the same length"

    colors = d.get("colors") or plt.cm.tab10.colors[:len(labels)]
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 1.6), 5))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#f0f0f0")

    bars = ax.bar(x, values, color=colors, edgecolor="#333", linewidth=0.9,
                  width=0.55, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, rotation=15, ha="right")
    ax.set_ylabel(d.get("ylabel", "Value"), fontsize=10)
    ax.set_xlabel(d.get("xlabel", ""), fontsize=10)
    ax.set_title(d.get("title", "Performance Metrics"), fontsize=11, fontweight="bold")
    ax.yaxis.grid(True, linestyle="--", alpha=0.6, zorder=0)
    ax.set_axisbelow(True)

    max_val = max(values)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + max_val * 0.01,
                str(val), ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    _ASSETS.mkdir(parents=True, exist_ok=True)
    out = _ASSETS / "task_completion_graph.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return f"Performance graph saved to {out}"
