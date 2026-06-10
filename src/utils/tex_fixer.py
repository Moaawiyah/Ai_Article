"""Post-processing fixes for LLM-generated LaTeX source."""

from __future__ import annotations

import re
from pathlib import Path


# ── Hebrew helpers ────────────────────────────────────────────────────────────
_HEBREW_CHAR = re.compile(r"[ְ-׿יִ-פֿ]")
_HEBREW_RUN = re.compile(
    r"[ְ-׿יִ-פֿ]"
    r"(?:[^\n]*[ְ-׿יִ-פֿ])?"
)


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
    cleaned = fix_tikz_node_linebreaks(cleaned)
    cleaned = fix_tikz_reserved_styles(cleaned)
    cleaned = fix_text_mode_math(cleaned)
    cleaned = fix_tables(cleaned)
    cleaned = fix_inline_citations(cleaned)
    cleaned = fix_tabular_colspec(cleaned)

    # Ensure bibliography starts on a new page
    if r'\begin{thebibliography}' in cleaned:
        cleaned = re.sub(r'(?:\\newpage\s*\n*)+(?=\\begin\{thebibliography\})', '', cleaned)
        cleaned = cleaned.replace(r'\begin{thebibliography}', '\\newpage\n\\begin{thebibliography}', 1)

    # Ensure \headheight is at least 15pt (needed for \small topic text in header)
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

    # ── Header / footer normalization ─────────────────────────────────────────
    _topic_tex = (topic
                  .replace("\\", "")
                  .replace("&", r"\&")
                  .replace("#", r"\#")
                  .replace("_", r"\_"))
    _topic_hdr = f"\\small {_topic_tex}"

    if r"\pagestyle{fancy}" in cleaned:
        # Wipe all existing individual header/footer assignments, then reinject cleanly
        cleaned = re.sub(r"\\fancyhead(\[[^\]]*\])?\{[^}]*\}", "", cleaned)
        cleaned = re.sub(r"\\fancyfoot(\[[^\]]*\])?\{[^}]*\}", "", cleaned)
        cleaned = re.sub(r"\\fancyhf\{[^}]*\}\n?", "", cleaned)
        hdr_block = (
            f"\n\\fancyhf{{}}\n"
            f"\\fancyhead[L]{{{_topic_hdr}}}\n"
            "\\fancyhead[R]{}\n"
            "\\fancyfoot[C]{\\thepage}\n"
        )
        cleaned = cleaned.replace(r"\pagestyle{fancy}", r"\pagestyle{fancy}" + hdr_block, 1)

    # Inject minimal fancyhdr setup if the LLM omitted it entirely
    if r"\fancyhead" not in cleaned and r"\begin{document}" in cleaned:
        fhdr = (
            f"\n\\pagestyle{{fancy}}\n\\fancyhf{{}}\n"
            f"\\fancyhead[L]{{{_topic_hdr}}}\n"
            "\\fancyhead[R]{}\n"
            "\\fancyfoot[C]{\\thepage}\n"
        )
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + fhdr, 1)
    # ─────────────────────────────────────────────────────────────────────────

    # ── Hebrew / polyglossia ──────────────────────────────────────────────────
    if _HEBREW_CHAR.search(cleaned):
        cleaned = fix_hebrew_ltr(cleaned)
        cleaned = fix_hebrew_runs(cleaned)
        if r'\setotherlanguage{hebrew}' not in cleaned:
            poly = (
                "\n\\usepackage{polyglossia}\n"
                "\\setdefaultlanguage{english}\n"
                "\\setotherlanguage{hebrew}\n"
                "\\newfontfamily\\hebrewfont[Script=Hebrew]{Times New Roman}\n"
            )
            if r'\setmainfont' in cleaned:
                cleaned = re.sub(
                    r'(\\setmainfont\{[^}]+\})',
                    lambda m: m.group(1) + poly,
                    cleaned, count=1,
                )
            elif r'\usepackage{fontspec}' in cleaned:
                cleaned = cleaned.replace(
                    r'\usepackage{fontspec}',
                    '\\usepackage{fontspec}' + poly,
                    1,
                )
    # ─────────────────────────────────────────────────────────────────────────

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
# math, TikZ, tabular, verbatim, bibliography, and Hebrew environments.
_PROTECTED = re.compile(
    r"\$\$.*?\$\$"                                              # display math $$...$$
    r"|\$[^$]*?\$"                                              # inline math $...$
    r"|\\\[.*?\\\]"                                             # \[ ... \]
    r"|\\\(.*?\\\)"                                             # \( ... \)
    r"|\\begin\{(equation|align|aligned|tikzpicture|tabular|"
    r"verbatim|lstlisting|thebibliography|hebrew)\*?\}.*?"
    r"\\end\{\1\*?\}",                                          # named environments
    re.DOTALL,
)

# Same as _PROTECTED but also shields already-wrapped \texthebrew{...} from double-wrapping.
_PROTECTED_HEB = re.compile(
    _PROTECTED.pattern + r"|\\texthebrew\{[^{}]*\}",
    re.DOTALL,
)


# TikZ keys that collide with built-in pgf keys when used as user style names.
_TIKZ_RESERVED = {
    "id", "name", "node", "at", "to", "every", "scale", "shift",
    "label", "text", "draw", "fill", "color", "shape",
    "above", "below", "left", "right", "anchor",
}


def fix_tikz_node_linebreaks(tex: str) -> str:
    """Add align=center to TikZ nodes whose label contains \\\\ (not allowed in LR mode)."""
    def _fix_pic(m: re.Match) -> str:
        block = m.group(0)

        def _fix_node(nm: re.Match) -> str:
            full  = nm.group(0)
            opts  = nm.group(1)   # "[...]" including brackets, or None
            label = nm.group(2)
            if "\\\\" not in label:
                return full
            if opts and "align" in opts:
                return full
            if opts:
                new_opts = opts[:-1] + ", align=center]"
                return full.replace(opts, new_opts, 1)
            return full.replace("\\node ", "\\node[align=center] ", 1)

        return re.sub(
            r"\\node(\[[^\]]*\])?\s*(?:\([^)]*\))?\s*\{([^}]*)\}",
            _fix_node, block,
        )

    return re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        _fix_pic, tex, flags=re.DOTALL,
    )


def fix_tikz_reserved_styles(tex: str) -> str:
    """Rename user-defined TikZ styles whose names collide with reserved pgf keys."""
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
        seg = re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\cite{{ref{mm.group(1)}}}', tex[last:m.start()])
        out.append(seg)
        out.append(m.group(0))
        last = m.end()
    out.append(re.sub(r'\[(\d{1,2})\]', lambda mm: f'\\cite{{ref{mm.group(1)}}}', tex[last:]))
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


def fix_tabular_colspec(tex: str) -> str:
    """Convert bare p/m/b column specs (no width arg) to p{3.5cm} so text wraps.

    Leaves p{3cm} and similar already-sized specs untouched.
    """
    def _fix(m: re.Match) -> str:
        spec = m.group(1)
        out: list[str] = []
        i = 0
        while i < len(spec):
            ch = spec[i]
            if ch == "{":
                j = spec.find("}", i)
                out.append(spec[i:j + 1])
                i = j + 1
            elif ch in "pmb":
                nxt = spec[i + 1] if i + 1 < len(spec) else ""
                out.append(ch if nxt in ("{", "[") else "p{3.5cm}")
                i += 1
            else:
                out.append(ch)
                i += 1
        return "\\begin{tabular}{" + "".join(out) + "}"

    return re.sub(r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}", _fix, tex)


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
    """Wrap bare superscripts and escape stray specials in text mode."""
    out: list[str] = []
    last = 0
    for m in _PROTECTED.finditer(tex):
        out.append(_fix_free_segment(tex[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_fix_free_segment(tex[last:]))
    return "".join(out)


# ── Hebrew-specific fixers ────────────────────────────────────────────────────

# Matches a LaTeX command (optionally with one {arg}) or a Latin-letter run.
_CMD_OR_LATIN = re.compile(
    r"(\\[a-zA-Z@]+\*?(?:\{[^{}]*\})?)"                          # group 1: LaTeX cmd → keep
    r"|([A-Za-z][A-Za-z0-9./+\-]*(?:\s+[A-Za-z0-9./+\-]+)*)",   # group 2: Latin run → wrap
)


def fix_hebrew_ltr(tex: str) -> str:
    """Inside every begin-hebrew/end-hebrew block, wrap Latin runs in textenglish."""
    def _wrap_run(m: re.Match) -> str:
        if m.group(1) is not None:
            return m.group(1)
        return f"\\textenglish{{{m.group(2)}}}"

    def _fix_block(m: re.Match) -> str:
        return _CMD_OR_LATIN.sub(_wrap_run, m.group(0))

    return re.sub(
        r"\\begin\{hebrew\}.*?\\end\{hebrew\}",
        _fix_block, tex, flags=re.DOTALL,
    )


def fix_hebrew_runs(tex: str) -> str:
    """Wrap bare Hebrew character runs in texthebrew outside all protected regions."""
    def _wrap(seg: str) -> str:
        return _HEBREW_RUN.sub(lambda r: f"\\texthebrew{{{r.group(0)}}}", seg)

    out: list[str] = []
    last = 0
    for m in _PROTECTED_HEB.finditer(tex):
        out.append(_wrap(tex[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_wrap(tex[last:]))
    return "".join(out)
