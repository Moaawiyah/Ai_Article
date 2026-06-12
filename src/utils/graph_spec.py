"""LLM-driven graph specification generator.

Reads the research brief and asks the configured LLM for a small JSON block
describing relative performance characteristics of the main topic and the two
comparative architectures found by the Researcher agent.

Parsing/validation/IO helpers live in ``graph_spec_parse.py``.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from utils.graph_fallback import fallback_spec
from utils.graph_spec_parse import (
    brief_fallback,
    extract_brief_spec,
    llm_params,
    log_spec,
    validate_and_normalize,
    write_spec,
)

log = logging.getLogger(__name__)

_PROMPT = """\
You are a networking-systems research analyst. Read the research brief below, identify the \
main architecture (the paper's subject) and the two comparative architectures it is evaluated \
against, and report their ACTUAL published performance figures from the academic literature.

The figures will plot two panels: a CDF of bottleneck queue length (packets) and average flow \
completion time (FCT, ms) vs network load (%). For each architecture, map the published results \
onto these four parameters.

CRITICAL — ground every number in real published data:
- Recall the real reported metrics from the original papers (e.g. the HULA, CONGA, ECMP, \
  Presto, NVGRE, or P4-ISC evaluation sections) and their relative rankings.
- For each architecture, set "data_basis" to "measured" ONLY if you are recalling actual \
  numbers reported in a real paper, and put the specific paper + figure/table in "source" \
  (e.g. "HULA, SOSR'16, Fig. 8"). Otherwise set "data_basis" to "estimated", give your best \
  literature-informed estimate, and explain the basis in "source".
- Do NOT force any particular architecture to win. Report the real measured ranking even if \
  the paper's own subject is not best on every metric.
- Never invent a citation. If you cannot attribute a number to a real source, it is "estimated".

Output ONLY valid JSON — no explanation, no markdown fences, no trailing text:
{{
  "main":   {{"name": "<main architecture short name, max 15 chars>",
             "median_queue": <median bottleneck queue length in packets, integer 1-500>,
             "p95_queue":    <95th-percentile queue length in packets, integer > median>,
             "base_fct_ms":  <average FCT in ms at low load (0-20% utilisation), float>,
             "fct_slope":    <FCT increase in ms per 1% additional load, float 0.001-0.5>,
             "data_basis":   "measured" | "estimated",
             "source":       "<paper + figure/table, or basis for the estimate>"}},
  "arch_a": {{"name": "<Comparative Architecture A short name, max 15 chars>",
             "median_queue": <integer 1-500>,
             "p95_queue":    <integer > median>,
             "base_fct_ms":  <float>,
             "fct_slope":    <float 0.001-0.5>,
             "data_basis":   "measured" | "estimated",
             "source":       "<paper + figure/table, or basis for the estimate>"}},
  "arch_b": {{"name": "<Comparative Architecture B short name, max 15 chars>",
             "median_queue": <integer 1-500>,
             "p95_queue":    <integer > median>,
             "base_fct_ms":  <float>,
             "fct_slope":    <float 0.001-0.5>,
             "data_basis":   "measured" | "estimated",
             "source":       "<paper + figure/table, or basis for the estimate>"}}
}}

Ensure all three are meaningfully different so the curves are visually distinct.

Research brief (truncated):
{brief}
"""


def generate_graph_spec(
    brief_path: Path, cfg, spec_out: Path | None = None, gatekeeper=None
) -> dict:
    """Produce the graph spec, preferring the researcher's embedded data block.

    Resolution order:
      1. The machine-readable Performance Data JSON block in the research brief
         (so the figure agrees with the article's prose and citations).
      2. A direct LLM recall call as a fallback when the brief has no such block.
      3. ``fallback_spec()`` / name-extraction when both are unavailable.
    """
    if not brief_path.exists():
        log.warning("Research brief not found at %s — using default graph profiles", brief_path)
        return fallback_spec()

    brief = brief_path.read_text(encoding="utf-8")
    brief_chars = cfg.graph_spec_brief_chars

    embedded = extract_brief_spec(brief)
    if embedded is not None:
        log_spec(embedded, "from researcher brief")
        write_spec(embedded, spec_out)
        return embedded

    log.info("No Performance Data block in brief — falling back to LLM recall")
    try:
        import litellm
        litellm.suppress_debug_info = True
    except ImportError:
        log.warning("litellm not available — using default graph profiles")
        return brief_fallback(brief_path, brief_chars)

    prompt = _PROMPT.format(brief=brief[:brief_chars])
    params = llm_params(cfg)

    def _call():
        """Invoke the configured LLM for the graph spec (gated when available)."""
        return litellm.completion(
            **params,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=cfg.graph_spec_max_tokens,
            temperature=cfg.graph_spec_temperature,
        )

    try:
        # Route through the central gatekeeper so this fallback LLM call is
        # rate-limited, retried, and logged like every other external call (§5.1).
        response = gatekeeper.execute(_call) if gatekeeper else _call()
        raw = response.choices[0].message.content.strip()
        log.debug("Graph spec raw response: %s", raw[:500])
        if not raw:
            raise ValueError("LLM returned empty response")
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        spec = validate_and_normalize(json.loads(raw))
        log_spec(spec, "LLM recall")
        write_spec(spec, spec_out)
        return spec
    except Exception as exc:
        log.warning("Graph spec LLM call failed (%s) — using default profiles", exc)
        return brief_fallback(brief_path, brief_chars)
