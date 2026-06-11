"""Tests for graph-spec service fallbacks and gatekeeper routing."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from utils.graph_spec import generate_graph_spec


def test_generate_graph_spec_routes_llm_through_gatekeeper(tmp_path):
    brief_path = tmp_path / "research_brief.md"
    brief_path.write_text("No structured performance block", encoding="utf-8")
    content = (
        '{"main":{"name":"M","median_queue":1,"p95_queue":2,'
        '"base_fct_ms":0.1,"fct_slope":0.01},'
        '"arch_a":{"name":"A","median_queue":2,"p95_queue":3,'
        '"base_fct_ms":0.2,"fct_slope":0.02},'
        '"arch_b":{"name":"B","median_queue":3,"p95_queue":4,'
        '"base_fct_ms":0.3,"fct_slope":0.03}}'
    )
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    cfg = SimpleNamespace(
        graph_spec_brief_chars=5000,
        graph_spec_max_tokens=100,
        graph_spec_temperature=0.0,
    )
    gatekeeper = MagicMock()
    gatekeeper.execute.side_effect = lambda call: call()
    with patch("utils.graph_spec.llm_params", return_value={"model": "test"}), patch(
        "litellm.completion", return_value=response
    ) as completion:
        spec = generate_graph_spec(brief_path, cfg, gatekeeper=gatekeeper)
    gatekeeper.execute.assert_called_once()
    completion.assert_called_once()
    assert spec["main"]["name"] == "M"


def test_generate_graph_spec_missing_brief_uses_fallback(tmp_path):
    spec = generate_graph_spec(tmp_path / "missing.md", SimpleNamespace())
    assert spec["main"]["name"] == "Main"
