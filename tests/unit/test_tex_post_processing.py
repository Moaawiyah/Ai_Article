"""Unit tests for the LaTeX post-processing modules (tex_*.py)."""

from __future__ import annotations

from utils.tex_hebrew import (
    fix_hebrew_ltr,
    fix_hebrew_runs,
    has_hebrew,
    inject_polyglossia,
)
from utils.tex_protected import _PROTECTED, _PROTECTED_HEB
from utils.tex_syntax import (
    fix_bracket_syntax,
    fix_inline_citations,
    fix_text_mode_math,
)
from utils.tex_tables import fix_tables, fix_tabular_colspec
from utils.tex_tikz import (
    ensure_tikz_bounded,
    fix_tikz_node_linebreaks,
    fix_tikz_reserved_styles,
)


def test_ensure_tikz_bounded_wraps_unbounded_picture():
    src = "\\begin{tikzpicture}\n\\node {a};\n\\end{tikzpicture}"
    out = ensure_tikz_bounded(src)
    assert r"\adjustbox{max width=\textwidth, max totalheight=0.9\textheight}" in out
    assert out.count("tikzpicture") == 2  # begin + end preserved


def test_ensure_tikz_bounded_skips_already_wrapped():
    src = (
        "\\adjustbox{max width=\\textwidth}{%\n"
        "\\begin{tikzpicture}\n\\node {a};\n\\end{tikzpicture}\n}"
    )
    out = ensure_tikz_bounded(src)
    assert out.count("adjustbox") == 1  # not double-wrapped


def test_protected_regex_matches_math():
    assert _PROTECTED.search("foo $x+y$ bar") is not None
    assert _PROTECTED.search(r"foo \[a=b\] bar") is not None
    assert _PROTECTED.search(r"\begin{equation} x \end{equation}") is not None


def test_protected_heb_matches_texthebrew():
    assert _PROTECTED_HEB.search(r"\texthebrew{שלום}") is not None


def test_fix_bracket_syntax_documentclass():
    out = fix_bracket_syntax(r"\documentclass[12pt][article]")
    assert out == r"\documentclass[12pt]{article}"


def test_fix_bracket_syntax_usepackage_same_name():
    out = fix_bracket_syntax(r"\usepackage[tikz]{tikz}")
    assert out == r"\usepackage{tikz}"


def test_fix_bracket_syntax_usepackage_known_split():
    out = fix_bracket_syntax(r"\usepackage[caption]{float}")
    assert r"\usepackage{caption}" in out
    assert r"\usepackage{float}"   in out


def test_fix_bracket_syntax_cite_and_bibitem():
    out = fix_bracket_syntax(r"\cite[ref1] and \bibitem[ref2]")
    assert r"\cite{ref1}" in out
    assert r"\bibitem{ref2}" in out


def test_fix_inline_citations_converts_outside_math():
    out = fix_inline_citations("Body text [4] then $[5]$ stays.")
    assert r"\cite{ref4}" in out
    assert "$[5]$" in out


def test_fix_text_mode_math_wraps_superscript():
    out = fix_text_mode_math("Use 2^{32} bits.")
    assert "$2^{32}$" in out


def test_fix_text_mode_math_escapes_specials():
    out = fix_text_mode_math("user_name & 100% #tag")
    assert r"\_" in out
    assert r"\&" in out
    assert r"\#" in out


def test_fix_text_mode_math_skips_protected():
    out = fix_text_mode_math(r"In $x_1$ keep it, outside x_1 escape.")
    assert "$x_1$" in out
    assert r"x\_1" in out


def test_fix_tables_wraps_in_adjustbox():
    src = "\\begin{table}\n\\begin{tabular}{ll}\na & b\\\\\n\\end{tabular}\n\\end{table}"
    out = fix_tables(src)
    assert r"\adjustbox{max width=\textwidth}" in out


def test_fix_tables_skips_already_wrapped():
    src = "\\begin{table}\n\\adjustbox{max width=\\textwidth}{x}\n\\end{table}"
    out = fix_tables(src)
    assert out.count("adjustbox") == 1


def test_fix_tables_retags_figure_with_tabular_as_table():
    src = "\\begin{figure}[H]\n\\centering\n\\begin{tabular}{ll}\na & b\\\\\n\\end{tabular}\n\\caption{X}\n\\end{figure}"
    out = fix_tables(src)
    assert r"\begin{table}[H]" in out
    assert r"\end{table}" in out
    assert r"\begin{figure}" not in out


def test_fix_tabular_colspec_replaces_bare_p():
    out = fix_tabular_colspec(r"\begin{tabular}{lpl}")
    assert "p{3.5cm}" in out


def test_fix_tabular_colspec_preserves_sized_p():
    out = fix_tabular_colspec(r"\begin{tabular}{lp{4cm}l}")
    assert "p{4cm}" in out
    assert "p{3.5cm}" not in out


def test_fix_tikz_node_linebreaks_adds_align_center():
    src = "\\begin{tikzpicture}\n\\node {a\\\\b};\n\\end{tikzpicture}"
    out = fix_tikz_node_linebreaks(src)
    assert "align=center" in out


def test_fix_tikz_node_linebreaks_preserves_no_linebreak():
    src = "\\begin{tikzpicture}\n\\node {simple};\n\\end{tikzpicture}"
    out = fix_tikz_node_linebreaks(src)
    assert "align=center" not in out


def test_fix_tikz_reserved_styles_renames_collision():
    src = (
        "\\begin{tikzpicture}\n"
        "\\tikzset{node/.style={draw}}\n"
        "\\node[node] (a) {x};\n"
        "\\end{tikzpicture}"
    )
    out = fix_tikz_reserved_styles(src)
    assert "nodenode/.style" in out
    assert "[nodenode]" in out
    assert "\\node[" in out  # the \node command itself must NOT be renamed


def test_fix_tikz_reserved_styles_preserves_builtin_node_usages():
    # 'every node/.style' and 'node distance' are built-ins, not user styles.
    src = (
        "\\begin{tikzpicture}[node distance=2cm, every node/.style={draw}]\n"
        "\\node (a) {x};\n"
        "\\end{tikzpicture}"
    )
    out = fix_tikz_reserved_styles(src)
    assert "node distance=2cm" in out          # key not mangled
    assert "every node/.style" in out          # built-in not renamed
    assert "nodenode" not in out               # no corruption at all


def test_has_hebrew_true_false():
    assert has_hebrew("Plain English") is False
    assert has_hebrew("Hello שלום world") is True


def test_fix_hebrew_runs_wraps_letters():
    out = fix_hebrew_runs("intro שלום outro")
    assert r"\texthebrew{שלום}" in out


def test_fix_hebrew_runs_skips_already_wrapped():
    src = r"already \texthebrew{שלום}"
    out = fix_hebrew_runs(src)
    assert out.count(r"\texthebrew{") == 1


def test_fix_hebrew_ltr_wraps_latin_inside_block():
    src = "\\begin{hebrew}\nאת REST API\n\\end{hebrew}"
    out = fix_hebrew_ltr(src)
    assert r"\textenglish{REST API}" in out


def test_inject_polyglossia_after_setmainfont():
    out = inject_polyglossia(r"\setmainfont{Times}")
    assert r"\usepackage{polyglossia}" in out
    assert r"\setotherlanguage{hebrew}" in out


def test_inject_polyglossia_after_fontspec_when_no_setmainfont():
    out = inject_polyglossia(r"\usepackage{fontspec}")
    assert r"\usepackage{polyglossia}" in out


def test_inject_polyglossia_idempotent():
    src = r"\setmainfont{X}" + "\n" + r"\setotherlanguage{hebrew}"
    assert inject_polyglossia(src) == src
