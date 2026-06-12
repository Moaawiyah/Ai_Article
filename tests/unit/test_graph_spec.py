"""Unit tests for utils.graph_spec.generate_graph_spec (3 resolution paths)."""

from __future__ import annotations

import builtins
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from utils.graph_spec import generate_graph_spec

_EMBEDDED_BRIEF = """
# Research Brief: HULA

```json
{
  "main":   {"name": "HULA",  "median_queue": 12, "p95_queue": 35,
             "base_fct_ms": 0.45, "fct_slope": 0.04,
             "data_basis": "measured", "source": "HULA, Fig. 8"},
  "arch_a": {"name": "NVGRE", "median_queue": 45, "p95_queue": 110,
             "base_fct_ms": 0.85, "fct_slope": 0.18,
             "data_basis": "estimated", "source": "NVGRE eval"},
  "arch_b": {"name": "CONGA", "median_queue": 70, "p95_queue": 190,
             "base_fct_ms": 1.05, "fct_slope": 0.22,
             "data_basis": "estimated", "source": "CONGA trend"}
}
```
"""

_LLM_JSON = json.dumps({
    "main":   {"name": "DCTCP", "median_queue": 10, "p95_queue": 30,
               "base_fct_ms": 0.4, "fct_slope": 0.03},
    "arch_a": {"name": "ECMP", "median_queue": 50, "p95_queue": 120,
               "base_fct_ms": 0.9, "fct_slope": 0.2},
    "arch_b": {"name": "PFC", "median_queue": 80, "p95_queue": 200,
               "base_fct_ms": 1.1, "fct_slope": 0.25},
})


def _cfg():
    """Minimal cfg with the attributes generate_graph_spec / llm_params read."""
    return SimpleNamespace(
        graph_spec_brief_chars=5000,
        graph_spec_max_tokens=2000,
        graph_spec_temperature=0.1,
        llm_provider="ollama",
        llm_model="qwen3:14b",
        llm_base_url="http://localhost:11434",
    )


def _fake_llm_response(content: str):
    """Build a litellm-style response object: choices[0].message.content."""
    resp = MagicMock()
    resp.choices[0].message.content = content
    return resp


# ── Path 1: embedded Performance-Data block (no LLM) ─────────────────────────
def test_embedded_block_is_preferred_without_llm(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text(_EMBEDDED_BRIEF, encoding="utf-8")
    spec_out = tmp_path / "graph_spec.json"

    with patch("utils.graph_spec.llm_params", side_effect=AssertionError("no LLM")):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg(), spec_out=spec_out)

    assert spec["main"]["name"] == "HULA"
    assert spec["arch_b"]["name"] == "CONGA"
    assert spec["main"]["data_basis"] == "measured"
    assert json.loads(spec_out.read_text())["main"]["name"] == "HULA"


# ── Path 2: no block → LLM recall, routed through the gatekeeper ─────────────
def test_llm_recall_path_parses_and_uses_gatekeeper(tmp_path: Path, gatekeeper):
    brief = tmp_path / "research_brief.md"
    brief.write_text("# Brief with no machine-readable block\nProse only.\n", encoding="utf-8")
    spec_out = tmp_path / "graph_spec.json"

    fake_litellm = MagicMock()
    fake_litellm.completion.return_value = _fake_llm_response(_LLM_JSON)

    with (
        patch.dict("sys.modules", {"litellm": fake_litellm}),
        patch.object(gatekeeper, "execute", wraps=gatekeeper.execute) as spy,
    ):
        spec = generate_graph_spec(
            brief_path=brief, cfg=_cfg(), spec_out=spec_out, gatekeeper=gatekeeper
        )

    assert spec["main"]["name"] == "DCTCP"
    assert spec["arch_a"]["name"] == "ECMP"
    spy.assert_called_once()  # the fallback LLM call went through the gatekeeper
    fake_litellm.completion.assert_called_once()
    assert json.loads(spec_out.read_text())["arch_b"]["name"] == "PFC"


def test_llm_recall_path_without_gatekeeper_calls_directly(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text("Prose-only brief, no block.\n", encoding="utf-8")

    fake_litellm = MagicMock()
    fake_litellm.completion.return_value = _fake_llm_response(_LLM_JSON)

    with patch.dict("sys.modules", {"litellm": fake_litellm}):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg())

    assert spec["main"]["name"] == "DCTCP"
    fake_litellm.completion.assert_called_once()


def test_llm_recall_strips_markdown_fences(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text("No block here.\n", encoding="utf-8")

    fenced = f"```json\n{_LLM_JSON}\n```"
    fake_litellm = MagicMock()
    fake_litellm.completion.return_value = _fake_llm_response(fenced)

    with patch.dict("sys.modules", {"litellm": fake_litellm}):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg())

    assert spec["main"]["name"] == "DCTCP"


def test_llm_failure_falls_back_to_brief_profiles(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text("Prose-only brief.\n", encoding="utf-8")

    fake_litellm = MagicMock()
    fake_litellm.completion.side_effect = RuntimeError("boom")

    with patch.dict("sys.modules", {"litellm": fake_litellm}):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg())

    # falls back to the static three-arch profile rather than raising
    assert {"main", "arch_a", "arch_b"} <= spec.keys()


def test_empty_llm_response_falls_back(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text("No block.\n", encoding="utf-8")

    fake_litellm = MagicMock()
    fake_litellm.completion.return_value = _fake_llm_response("   ")

    with patch.dict("sys.modules", {"litellm": fake_litellm}):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg())

    assert {"main", "arch_a", "arch_b"} <= spec.keys()


def test_missing_litellm_falls_back_to_brief_profiles(tmp_path: Path):
    brief = tmp_path / "research_brief.md"
    brief.write_text("Prose-only brief, no block.\n", encoding="utf-8")

    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "litellm":
            raise ImportError("simulated missing litellm")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=_fake_import):
        spec = generate_graph_spec(brief_path=brief, cfg=_cfg())

    assert {"main", "arch_a", "arch_b"} <= spec.keys()


# ── Path 3: missing brief → fallback_spec() ──────────────────────────────────
def test_missing_brief_returns_fallback(tmp_path: Path):
    missing = tmp_path / "does_not_exist.md"
    spec = generate_graph_spec(brief_path=missing, cfg=_cfg())
    assert {"main", "arch_a", "arch_b"} <= spec.keys()
    assert spec["main"]["name"] == "Main"
