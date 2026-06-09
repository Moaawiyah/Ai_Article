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
    cleaned = fix_tikz_reserved_styles(cleaned)
    cleaned = fix_text_mode_math(cleaned)
    cleaned = fix_tables(cleaned)
    cleaned = fix_inline_citations(cleaned)

    # Ensure bibliography starts on a new page
    if r'\begin{thebibliography}' in cleaned:
        cleaned = re.sub(r'(?:\\newpage\s*\n*)+(?=\\begin\{thebibliography\})', '', cleaned)
        cleaned = cleaned.replace(r'\begin{thebibliography}', '\\newpage\n\\begin{thebibliography}', 1)

    # Ensure \headheight is large enough for fancyhdr (avoids repeated warnings)
    if r'\usepackage{fancyhdr}' in cleaned and r'\setlength{\headheight}' not in cleaned:
        cleaned = cleaned.replace(
            r'\usepackage{fancyhdr}',
            '\\usepackage{fancyhdr}\n\\setlength{\\headheight}{14pt}',
            1,
        )

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


# Regions whose contents are already valid LaTeX and must never be touched:
# math, TikZ, tabular, verbatim, and the bibliography block.
_PROTECTED = re.compile(
    r"\$\$.*?\$\$"                                              # display math $$...$$
    r"|\$[^$]*?\$"                                              # inline math $...$
    r"|\\\[.*?\\\]"                                             # \[ ... \]
    r"|\\\(.*?\\\)"                                             # \( ... \)
    r"|\\begin\{(equation|align|aligned|tikzpicture|tabular|"
    r"verbatim|lstlisting|thebibliography)\*?\}.*?"
    r"\\end\{\1\*?\}",                                          # named environments
    re.DOTALL,
)


# TikZ keys that collide with built-in pgf keys when used as user style names.
_TIKZ_RESERVED = {
    "id", "name", "node", "at", "to", "every", "scale", "shift",
    "label", "text", "draw", "fill", "color", "shape",
    "above", "below", "left", "right", "anchor",
}


def fix_tikz_reserved_styles(tex: str) -> str:
    """Rename user-defined TikZ styles whose names collide with reserved pgf keys.

    E.g. ``id/.style={...}`` + ``\\node[id]`` crashes with
    "The key '/tikz/id' requires a value"; both the definition and every usage
    are renamed to ``idnode`` within each tikzpicture.
    """
    def _fix_pic(m: re.Match) -> str:
        block   = m.group(0)
        defined = set(re.findall(r"([A-Za-z]\w*)/\.style", block))
        for name in sorted(defined & _TIKZ_RESERVED):
            new = f"{name}node"
            block = re.sub(rf"(?<![\w])({re.escape(name)})(?=/\.style)", new, block)
            block = re.sub(rf"(?<![\w/.])({re.escape(name)})(?![\w])", new, block)
        return block

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _fix_pic, tex, flags=re.DOTALL,
    )


def fix_inline_citations(tex: str) -> str:
    """Convert leftover [N] citation markers to \\cite{refN} outside protected regions."""
    out: list[str] = []
    last = 0
    for m in _PROTECTED.finditer(tex):
        seg = re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\\\cite{{ref{mm.group(1)}}}', tex[last:m.start()])
        out.append(seg)
        out.append(m.group(0))
        last = m.end()
    out.append(re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\\\cite{{ref{mm.group(1)}}}', tex[last:]))
    return ''.join(out)


def fix_tables(tex: str) -> str:
    """Wrap every tabular in a table float with adjustbox to prevent page-width overflow."""
    def _wrap(m: re.Match) -> str:
        block = m.group(0)
        if r'\adjustbox' in block or r'\resizebox' in block:
            return block
        block = re.sub(
            r'(\\begin\{tabular\})',
            r'  \\adjustbox{max width=\\textwidth}{\n  \1',
            block, count=1,
        )
        block = re.sub(r'(\\end\{tabular\})', r'\1\n  }', block, count=1)
        return block

    return re.sub(r'\\begin\{table\}.*?\\end\{table\}', _wrap, tex, flags=re.DOTALL)


def _fix_free_segment(seg: str) -> str:
    """Repair bare math/special characters in a text-mode (non-protected) segment."""
    # Superscripts written as prose: 2^{32} or 2^32 → $2^{32}$
    seg = re.sub(r"(\w+)\^\{([^}]*)\}", r"$\1^{\2}$", seg)
    seg = re.sub(r"(\w+)\^(\w+)",       r"$\1^{\2}$", seg)
    # Stray specials that crash text mode (skip already-escaped ones)
    seg = re.sub(r"(?<!\\)_", r"\\_", seg)
    seg = re.sub(r"(?<!\\)&", r"\\&", seg)
    seg = re.sub(r"(?<!\\)#", r"\\#", seg)
    return seg


def fix_text_mode_math(tex: str) -> str:
    """Wrap bare superscripts and escape stray specials in text mode.

    Math, TikZ, tabular, verbatim, and bibliography regions are left untouched so
    that legitimate `^`, `_`, and `&` inside them keep their meaning.
    """
    out: list[str] = []
    last = 0
    for m in _PROTECTED.finditer(tex):
        out.append(_fix_free_segment(tex[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_fix_free_segment(tex[last:]))
    return "".join(out)
