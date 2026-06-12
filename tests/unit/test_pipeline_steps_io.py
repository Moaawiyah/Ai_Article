"""Unit tests for pipeline_steps' IO passes: compile_step and validate_step.

The token-usage and graph passes are covered in ``test_pipeline_steps.py``.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pipeline_steps


@contextmanager
def _noop_timed_stage(*_args, **_kwargs):
    """Stand-in for utils.logger.timed_stage (a context manager)."""
    yield


def _cfg(tmp_path: Path) -> SimpleNamespace:
    """cfg with the Path attributes the step functions read."""
    return SimpleNamespace(
        topic="Test Topic",
        output_latex=tmp_path / "latex",
        output_pdf=tmp_path / "pdf",
        log_dir=tmp_path / "logs",
    )


# ── compile_step ─────────────────────────────────────────────────────────────
def test_compile_step_returns_true_on_success(tmp_path):
    log = MagicMock()
    cfg = _cfg(tmp_path)
    result = SimpleNamespace(
        success=True, pdf_path=tmp_path / "pdf" / "article.pdf",
        elapsed=1.5, error_summary="", log_path=tmp_path / "x.log",
        tex_path=tmp_path / "latex" / "article.tex",
    )

    with (
        patch("pipeline_steps.strip_tex_fences") as strip,
        patch("pipeline_steps.compile_pdf", return_value=result) as compile_pdf,
        patch("pipeline_steps.timed_stage", _noop_timed_stage),
    ):
        ok = pipeline_steps.compile_step(cfg, log)

    assert ok is True
    strip.assert_called_once()
    compile_pdf.assert_called_once()


def test_compile_step_returns_false_and_logs_on_failure(tmp_path, capsys):
    log = MagicMock()
    cfg = _cfg(tmp_path)
    result = SimpleNamespace(
        success=False, pdf_path=None, elapsed=0.2,
        error_summary="undefined control sequence",
        log_path=tmp_path / "x.log", tex_path=tmp_path / "latex" / "article.tex",
    )

    with (
        patch("pipeline_steps.strip_tex_fences"),
        patch("pipeline_steps.compile_pdf", return_value=result),
        patch("pipeline_steps.timed_stage", _noop_timed_stage),
    ):
        ok = pipeline_steps.compile_step(cfg, log)

    assert ok is False
    out = capsys.readouterr().out
    assert "PDF COMPILATION FAILED" in out
    assert "undefined control sequence" in out
    log.error.assert_called()


# ── validate_step ────────────────────────────────────────────────────────────
def _check(name, passed, fix=""):
    return SimpleNamespace(name=name, passed=passed, fix=fix)


def test_validate_step_runs_checklist_all_passed(tmp_path, capsys):
    log = MagicMock()
    cfg = _cfg(tmp_path)
    report = SimpleNamespace(
        passed=13, failed=0,
        checks=[_check(f"check-{i}", True) for i in range(13)],
    )

    with (
        patch("pipeline_steps.validate", return_value=report) as validate,
        patch("pipeline_steps.timed_stage", _noop_timed_stage),
    ):
        pipeline_steps.validate_step(cfg, log)

    validate.assert_called_once()
    assert validate.call_args.kwargs["tex_path"] == cfg.output_latex / "article.tex"
    assert validate.call_args.kwargs["pdf_path"] == cfg.output_pdf / "article.pdf"
    out = capsys.readouterr().out
    assert "VALIDATION: 13/13 passed" in out
    assert "All requirements satisfied." in out
    log.info.assert_any_call("Result: %d/13 passed, %d failed", 13, 0)


def test_validate_step_reports_failures_with_fixes(tmp_path, capsys):
    log = MagicMock()
    cfg = _cfg(tmp_path)
    report = SimpleNamespace(
        passed=11, failed=2,
        checks=[
            _check("page-count", False, "Add more pages"),
            _check("bibliography", False, "Add 8 references"),
            _check("tikz", True),
        ],
    )

    with (
        patch("pipeline_steps.validate", return_value=report),
        patch("pipeline_steps.timed_stage", _noop_timed_stage),
    ):
        pipeline_steps.validate_step(cfg, log)

    out = capsys.readouterr().out
    assert "VALIDATION: 11/13 passed" in out
    assert "page-count" in out
    assert "Fix: Add more pages" in out
    assert "All requirements satisfied." not in out
