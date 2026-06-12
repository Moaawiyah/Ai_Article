"""Helpers for the graph specification: LLM params, parsing, validation, IO.

Split out of ``graph_spec.py`` to keep each module within the 150-line budget.
These helpers turn raw text/JSON (from the research brief or an LLM reply) into
a validated three-architecture spec, and persist it.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from utils.graph_fallback import extract_arch_names, fallback_spec

log = logging.getLogger(__name__)

_REQUIRED_FIELDS = ("name", "median_queue", "p95_queue", "base_fct_ms", "fct_slope")


def llm_params(cfg) -> dict:
    """Extract LiteLLM call kwargs from PipelineConfig for the configured provider."""
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
    if provider == "gemini":
        model_name = model if model.startswith("gemini/") else f"gemini/{model}"
        return {"model": model_name, "api_key": os.environ.get("GEMINI_API_KEY", "")}
    if provider == "groq":
        model_name = model if model.startswith("groq/") else f"groq/{model}"
        return {"model": model_name, "api_key": os.environ.get("GROQ_API_KEY", "")}
    return {"model": model}


def brief_fallback(brief_path: Path, brief_chars: int) -> dict:
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


def validate_and_normalize(spec: dict) -> dict:
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


def log_spec(spec: dict, origin: str) -> None:
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


def extract_brief_spec(brief: str) -> dict | None:
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
            return validate_and_normalize(spec)
        except ValueError:
            continue
    return None


def write_spec(spec: dict, spec_out: Path | None) -> None:
    """Persist the spec to ``spec_out`` as pretty JSON (no-op if path is None)."""
    if spec_out:
        spec_out.parent.mkdir(parents=True, exist_ok=True)
        spec_out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
