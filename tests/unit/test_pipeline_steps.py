"""Unit tests for pipeline_steps: token-usage and graph post-passes.

The compile and validate passes are covered in ``test_pipeline_steps_io.py``.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pipeline_steps


def _cfg(tmp_path: Path) -> SimpleNamespace:
    """cfg with the Path attributes the step functions read."""
    return SimpleNamespace(
        topic="Test Topic",
        output_research=tmp_path / "research",
        output_assets=tmp_path / "assets",
        output_latex=tmp_path / "latex",
        output_pdf=tmp_path / "pdf",
        log_dir=tmp_path / "logs",
        price_input_per_1m=0.07,
        price_cached_per_1m=0.01,
        price_output_per_1m=0.40,
    )


# ── print_token_usage ────────────────────────────────────────────────────────
def test_print_token_usage_computes_cost(tmp_path, capsys):
    log = MagicMock()
    usage = SimpleNamespace(
        prompt_tokens=1_000_000,
        cached_prompt_tokens=2_000_000,
        completion_tokens=500_000,
        total_tokens=3_500_000,
    )
    result = SimpleNamespace(token_usage=usage)

    pipeline_steps.print_token_usage(result, _cfg(tmp_path), log)

    # cost = (1e6*0.07 + 2e6*0.01 + 5e5*0.40) / 1e6 = 0.07 + 0.02 + 0.20 = 0.29
    out = capsys.readouterr().out
    assert "cost:$0.290000" in out
    assert "prompt:1000000" in out
    log.info.assert_any_call("TOKEN USAGE & COST")


def test_print_token_usage_handles_missing_usage(tmp_path):
    log = MagicMock()
    result = SimpleNamespace(token_usage=None)

    pipeline_steps.print_token_usage(result, _cfg(tmp_path), log)

    log.warning.assert_called_once_with("Token usage not available from provider")
    log.info.assert_not_called()


def test_print_token_usage_treats_none_fields_as_zero(tmp_path, capsys):
    log = MagicMock()
    usage = SimpleNamespace(
        prompt_tokens=None, cached_prompt_tokens=None,
        completion_tokens=None, total_tokens=None,
    )
    result = SimpleNamespace(token_usage=usage)

    pipeline_steps.print_token_usage(result, _cfg(tmp_path), log)

    out = capsys.readouterr().out
    assert "cost:$0.000000" in out


# ── graph_step ───────────────────────────────────────────────────────────────
def test_graph_step_forwards_gatekeeper_and_injects(tmp_path):
    log = MagicMock()
    cfg = _cfg(tmp_path)
    gatekeeper = MagicMock()
    spec = {"main": {}, "arch_a": {}, "arch_b": {}}

    with (
        patch("pipeline_steps.generate_graph_spec", return_value=spec) as gen_spec,
        patch("pipeline_steps.generate_performance_graph", return_value="benchmark.png") as gen_graph,
        patch("pipeline_steps.inject_figure") as inject,
    ):
        pipeline_steps.graph_step(cfg, log, gatekeeper=gatekeeper)

    # gatekeeper is forwarded to the spec generator
    assert gen_spec.call_args.kwargs["gatekeeper"] is gatekeeper
    assert gen_spec.call_args.kwargs["brief_path"] == cfg.output_research / "research_brief.md"
    gen_graph.assert_called_once_with(cfg.topic, cfg.output_latex, spec=spec)
    inject.assert_called_once_with(
        cfg.output_latex / "article.tex", "benchmark.png", spec, log
    )


def test_graph_step_early_returns_when_graph_is_none(tmp_path):
    log = MagicMock()
    cfg = _cfg(tmp_path)

    with (
        patch("pipeline_steps.generate_graph_spec", return_value={"main": {}}),
        patch("pipeline_steps.generate_performance_graph", return_value=None),
        patch("pipeline_steps.inject_figure") as inject,
    ):
        pipeline_steps.graph_step(cfg, log)

    inject.assert_not_called()
