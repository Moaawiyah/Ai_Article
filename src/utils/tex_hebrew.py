"""Hebrew / polyglossia post-processing: BiDi wrappers for mixed-script source."""

from __future__ import annotations

import re

from utils.tex_protected import _PROTECTED_HEB

_HEBREW_CHAR = re.compile(r"[ְ-׿יִ-פֿ]")
_HEBREW_RUN = re.compile(
    r"[ְ-׿יִ-פֿ]"
    r"(?:[^\n]*[ְ-׿יִ-פֿ])?"
)

_CMD_OR_LATIN = re.compile(
    r"(\\[a-zA-Z@]+\*?(?:\{[^{}]*\})?)"
    r"|([A-Za-z][A-Za-z0-9./+\-]*(?:\s+[A-Za-z0-9./+\-]+)*)",
)


def has_hebrew(tex: str) -> bool:
    """Return True if any Hebrew character appears in *tex*."""
    return bool(_HEBREW_CHAR.search(tex))


def fix_hebrew_ltr(tex: str) -> str:
    """Inside every begin-hebrew/end-hebrew block, wrap Latin runs in textenglish."""
    def _wrap_run(m: re.Match) -> str:
        """Leave LaTeX commands untouched; wrap Latin text runs in \\textenglish."""
        if m.group(1) is not None:
            return m.group(1)
        return f"\\textenglish{{{m.group(2)}}}"

    def _fix_block(m: re.Match) -> str:
        """Apply the Latin-run wrapping inside one hebrew environment block."""
        return _CMD_OR_LATIN.sub(_wrap_run, m.group(0))

    return re.sub(
        r"\\begin\{hebrew\}.*?\\end\{hebrew\}",
        _fix_block, tex, flags=re.DOTALL,
    )


def fix_hebrew_runs(tex: str) -> str:
    """Wrap bare Hebrew character runs in texthebrew outside all protected regions."""
    def _wrap(seg: str) -> str:
        """Wrap bare Hebrew character runs in *seg* with \\texthebrew."""
        return _HEBREW_RUN.sub(lambda r: f"\\texthebrew{{{r.group(0)}}}", seg)

    out: list[str] = []
    last = 0
    for m in _PROTECTED_HEB.finditer(tex):
        out.append(_wrap(tex[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_wrap(tex[last:]))
    return "".join(out)


def inject_polyglossia(tex: str) -> str:
    """Insert polyglossia + Hebrew font setup after fontspec / setmainfont."""
    if r'\setotherlanguage{hebrew}' in tex:
        return tex
    poly = (
        "\n\\usepackage{polyglossia}\n"
        "\\setdefaultlanguage{english}\n"
        "\\setotherlanguage{hebrew}\n"
        "\\newfontfamily\\hebrewfont[Script=Hebrew]{Times New Roman}\n"
    )
    if r'\setmainfont' in tex:
        return re.sub(
            r'(\\setmainfont\{[^}]+\})',
            lambda m: m.group(1) + poly,
            tex, count=1,
        )
    if r'\usepackage{fontspec}' in tex:
        return tex.replace(
            r'\usepackage{fontspec}',
            '\\usepackage{fontspec}' + poly,
            1,
        )
    return tex
