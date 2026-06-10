"""Fallback graph spec + architecture-name extraction from a research brief.

Used by graph_spec.py when the LLM call fails or is unavailable, so the
pipeline can still render a meaningful figure.
"""

from __future__ import annotations

import re

_FALLBACK: dict = {
    "main":   {"name": "Main",           "median_queue": 12,  "p95_queue": 45,
               "base_fct_ms": 1.2,  "fct_slope": 0.015,
               "data_basis": "estimated", "source": "synthetic fallback profile"},
    "arch_a": {"name": "Architecture A", "median_queue": 60,  "p95_queue": 200,
               "base_fct_ms": 4.0,  "fct_slope": 0.080,
               "data_basis": "estimated", "source": "synthetic fallback profile"},
    "arch_b": {"name": "Architecture B", "median_queue": 120, "p95_queue": 380,
               "base_fct_ms": 8.0,  "fct_slope": 0.160,
               "data_basis": "estimated", "source": "synthetic fallback profile"},
}


def fallback_spec() -> dict:
    """Return a deep copy of the default spec so callers can mutate freely."""
    return {k: dict(v) for k, v in _FALLBACK.items()}


def extract_arch_names(brief: str) -> tuple[str, str, str]:
    """Parse main topic and comparative arch names from a research brief."""
    main_m = re.search(r'^#\s+Research Brief:\s*(.+)', brief, re.MULTILINE)
    if main_m:
        title = main_m.group(1).strip()
        main_name = (title.split(':')[0] if ':' in title else title.split()[0])[:15]
    else:
        main_name = "Main"

    def _clean(raw: str) -> str:
        raw = re.sub(r'\s*\([^)]*\)', '', raw)
        return raw.strip().rstrip('.').strip()[:20]

    a_m = re.search(r'Comparative Architecture A:\s*\*{0,2}([^\n*]+)', brief, re.IGNORECASE)
    name_a = _clean(a_m.group(1)) if a_m else "Architecture A"

    b_m = re.search(r'Comparative Architecture B:\s*\*{0,2}([^\n*]+)', brief, re.IGNORECASE)
    name_b = _clean(b_m.group(1)) if b_m else "Architecture B"

    return main_name, name_a, name_b
