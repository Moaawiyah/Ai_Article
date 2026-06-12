"""Unit tests for validator_types, validator_checks, and tex_validator."""

from __future__ import annotations

from pathlib import Path

from utils.tex_validator import _check_compilation, _check_english_and_hebrew, validate
from utils.validator_checks import (
    check_academic_visuals,
    check_formula,
    check_headers_footers,
    check_pdf_exists,
    check_sections,
    check_table,
    check_tex_exists,
    check_title_page,
    check_toc,
)
from utils.validator_types import CheckResult, ValidationReport


def test_check_result_as_markdown_pass():
    md = CheckResult("Name", True, "ok").as_markdown()
    assert "PASS" in md
    assert "Name" in md


def test_check_result_as_markdown_fail_with_fix():
    md = CheckResult("X", False, "missing", fix="add it").as_markdown()
    assert "FAIL" in md
    assert "add it" in md


def test_validation_report_aggregates():
    rpt = ValidationReport(checks=[
        CheckResult("a", True, "ok"),
        CheckResult("b", False, "bad", "do x"),
    ])
    assert rpt.passed == 1
    assert rpt.failed == 1
    assert rpt.all_passed is False


def test_validation_report_all_passed():
    rpt = ValidationReport(checks=[CheckResult("a", True, "ok")])
    assert rpt.all_passed
    md = rpt.as_markdown(Path("t.tex"), Path("t.pdf"), Path("t.log"))
    assert "All requirements satisfied" in md


def test_check_tex_exists(tmp_path):
    p = tmp_path / "article.tex"
    p.write_text("x", encoding="utf-8")
    assert check_tex_exists(p).passed
    assert not check_tex_exists(tmp_path / "missing.tex").passed


def test_check_pdf_exists(tmp_path):
    p = tmp_path / "article.pdf"
    p.write_bytes(b"%PDF-1.5")
    assert check_pdf_exists(p).passed


def test_check_title_page_pass_fail():
    assert check_title_page(r"\title{T}\maketitle").passed
    assert not check_title_page(r"\title{T}").passed


def test_check_toc():
    assert check_toc(r"\tableofcontents").passed
    assert not check_toc("no toc").passed


def test_check_headers_footers():
    src = r"\usepackage{fancyhdr}" + "\n" + r"\fancyhead[L]{x}"
    assert check_headers_footers(src).passed
    assert not check_headers_footers("plain").passed


def test_check_sections():
    assert check_sections(r"\section{Intro}").passed
    assert not check_sections("plain").passed


def test_check_table():
    assert check_table(r"\begin{tabular}{ll}").passed
    assert not check_table("plain").passed


def test_check_academic_visuals_requires_three_distinct_containers():
    tex = (
        r"\begin{figure}\begin{tikzpicture}\end{tikzpicture}\end{figure}"
        r"\begin{table}\begin{tabular}{ll}\end{tabular}\end{table}"
        r"\begin{figure}\includegraphics{x.png}\end{figure}"
    )
    assert check_academic_visuals(tex, 3).passed
    assert not check_academic_visuals(r"\begin{figure}\end{figure}", 3).passed


def test_check_formula_equation():
    assert check_formula(r"\begin{equation}x\end{equation}").passed


def test_check_formula_inline():
    assert check_formula("inline $x+1$ math").passed


def test_check_formula_none():
    assert not check_formula("plain text").passed


def test_english_and_hebrew_pass():
    tex = r"\begin{hebrew}שלום \textenglish{P4}\end{hebrew} English body."
    assert _check_english_and_hebrew(tex).passed


def test_english_and_hebrew_fail_when_hebrew_absent():
    res = _check_english_and_hebrew(r"\section{Intro} English only, no bidi.")
    assert not res.passed
    assert "begin{hebrew}" in res.evidence


def test_english_and_hebrew_fail_on_stray_hebrew_outside_env():
    tex = r"\begin{hebrew}שלום\end{hebrew} then leaked שלום outside."
    assert not _check_english_and_hebrew(tex).passed


def test_english_and_hebrew_fail_on_setrl():
    tex = r"\begin{hebrew}שלום\end{hebrew} \setRL here"
    assert not _check_english_and_hebrew(tex).passed


def test_english_and_hebrew_requires_wrapped_technical_terms():
    tex = r"\begin{hebrew}מערכת CrewAI בעברית\end{hebrew}"
    result = _check_english_and_hebrew(tex)
    assert not result.passed
    assert "textenglish" in result.evidence


def test_english_and_hebrew_rejects_unicode_direction_controls():
    tex = "\\begin{hebrew}שלום\\end{hebrew}\u200f"
    assert not _check_english_and_hebrew(tex).passed


def test_compilation_check_requires_minimum_pages(tmp_path, monkeypatch):
    pdf_path = tmp_path / "article.pdf"
    pdf_path.write_bytes(b"%PDF")

    class FakePdf:
        pages = [object()] * 14

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr("pdfplumber.open", lambda _path: FakePdf())
    result = _check_compilation(pdf_path, tmp_path / "compile.log", 15)
    assert not result.passed
    assert "14 pages" in result.evidence


def test_validate_full_report(tmp_path):
    tex_path = tmp_path / "article.tex"
    pdf_path = tmp_path / "article.pdf"
    log_path = tmp_path / "compile.log"
    report_path = tmp_path / "report.md"

    tex_path.write_text(
        r"\title{T}\maketitle"
        + r"\tableofcontents"
        + r"\usepackage{fancyhdr}\fancyhead[L]{h}"
        + r"\section{A}"
        + r"\begin{tabular}{ll}\end{tabular}"
        + r"\begin{figure}\includegraphics{x.png}\end{figure}"
        + r"\begin{equation}x\end{equation}"
        + r"\begin{tikzpicture}\end{tikzpicture}"
        + r"\cite{r1}\cite{r2}\cite{r3}"
        + r"\begin{thebibliography}{9}"
        + r"\bibitem{r1}a\bibitem{r2}b\bibitem{r3}c\bibitem{r4}d"
        + r"\bibitem{r5}e\bibitem{r6}f\bibitem{r7}g\bibitem{r8}h"
        + r"\end{thebibliography}",
        encoding="utf-8",
    )
    pdf_path.write_bytes(b"%PDF-1.5")

    report = validate(tex_path, pdf_path, log_path, report_path)
    assert report.passed >= 11
    assert report_path.exists()


def test_validate_missing_files_does_not_crash(tmp_path):
    report = validate(
        tex_path=tmp_path / "missing.tex",
        pdf_path=tmp_path / "missing.pdf",
        log_path=tmp_path / "missing.log",
        report_path=tmp_path / "report.md",
    )
    assert report.failed > 0
