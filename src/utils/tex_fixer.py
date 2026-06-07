"""Post-processing fixes for LLM-generated LaTeX source."""

from __future__ import annotations

import re
from pathlib import Path


def strip_tex_fences(tex_path: Path) -> None:
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

    # Move fancyhdr setup lines from preamble to after \begin{document}
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

    # Inject minimal fancyhdr setup if the LLM omitted it entirely
    if r"\fancyhead" not in cleaned and r"\begin{document}" in cleaned:
        fhdr = (
            "\n\\pagestyle{fancy}\n\\fancyhead{}\n"
            "\\fancyhead[L]{Article}\n\\fancyhead[R]{\\thepage}\n"
            "\\fancyfoot{}\\fancyfoot[C]{}\n"
        )
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + fhdr, 1)

    tex_path.write_text(cleaned + "\n", encoding="utf-8")


_KNOWN_PKGS = {
    "caption", "float", "booktabs", "graphicx", "amsmath", "amssymb",
    "tikz", "pgfplots", "hyperref", "fontspec", "geometry", "microtype",
}


def fix_bracket_syntax(tex: str) -> str:
    """Fix square-bracket LaTeX args generated when backstory {X} was sanitized to [X]."""
    # \documentclass[opts][class] → \documentclass[opts]{class}
    tex = re.sub(
        r"\\documentclass(\[[^\]]*\])\[([A-Za-z0-9@]+)\]",
        r"\\documentclass\1{\2}", tex,
    )

    # \usepackage[opt]{pkg}: same name → \usepackage{pkg}; known package as opt → split
    def _fix_usepackage(m: re.Match) -> str:
        opt, pkg = m.group(1), m.group(2)
        if opt == pkg:
            return f"\\usepackage{{{pkg}}}"
        if opt.lower() in _KNOWN_PKGS:
            return f"\\usepackage{{{opt}}}\n\\usepackage{{{pkg}}}"
        return m.group(0)
    tex = re.sub(r"\\usepackage\[([A-Za-z0-9]+)\]\{([A-Za-z0-9]+)\}", _fix_usepackage, tex)

    # \cite[key] → \cite{key}  (letter-starting keys, not page numbers)
    tex = re.sub(r"\\cite\[([A-Za-z][A-Za-z0-9_-]*)\]", r"\\cite{\1}", tex)

    # \bibitem[key] → \bibitem{key}
    tex = re.sub(r"\\bibitem\[([A-Za-z][A-Za-z0-9_-]*)\]", r"\\bibitem{\1}", tex)

    # \end{thebibliography missing closing }
    tex = re.sub(r"\\end\{thebibliography\s*\n", r"\\end{thebibliography}\n", tex)

    return tex
