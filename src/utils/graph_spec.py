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

log = logging.getLogger(__name__)

_PROMPT = """\
You are a data extraction assistant. Read the research brief below and provide realistic \
bottleneck queue distribution parameters for the main architecture and the two older/related \
comparative architectures mentioned in it.

These parameters will be used to plot a CDF (Cumulative Distribution Function) of \
bottleneck queue length, showing how each architecture handles queuing under load.

Output ONLY valid JSON — no explanation, no markdown fences, no trailing text:
{{
  "main":   {{"name": "<main architecture short name, max 15 chars>",
             "median_queue": <median bottleneck queue length in packets, integer 1-500>,
             "p95_queue":    <95th-percentile queue length in packets, integer > median>,
             "base_fct_ms":  <average FCT in ms at low load (0-20% utilisation), float>,
             "fct_slope":    <FCT increase in ms per 1% additional load, float 0.001-0.5>}},
  "arch_a": {{"name": "<Comparative Architecture A short name, max 15 chars>",
             "median_queue": <integer 1-500>,
             "p95_queue":    <integer > median>,
             "base_fct_ms":  <float>,
             "fct_slope":    <float 0.001-0.5>}},
  "arch_b": {{"name": "<Comparative Architecture B short name, max 15 chars>",
             "median_queue": <integer 1-500>,
             "p95_queue":    <integer > median>,
             "base_fct_ms":  <float>,
             "fct_slope":    <float 0.001-0.5>}}
}}

Rules:
- The main architecture (the paper's subject) must be the best performer: smallest queues
  and lowest FCT under all load levels.
- arch_a and arch_b are older/legacy systems: they build longer queues and have higher FCT,
  especially under heavy load.
- Base values on known relative performance rankings from networking literature.
- Ensure all three are meaningfully different so the curves are visually distinct.

Research brief (truncated):
{brief}
"""

_FALLBACK: dict = {
    "main":   {"name": "Main",           "median_queue": 12,  "p95_queue": 45,
               "base_fct_ms": 1.2,  "fct_slope": 0.015},
    "arch_a": {"name": "Architecture A", "median_queue": 60,  "p95_queue": 200,
               "base_fct_ms": 4.0,  "fct_slope": 0.080},
    "arch_b": {"name": "Architecture B", "median_queue": 120, "p95_queue": 380,
               "base_fct_ms": 8.0,  "fct_slope": 0.160},
}


def _extract_arch_names(brief: str) -> tuple[str, str, str]:
    """Parse main topic and comparative arch names from a research brief."""
    # Main topic: first heading "# Research Brief: <Title>"
    main_m = re.search(r'^#\s+Research Brief:\s*(.+)', brief, re.MULTILINE)
    if main_m:
        title = main_m.group(1).strip()
        main_name = (title.split(':')[0] if ':' in title else title.split()[0])[:15]
    else:
        main_name = "Main"

    def _clean(raw: str) -> str:
        raw = re.sub(r'\s*\([^)]*\)', '', raw)  # strip parentheticals
        return raw.strip().rstrip('.').strip()[:20]

    a_m = re.search(r'Comparative Architecture A:\s*\*{0,2}([^\n*]+)', brief, re.IGNORECASE)
    name_a = _clean(a_m.group(1)) if a_m else "Architecture A"

    b_m = re.search(r'Comparative Architecture B:\s*\*{0,2}([^\n*]+)', brief, re.IGNORECASE)
    name_b = _clean(b_m.group(1)) if b_m else "Architecture B"

    return main_name, name_a, name_b


def _llm_params(cfg) -> dict:
    """Extract LiteLLM call kwargs from PipelineConfig."""
    provider = cfg.llm_provider
    model    = cfg.llm_model
    base_url = cfg.llm_base_url

    if provider == "zhipuai":
        return dict(model=f"openai/{model}", api_base=base_url,
                    api_key=os.environ.get("ZHIPUAI_API_KEY", ""))
    if provider == "ollama":
        return dict(model=f"ollama_chat/{model}", api_base=base_url)
    if provider == "anthropic":
        return dict(model=model, api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    if provider == "openai":
        return dict(model=model, api_key=os.environ.get("OPENAI_API_KEY", ""))
    return dict(model=model)


def generate_graph_spec(brief_path: Path, cfg, spec_out: Path | None = None) -> dict:
    """Call the LLM to produce a graph spec from the research brief.

    Falls back to ``_FALLBACK`` on any error so the graph always renders.
    Saves the spec to *spec_out* (if given) for transparency / debugging.
    """
    try:
        import litellm
        litellm.suppress_debug_info = True
    except ImportError:
        log.warning("litellm not available — using default graph profiles")
        return _FALLBACK

    if not brief_path.exists():
        log.warning("Research brief not found at %s — using default graph profiles", brief_path)
        return _FALLBACK

    brief = brief_path.read_text(encoding="utf-8")[:5000]
    prompt = _PROMPT.format(brief=brief)
    params = _llm_params(cfg)

    try:
        response = litellm.completion(
            **params,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        log.debug("Graph spec raw response: %s", raw[:500])
        if not raw:
            raise ValueError("LLM returned empty response")
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        # Extract JSON object if surrounded by extra text
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        spec = json.loads(raw)
        for key in ("main", "arch_a", "arch_b"):
            if key not in spec:
                raise ValueError(f"Missing key: {key}")
            for field in ("name", "median_queue", "p95_queue", "base_fct_ms", "fct_slope"):
                if field not in spec[key]:
                    raise ValueError(f"Missing field {field} in {key}")
        log.info(
            "Graph spec — %s vs %s vs %s",
            spec["main"]["name"], spec["arch_a"]["name"], spec["arch_b"]["name"],
        )
        if spec_out:
            spec_out.parent.mkdir(parents=True, exist_ok=True)
            spec_out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        return spec
    except Exception as exc:
        log.warning("Graph spec LLM call failed (%s) — using default profiles", exc)
        fallback = {k: dict(v) for k, v in _FALLBACK.items()}
        try:
            if brief_path.exists():
                brief_text = brief_path.read_text(encoding="utf-8")[:5000]
                main_name, name_a, name_b = _extract_arch_names(brief_text)
                fallback["main"]["name"]   = main_name
                fallback["arch_a"]["name"] = name_a
                fallback["arch_b"]["name"] = name_b
                log.info("Brief-extracted names: %s | %s | %s", main_name, name_a, name_b)
        except Exception as e2:
            log.warning("Could not extract arch names from brief: %s", e2)
        return fallback
