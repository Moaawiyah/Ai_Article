"""End-to-end test for strip_tex_fences — the orchestrator."""

from __future__ import annotations

from utils.tex_fixer import strip_tex_fences


def test_strip_tex_fences_removes_markdown_fences(tmp_path):
    src = "```latex\n\\documentclass{article}\n\\begin{document}\nhello\n\\end{document}\n```"
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="Test Topic")
    out = p.read_text(encoding="utf-8")
    assert "```" not in out
    assert r"\begin{document}" in out


def test_strip_tex_fences_injects_fancyhdr_when_missing(tmp_path):
    src = "\\documentclass{article}\n\\usepackage{fancyhdr}\n\\begin{document}\nhi\n\\end{document}"
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="My Paper")
    out = p.read_text(encoding="utf-8")
    assert r"\fancyhead[L]" in out
    assert r"\setlength{\headheight}{15pt}" in out


def test_strip_tex_fences_inserts_polyglossia_for_hebrew(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\usepackage{fontspec}\n"
        "\\setmainfont{Times}\n"
        "\\begin{document}\n"
        "שלום world\n"
        "\\end{document}\n"
    )
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="Hebrew Doc")
    out = p.read_text(encoding="utf-8")
    assert r"\usepackage{polyglossia}" in out
    assert r"\texthebrew{" in out


def test_strip_tex_fences_handles_special_chars_in_topic(tmp_path):
    src = "\\documentclass{article}\n\\begin{document}\nhi\n\\end{document}"
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="Topic & code_name #1")
    out = p.read_text(encoding="utf-8")
    assert r"\&" in out
    assert r"\_" in out
    assert r"\#" in out


def test_strip_tex_fences_removes_redundant_references_heading(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        "\\section{References}\n"
        "\\begin{thebibliography}{99}\n"
        "\\bibitem{ref1} Ref\n"
        "\\end{thebibliography}\n"
        "\\end{document}\n"
    )
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="Refs")
    out = p.read_text(encoding="utf-8")
    assert r"\section{References}" not in out
    assert out.count(r"\begin{thebibliography}") == 1


def test_strip_tex_fences_retags_tabular_figure_and_wraps_adjustbox(tmp_path):
    src = (
        "\\documentclass{article}\n"
        "\\usepackage{adjustbox}\n"
        "\\begin{document}\n"
        "\\begin{figure}[H]\n"
        "\\centering\n"
        "\\begin{tabular}{ll}\n"
        "a & b\\\\\n"
        "\\end{tabular}\n"
        "\\caption{Tab}\n"
        "\\end{figure}\n"
        "\\end{document}\n"
    )
    p = tmp_path / "article.tex"
    p.write_text(src, encoding="utf-8")
    strip_tex_fences(p, topic="Tables")
    out = p.read_text(encoding="utf-8")
    assert r"\begin{table}[H]" in out
    assert r"\adjustbox{max width=\textwidth}" in out
    assert r"\begin{figure}[H]" not in out
