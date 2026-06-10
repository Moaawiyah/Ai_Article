"""LLM-driven graph specification generator.

Reads the research brief and asks the configured LLM for a small JSON block
describing relative performance characteristics of the main topic and the two
comparative architectures found by the Researcher agent.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from agent_ai.utils.graph_fallback import extract_arch_names, fallback_spec

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


def _llm_params(cfg) -> dict:
    """Extract LiteLLM call kwargs from PipelineConfig."""
    provider = cfg.llm_provider
    model    = cfg.llm_model
    base_url = cfg.llm_base_url

    if provider == "zhipuai":
        return {"model": f"openai/{model}", "api_base": base_url,
                "api_key": os.environ.get("ZHIPUAI_API_KEY", "")}
    if provider == "ollama":
        return {"model": f"ollama_chat/{model}", "api_base": base_url}
    if provider == "anthropic":
        return {"model": model, "api_key": os.environ.get("ANTHROPIC_API_KEY", "")}
    if provider == "openai":
        return {"model": model, "api_key": os.environ.get("OPENAI_API_KEY", "")}
    return {"model": model}


def _brief_fallback(brief_path: Path, brief_chars: int) -> dict:
    """Return the static fallback with arch names taken from the brief when possible."""
    spec = fallback_spec()
    try:
        if brief_path.exists():
            brief_text = brief_path.read_text(encoding="utf-8")[:brief_chars]
            main_name, name_a, name_b = extract_arch_names(brief_text)
            spec["main"]["name"]   = main_name
            spec["arch_a"]["name"] = name_a
            spec["arch_b"]["name"] = name_b
            log.info("Brief-extracted names: %s | %s | %s", main_name, name_a, name_b)
    except Exception as e2:
        log.warning("Could not extract arch names from brief: %s", e2)
    return spec


_REQUIRED_FIELDS = ("name", "median_queue", "p95_queue", "base_fct_ms", "fct_slope")


def _validate_and_normalize(spec: dict) -> dict:
    """Validate the three-arch structure and normalize provenance fields in place.

    Raises ValueError if a required key/field is missing. ``data_basis`` and
    ``source`` are optional in the source data and default to "estimated"/"".
    """
    for key in ("main", "arch_a", "arch_b"):
        if key not in spec:
            raise ValueError(f"Missing key: {key}")
        for field in _REQUIRED_FIELDS:
            if field not in spec[key]:
                raise ValueError(f"Missing field {field} in {key}")
        basis = str(spec[key].get("data_basis", "estimated")).strip().lower()
        spec[key]["data_basis"] = "measured" if basis == "measured" else "estimated"
        spec[key]["source"] = str(spec[key].get("source", "")).strip()
    return spec


def _log_spec(spec: dict, origin: str) -> None:
    """Log the chosen architectures and the provenance of each series."""
    log.info(
        "Graph spec (%s) — %s vs %s vs %s",
        origin, spec["main"]["name"], spec["arch_a"]["name"], spec["arch_b"]["name"],
    )
    for key in ("main", "arch_a", "arch_b"):
        log.info(
            "  %-7s %-15s [%s] %s",
            key + ":", spec[key]["name"], spec[key]["data_basis"],
            spec[key]["source"] or "(no source given)",
        )


def _extract_brief_spec(brief: str) -> dict | None:
    """Parse the researcher's machine-readable Performance Data JSON block.

    Scans fenced ```json blocks (and bare {...} objects as a fallback) and
    returns the first one that validates as a three-arch spec, or None.
    """
    candidates = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", brief, re.DOTALL)
    # Greedy bare-object fallback for when the model omits the code fence.
    bare = re.search(r"\{.*\}", brief, re.DOTALL)
    if bare:
        candidates.append(bare.group(0))
    for raw in candidates:
        try:
            spec = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        if not (isinstance(spec, dict) and {"main", "arch_a", "arch_b"} <= spec.keys()):
            continue
        try:
            return _validate_and_normalize(spec)
        except ValueError:
            continue
    return None


def _write_spec(spec: dict, spec_out: Path | None) -> None:
    if spec_out:
        spec_out.parent.mkdir(parents=True, exist_ok=True)
        spec_out.write_text(json.dumps(spec, indent=2), encoding="utf-8")


def generate_graph_spec(brief_path: Path, cfg, spec_out: Path | None = None) -> dict:
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

    embedded = _extract_brief_spec(brief)
    if embedded is not None:
        _log_spec(embedded, "from researcher brief")
        _write_spec(embedded, spec_out)
        return embedded

    log.info("No Performance Data block in brief — falling back to LLM recall")
    try:
        import litellm
        litellm.suppress_debug_info = True
    except ImportError:
        log.warning("litellm not available — using default graph profiles")
        return _brief_fallback(brief_path, brief_chars)

    prompt = _PROMPT.format(brief=brief[:brief_chars])
    params = _llm_params(cfg)

    try:
        response = litellm.completion(
            **params,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=cfg.graph_spec_max_tokens,
            temperature=cfg.graph_spec_temperature,
        )
        raw = response.choices[0].message.content.strip()
        log.debug("Graph spec raw response: %s", raw[:500])
        if not raw:
            raise ValueError("LLM returned empty response")
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        spec = _validate_and_normalize(json.loads(raw))
        _log_spec(spec, "LLM recall")
        _write_spec(spec, spec_out)
        return spec
    except Exception as exc:
        log.warning("Graph spec LLM call failed (%s) — using default profiles", exc)
        return _brief_fallback(brief_path, brief_chars)
