"""Unit tests for md_document, md_converters, md_to_latex."""

from __future__ import annotations

from utils.md_converters import (
    convert_bibliography,
    convert_bold_italic,
    convert_citations,
    convert_formulas,
    convert_headings,
    convert_images,
    convert_inline_code,
    convert_tables,
    strip_markdown_artifacts,
)
from utils.md_document import build_preamble, build_title_block, escape
from utils.md_to_latex import convert


def test_escape_special_chars():
    assert escape("a & b $ c") == r"a \& b \$ c"
    assert escape("under_score") == r"under\_score"
    assert escape("100%") == r"100\%"


def test_build_preamble_contains_required_packages():
    out = build_preamble()
    assert r"\usepackage{fancyhdr}" in out
    assert r"\usepackage{fontspec}" in out
    assert r"\usepackage{tikz}" in out


def test_build_title_block():
    out = build_title_block("My Title", "Alice", "CS101", r"\today")
    assert r"\title{My Title}" in out
    assert r"\author{Alice" in out
    assert r"\maketitle" in out


def test_convert_headings_levels():
    out = convert_headings("## H2\n### H3\n#### H4")
    assert r"\section{H2}" in out
    assert r"\subsection{H3}" in out
    assert r"\subsubsection{H4}" in out


def test_convert_bold_italic():
    out = convert_bold_italic("**bold** and *italic*")
    assert r"\textbf{bold}" in out
    assert r"\textit{italic}" in out


def test_convert_inline_code():
    out = convert_inline_code("Use `foo_bar` here.")
    assert r"\texttt{foo\_bar}" in out


def test_convert_formulas_block():
    out = convert_formulas("$$x^2 + y^2 = z^2$$")
    assert r"\begin{equation}" in out
    assert "x^2 + y^2 = z^2" in out


def test_convert_images_to_figure():
    out = convert_images("![Figure: caption](/path/to/plot.png)")
    assert r"\begin{figure}" in out
    assert r"\includegraphics" in out
    assert "plot.png" in out


def test_convert_tables_simple():
    src = "| Col1 | Col2 |\n|------|------|\n| a    | 1    |\n| b    | 2    |\n"
    out = convert_tables(src)
    assert r"\begin{tabular}" in out
    assert r"\toprule" in out
    assert r"\bottomrule" in out


def test_convert_citations():
    out = convert_citations("See [3] and [12].")
    assert r"\cite{ref3}" in out
    assert r"\cite{ref12}" in out


def test_convert_bibliography_header():
    out = convert_bibliography("## References\n")
    assert r"\begin{thebibliography}" in out


def test_strip_markdown_artifacts():
    out = strip_markdown_artifacts("body\n---\n<!-- hidden -->\nrest")
    assert "---" not in out
    assert "<!--" not in out


def test_convert_full_pipeline():
    md = "## Intro\n\nSome text [1].\n\n$$E=mc^2$$\n"
    out = convert(md, title="T", author="A", course="C")
    assert r"\documentclass" in out
    assert r"\begin{document}" in out
    assert r"\section{Intro}" in out
    assert r"\cite{ref1}" in out
    assert r"\end{document}" in out
