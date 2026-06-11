"""Unit tests for compile_result and pdf_compiler."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from utils.compile_result import CompileResult
from utils.pdf_compiler import _extract_error, compile_pdf


def test_compile_result_str_success():
    cr = CompileResult(
        success=True,
        pdf_path=Path("/tmp/article.pdf"),
        tex_path=Path("/tmp/article.tex"),
        log_path=Path("/tmp/log"),
        elapsed=1.5,
        error_summary="",
    )
    assert "[PDF OK]" in str(cr)
    assert "1.5s" in str(cr)


def test_compile_result_str_failure():
    cr = CompileResult(
        success=False,
        pdf_path=None,
        tex_path=Path("/tmp/article.tex"),
        log_path=Path("/tmp/log"),
        elapsed=0.5,
        error_summary="! Missing $",
    )
    s = str(cr)
    assert "[PDF FAIL]" in s
    assert "Missing $" in s


def test_extract_error_returns_first_bang_line():
    output = "Normal output\n! LaTeX Error: foo\nmore\n"
    assert _extract_error(output) == "! LaTeX Error: foo"


def test_extract_error_falls_back_to_last_line():
    output = "no bang\nlast line\n"
    assert _extract_error(output) == "last line"


def test_extract_error_empty():
    assert "Unknown" in _extract_error("")


def test_compile_pdf_missing_source(tmp_path):
    result = compile_pdf(
        tex_path=tmp_path / "missing.tex",
        output_dir=tmp_path / "out",
        log_path=tmp_path / "log.log",
    )
    assert result.success is False
    assert "not found" in result.error_summary


def test_compile_pdf_lualatex_missing(tmp_path):
    tex = tmp_path / "x.tex"
    tex.write_text("\\documentclass{article}\\begin{document}hi\\end{document}", encoding="utf-8")
    with patch("utils.pdf_compiler.subprocess.run", side_effect=FileNotFoundError):
        result = compile_pdf(
            tex_path=tex,
            output_dir=tmp_path / "out",
            log_path=tmp_path / "log.log",
        )
    assert result.success is False
    assert "lualatex not found" in result.error_summary
