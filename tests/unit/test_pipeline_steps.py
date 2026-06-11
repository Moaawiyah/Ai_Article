"""Tests for deterministic pipeline post-processing."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pipeline_steps import compile_step, graph_step, print_token_usage, validate_step
from utils.compile_result import CompileResult


def _cfg(tmp_path: Path):
    return SimpleNamespace(
        topic="Topic",
        output_research=tmp_path / "research",
        output_assets=tmp_path / "assets",
        output_latex=tmp_path / "latex",
        output_pdf=tmp_path / "pdf",
        log_dir=tmp_path / "logs",
        price_input_per_1m=1.0,
        price_cached_per_1m=0.5,
        price_output_per_1m=2.0,
    )


def _spec(basis="measured"):
    def item(name):
        return {
            "name": name,
            "median_queue": 1,
            "p95_queue": 2,
            "base_fct_ms": 0.1,
            "fct_slope": 0.01,
            "data_basis": basis,
            "source": f"{name} source",
        }

    return {"main": item("Main"), "arch_a": item("A"), "arch_b": item("B")}


def test_print_token_usage_with_and_without_usage(tmp_path, capsys):
    cfg = _cfg(tmp_path)
    log = MagicMock()
    print_token_usage(SimpleNamespace(token_usage=None), cfg, log)
    log.warning.assert_called_once()

    usage = SimpleNamespace(
        prompt_tokens=100,
        cached_prompt_tokens=20,
        completion_tokens=50,
        total_tokens=170,
    )
    print_token_usage(SimpleNamespace(token_usage=usage), cfg, log)
    assert "total:170" in capsys.readouterr().out


def test_graph_step_injects_generated_figure(tmp_path):
    cfg = _cfg(tmp_path)
    cfg.output_latex.mkdir()
    tex = cfg.output_latex / "article.tex"
    tex.write_text(
        "\\section{Evaluation}\nText\n\\section{Conclusion}\nDone\n"
        "\\begin{thebibliography}{9}\\end{thebibliography}",
        encoding="utf-8",
    )
    gatekeeper = MagicMock()
    with patch("pipeline_steps.generate_graph_spec", return_value=_spec()), patch(
        "pipeline_steps.generate_performance_graph", return_value="benchmark.png"
    ):
        graph_step(cfg, MagicMock(), gatekeeper)
    output = tex.read_text(encoding="utf-8")
    assert "\\includegraphics" in output
    assert "Based on published measurements" in output


def test_graph_step_skips_when_renderer_unavailable(tmp_path):
    cfg = _cfg(tmp_path)
    with patch("pipeline_steps.generate_graph_spec", return_value=_spec()), patch(
        "pipeline_steps.generate_performance_graph", return_value=None
    ):
        graph_step(cfg, MagicMock(), MagicMock())


def test_compile_step_success_and_failure(tmp_path, capsys):
    cfg = _cfg(tmp_path)
    cfg.output_latex.mkdir()
    cfg.output_pdf.mkdir()
    cfg.log_dir.mkdir()
    tex = cfg.output_latex / "article.tex"
    tex.write_text("x", encoding="utf-8")
    success = CompileResult(
        True, cfg.output_pdf / "article.pdf", tex, cfg.log_dir / "log", 0.1, ""
    )
    failure = CompileResult(False, None, tex, cfg.log_dir / "log", 0.1, "bad")
    with patch("pipeline_steps.strip_tex_fences"), patch(
        "pipeline_steps.compile_pdf", side_effect=[success, failure]
    ):
        assert compile_step(cfg, MagicMock()) is True
        assert compile_step(cfg, MagicMock()) is False
    assert "PDF COMPILATION FAILED" in capsys.readouterr().out


def test_validate_step_reports_failures(tmp_path, capsys):
    cfg = _cfg(tmp_path)
    report = SimpleNamespace(
        passed=12,
        failed=1,
        checks=[SimpleNamespace(passed=False, name="Table", fix="Add table")],
    )
    with patch("pipeline_steps.validate", return_value=report):
        validate_step(cfg, MagicMock())
    assert "Add table" in capsys.readouterr().out
