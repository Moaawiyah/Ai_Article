"""Unit tests for graph_fallback and graph_spec (+ graph_spec_parse)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from utils.graph_fallback import extract_arch_names, fallback_spec
from utils.graph_spec import generate_graph_spec
from utils.graph_spec_parse import extract_brief_spec


def test_fallback_spec_has_all_keys():
    spec = fallback_spec()
    assert {"main", "arch_a", "arch_b"} <= spec.keys()
    for v in spec.values():
        assert {"name", "median_queue", "p95_queue", "base_fct_ms", "fct_slope"} <= v.keys()


def test_fallback_spec_independent_copies():
    a = fallback_spec()
    a["main"]["name"] = "MUTATED"
    b = fallback_spec()
    assert b["main"]["name"] != "MUTATED"


def test_extract_arch_names_from_brief():
    brief = (
        "# Research Brief: HULA Load Balancing\n\n"
        "Comparative Architecture A: **ECMP (legacy)**\n"
        "Comparative Architecture B: CONGA.\n"
    )
    main, a, b = extract_arch_names(brief)
    assert main == "HULA Load Bala"[:15] or main == "HULA Load Balan"[:15] or "HULA" in main
    assert "ECMP" in a
    assert "CONGA" in b


def test_extract_arch_names_fallback_when_missing():
    main, a, b = extract_arch_names("nothing here")
    assert main == "Main"
    assert a == "Architecture A"
    assert b == "Architecture B"


def test_extract_brief_spec_from_fenced_json():
    brief = """
## 3. Comparative Architecture Analysis

Comparative Architecture A: NVGRE
Comparative Architecture B: CONGA

```json
{
  "main": {
    "name": "HULA",
    "median_queue": 12,
    "p95_queue": 35,
    "base_fct_ms": 0.45,
    "fct_slope": 0.04,
    "data_basis": "measured",
    "source": "HULA, Fig. 8"
  },
  "arch_a": {
    "name": "NVGRE",
    "median_queue": 45,
    "p95_queue": 110,
    "base_fct_ms": 0.85,
    "fct_slope": 0.18,
    "source": "Estimated from NVGRE evaluation"
  },
  "arch_b": {
    "name": "CONGA",
    "median_queue": 70,
    "p95_queue": 190,
    "base_fct_ms": 1.05,
    "fct_slope": 0.22,
    "data_basis": "estimated",
    "source": "CONGA, approximate trend"
  }
}
```
"""
    spec = extract_brief_spec(brief)

    assert spec is not None
    assert spec["main"]["name"] == "HULA"
    assert spec["main"]["data_basis"] == "measured"
    assert spec["arch_a"]["data_basis"] == "estimated"
    assert spec["arch_a"]["source"] == "Estimated from NVGRE evaluation"


def test_extract_brief_spec_returns_none_when_json_shape_is_wrong():
    brief = """
```json
{"unexpected": true}
```
"""
    assert extract_brief_spec(brief) is None


def test_generate_graph_spec_prefers_embedded_researcher_block(tmp_path):
    brief_path = tmp_path / "research_brief.md"
    spec_out = tmp_path / "graph_spec.json"
    brief_path.write_text(
        """
# Research Brief: HULA

```json
{
  "main": {
    "name": "HULA",
    "median_queue": 12,
    "p95_queue": 35,
    "base_fct_ms": 0.45,
    "fct_slope": 0.04,
    "data_basis": "measured",
    "source": "HULA, Fig. 8"
  },
  "arch_a": {
    "name": "NVGRE",
    "median_queue": 45,
    "p95_queue": 110,
    "base_fct_ms": 0.85,
    "fct_slope": 0.18,
    "data_basis": "estimated",
    "source": "Estimated from NVGRE evaluation"
  },
  "arch_b": {
    "name": "CONGA",
    "median_queue": 70,
    "p95_queue": 190,
    "base_fct_ms": 1.05,
    "fct_slope": 0.22,
    "data_basis": "estimated",
    "source": "CONGA, approximate trend"
  }
}
```
""",
        encoding="utf-8",
    )
    cfg = SimpleNamespace(graph_spec_brief_chars=5000)

    with patch("utils.graph_spec.llm_params", side_effect=AssertionError("LLM path should not run")):
        spec = generate_graph_spec(brief_path=brief_path, cfg=cfg, spec_out=spec_out)

    assert spec["main"]["name"] == "HULA"
    assert spec["arch_b"]["name"] == "CONGA"
    assert '"data_basis": "measured"' in spec_out.read_text(encoding="utf-8")
