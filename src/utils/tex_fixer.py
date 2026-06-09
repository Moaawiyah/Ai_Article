"""Post-processing fixes for LLM-generated LaTeX source."""

from __future__ import annotations

import re
from pathlib import Path


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

    # Force the left header to the article topic (LLM tends to hardcode "Article")
    _topic_tex = topic.replace("\\", "").replace("&", r"\&").replace("#", r"\#").replace("_", r"\_")
    cleaned = re.sub(
        r"\\fancyhead\[L\]\{[^}]*\}",
        lambda _m: "\\fancyhead[L]{\\small " + _topic_tex + "}",
        cleaned,
    )

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
    cleaned = fix_tabular_colspec(cleaned)
    cleaned = fix_tables(cleaned)
    cleaned = fix_inline_citations(cleaned)
    cleaned = fix_hebrew_ltr(cleaned)
    cleaned = fix_hebrew_runs(cleaned)

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

    # Inject polyglossia BiDi setup if Hebrew content is present but polyglossia is missing
    if _HEBREW_CHAR.search(cleaned) and r'\setotherlanguage{hebrew}' not in cleaned:
        poly = (
            '\\usepackage{polyglossia}\n'
            '\\setmainlanguage{english}\n'
            '\\setotherlanguage{hebrew}\n'
            '\\newfontfamily\\hebrewfont{Times New Roman}[Script=Hebrew]\n'
        )
        if r'\setmainfont{Times New Roman}' in cleaned:
            cleaned = cleaned.replace(
                '\\setmainfont{Times New Roman}',
                '\\setmainfont{Times New Roman}\n' + poly, 1,
            )
        elif r'\usepackage{fontspec}' in cleaned:
            cleaned = cleaned.replace(
                r'\usepackage{fontspec}', r'\usepackage{fontspec}' + '\n' + poly, 1,
            )

    # Inject minimal fancyhdr setup if the LLM omitted it entirely
    if r"\fancyhead" not in cleaned and r"\begin{document}" in cleaned:
        fhdr = (
            "\n\\pagestyle{fancy}\n\\fancyhead{}\n"
            "\\fancyhead[L]{\\small " + _topic_tex + "}\n\\fancyhead[R]{\\thepage}\n"
            "\\fancyfoot{}\\fancyfoot[C]{\\thepage}\n"
        )
        cleaned = cleaned.replace(r"\begin{document}", r"\begin{document}" + fhdr, 1)

    # Page number belongs in the centre footer, not the header. Strip any placeholder
    # footer text (the LLM tends to drop a course placeholder there) and clear the header page no.
    if r"\pagestyle{fancy}" in cleaned:
        cleaned = re.sub(r"(\\fancyhead\[R\])\{[^}]*\}", r"\1{}", cleaned)
        if r"\fancyfoot[C]" in cleaned:
            cleaned = re.sub(r"(\\fancyfoot\[C\])\{[^}]*\}", r"\1{\\thepage}", cleaned)
        else:
            cleaned = cleaned.replace(
                r"\pagestyle{fancy}", "\\pagestyle{fancy}\n\\fancyfoot[C]{\\thepage}", 1,
            )

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
    r"verbatim|lstlisting|thebibliography|hebrew)\*?\}.*?"
    r"\\end\{\1\*?\}",                                          # named environments
    re.DOTALL,
)


# Any Hebrew codepoint — used to decide whether polyglossia setup is needed.
_HEBREW_CHAR = re.compile(r"[֐-׿]")

# A run of Hebrew text on one line: from the first Hebrew char to the last Hebrew
# char on that line, keeping any English terms/digits in between (luabidi reorders them).
_HEBREW_RUN = re.compile(r"[֐-׿](?:[^\n]*[֐-׿])?")

# Protected regions PLUS already-wrapped Hebrew, so fix_hebrew_runs is idempotent.
_PROTECTED_HEB = re.compile(_PROTECTED.pattern + r"|\\texthebrew\{[^{}]*\}", re.DOTALL)


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


# Inside a Hebrew (RTL) block, match either a LaTeX command (+ optional brace arg) to leave
# untouched, or a run of Latin text to wrap in \textenglish{} for correct LTR rendering.
_CMD_OR_LATIN = re.compile(
    r"(\\[a-zA-Z@]+\*?(?:\{[^{}]*\})?)"                          # group 1: LaTeX command+arg
    r"|([A-Za-z][A-Za-z0-9./+\-]*(?:\s+[A-Za-z0-9./+\-]+)*)",    # group 2: English run
)


def fix_hebrew_ltr(tex: str) -> str:
    """Wrap English runs inside Hebrew RTL blocks with \\textenglish{} for correct LTR direction.

    LaTeX commands (e.g. ``\\section*{...}``, ``\\cite{refN}``, already-present
    ``\\textenglish{...}``) are matched first and left untouched; only bare Latin runs are wrapped.
    Hebrew characters and standalone digits are left as-is.
    """
    def _wrap_run(m: re.Match) -> str:
        if m.group(1) is not None:          # a LaTeX command — keep verbatim
            return m.group(1)
        return f"\\textenglish{{{m.group(2)}}}"

    def _fix_block(m: re.Match) -> str:
        return _CMD_OR_LATIN.sub(_wrap_run, m.group(0))

    return re.sub(
        r"\\begin\{hebrew\}.*?\\end\{hebrew\}",
        _fix_block, tex, flags=re.DOTALL,
    )


def fix_hebrew_runs(tex: str) -> str:
    """Wrap inline Hebrew runs in \\texthebrew{...} so they render RTL inside the LTR document.

    The document's main language is English (LTR). Bare Hebrew sentences in the body are wrapped
    as RTL islands. Protected regions (math, TikZ, tables, bibliography, ``\\begin{hebrew}`` blocks)
    and already-wrapped ``\\texthebrew{...}`` runs are skipped, so the pass is idempotent.
    """
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


def fix_tabular_colspec(tex: str) -> str:
    """Repair tabular column specs with a bare ``p``/``m``/``b`` (these require a width arg).

    The LLM sometimes emits e.g. ``\\begin{tabular}{llccp}`` — a paragraph column with no width,
    which crashes with "Missing p-arg in array arg". Bare ``p``/``m``/``b`` (not followed by a
    ``{width}``) are converted to ``l``; adjustbox already keeps the table within the page width.
    """
    def _fix(m: re.Match) -> str:
        spec = m.group(1)
        out: list[str] = []
        i = 0
        while i < len(spec):
            ch = spec[i]
            if ch == "{":                              # skip a {…} group (e.g. p{3cm}, >{…})
                j = spec.find("}", i)
                if j == -1:
                    out.append(spec[i:]); break
                out.append(spec[i:j + 1]); i = j + 1
            elif ch in "pmb":                          # p/m/b need a {width}; bare ones → l
                nxt = spec[i + 1] if i + 1 < len(spec) else ""
                out.append(ch if nxt in ("{", "[") else "l")
                i += 1
            else:
                out.append(ch); i += 1
        return "\\begin{tabular}{" + "".join(out) + "}"

    # Match the column-spec braces allowing one level of nested {…} (e.g. p{3cm}).
    return re.sub(
        r"\\begin\{tabular\}\{((?:[^{}]|\{[^{}]*\})*)\}",
        _fix, tex,
    )


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
