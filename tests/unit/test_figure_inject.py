"""Unit tests for the benchmark-figure caption/injection helpers."""

from __future__ import annotations

from utils.figure_inject import _build_caption, _place, _tex_escape, inject_figure

_SPEC = {
    "main":   {"name": "HULA",  "source": "HULA, SOSR'16", "data_basis": "measured"},
    "arch_a": {"name": "CONGA", "source": "CONGA, SIGCOMM'14", "data_basis": "measured"},
    "arch_b": {"name": "ECMP",  "source": "", "data_basis": "estimated"},
}


def test_tex_escape_escapes_specials():
    assert _tex_escape("a_b & c%") == r"a\_b \& c\%"


def test_build_caption_measured_lists_sources():
    spec = {k: dict(v, data_basis="measured", source=f"src-{k}") for k, v in _SPEC.items()}
    caption = _build_caption(spec)
    assert "Based on published measurements" in caption
    assert "HULA vs.\\ CONGA vs.\\ ECMP" in caption


def test_build_caption_mixed_basis_notes_estimates():
    caption = _build_caption(_SPEC)  # arch_b is estimated
    assert "literature-informed" in caption


def test_build_caption_no_sources_is_illustrative():
    spec = {k: {"name": v["name"], "data_basis": "estimated"} for k, v in _SPEC.items()}
    assert "illustrative" in _build_caption(spec)


def test_place_after_evaluation_section():
    src = "\\section{Evaluation}\nbody\n\\section{Conclusion}\nend"
    out = _place(src, "FIG")
    assert out.index("FIG") < out.index("Conclusion")
    assert out.index("FIG") > out.index("Evaluation")


def test_place_falls_back_to_before_bibliography():
    src = "\\section{Intro}\ntext\n\\begin{thebibliography}{9}\n\\end{thebibliography}"
    out = _place(src, "FIG")
    assert out.index("FIG") < out.index("thebibliography")


def test_place_falls_back_to_end_document():
    src = "no sections here\n\\end{document}"
    out = _place(src, "FIG")
    assert out.index("FIG") < out.index("\\end{document}")


def test_inject_figure_writes_block(tmp_path):
    tex = tmp_path / "article.tex"
    tex.write_text("\\section{Evaluation}\nx\n\\end{document}", encoding="utf-8")
    logged = []
    inject_figure(tex, "perf.png", _SPEC, type("L", (), {"info": lambda self, *a: logged.append(a)})())
    out = tex.read_text(encoding="utf-8")
    assert "\\includegraphics[width=\\textwidth]{perf.png}" in out
    assert "\\label{fig:perf}" in out
    assert logged  # injection was logged
