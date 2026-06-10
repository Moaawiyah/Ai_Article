"""Bracket / citation / text-mode LaTeX repairs."""

from __future__ import annotations

import re

from agent_ai.utils.tex_protected import _PROTECTED

_KNOWN_PKGS = {
    "caption", "float", "booktabs", "graphicx", "amsmath", "amssymb",
    "tikz", "pgfplots", "hyperref", "fontspec", "geometry", "microtype",
}


def fix_bracket_syntax(tex: str) -> str:
    """Repair square-bracket LaTeX args produced when {X} was sanitized to [X]."""
    tex = re.sub(
        r"\\documentclass(\[[^\]]*\])\[([A-Za-z0-9@]+)\]",
        r"\\documentclass\1{\2}", tex,
    )

    def _fix_usepackage(m: re.Match) -> str:
        opt, pkg = m.group(1), m.group(2)
        if opt == pkg:
            return f"\\usepackage{{{pkg}}}"
        if opt.lower() in _KNOWN_PKGS:
            return f"\\usepackage{{{opt}}}\n\\usepackage{{{pkg}}}"
        return m.group(0)
    tex = re.sub(r"\\usepackage\[([A-Za-z0-9]+)\]\{([A-Za-z0-9]+)\}", _fix_usepackage, tex)

    tex = re.sub(r"\\cite\[([A-Za-z][A-Za-z0-9_-]*)\]", r"\\cite{\1}", tex)
    tex = re.sub(r"\\bibitem\[([A-Za-z][A-Za-z0-9_-]*)\]", r"\\bibitem{\1}", tex)
    tex = re.sub(r"\\end\{thebibliography\s*\n", r"\\end{thebibliography}\n", tex)
    return tex


def fix_inline_citations(tex: str) -> str:
    """Convert leftover [N] citation markers to \\cite{refN} outside protected regions."""
    out: list[str] = []
    last = 0
    for m in _PROTECTED.finditer(tex):
        seg = re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\cite{{ref{mm.group(1)}}}', tex[last:m.start()])
        out.append(seg)
        out.append(m.group(0))
        last = m.end()
    out.append(re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\cite{{ref{mm.group(1)}}}', tex[last:]))
    return ''.join(out)


def _fix_free_segment(seg: str) -> str:
    """Repair bare math/special characters in a text-mode (non-protected) segment."""
    seg = re.sub(r"(\w+)\^\{([^}]*)\}", r"$\1^{\2}$", seg)
    seg = re.sub(r"(\w+)\^(\w+)",       r"$\1^{\2}$", seg)
    seg = re.sub(r"(?<!\\)_", r"\\_", seg)
    seg = re.sub(r"(?<!\\)&", r"\\&", seg)
    seg = re.sub(r"(?<!\\)#", r"\\#", seg)
    return seg


def fix_text_mode_math(tex: str) -> str:
    """Wrap bare superscripts and escape stray specials in text mode."""
    out: list[str] = []
    last = 0
    for m in _PROTECTED.finditer(tex):
        out.append(_fix_free_segment(tex[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_fix_free_segment(tex[last:]))
    return "".join(out)
