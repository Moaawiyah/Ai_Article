"""Top-level driver that applies every LaTeX post-pass to article.tex."""

from __future__ import annotations

import re
from pathlib import Path

from utils.tex_hebrew import (
    fix_hebrew_ltr,
    fix_hebrew_runs,
    has_hebrew,
    inject_polyglossia,
)
from utils.tex_syntax import (
    fix_bracket_syntax,
    fix_inline_citations,
    fix_text_mode_math,
)
from utils.tex_tables import fix_table_math, fix_tables, fix_tabular_colspec
from utils.tex_tikz import fix_tikz_node_linebreaks, fix_tikz_reserved_styles


def strip_tex_fences(tex_path: Path, topic: str = "Article") -> None:
    """Remove markdown fences and fix common LLM LaTeX mistakes in article.tex."""
    text = tex_path.read_text(encoding="utf-8")

    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip())

    cleaned = re.sub(r"\\thispagestyle\s*\{\s*\}", r"\\thispagestyle{empty}", cleaned)
    cleaned = re.sub(r"\\pagestyle\s*\{\s*\}", r"\\pagestyle{fancy}", cleaned)
    cleaned = re.sub(r"(\\documentclass(?:\[[^\]]*\])?)\{\s*\}", r"\1{article}", cleaned)

    cleaned = re.sub(
        r"\\fancyfoot(\[[^\]]*\])\{\\textsc\{([^}]+)\}\}",
        r"\\fancyfoot\1{\2}", cleaned,
    )
    cleaned = re.sub(r"\\fancyhead\[([LR])[EO]\]", r"\\fancyhead[\1]", cleaned)

    _fhdr = re.compile(
        r"(\\pagestyle\{fancy\}|\\fancyhf\{[^}]*\}|\\fancyhead[^\n]*|\\fancyfoot[^\n]*"
        r"|\\renewcommand\{\\(?:head|foot)rulewidth\}\{[^}]+\}"
        r"|\\setlength\{\\(?:head|foot)rulewidth\}\{[^}]+\})\n",
        re.MULTILINE,
    )
    fhdr_lines = _fhdr.findall(cleaned)
    if fhdr_lines and r"\begin{document}" in cleaned:
        cleaned = _fhdr.sub("", cleaned)
        inject  = "\n" + "\n".join(fhdr_lines) + "\n"
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + inject, 1)

    cleaned = re.sub(r"\n?\\thispagestyle\{[^}]*\}", "", cleaned)
    cleaned = re.sub(r"(\\\\)\s+\[", r"\1 {[}", cleaned)
    cleaned = fix_bracket_syntax(cleaned)
    cleaned = fix_tikz_node_linebreaks(cleaned)
    cleaned = fix_tikz_reserved_styles(cleaned)
    cleaned = fix_text_mode_math(cleaned)
    cleaned = fix_table_math(cleaned)
    cleaned = fix_tables(cleaned)
    cleaned = fix_inline_citations(cleaned)
    cleaned = fix_tabular_colspec(cleaned)

    if r'\begin{thebibliography}' in cleaned:
        cleaned = re.sub(
            r'(?:\\newpage\s*)?\\section\{(?:References|Bibliography)\}\s*(?=\\newpage\s*\\begin\{thebibliography\}|\\begin\{thebibliography\})',
            '',
            cleaned,
            count=1,
        )
        cleaned = re.sub(r'(?:\\newpage\s*\n*)+(?=\\begin\{thebibliography\})', '', cleaned)
        cleaned = cleaned.replace(r'\begin{thebibliography}', '\\newpage\n\\begin{thebibliography}', 1)

    if r'\usepackage{fancyhdr}' in cleaned:
        if r'\setlength{\headheight}' not in cleaned:
            cleaned = cleaned.replace(
                r'\usepackage{fancyhdr}',
                '\\usepackage{fancyhdr}\n\\setlength{\\headheight}{15pt}',
                1,
            )
        else:
            cleaned = re.sub(
                r'\\setlength\{\\headheight\}\{[^}]*\}',
                r'\\setlength{\\headheight}{15pt}',
                cleaned,
            )

    _topic_tex = (topic
                  .replace("\\", "")
                  .replace("&", r"\&")
                  .replace("#", r"\#")
                  .replace("_", r"\_"))
    _topic_hdr = f"\\small {_topic_tex}"

    if r"\pagestyle{fancy}" in cleaned:
        cleaned = re.sub(r"\\fancyhead(\[[^\]]*\])?\{[^}]*\}", "", cleaned)
        cleaned = re.sub(r"\\fancyfoot(\[[^\]]*\])?\{[^}]*\}", "", cleaned)
        cleaned = re.sub(r"\\fancyhf\{[^}]*\}\n?", "", cleaned)
        hdr_block = (
            "\n\\fancyhf{}\n"
            f"\\fancyhead[L]{{{_topic_hdr}}}\n"
            "\\fancyhead[R]{}\n"
            "\\fancyfoot[C]{\\thepage}\n"
        )
        cleaned = cleaned.replace(r"\pagestyle{fancy}", r"\pagestyle{fancy}" + hdr_block, 1)

    if r"\fancyhead" not in cleaned and r"\begin{document}" in cleaned:
        fhdr = (
            "\n\\pagestyle{fancy}\n\\fancyhf{}\n"
            f"\\fancyhead[L]{{{_topic_hdr}}}\n"
            "\\fancyhead[R]{}\n"
            "\\fancyfoot[C]{\\thepage}\n"
        )
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + fhdr, 1)

    if has_hebrew(cleaned):
        cleaned = fix_hebrew_ltr(cleaned)
        cleaned = fix_hebrew_runs(cleaned)
        cleaned = inject_polyglossia(cleaned)

    tex_path.write_text(cleaned + "\n", encoding="utf-8")
